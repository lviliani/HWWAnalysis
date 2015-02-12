#!/usr/bin/env python

import sys
import ROOT
import os
import re
import glob
import optparse
import hwwinfo
import hwwsamples
import hwwtools
import numpy
import array
import bisect
import datadriven
import logging

#  __  __                      
# |  \/  |___ _ _ __ _ ___ _ _ 
# | |\/| / -_) '_/ _` / -_) '_|
# |_|  |_\___|_| \__, \___|_|  
#                |___/         


class ShapeMerger:
    _logger = logging.getLogger('ShapeMerger')
    def __init__(self, simask = None, fillEmptyBins = False):
        self.sets = []
        self.histograms = {}
        self.processes = []
        self._simask = simask
        self.fillEmptyBins = fillEmptyBins

    def add(self,s):
        # add a collection to be summed
        self.sets.append(s)

    def sum(self):
        # sum the collections together
        if len(self.sets) == 0:
            print 'No sets defined'
            return
        

        # collect processames
        procs = set()
        for s in self.sets:
            procs |= set(s.nominals)

        self.processes = list(procs)

        # build an histogram template
        shapes = {}
        
        # loop over all the sets
        for s in self.sets:
            for n,h in s.histograms.iteritems():
                if n in shapes:
                    continue
                # ->> ninja
                dummy = h.Clone()

                dummy.Reset()
                shapes[n] = dummy

        for n,h in shapes.iteritems():
            for s in self.sets:
                if n not in s.histograms:
                    self._logger.info('Warning: '+n+' is not available in set '+s.label)
                    continue
                dummy = s.histograms[n]
                h2add = dummy.Clone()
                h.Add(h2add)

            # remove the negative bins before storing it
            self._removeNegativeBins(h)
            if self.fillEmptyBins and "Data" not in n: self._fillEmptyBins(h)
            self.histograms[n] = h


    def injectSignal(self):
        signals = hwwsamples.signals
        if 'Data' in self.histograms:
            return

        print ' '*4+' - injecting signal!'
        nomRegex = re.compile('^([^ ]+)$')
        injRegex = re.compile('^([^ ]+)-SI$')

        sisignals = [ n for n in self.processes if injRegex.match(n) ]
        backgrounds = [ n for n in self.histograms if n not in sisignals and n not in signals and nomRegex.match(n) ]

        # filter the sisignals on simask
        injected = [ n for n in sisignals if n[:-3] in self._simask ] if self._simask else sisignals 

        pseudo = self.histograms[backgrounds[0]].Clone('histo_PseudoData')
        pseudo.SetTitle('Data')
        pseudo.Reset()
        inputs = []
        inputs.extend(injected)
        inputs.extend(backgrounds)

        # remove "CHI" in the list of backgrounds for signal injection
        #print " BEFORE   ", inputs
        #inputs = filter(lambda a: a != "CHITOP-Top", inputs)
        inputs = filter(lambda a: "CHI" not in a, inputs)
        #print " FILTERED ", inputs


        for n in inputs:
            self._logger.debug('SI: adding %s',n)
            pseudo.Add(self.histograms[n])
            #print "integral [", self.histograms[n].GetTitle(), "] = ", self.histograms[n].Integral() , " --> ", pseudo.Integral ()

        # remove the injected from the histograms and processes
        map(self.histograms.pop,   sisignals)
        map(self.processes.remove, sisignals)

        nBins = pseudo.GetNbinsX()
        xax = pseudo.GetXaxis()

        data = pseudo.Clone('histo_Data')
        data.SetTitle('Data')
        data.Reset()

        for i in xrange(1,nBins+1):
            entries = ROOT.TMath.Nint(pseudo.GetAt(i)) 
            for j in xrange(entries):
                data.Fill(xax.GetBinCenter(i))

        self.histograms['Data'] = data
        self.processes.append('Data')

    
    def _removeNegativeBins(self,h):
        # move it in the merger as last step
        # TODO

        integral = h.Integral() if h.Integral() >=0 else 0.001 
        for i in xrange(1,h.GetNbinsX()+1):
            c = h.GetBinContent(i)
            if c < 0.:
                h.SetAt(0.,i)
        if 'WJet' in h.GetName():
            self._logger.debug('Neg Bins removal %-50s : %.3f %.3f',h.GetName(),integral,h.Integral())

        if h.Integral() > 0:
            h.Scale(integral/h.Integral())


    def _fillEmptyBins(self,h):
        
        integral = h.Integral() if h.Integral() >=0 else 0.001
        for i in xrange(1,h.GetNbinsX()+1):
            c = h.GetBinContent(i)
            if c < 0.00001:
                filling = 0.001 if integral>1 else 0.001*integral
                h.SetAt(filling,i)
                h.SetBinError(i,filling)
            
        if h.Integral() > 0:
            h.Scale(integral/h.Integral())


    def applyDataDriven(self, mass,estimates):
        ''' rescale to the data driven estimates if available'''
        for p,e in estimates.iteritems():
            # p is "Top", "DYmm", ... only the ones that are datadriven

            nominal = self.histograms[p]
            proRegex = re.compile('^'+p+' .+')
            # move here the selection on 
            shapes = [ h for n,h in self.histograms.iteritems() if proRegex.match(n) ]

            shapes.append(nominal)

            for shape in shapes:
                # shape.GetName() e.g. histo_Top_CMS_8TeV_hww_Top_of_2j_stat_shapeUp
                if shape.Integral() == 0.: 
                    self._logger.warning('Empty histogram: '+p)
                    continue
                self._logger.debug('DD to %-50s : %.3f -> %.3f',shape.GetName(), shape.Integral(), e.Nsig())

                # - check if there are "CHI" regions (CHI samples), where datadriven estimations have been performed
                # p = "Top"

                #  e.g. histo_Top_CMS_8TeV_hww_Top_of_2j_stat_shapeUp
                reducedName = shape.GetName()
                #  e.g.       Top_CMS_8TeV_hww_Top_of_2j_stat_shapeUp
                reducedName = reducedName[6:]

                foundCHI = False
                for vNameHisto,vHisto in self.histograms.iteritems() :
                  reducedNameInHisto = vHisto.GetName()
                  reducedNameInHisto = reducedNameInHisto[6:]

                  if reducedNameInHisto == 'CHITOP-'+reducedName :
                    # scale by datadriven/systematics at CHI level, so that at CHI level, the two coincide
                    scaleFactor = e.Nsig()/vHisto.Integral()
                    scaleFactorToScaleAlpha = shape.Integral()/vHisto.Integral()
                    shape.Scale(scaleFactor)
                    print "ScaleFactor[",reducedName,",",shape.GetName(),"] = ",scaleFactor

                    if reducedNameInHisto == 'CHITOP-'+p : # the nominal!
                        card = open( "ScaleFactors.py" ,"a")
                        card.write('scaleFactor.update({%d' % mass + ': {\'%s' % reducedNameInHisto + '\': %-.5f' % scaleFactorToScaleAlpha + '}})\n')
                        card.close()

                    foundCHI = True

                  #
                  # Nsig = Nctr * alpha
                  #
                  # the statistical fluctuation fails with this "string" test:
                  #     e.g. Top_CMS_8TeV_hww_Top_of_2j_stat_shapeDown
                  #specialReducedName = 'CHITOP-',p
                  if reducedNameInHisto.startswith("CHITOP-"+p) and ( (reducedNameInHisto.endswith("_stat_shapeDown") and reducedName.endswith("_stat_shapeDown")) or (reducedNameInHisto.endswith("_stat_shapeUp") and reducedName.endswith("_stat_shapeUp")) ):
                    scaleFactor = e.Nsig()/vHisto.Integral()
                    shape.Scale(scaleFactor)
                    print "special (statistical) ScaleFactor[",reducedName,",",shape.GetName(),"] = ",scaleFactor
                    foundCHI = True

                  #
                  # only for bin-by-bin case:
                  #    -> at CHI level there may be bbb fluctuations
                  #    -> the only constraint is that at CHI level the normalization MUST be the datadriven one
                  #    -> then we apply a scale factor as for the global statistical fluctuation, as in the "unified" approach
                  #
                  # the statistical fluctuation fails with this "string" test:
                  #     e.g. Top_CMS_8TeV_hww_Top_of_2j_stat_shape_bin1Down   does not match with     CHITOP-Top_CMS_8TeV_hww_CHITOP-Top_of_2j_stat_shape_bin1Down
                  #
                  for iBin in range(0,shape.GetNbinsX()) :
                     #if reducedNameInHisto.startswith("CHITOP-"+p) : 
                         #print "     >>>> reducedNameInHisto = "+reducedNameInHisto
                         #print "      <<< reducedName = "+reducedName
                         # e.g. CHITOP-Top_CMS_8TeV_hww_CHITOP-Top_of_2j_stat_shape_bin6Down
                         #      CHITOP-Top   ---> then ok first test
                         #                                              _stat_shape_bin6Down   ---> then ok next step
                     if reducedNameInHisto.startswith("CHITOP-"+p) and (
                           (reducedNameInHisto.endswith("_stat_shape_bin"+str(iBin+1)+"Down") and reducedName.endswith("_stat_shape_bin"+str(iBin+1)+"Down")) 
                           or
                           (reducedNameInHisto.endswith("_stat_shape_bin"+str(iBin+1)+"Up") and reducedName.endswith("_stat_shape_bin"+str(iBin+1)+"Up")) ):
                        scaleFactor = e.Nsig()/vHisto.Integral()
                        shape.Scale(scaleFactor)
                        print "special (statistical bin) ScaleFactor[",reducedName,",",shape.GetName(),"] = ",scaleFactor
                        foundCHI = True

                if not foundCHI :
                  # "normal" data driven
                  print "normal ScaleFactor[",reducedName,",",shape.GetName(),"] = ",e.Nsig()/shape.Integral()
                  shape.Scale(e.Nsig()/shape.Integral())



    def applyDataDrivenRelative(self, estimates):
        ''' rescale to the data driven estimates if available'''
        for p,e in estimates.iteritems():
            print 'DEBUG ---> DD',p
            nominal = self.histograms[p]
            if nominal.Integral() == 0:
                print 'Empty histogram',p,': Data driven rescaling skipped'
                continue
            proRegex = re.compile('^'+p+' .+')
            shapes = [ h for n,h in self.histograms.iteritems() if proRegex.match(n) ]
            if p == 'DYLL':
                print '+'*20
                print p,' Nsig', e.Nsig(),'  Nctrl', e.Nctr,' alpha', e.alpha,'dalpha',e.delta
                print p,nominal.Integral()
                print '+'*20
            factor = e.Nsig()/nominal.Integral()
            shapes.append(nominal)

            for shape in shapes:
                shape.Scale(factor)

    def save(self, path):
        # save the final output file
        outFile = ROOT.TFile.Open(path,'recreate')
        for n,h in self.histograms.iteritems():
            h.Write()

        names = ROOT.TObjArray()
        for name in self.processes:
            names.Add(ROOT.TObjString(name))

        names.Write('processes',ROOT.TObject.kSingleKey)

        outFile.Close()



#  __  __ _             
# |  \/  (_)_ _____ _ _ 
# | |\/| | \ \ / -_) '_|
# |_|  |_|_/_\_\___|_|  


class ShapeMixer:
    _logger = logging.getLogger('ShapeMixer')
    def __init__(self, label):
        self.label = label
        self.rebin = 1
        self.nominalsPath = None
        self.systSearchPath = None
        self.histograms = {}

        self.nominals = {}
        self.statistical = {}
        self.experimental = {}
        self.generators = {}
        self.fakerate = {}
        self.templates = {}
        
        self.factors  = {}
        self.indent   = 4
        self.nameMap  = {}
        self.lumiMask = []
        self.lumi     = 1.
        self.statmode = 'unified'

    def __del__(self):
        self._disconnect()
    
    def _connect(self,iCP2 , iBRn):
        self._logger.debug('Opening '+self.nominalsPath)
        if not os.path.exists(self.nominalsPath):
            raise IOError('Root file '+self.nominalsPath+' doesn\'t exists.')
        self.shapeFile = ROOT.TFile.Open(self.nominalsPath)
        self.systFiles = {}
        for file in glob.glob(self.systSearchPath):
            if opt.ewksinglet:
              m = re.search('_(e|m)(e|m).EWKSinglet_CP2_'+str(opt.cprimesq[iCP2]).replace('.','d')+'_BRnew_'+str(opt.brnew[iBRn]).replace('.','d')+'_(.*).root',file)
            else:
              m = re.search('_(e|m)(e|m)_(.*).root',file)
            if m is None:
                raise NameError('something went wrong, this \''+file+'\' doesn\'t look like a experimental file')
            self.systFiles[m.group(3)] = ROOT.TFile.Open(file)

    def _remodel(self,h):
        nBins = h.GetNbinsX()
        entries = h.GetEntries()
        underFlow = h.GetBinContent(0)
        overFlow  = h.GetBinContent(nBins+1)
        bin1      = h.GetBinContent(1)
        binN      = h.GetBinContent(nBins)

        h.SetAt(0.,0)
        h.SetAt(underFlow+bin1,1)
        h.SetAt(overFlow+binN, nBins)
        h.SetAt(0.,nBins+1,)
        h.Rebin(self.rebin)


    def _mirror(self,process, nom, shift, systName, scale2Nom = False):
        up = shift.Clone('histo_'+process+'_'+systName+'Up')
        up.SetTitle(process+' '+systName+' Up')
        # rescale before mirroring, if necessary
        if scale2Nom:
            up.Scale(nom.Integral()/up.Integral())

        down = nom.Clone('histo_'+process+'_'+systName+'Down')
        down.SetTitle(process+' '+systName+' Down')
        down.Scale(2.)
        down.Add(up,-1)
        # rescale if necessary
        if scale2Nom:
            down.Scale(nom.Integral()/down.Integral())

        return (up, down)


    @staticmethod
    def _pushbin(h,bin,alpha):
        c = h.GetBinContent(bin)
        e = h.GetBinError(bin)
        x = c+alpha*e
        h.SetAt( x if x > 0. else c*0.001, bin)

    @staticmethod
    def _morphstat(h, eff):

        nx = h.GetNbinsX()
        statName  = h.GetName()+'_'+eff
        statTitle = h.GetTitle()+' '+eff

        morphed = {}

        # global shape morphing 
        # clone the nominal twice
        statUp = h.Clone(statName+'Up')
        statUp.SetTitle(statTitle+' Up')

        statDown = h.Clone(statName+'Down')
        statDown.SetTitle(statTitle+' Down')

        morphed[statUp.GetTitle()] = statUp
        morphed[statDown.GetTitle()] = statDown

        # the histogram is empty, skip the rest
        if h.GetEntries() == 0. and h.Integral() == 0.0: return morphed

        for i in xrange(0,nx+2):
            ShapeMixer._pushbin(statUp,  i, +1)
            ShapeMixer._pushbin(statDown,i, -1)

        # rescale to the original, shape only
        if statUp.Integral() != 0.:
            statUp.Scale(h.Integral()/statUp.Integral())
        # rescale to the original, shape only
        if statDown.Integral() != 0.:
            statDown.Scale(h.Integral()/statDown.Integral())

        return morphed

    @staticmethod
    def _morphstatbbb(h, eff):

        nx = h.GetNbinsX()
        statName  = h.GetName()+'_'+eff
        statTitle = h.GetTitle()+' '+eff

        morphed = {}
        # bin-by-bin morphing
        # clone the histogram once per bin
        for i in xrange(1,nx+1):
            binName  = '{0}_bin{1}'.format(statName,i) 
            binTitle = '{0}_bin{1}'.format(statTitle,i) 

            binUp   = h.Clone(binName+'Up' )
            binUp.SetTitle(binTitle+' Up' )
            binDown = h.Clone(binName+'Down' )
            binDown.SetTitle(binTitle+' Down' )

            morphed[binUp.GetTitle()] = binUp
            morphed[binDown.GetTitle()] = binDown

            # the histogram is empty, skip the rest
            if h.GetEntries() == 0. and h.Integral() == 0.0: continue
            
            ShapeMixer._pushbin( binUp,   i, +1)
            ShapeMixer._pushbin( binDown, i, -1)

            if i == 1:
                ShapeMixer._pushbin( binUp,   0, +1)
                ShapeMixer._pushbin( binDown, 0, -1)
            elif i == nx:
                ShapeMixer._pushbin( binUp,   nx, +1)
                ShapeMixer._pushbin( binDown, nx, -1)

            # rescale to the original, shape only
            if binUp.Integral() != 0.:
                binUp.Scale(h.Integral()/binUp.Integral())

            # rescale to the original, shape only
            if binDown.Integral() != 0.:
                binDown.Scale(h.Integral()/binDown.Integral())

        return morphed


    # ---
    def mix(self, chan, scale2nom , iCP2 , iBRn ):
        # mixing histograms

        self._connect(iCP2 , iBRn)

        suffix = '_'+opt.energy

        # -----------------------------------------------------------------
        # Nominal shapes
        #
        for k in self.shapeFile.GetListOfKeys():
            h = k.ReadObj()
            # only 1d histograms supported
            if h.GetDimension() != 1: 
                continue
            self._remodel(h)
            self.nominals[h.GetTitle()] = h

            #print h.GetTitle()
            #print h.Integral()

        # -----------------------------------------------------------------
        # WJet shape syst
        #
        #   - add the WJets shape systematics derived from miscalculated weights
        #   e and mu fake separated
        #   - shape variation is taken w.r.t. the "nominal"
        #   - WJetFakeRate-nominal is needed for 7 TeV where the variation
        #   is taken from 8 TeV sample and has to be transformed relative
        #   to the 7 TeV nominal template

        wJet = self.nominals['WJet']
        if 'WJetFakeRate-nominal' in self.nominals :
            wJetSystNom = self.nominals.pop('WJetFakeRate-nominal')
        else : wJetSystNom = 0.

        if 'WJetFakeRate-eUp' in self.nominals:
            wJetSystName = 'CMS{0}_hww_WJet_FakeRate_e_shape'.format(suffix)
            wJetEffeUp = self.nominals.pop('WJetFakeRate-eUp')
            wJetShapeUp = wJetEffeUp.Clone('histo_WJet_'+wJetSystName+'Up')
            wJetShapeUp.SetTitle('WJet '+wJetSystName+' Up')
            if wJetSystNom : wJetShapeUp.Divide(wJetSystNom)
            if wJetSystNom : wJetShapeUp.Multiply(wJet)
            #wJetShapeUp.Scale(wJet.Integral()/wJetShapeUp.Integral())
            self.fakerate[wJetShapeUp.GetTitle()] = wJetShapeUp

        if 'WJetFakeRate-eDn' in self.nominals:
            wJetSystName = 'CMS{0}_hww_WJet_FakeRate_e_shape'.format(suffix)
            wJetEffeDown = self.nominals.pop('WJetFakeRate-eDn')
            wJetShapeDown = wJetEffeDown.Clone('histo_WJet_'+wJetSystName+'Down')
            wJetShapeDown.SetTitle('WJet '+wJetSystName+' Down')
            if wJetSystNom : wJetShapeDown.Divide(wJetSystNom)
            if wJetSystNom : wJetShapeDown.Multiply(wJet)
            #wJetShapeDown.Scale(wJet.Integral()/wJetShapeDown.Integral())
            self.fakerate[wJetShapeDown.GetTitle()] = wJetShapeDown

        if 'WJetFakeRate-mUp' in self.nominals:
            wJetSystName = 'CMS{0}_hww_WJet_FakeRate_m_shape'.format(suffix)
            wJetEffmUp = self.nominals.pop('WJetFakeRate-mUp')
            wJetShapeUp = wJetEffmUp.Clone('histo_WJet_'+wJetSystName+'Up')
            wJetShapeUp.SetTitle('WJet '+wJetSystName+' Up')
            if wJetSystNom : wJetShapeUp.Divide(wJetSystNom)
            if wJetSystNom : wJetShapeUp.Multiply(wJet)
            #wJetShapeUp.Scale(wJet.Integral()/wJetShapeUp.Integral())
            self.fakerate[wJetShapeUp.GetTitle()] = wJetShapeUp

        if 'WJetFakeRate-mDn' in self.nominals:
            wJetSystName = 'CMS{0}_hww_WJet_FakeRate_m_shape'.format(suffix)
            wJetEffmDown = self.nominals.pop('WJetFakeRate-mDn')
            wJetShapeDown = wJetEffmDown.Clone('histo_WJet_'+wJetSystName+'Down')
            wJetShapeDown.SetTitle('WJet '+wJetSystName+' Down')
            if wJetSystNom : wJetShapeDown.Divide(wJetSystNom)
            if wJetSystNom : wJetShapeDown.Multiply(wJet)
            #wJetShapeDown.Scale(wJet.Integral()/wJetShapeDown.Integral())
            self.fakerate[wJetShapeDown.GetTitle()] = wJetShapeDown

        if 'WJetSS' in self.nominals:
            wJetSystName = 'CMS{0}_hww_WJet_ctrlSS_shape'.format(suffix)
            wJetSSUp = self.nominals.pop('WJetSS')
            wJetShapeUp = wJetSSUp.Clone('histo_WJet_'+wJetSystName+'Up')
            wJetShapeUp.SetTitle('WJet '+wJetSystName+' Up')
            wJetShapeUp.Scale(wJet.Integral()/wJetShapeUp.Integral())
            self.fakerate[wJetShapeUp.GetTitle()] = wJetShapeUp            
            #copy the nominal
            wJetShapeDown = wJet.Clone('histo_WJet_'+wJetSystName+'Down')
            wJetShapeDown.SetTitle('WJet '+wJetSystName+' Down')
            wJetShapeDown.Scale(2.)
            wJetShapeDown.Add(wJetSSUp, -1)
            wJetShapeDown.Scale(wJet.Integral()/wJetShapeDown.Integral())
            self.fakerate[wJetShapeDown.GetTitle()] = wJetShapeDown

        # -----------------------------------------------------------------
        # WJets shape syst
        #
        #   take the shape from the detajj and Mjj loosened sample
        #   down is mirrored
        #   -> no effect of 0/1 jet bin since detajj and Mjj is not useful in 0/1 jet bin
        #
        if 'WJet-template' in self.nominals:
            WJetmc        = self.nominals.pop('WJet')
            WJetShape     = self.nominals.pop('WJet-template')
            WJetSystName = 'CMS{0}_hww_WJet_template_shape'.format(suffix)
            WJetShapeSyst = self.nominals.pop('WJet-templatesyst') if 'WJet-templatesyst' in self.nominals else None

            WJetnom = WJetShape.Clone('histo_WJet')
            WJetnom.SetTitle('WJet')
            if WJetnom.Integral() == 0.:
                # no entries in the reference shape
                # 
                if WJetmc.Integral() != 0.:
                    self._logger.warn('WJet shape template has no entries, but the standard mc is not (%f,%d)', WJetmc.Integral(), WJetmc.GetEntries())
                    self.nominals['WJet'] = WJetmc
                else:
                    self.nominals['WJet'] = WJetnom
            else:
                WJetnom.Scale( (WJetmc.Integral() if WJetmc.Integral() != 0. else 0.001)/WJetnom.Integral() )
                self.nominals['WJet'] = WJetnom


                if WJetShapeSyst and WJetShapeSyst.Integral() != 0.:
                    WJetShapeUp, WJetShapeDown = self._mirror('WJet',WJetnom,WJetShapeSyst, WJetSystName,True)

                    self.templates[WJetShapeUp.GetTitle()]   = WJetShapeUp
                    self.templates[WJetShapeDown.GetTitle()] = WJetShapeDown

        if 'WJetFakeRate-template' in self.nominals:
            wJetEff = self.nominals.pop('WJetFakeRate-template')
            wJetSystName = 'CMS{0}_hww_WJet_FakeRate_jet_shape'.format(suffix)
            wJetShapeUp = wJetEff.Clone('histo_WJet_'+wJetSystName+'Up')
            wJetShapeUp.SetTitle('WJet '+wJetSystName+' Up')
            wJetShapeUp.Scale(wJet.Integral()/wJetShapeUp.Integral())
            self.fakerate[wJetShapeUp.GetTitle()] = wJetShapeUp

            wJetShapeDown = wJet.Clone('histo_WJet_'+wJetSystName+'Down')
            wJetShapeDown.SetTitle('WJet '+wJetSystName+' Down')
            wJetShapeDown.Scale(2)
            wJetShapeDown.Add(wJetShapeUp,-1)
            wJetShapeDown.Scale(wJet.Integral()/wJetShapeDown.Integral())
            self.fakerate[wJetShapeDown.GetTitle()] = wJetShapeDown


        # -----------------------------------------------------------------
        # WJets shape syst for vh analysis
        #
        #   Using the "2j" tag in the sample name we trigger this feature
        #   -> no effect of 0/1 jet bin since since no "2j" in the samples names
        #
        #   Using different pt threshold as systematics
        #   calculated on the fly, for both shape AND normalization
        #   -> shape is NOT normalized to nominal!
        #
        #   Generic case: the variation is calculated in a template phase space
        #                 "template" is used as a reference, while "Wjet" is the target
        #                 "up/down" are then scaled to *target/nominal
        #                 In case no template (or template = nominal) then, it is just as using "up/down" after nominal cuts
        #

        wjet2jScale = 1.

        if 'WJetFakeRate-2j-template' in self.nominals:
            WJetmc        = self.nominals.pop('WJet')
            WJetShape     = self.nominals.pop('WJetFakeRate-2j-template')
            WJetSystName = 'CMS{0}_hww_WJet_template_shape_2j'.format(suffix)

            WJetnom = WJetShape.Clone('histo_WJet')
            WJetnom.SetTitle('WJet')
            if WJetnom.Integral() == 0.:
                wjet2jScale = 0
                # then quit shape uncertainty for Wjets!!!
                # no entries in the template shape --> what?!? How the heck is it possible?
                #   0 entries, then let's neglect the Wjets sample!
                #if WJetmc.Integral() != 0.:
                    #self._logger.warn('WJet shape template has no entries, but the standard mc is not (%f,%d)', WJetmc.Integral(), WJetmc.GetEntries())
                    #self.nominals['WJet'] = WJetmc
                #else:
                    #self.nominals['WJet'] = WJetnom
            else:
                # scale the "template" to the "nominal"
                wjet2jScale = (WJetmc.Integral()/WJetnom.Integral()) if WJetmc.Integral() != 0. else 1.0
                WJetnom.Scale( (WJetmc.Integral() if WJetmc.Integral() != 0. else 0.001)/WJetnom.Integral() )
                self.nominals['WJet'] = WJetnom

        if 'WJetFakeRate-2j-eUp' in self.nominals:
            wJetSystName = 'CMS{0}_hww_WJet_FakeRate_e_shape_2j'.format(suffix)
            wJetEffeUp = self.nominals.pop('WJetFakeRate-2j-eUp')
            wJetShapeUp = wJetEffeUp.Clone('histo_WJet_'+wJetSystName+'Up')
            wJetShapeUp.SetTitle('WJet '+wJetSystName+' Up')
            wJetShapeUp.Scale(wjet2jScale)  # in case it is a template it scales!
            if wjet2jScale != 0 and wJetShapeUp.Integral() != 0 :
                self.fakerate[wJetShapeUp.GetTitle()] = wJetShapeUp

        if 'WJetFakeRate-2j-eDn' in self.nominals:
            wJetSystName = 'CMS{0}_hww_WJet_FakeRate_e_shape_2j'.format(suffix)
            wJetEffeDown = self.nominals.pop('WJetFakeRate-2j-eDn')
            wJetShapeDown = wJetEffeDown.Clone('histo_WJet_'+wJetSystName+'Down')
            wJetShapeDown.SetTitle('WJet '+wJetSystName+' Down')
            wJetShapeDown.Scale(wjet2jScale)  # in case it is a template it scales!
            if wjet2jScale != 0 and wJetShapeDown.Integral() != 0 :
                self.fakerate[wJetShapeDown.GetTitle()] = wJetShapeDown

        if 'WJetFakeRate-2j-mUp' in self.nominals:
            wJetSystName = 'CMS{0}_hww_WJet_FakeRate_m_shape_2j'.format(suffix)
            wJetEffmUp = self.nominals.pop('WJetFakeRate-2j-mUp')
            wJetShapeUp = wJetEffmUp.Clone('histo_WJet_'+wJetSystName+'Up')
            wJetShapeUp.SetTitle('WJet '+wJetSystName+' Up')
            wJetShapeUp.Scale(wjet2jScale)  # in case it is a template it scales!
            if wjet2jScale != 0 and wJetShapeUp.Integral() != 0 :
                self.fakerate[wJetShapeUp.GetTitle()] = wJetShapeUp

        if 'WJetFakeRate-2j-mDn' in self.nominals:
            wJetSystName = 'CMS{0}_hww_WJet_FakeRate_m_shape_2j'.format(suffix)
            wJetEffmDown = self.nominals.pop('WJetFakeRate-2j-mDn')
            wJetShapeDown = wJetEffmDown.Clone('histo_WJet_'+wJetSystName+'Down')
            wJetShapeDown.SetTitle('WJet '+wJetSystName+' Down')
            wJetShapeDown.Scale(wjet2jScale)  # in case it is a template it scales!
            if wjet2jScale != 0 and wJetShapeDown.Integral() != 0 :
                self.fakerate[wJetShapeDown.GetTitle()] = wJetShapeDown


        # -----------------------------------------------------------------
        # DY shape syst
        #
        #   take the shape from the pfmet loosened sample
        #   down is mirrored
        if 'DYLL-template' in self.nominals:
            dyLLmc        = self.nominals.pop('DYLL')
            dyLLShape     = self.nominals.pop('DYLL-template')
            dyLLSystName = 'CMS{0}_hww_DYLL_template_shape'.format(suffix)
            dyLLShapeSyst = self.nominals.pop('DYLL-templatesyst') if 'DYLL-templatesyst' in self.nominals else None

            dyLLnom = dyLLShape.Clone('histo_DYLL')
            dyLLnom.SetTitle('DYLL')
            if dyLLnom.Integral() == 0.:
                # no entries in the reference shape
                # 
                if dyLLmc.Integral() != 0.:
                    self._logger.warn('DYLL shape template has no entries, but the standard mc is not (%f,%d)', dyLLmc.Integral(), dyLLmc.GetEntries())
                    self.nominals['DYLL'] = dyLLmc
                else:
                    self.nominals['DYLL'] = dyLLnom
            else:
                dyLLnom.Scale( (dyLLmc.Integral() if dyLLmc.Integral() != 0. else 0.001)/dyLLnom.Integral() )
                self.nominals['DYLL'] = dyLLnom
                

                if dyLLShapeSyst and dyLLShapeSyst.Integral() != 0.:
                    dyLLShapeUp, dyLLShapeDown = self._mirror('DYLL',dyLLnom,dyLLShapeSyst, dyLLSystName,True)

                    self.templates[dyLLShapeUp.GetTitle()]   = dyLLShapeUp
                    self.templates[dyLLShapeDown.GetTitle()] = dyLLShapeDown


        # -----------------------------------------------------------------
        # VgS and Vg shape template
        #
        #   take the shape from the loose leptons selection
        #   systematics is taken care of by eff_l
        for vg in ['VgS','Vg']:
            if vg+'-template' in self.nominals:
                vgmc        = self.nominals.pop(vg)
                vgShape     = self.nominals.pop(vg+'-template')
            
                vgnom = vgShape.Clone('histo_'+vg)
                vgnom.SetTitle(vg)
                if vgnom.Integral() == 0.:
                    # no entries in the reference shape
                    #
                    if vgmc.Integral() != 0.:
                        self._logger.warn(vg+' shape template has no entries, but the standard mc is not (%f,%d)', vgmc.Integral(), vgmc.GetEntries())
                        self.nominals[vg] = vgmc
                    else:
                        self.nominals[vg] = vgnom
                else:
                    vgnom.Scale( (vgmc.Integral() if vgmc.Integral() != 0. else 0.001)/vgnom.Integral() )
                    self.nominals[vg] = vgnom
                
        # -----------------------------------------------------------------
        # WW generator shapes
        #
        mcAtNLO = {} 
        if 'WW' in self.nominals:
            madWW = self.nominals['WW']
            wwNLOs = ['WWnlo','WWnloUp','WWnloDown',]

            if set(wwNLOs).issubset(self.nominals):
                for t in wwNLOs:
                    mcAtNLO[t] = self.nominals[t]
                    del self.nominals[t]

                if madWW.GetNbinsX()>1:
                    wwGenUp = mcAtNLO['WWnlo'].Clone('histo_WW_Gen_nlo_WWUp')
                    wwGenUp.SetTitle('WW Gen_nlo_WW Up')
                    wwGenUp.Scale(madWW.Integral()/wwGenUp.Integral())
                    self.generators[wwGenUp.GetTitle()] = wwGenUp
                    
                    #copy the nominal
                    wwGenDown = madWW.Clone('histo_WW_Gen_nlo_WWDown')
                    wwGenDown.SetTitle('WW Gen_nlo_WW Down')
                    wwGenDown.Scale(2.)
                    wwGenDown.Add(wwGenUp, -1)
                    if (wwGenDown.Integral() != 0) : wwGenDown.Scale(madWW.Integral()/wwGenDown.Integral())
                    self.generators[wwGenDown.GetTitle()] = wwGenDown


                    # MC@NLO scale
                    wwScaleUp = mcAtNLO['WWnloUp'].Clone('histo_WW_Gen_scale_WWUp')
                    wwScaleUp.SetTitle('WW Gen_scale_WW Up')
                    wwScaleUp.Divide(mcAtNLO['WWnlo'])
                    wwScaleUp.Multiply(madWW)
                    if  (wwScaleUp.Integral() != 0) : wwScaleUp.Scale(madWW.Integral()/wwScaleUp.Integral())
                    self.generators[wwScaleUp.GetTitle()] = wwScaleUp
                    
                    wwScaleDown = mcAtNLO['WWnloDown'].Clone('histo_WW_Gen_scale_WWDown')
                    wwScaleDown.SetTitle('WW Gen_scale_WW Down')
                    wwScaleDown.Divide(mcAtNLO['WWnlo'])
                    wwScaleDown.Multiply(madWW)
                    if (wwScaleDown.Integral() != 0) : wwScaleDown.Scale(madWW.Integral()/wwScaleDown.Integral())
                    self.generators[wwScaleDown.GetTitle()] = wwScaleDown

        mcAtNLOnorm = {} 
        if 'WW' in self.nominals:
            madWW = self.nominals['WW']
            wwNLOs = ['WWnloNorm']

            if set(wwNLOs).issubset(self.nominals):
                for t in wwNLOs:
                    mcAtNLOnorm[t] = self.nominals[t]
                    del self.nominals[t]

                if madWW.GetNbinsX()>1:
                    # A (nominal) and B (alternative)
                    # take B-A, divide by 2 and shape up/down symmetrically
                    # this will ensure |A-B| as error in normalization
                    # and not double count the downward variation!
                    # that is ---> up   = A + (A-B)/2
                    # that is ---> down = A - (A-B)/2
                    
                    wwGenDifference = mcAtNLOnorm['WWnloNorm'].Clone('histo_WW_Gen_nlo_WW_difference')
                    wwGenDifference.SetTitle('WW Gen_nlo_WW difference temp')
                    wwGenDifference.Add(madWW, -1)
                    wwGenDifference.Scale(0.5)

                    wwGenUp = madWW.Clone('histo_WW_Gen_nlo_WWUp')
                    wwGenUp.SetTitle('WW Gen_nlo_WW Up')
                    wwGenUp.Add(wwGenDifference, 1)
                    self.generators[wwGenUp.GetTitle()] = wwGenUp

                    #copy the nominal
                    wwGenDown = madWW.Clone('histo_WW_Gen_nlo_WWDown')
                    wwGenDown.SetTitle('WW Gen_nlo_WW Down')
                    wwGenDown.Add(wwGenDifference, -1)
                    self.generators[wwGenDown.GetTitle()] = wwGenDown
                    
                    

        mcPOWnorm = {} 
        if 'WW' in self.nominals:
            madWW = self.nominals['WW']
            wwPOWs = ['WWpow']

            if set(wwPOWs).issubset(self.nominals):
                for t in wwPOWs:
                    mcPOWnorm[t] = self.nominals[t]
                    del self.nominals[t]

                # A (nominal) and B (alternative)
                # down = A
                # up   = B

                # if 0 events, due to low MC statistics of the alternative sample, then *do nothing*
                if mcPOWnorm['WWpow'].Integral() > 0 :
                    wwGenUp = mcPOWnorm['WWpow'].Clone('histo_WW_Gen_pow_WWUp')
                else :
                    wwGenUp = madWW.Clone('histo_WW_Gen_pow_WWUp')
                wwGenUp.SetTitle('WW Gen_pow_WW Up')
                self.generators[wwGenUp.GetTitle()] = wwGenUp

                #copy the nominal
                wwGenDown = madWW.Clone('histo_WW_Gen_pow_WWDown')
                wwGenDown.SetTitle('WW Gen_pow_WW Down')
                self.generators[wwGenDown.GetTitle()] = wwGenDown

        mcPhantomMGnorm = {} 
        if 'WWewk' in self.nominals:
            phantomWW = self.nominals['WWewk']
            madgraphWW = ['WWewkMG']

            #print " > do comparison MG / Phantom"
            #print " > ", self.nominals
            if set(madgraphWW).issubset(self.nominals):
                for t in madgraphWW:
                    mcPhantomMGnorm[t] = self.nominals[t]
                    del self.nominals[t]

                # A (nominal) and B (alternative)
                # down = A
                # up   = B

                wwewkGenUp = mcPhantomMGnorm['WWewkMG'].Clone('histo_WWewk_Gen_MGPH_WWewkUp')
                wwewkGenUp.SetTitle('WWewk Gen_MGPH_WWewk Up')
                self.generators[wwewkGenUp.GetTitle()] = wwewkGenUp

                #copy the nominal
                wwewkGenDown = phantomWW.Clone('histo_WWewk_Gen_MGPH_WWewkDown')
                wwewkGenDown.SetTitle('WWewk Gen_MGPH_WWewk Down')
                self.generators[wwewkGenDown.GetTitle()] = wwewkGenDown



        # -----------------------------------------------------------------
        # Top shapes
        #
        fracTW = {} 
        if 'Top' in self.nominals:
            pytTop = self.nominals['Top']
            fracTWs = ['TopTW',]

            if set(fracTWs).issubset(self.nominals):
                for t in fracTWs:
                    fracTW[t] = self.nominals[t]
                    del self.nominals[t]

                if pytTop.GetNbinsX()>1:
                    topGenUp = fracTW['TopTW'].Clone('histo_Top_CMS{0}_hww_Top_fTWUp'.format(suffix))
                    topGenUp.SetTitle('Top CMS_hww_Top_fTW Up')
                    topGenUp.Scale(pytTop.Integral()/topGenUp.Integral())
                    self.generators[topGenUp.GetTitle()] = topGenUp

                    #copy the nominal
                    topGenDown = pytTop.Clone('histo_Top_CMS{0}_hww_Top_fTWDown'.format(suffix))
                    topGenDown.SetTitle('Top CMS_hww_Top_fTW Down')
                    topGenDown.Scale(2.)
                    topGenDown.Add(topGenUp, -1)
                    topGenDown.Scale(pytTop.Integral()/topGenDown.Integral())
                    self.generators[topGenDown.GetTitle()] = topGenDown

            ctrlTT = {} 
            ctrlTTs = ['TopCtrl',]

            if set(ctrlTTs).issubset(self.nominals):
                for t in ctrlTTs:
                    ctrlTT[t] = self.nominals[t]
                    del self.nominals[t]

                if pytTop.GetNbinsX()>1:
                    topCtrlUp = ctrlTT['TopCtrl'].Clone('histo_Top_CMS{0}_hww_Top_ctrlTTUp'.format(suffix))
                    topCtrlUp.SetTitle('Top CMS_hww_Top_ctrlTT Up')
                    topCtrlUp.Scale(pytTop.Integral()/topCtrlUp.Integral())
                    self.generators[topCtrlUp.GetTitle()] = topCtrlUp
                    
                    #copy the nominal
                    topCtrlDown = pytTop.Clone('histo_Top_CMS{0}_hww_Top_ctrlTTDown'.format(suffix))
                    topCtrlDown.SetTitle('Top CMS_hww_Top_ctrlTT Down')
                    topCtrlDown.Scale(2.)
                    topCtrlDown.Add(topCtrlUp, -1)
                    topCtrlDown.Scale(pytTop.Integral()/topCtrlDown.Integral())
                    self.generators[topCtrlDown.GetTitle()] = topCtrlDown

                ctrlTDD = {}
                ctrlTDDs = ['Top-template',]
        
                if set(ctrlTDDs).issubset(self.nominals):
                    for t in ctrlTDDs:
                        ctrlTDD[t] = self.nominals[t]
                        del self.nominals[t]
                    topDDUp = ctrlTDD['Top-template'].Clone('histo_Top_CMS{0}_hww_Top_ddTTUp'.format(suffix))
                    topDDUp.SetTitle('Top CMS_hww_Top_ddTT Up')
                    topDDUp.Scale(pytTop.Integral()/topDDUp.Integral())
                    self.generators[topDDUp.GetTitle()] = topDDUp
                
                    #copy the nominal
                    topDDDown = pytTop.Clone('histo_Top_CMS{0}_hww_Top_ddTTDown'.format(suffix))
                    topDDDown.SetTitle('Top CMS_hww_Top_ddTT Down')
                    topDDDown.Scale(2.)
                    topDDDown.Add(topCtrlUp, -1)
                    topDDDown.Scale(pytTop.Integral()/topCtrlDown.Integral())
                    self.generators[topDDDown.GetTitle()] = topDDDown

        # -----------------------------------------------------------------
        # JHU vs PowHeg (DEPRECATED BUT DON'T DELETE FOR NOW PLEASE)
        #

#        if 'jhu_NLO' in self.nominals:
#           jhuNLO = self.nominals.pop('jhu_NLO')
#           if 'jhu' in self.nominals:
#             jhuNom    = self.nominals['ggH']
#             jhuRel    = jhuNLO.Clone('jhuRel') 
#             jhuRel.Add(jhuNom,-1)
#             jhuRel.Divide(jhuNom)
#
#             jhuSys    = jhuNom.Clone('jhuSys')
#             jhuSys.Multiply(jhuRel)
#             jhuNLOUp  = jhuNom.Clone('histo_jhu_Gen_JHU_NLOUp')
#             jhuNLOUp.SetTitle('JHU NLO Up')
#             jhuNLOUp.Add(jhuSys,1.) 
#             self.generators[jhuNLOUp.GetTitle()] = jhuNLOUp
# 
#             jhuNLODown= jhuNom.Clone('histo_jhu_Gen_JHU_NLODown')
#             jhuNLODown.SetTitle('JHU NLO Down')
#             jhuNLODown.Add(jhuSys,-1.)
#             self.generators[jhuNLODown.GetTitle()] = jhuNLODown
#
#             if 'ggH_ALT' in self.nominals: 
#                jhu_ALTNom = self.nominals['ggH_ALT']
#
#                jhu_ALTSys    = jhu_ALTNom.Clone('jhuALTSys')
#                jhu_ALTSys.Multiply(jhuRel)
#                jhu_ALTNLOUp  = jhu_ALTNom.Clone('histo_ggH_ALT_Gen_JHU_NLOUp')
#                jhu_ALTNLOUp.SetTitle('ggH_ALT NLO Up')
#                jhu_ALTNLOUp.Add(jhu_ALTSys,1.)
#                self.generators[jhu_ALTNLOUp.GetTitle()] = jhu_ALTNLOUp
#
#                jhu_ALTNLODown= jhu_ALTNom.Clone('histo_ggH_ALT_Gen_JHU_NLODown')
#                jhu_ALTNLODown.SetTitle('ggH_ALT NLO Down')
#                jhu_ALTNLODown.Add(jhu_ALTSys,-1.)
#                self.generators[jhu_ALTNLODown.GetTitle()] = jhu_ALTNLODown

        # -----------------------------------------------------------------
        # Statistical
        #
        # prepare the dictionary
        nomkeys = self.nominals.keys()
        if self.statmode == 'unified':
            # all unified
            statmodes = dict(zip(nomkeys,['unified']*len(nomkeys)))
        elif self.statmode == 'bybin':
            # all bybin
            statmodes = dict(zip(nomkeys,['bybin']*len(nomkeys)))
        elif isinstance(self.statmode, list):
            # use the list as a mask for the bybin
            statmodes = {}
            for n in nomkeys:
                statmodes[n] = 'bybin' if n in self.statmode else 'unified'
        else:
            raise ValueError('Invalid option %s (can be \'unified\',\'bybin\')' % self.statmode)

        for n,h in self.nominals.iteritems():
            # skip data or injected sample
            if n in ['Data'] or '-SI' in n:
                continue
            # skip stat error if there is only one bin since it is renormalised
            if h.GetNbinsX() == 1:
                continue
            effName = 'CMS{0}_hww_{1}_{2}_stat_shape'.format(suffix,n,chan)

            if statmodes[n] == 'unified' :
                self._logger.debug('Generating unified morphs for %s', n)
                morphs = self._morphstat(h,effName)

            elif statmodes[n] == 'bybin' :
                self._logger.debug('Generating bybin morphs for %s', n)
                morphs = self._morphstatbbb(h,effName)
            else:
                raise ValueError('Invalid option %s (can be \'unified\',\'bybin\')' % self.statmode)

            self.statistical.update(morphs)

        #
        # Experimental
        #
        udRegex = re.compile("(.+)(Up|Down)$")
        allSysts = {}
        for n,syst in self.systFiles.iteritems():
            histograms = []
            for k in syst.GetListOfKeys():
                h = k.ReadObj()
                if h.GetDimension() != 1: 
                    continue
                self._remodel(h)
                histograms.append(h)
                #print "------------------------"
                #print h.GetName()
                #print h.Integral()

            m = udRegex.match(n)
            if m is not None:
                systName = 'CMS{0}_'.format(suffix)+m.group(1)
                if 'interf_ggH' in systName : systName = 'interf_ggH' 
                if 'interf_qqH' in systName : systName = 'interf_qqH' 
                systShift = m.group(2)
                # x-check on the regex match
                if not( n.endswith('Up') or n.endswith('Down') ):
                    raise RuntimeError(n+' doesn\'t end with Up or Down!')

                for h in histograms:

                    if not h.GetTitle() in self.nominals:
                        raise RuntimeError('Systematic '+h.GetTitle()+' found, but no nominal shape')

                    h.SetName(h.GetName()+'_'+systName+systShift)
                    h.SetTitle(h.GetTitle()+' '+systName+' '+systShift)

                    self.experimental[h.GetTitle()] = h
            else:
                systName = 'CMS{0}_'.format(suffix)+n

                for h in histograms:
                    if not h.GetTitle() in self.nominals:
                        raise RuntimeError('Systematic '+h.GetTitle()+' found, but no nominal shape')
                    # we call up the shape taken from the experimental file
                    systUp = h.Clone(h.GetName()+'_'+systName+'Up')
                    systUp.SetTitle(h.GetTitle()+' '+systName+' Up')

                    self.experimental[systUp.GetTitle()] = systUp

                    # down = nominal histogram
                    systDown = self.nominals[h.GetTitle()].Clone(h.GetName()+'_'+systName+'Down')
                    systDown.SetTitle(h.GetTitle()+' '+systName+' Down')
                    self.experimental[systDown.GetTitle()] = systDown

                    # copy the nominal histogram and mirror up to get down
                    #systDown = self.nominals[h.GetTitle()].Clone(h.GetName()+'_'+systName+'Down')
                    #systDown.SetTitle(h.GetTitle()+' '+systName+' Down')
                    #for iSample,iSyst in scale2nom:
                    #    if not ( (iSample == '*' or iSample in h.GetName()) and (iSyst == '*' or iSyst in systName) ):
                    #        continue
                    #    systUp.Scale(systDown.Integral()/systUp.Integral())
                    #systDown.Scale(2)
                    #systDown.Add(systUp,-1)

                    #self.experimental[systDown.GetTitle()] = systDown

        # check none of the experimental systematics to be 0
        for n in self.experimental.keys():
            # the process name is the first token of the systematic name
            process = n.split()[0] 
            syst = self.experimental[n]
            if syst.Integral() > 0: continue

            # fish the nominal
            h = self.nominals[process]

            newsyst = h.Clone(syst.GetName())
            newsyst.SetTitle(syst.GetTitle())
            self._logger.debug('>> Attention: systematic '+newsyst.GetName()+' has 0 integral -> using nominal (variation suppressed)')
            self.experimental[n] = newsyst





#             print 'systName:',systName,n
#         print 'Systematics',',\n'.join([ n+';'+h.GetName() for n,h in self.experimental.iteritems()])
#         print 'Nominals','\n'.join([ n+';'+h.GetName()+';'+h.GetTitle() for n,h in self.nominals.iteritems()])

        # add the nominals and the experimental to 1 container
        self.histograms.update(self.nominals)
        self.histograms.update(self.fakerate)
        self.histograms.update(self.templates)
        self.histograms.update(self.generators)
        self.histograms.update(self.statistical)
        self.histograms.update(self.experimental)


#         sys.exit(0)

    def scale2Nominals(self, list):
        if not list:
            return

        print '   - Scaling systematic shapes to nominal:',
        sanityCheck = dict([(ss,0) for ss in list])

        for name,hSys in self.experimental.iteritems():
            tokens = name.split()
            sample = tokens[0]
            syst   = tokens[1]
            for iSample,iSyst in list:
                if not ( (iSample == '*' or iSample == sample) and (iSyst == '*' or iSyst == syst) ):
                    continue
                sanityCheck[(iSample,iSyst)] += 1
                if sample not in self.nominals:
                    raise RuntimeError('Nominal histogram '+sample+' not found')
                hNom = self.nominals[sample]
                if hNom.Integral() and hSys.Integral():
                    hSys.Scale(hNom.Integral()/hSys.Integral())
        
        #for ss,k in sanityCheck.iteritems():
        #    if k == 0:
        #        raise NameError('sample,systematic pair not found '+ss[0]+':'+ss[1])

    def jhuMixer(self,ggqqMixIn):
        ggqqMix = float(ggqqMixIn)
        print '   - jhuMixer -> gg/qq Fraction = ',ggqqMix

        # Find Nominal jhu histograms
        ggH_ALT  = 0
        qqH_ALT  = 0
        jhu_NORM = 0
        for name,hist in self.nominals.iteritems():
            tokens = name.split()
            sample = tokens[0]
            if ( sample == 'ggH_ALT' ):
               ggH_ALT = hist 
            if ( sample == 'qqH_ALT' ):
               qqH_ALT = hist 
            if ( sample == 'jhu_NORM' ):
               jhu_NORM = hist 
        print ggH_ALT , qqH_ALT , jhu_NORM
       
        # Check if NORM is needed 
        if not jhu_NORM: 
            return
        if (jhu_NORM.Integral() ==0.):
            return

        # Compute NORM factors
        ggH_ALT_Scale  = 1.0
        qqH_ALT_Scale  = 1.0
        if ( ggH_ALT and qqH_ALT):
           ggH_ALT_Scale = jhu_NORM.Integral()*ggqqMix       / ggH_ALT.Integral()
           qqH_ALT_Scale = jhu_NORM.Integral()*(1.0-ggqqMix) / qqH_ALT.Integral()
        elif ( ggH_ALT ):
           ggH_ALT_Scale = jhu_NORM.Integral()               / ggH_ALT.Integral()
        elif ( qqH_ALT ):
           qqH_ALT_Scale = jhu_NORM.Integral()               / qqH_ALT.Integral()

        # Apply to all 
        for name,hist in self.histograms.iteritems():
            tokens = name.split()
            sample = tokens[0]
            if ( sample == 'ggH_ALT' ):
               if (ggH_ALT_Scale>0):
                 hist.Scale(ggH_ALT_Scale)
               else:
                 hist.Reset()
            if ( sample == 'qqH_ALT' ):
               if (qqH_ALT_Scale>0):
                 hist.Scale(qqH_ALT_Scale)
               else:
                 hist.Reset()
        # Drop jhu_NORM
        self.nominals.pop('jhu_NORM')

    def _rename(self):
        print '   - Renaming'
        histograms2 = {}
        for (n,h) in self.histograms.iteritems():
            if n in self.nameMap:
                nn = self.nameMap[n]
                h.SetName('histo_'+nn)
                h.SetTitle(nn)
                histograms2[nn] = h
            else:
                histograms2[n] = h

        self.histograms = histograms2


    # not used anymore
    def applyScaleFactors(self, factors={}):
        print '    - Applying scaling factors'
        for n,h in self.histograms.iteritems():
            # get the identification token
            type = n.split()[0]
            if type in factors:
#                 print n,factors[type]
                h.Scale(factors[type])

            if not type in self.lumiMask:
                integral = h.Integral()
                h.Scale(self.lumi)
                self._logger.debug('Lumi scale (%.2f) %-50s : %.3f -> %.3f',self.lumi,h.GetName(),integral,h.Integral())
    
    def close(self):
        self._disconnect()

    def _disconnect(self):
        if hasattr(self,'shapeFile'):
            self.shapeFile.Close()

        if hasattr(self,'systFiles'):
            for n,f in self.systFiles.iteritems():
                f.Close()





if __name__ == '__main__':
    print '''
-------------------------------------------------------------------------------
  ______     _ _  _____ _                      __  __                          
 |  ____|   (_) |/ ____| |                    |  \/  |                         
 | |____   ___| | (___ | |__   __ _ _ __   ___| \  / | ___ _ __ __ _  ___ _ __ 
 |  __\ \ / / | |\___ \| '_ \ / _` | '_ \ / _ \ |\/| |/ _ \ '__/ _` |/ _ \ '__|
 | |___\ V /| | |____) | | | | (_| | |_) |  __/ |  | |  __/ | | (_| |  __/ |   
 |______\_/ |_|_|_____/|_| |_|\__,_| .__/ \___|_|  |_|\___|_|  \__, |\___|_|   
                                   | |                          __/ |          
                                   |_|                         |___/           
-------------------------------------------------------------------------------
'''
    mypath = os.path.dirname(os.path.abspath(__file__))
    #  ___       __           _ _      
    # |   \ ___ / _|__ _ _  _| | |_ ___
    # | |) / -_)  _/ _` | || | |  _(_-<
    # |___/\___|_| \__,_|\_,_|_|\__/__/

    usage = '''

    %prog [options]
    '''
    parser = optparse.OptionParser(usage)

    parser.add_option('-n', '--dry',   dest='dry',   help='Dry run', action='store_true' )
    parser.add_option('-r', '--rebin', dest='rebin', help='Rebin by', type='int', default=1)

    parser.add_option('--no_wwdd_above'     , dest='noWWddAbove'       , help='No WW dd above this mass'         , default=None  , type='int' )
    parser.add_option('--dataset'           , dest='dataset'           , help='Dataset to process'               , default=None)
    parser.add_option('--mcset'             , dest='mcset'             , help='Mcset to process'                 , default=None)
    parser.add_option('--tag'               , dest='tag'               , help='Tag used for the shape file name' , default=None)
    parser.add_option('--statmode'          , dest='statmode'          , help='Production mode for stat-shapes (default = %default)', default='unified')
    parser.add_option('--path_dd'           , dest='path_dd'           , help='Data driven path'                 , default=None)
    parser.add_option('--path_scale'        , dest='path_scale'        , help='Scale factors'                    , default=None)
    parser.add_option('--path_shape_raw'    , dest='path_shape_raw'    , help='Input directory of raw shapes'    , default=None)
    parser.add_option('--path_shape_merged' , dest='path_shape_merged' , help='Destination directory for merged' , default=None)
    parser.add_option('--no-syst',       dest='makeSyst',   help='Do not produce the systematics',        action='store_false',   default=True)
    parser.add_option('--simask'            , dest='simask'            , help='Signal injection mask' , default=None, type='string' , action='callback' , callback=hwwtools.list_maker('simask'))

    parser.add_option('--fillEmptyBins'     , dest='fillEmptyBins'     , help='fillEmptyBins used to fill empty bins' , default=False)

    parser.add_option('--jhuMixFrac'        , dest='jhuMixFrac'        , help='gg JHU Faction'             , default=1)

    # EWK Doublet Model
    parser.add_option('--ewksinglet',    dest='ewksinglet',  help='On/Off EWK singlet model',           default=False , action='store_true')   
    parser.add_option('--cprimesq'  ,    dest='cprimesq',    help='EWK singlet C\'**2 mixing value',    default=[1.]  , type='string'  , action='callback' , callback=hwwtools.list_maker('cprimesq',',',float))
    parser.add_option('--brnew'     ,    dest='brnew'   ,    help='EWK singlet BRNew values',           default=[0.]  , type='string'  , action='callback' , callback=hwwtools.list_maker('brnew',',',float))


# discontined
#     parser.add_option('--scale2nominal', dest='scale2nom', help='Systematics to normalize to nominal ', default='')
#     parser.add_option('--ninja', dest='ninja', help='Ninja', action='store_true', default=False )
  
    hwwtools.addOptions(parser)
    hwwtools.loadOptDefaults(parser)


    (opt, args) = parser.parse_args()

    print opt.simask
    print 'dataset:    ',opt.dataset

    print 'jhuMixFrac = ',opt.jhuMixFrac

    scale2nom = []
    if '2012' in opt.dataset and opt.makeSyst : scale2nom = scale2nom+[('Vg','*'), ('VgS','*')]
    # in the future good to have a way of removing processes which are not in mcset
    #scale2nom = [(p,s) for p,s in scale2nom if p in hwwsamples.mcsets(opt.mcset)]
    for p,s in scale2nom:
        print 'scaling to nominal: '+p+' syst '+s

    sys.argv.append( '-b' )
    ROOT.gROOT.SetBatch()

    if not opt.debug:
        pass
    elif opt.debug == 2:
        print 'Logging level set to DEBUG (%d)' % opt.debug
        logging.basicConfig(level=logging.DEBUG)
    elif opt.debug == 1:
        print 'Logging level set to INFO (%d)' % opt.debug
        logging.basicConfig(level=logging.INFO)

    logging.debug('Used options')
    logging.debug(', '.join([ '{0} = {1}'.format(a,b) for a,b in opt.__dict__.iteritems()]))
    #  ___                         _              
    # | _ \__ _ _ _ __ _ _ __  ___| |_ ___ _ _ ___
    # |  _/ _` | '_/ _` | '  \/ -_)  _/ -_) '_(_-<
    # |_| \__,_|_| \__,_|_|_|_\___|\__\___|_| /__/
    #                                             

    nomPath   = opt.path_shape_raw+'/nominals/' 
    systPath  = opt.path_shape_raw+'/systematics/' 
    mergedDir = opt.path_shape_merged

#     masses = hwwinfo.masses[:] if opt.mass == 0 else [opt.mass]
    masses = opt.mass

    if not opt.variable or not opt.lumi:
        parser.error('The variable and the luminosty must be defined')

    tag  = opt.tag if opt.tag else opt.variable
    var  = opt.variable
    lumiMask = ['Data']
    nameTmpl  = 'shape_Mh{0}_{1}_'+tag+'_shapePreSel_{2}'
    os.system('mkdir -p '+mergedDir)

    ROOT.TH1.SetDefaultSumw2(True)


    #  _                  
    # | |   ___  ___ _ __ 
    # | |__/ _ \/ _ \ '_ \
    # |____\___/\___/ .__/
    #               |_|   
    #     
    reader = datadriven.DDCardReader( opt.path_dd )

    channels =  dict([ (k,v) for k,v in hwwinfo.channels.iteritems() if k in opt.chans])

    nModel = 1
    if opt.ewksinglet : nModel = len(opt.cprimesq)*len(opt.brnew)
    for iModel in xrange(0,nModel):
      iCP2 = iModel%len(opt.cprimesq)
      iBRn = (int(iModel/len(opt.cprimesq)))
      for mass in masses:
        if '2011' in opt.dataset and (mass==145 or mass==155): continue
        for chan,(cat,fl) in channels.iteritems():
            flavors = hwwinfo.flavors[fl]
            # print chan,cat,fl,flavors
            # open output file
            m = ShapeMerger( simask = opt.simask, fillEmptyBins = opt.fillEmptyBins)
            print '-'*100
            print 'ooo Processing',mass, chan
            print '-'*100


            for fl in flavors:
                print '  o Channel:',fl
                # configure
                label = 'mH{0} {1} {2}'.format(mass,cat,fl)
                ss = ShapeMixer(label)
                if opt.ewksinglet:
                  ss.nominalsPath   = os.path.join(nomPath,nameTmpl.format(mass, cat, fl)+'.EWKSinglet_CP2_'+str(opt.cprimesq[iCP2]).replace('.','d')+'_BRnew_'+str(opt.brnew[iBRn]).replace('.','d')+'.root')
                  ss.systSearchPath = os.path.join(systPath,nameTmpl.format(mass, cat, fl)+'.EWKSinglet_CP2_'+str(opt.cprimesq[iCP2]).replace('.','d')+'_BRnew_'+str(opt.brnew[iBRn]).replace('.','d')+'_*.root')
                else:
                  ss.nominalsPath   = os.path.join(nomPath,nameTmpl.format(mass, cat, fl)+'.root')
                  ss.systSearchPath = os.path.join(systPath,nameTmpl.format(mass, cat, fl)+'_*.root')
                ss.lumiMask = lumiMask
                ss.lumi     = opt.lumi
                ss.rebin    = opt.rebin
                ss.statmode = opt.statmode

                print ss.nominalsPath
                print ss.systSearchPath 

                # run
                print '     - mixing histograms'
                ss.mix(chan, scale2nom , iCP2 , iBRn)

                ss.scale2Nominals( scale2nom )

                ss.jhuMixer(opt.jhuMixFrac) 

                ss.applyScaleFactors()
                
                m.add(ss)
            print '  - summing sets'
            m.sum()

            
            if not reader.iszombie:
                print '  - data driven'
                # make a filter to remove the dd >= noWWddAbove for WW 
                wwfilter = datadriven.DDWWFilter(reader, opt.noWWddAbove)
                (estimates,dummy) = wwfilter.get(mass,chan)
                print mass,estimates
                m.applyDataDriven( mass,estimates )

            m.injectSignal()
            if not opt.dry:
                if opt.ewksinglet:
                  output = 'hww-{lumi:.2f}fb.mH{mass}.{channel}.EWKSinglet_CP2_{cprimsq}_BRnew_{brnew}_shape.root'.format(lumi=opt.lumi,mass=mass,channel=chan,cprimsq=str(opt.cprimesq[iCP2]).replace('.','d'),brnew=str(opt.brnew[iBRn]).replace('.','d')  )
                else:
                  output = 'hww-{lumi:.2f}fb.mH{mass}.{channel}_shape.root'.format(lumi=opt.lumi,mass=mass,channel=chan)
                path = os.path.join(mergedDir,output)
                print '  - writing to',path
                m.save(path)

    print 'Used options'
    print ', '.join([ '{0} = {1}'.format(a,b) for a,b in opt.__dict__.iteritems()])
