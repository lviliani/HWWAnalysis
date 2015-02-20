#!/usr/bin/env python

import optparse
import ROOT
import sys
import re
import os.path
import logging
import pdb
import fnmatch

import hwwinfo
import hwwtools
import hwwsamples

import datadriven
from HWWAnalysis.Misc.odict import OrderedDict
from systematicUncertainties import getCommonSysts,addFakeBackgroundSysts,floatNorm

# da http://cmssw.cvs.cern.ch/cgi-bin/cmssw.cgi/UserCode/Mangano/WWAnalysis/AnalysisStep/python/systematicUncertainties.py


# class AutoVivification(dict):
#     """Implementation of perl's autovivification feature."""
#     def __getitem__(self, item):
#         try:
#             return dict.__getitem__(self, item)
#         except KeyError:
#             value = self[item] = type(self)()
#             return value

class ShapeDatacardWriter:
    _log = logging.getLogger('ShapeDatacardWriter')

    '''Dump a crappy datacard to file'''
    
    def __init__(self, mass, bin, shape=True, dataTag='2012A'):
        self._mass = mass
        self._bin = bin
        self._shape = shape
        self._dataTag = dataTag

    def __del__(self):
        pass

#     def write(self, yields, nuisances, path, fileFmt, signals = ['ggH', 'vbfH', 'wzttH']):
    def write(self, yields, nuisances, path, fileFmt, signals = hwwsamples.signals ):

        cardPath = path.format(mass = self._mass, bin = self._bin)
        print 'Writing to '+cardPath 
        card = open( cardPath ,"w")
        card.write('## Shape input card for H->WW analysis\n')
        
        card.write('imax 1 number of channels\n')
        card.write('jmax * number of background\n')
        card.write('kmax * number of nuisance parameters\n') 

        card.write('-'*100+'\n')
        card.write('bin         %s' % self._bin+'\n')
        if 'Data' not in yields:
            self._log.warning( 'Yields: '+','.join(yields.keys()) )
            raise RuntimeError('No Data found!')
        card.write('observation %.0f\n' % yields['Data']._N)
        # replace the second * with the bin?

        if self._shape:
            card.write('shapes  *           * '+
                       fileFmt.format(mass=self._mass, bin=self._bin)+
                       '     histo_$PROCESS histo_$PROCESS_$SYSTEMATIC'+'\n')
            card.write('shapes  data_obs    * '+
                       fileFmt.format(mass=self._mass, bin=self._bin)+
                       '     histo_Data'+'\n')

        card.write('-'*100+'\n')
        
        bkgs = [ name for name in yields if name not in signals and name != 'Data']
        sigs = [ name for name in yields if name in signals ]
        keyline = []
        keyline.extend([ (-i,s,yields[s]._N) for i,s in enumerate(sigs) ])
        keyline.extend([ (i+1,b,yields[b]._N) for i,b in enumerate(bkgs) ])

        coldef = 15

        card.write('bin'.ljust(58)+''.join([self._bin.ljust(coldef)*len(keyline)])+'\n')
        card.write('process'.ljust(58)+''.join([n.ljust(coldef) for (i,n,N) in keyline])+'\n' )
        card.write('process'.ljust(58)+''.join([('%d' % i).ljust(coldef) for (i,n,N) in keyline])+'\n' )
        card.write('rate'.ljust(58)+''.join([('%-.4f' % N).ljust(coldef) for (i,n,N) in keyline])+'\n' )
        card.write('-'*100+'\n')

#         nmax = max([len(n) for n in nuisances]

        for name in nuisances:
            (pdf,effect) = nuisances[name]
            # if this nuisance has no effect on any sample, not even write it!  --> "isAgoodNuisance"
            isAgoodNuisance = False
            for i,p,y in keyline:
                if p in effect:
                  isAgoodNuisance = True

            if 'WW' in signals and 'Gen_nlo_WW' in name:
                isAgoodNuisance = False

            if (isAgoodNuisance) :
               if len(pdf) == 1: card.write('{0:<41} {1:<7}         '.format(name,pdf[0]))
               else:             card.write('{0:<41} {1:<7} {2:<6}  '.format(name,pdf[0],pdf[1]))
               for i,p,y in keyline:
                   if p in effect:
                       #if 'FakeRate' in name:
                       if   (pdf[0]=='gmN'):                        card.write('%-10.5f'      % effect[p])
                       elif (pdf[0]=='shape' or pdf[0]=='shapeN2'): card.write('%-10d'        % effect[p])
                       elif (isinstance(effect[p], tuple)):         card.write('%.2f/%-5.2f' % (effect[p][0],effect[p][1]))
                       else:                                        card.write('%-10.3f'      % effect[p])
                   else: card.write('-'.ljust(coldef))
               card.write('\n')

        card.close()

class Yield:
    def __init__(self,*args,**kwargs):
        if not args:
            raise RuntimeError('Specify number of entries')
        self._N = args[0]
        if 'name' in kwargs:
            self._name = kwargs['name']
        if 'entries' in kwargs:
            self._entries = kwargs['entries']


class ShapeLoader:
    '''Load the histogram data from the shape file
    + Yields
    + Nuisance shapes and parameters'''
    _log = logging.getLogger('ShapeLoader')

    def __init__(self, path):
        self._src = ROOT.TFile.Open(path)
        self._yields = OrderedDict()

    def __del__(self):
        del self._src

    def yields(self):
        return self._yields.copy()

    def effects(self):
        return self._effects.copy()

    def load(self):
        # load the list of processes
        processes = sorted([ p.GetName() for p in self._src.Get('processes') ])
        # load the histograms and calculate the yields
        names = sorted([ k.GetName() for k in self._src.GetListOfKeys() ])
        names.remove('processes')


        self._nominals    = []
        self._systematics = []
        
        self._nominals = [ ('histo_'+p,p) for p in processes if 'histo_'+p in names] 
        if len(self._nominals) != len(processes):
            raise RuntimeError('Not all process shapes have been found')

        for p in processes:
            systre = re.compile('^histo_%s_(.+)(Up|Down)$' % p)
            systp = []
            for name in names:
                m = systre.match(name)
                if not m: continue
                systp.append( (name,p,m.group(1),m.group(2)) )
#             systs = [ (name,p, for name in names if systre.match(name) ]
#               print 'xxx',p,systp
#                print 'xxx',p,m.group(1),m.group(2)
            self._systematics += systp

        self._systematics = sorted(self._systematics)

        for name,process in self._nominals:
#             process = self._nomRegex.match(name).group(1)
            h = self._src.Get(name)
            N =  h.Integral(0,h.GetNbinsX())
            entries = h.GetEntries()

            # TODO: DYTT cleanup
#             if entries < 5: continue

            self._yields[process] = Yield( N, name=process, entries=entries ) 
#             self._yields[process] = Yield( N, name=process, entries=entries, shape=h ) 
        
        ups = {}
        downs = {}
        for name,process,effect,var in self._systematics:
            # check for Up/Down
#             (process,effect,var) = self._systRegex.match(name).group(1,2,3)
            print "process,effect,var = ", process,effect,var
            if var == 'Up': 
                if effect not in ups: ups[effect]= []
                ups[effect].append(process)
            elif var == 'Down':
                if effect not in downs: downs[effect]= []
                downs[effect].append(process)
        # check 
        print " ups = ", ups
        print " downs = ", downs

        for effect in ups:
            if set(ups[effect]) != set(downs[effect]):
                sUp = set(ups[effect])
                sDown = set(downs[effect])
                raise RuntimeError('Some systematics shapes for '+effect+' not found in up and down variation: \n '+', '.join( (sUp | sDown) - ( sUp & sDown ) ))
        
        # all checks out, save only one
        self._effects = ups

class NuisanceMapBuilder:
    _log = logging.getLogger('NuisanceMapBuilder')

    def __init__(self, ddPath, noWWddAbove, shape=True, isssactive=False, statmode='unified'):
        self._common       = OrderedDict()
        self._0jetOnly     = OrderedDict()
        self._1jetOnly     = OrderedDict()
        self._ddEstimates  = OrderedDict()
        self._shape        = shape
        self._isssactive   = isssactive
        # to options
        self.statShapeVeto = []
        self.expShapeVeto  = OrderedDict()
        self._statmode     = statmode

        # data driven reader and filter for the ww
        self._ddreader      = datadriven.DDCardReader(ddPath)
        self._wwddfilter    = datadriven.DDWWFilter(self._ddreader, noWWddAbove)

# This is deprecated ( Xavier, 21 Nov 2013 )
#        self._build()
# 
#    def _build(self):
#        # common 0/1/2 jet systematics
#        pureMC = [ 'VgS', 'Vg', 'VV', 'ggH', 'qqH', 'wzttH', 'ZH', 'WH', 'ttH', 'Other', 'VVV', 'WW', 'WWewk']
#        dummy = {}
#        dummy['CMS_fake_e']    = (1.50, ['WJet']) # take the average of ee/me 
##         dummy['CMS_fake_m']    = (1.42, ['WJet']) # take the average of mm/em
#        dummy['CMS_eff_l']     = (1.04, pureMC)
#        dummy['CMS_p_scale_e'] = (1.02, pureMC)
##         dummy['CMS_p_scale_m'] = (1.01, pureMC)
#        dummy['CMS_p_scale_j'] = (1.02, pureMC)
#        dummy['CMS_met']       = (1.02, pureMC)
#        dummy['lumi']          = (1.04, pureMC)
#
#        for k,v in dummy.iteritems():
#            self._common[k] = (['lnN'], dict([( process, v[0]) for process in v[1] ]) )
#
#        self._common['pdf_gg']    = (['lnN'],dict([('ggWW',1.04),('ggH',1.08)]) )
#        self._common['pdf_qqbar'] = (['lnN'],dict([('WW',1.04),('VV',1.04),('qqH',1.02)]) )
#        self._common['pdf_assoc'] = (['lnN'],dict([('WW',1.04)]) )
#
#        dummy = {} 
#        # both 0/1 jets but different
#        dummy['CMS_QCDscale_WW_EXTRAP'] = ([0.95, 1.21], ['WW'])
#        dummy['QCDscale_VV']            = ([1.03, 1.03], ['VV'])
#        dummy['QCDscale_ggH1in']        = ([0.89, 1.39], ['ggH'])
#        dummy['QCDscale_ggH_ACEPT']     = ([1.02, 1.02], ['ggH'])
#        dummy['QCDscale_ggVV']          = ([1.30, 1.30], ['ggWW'])
#        dummy['QCDscale_qqH']           = ([1.01, 1.01], ['qqH'])
#        dummy['QCDscale_qqH_ACEPT']     = ([1.02, 1.02], ['qqH'])
#        dummy['QCDscale_wzttH_ACEPT']   = ([1.02, 1.02], ['wzttH'])
#        dummy['QCDscale_wzttH']         = ([1.01, 1.01], ['wzttH'])
#        dummy['UEPS']                   = ([0.94, 1.11], ['ggH'])
#
#        for k,v in dummy.iteritems():
#            self._0jetOnly[k] = (['lnN'], dict([( process, v[0][0]) for process in v[1] ]) )
#            self._1jetOnly[k] = (['lnN'], dict([( process, v[0][1]) for process in v[1] ]) )
#
#
#        # 0 jets only
#        dummy = {}
#
#        dummy['CMS_fake_Vg']  = (2.00,['Vg']) # Vg, 0jet 
#        dummy['QCDscale_Vg']  = (1.50,['Vg']) 
#        dummy['QCDscale_ggH'] = (1.16,['ggH']) # 0 jets only
#        for k,v in dummy.iteritems():
#            self._0jetOnly[k] = (['lnN'], dict([( process, v[0]) for process in v[1] ]) )
#
#        # 1 jet only
#        dummy = {}
#        dummy['QCDscale_ggH2in'] = (0.95,['ggH']) # 1 jey only
#        for k,v in dummy.iteritems():
#            self._1jetOnly[k] = (['lnN'], dict([( process, v[0]) for process in v[1] ]) )
#

    def _addDataDrivenNuisances(self, nuisances, yields, mass, channel, jetcat, suffix, opts):

        if self._ddreader.iszombie: return
        (estimates,dummy) = self._wwddfilter.get(mass, channel)

        pdf = 'lnN'

        # this mapping specifies the context of the systematics (i.e. jet category, channel) and how the dds must be combined between channels.
        # separate cut-based DD estimates from shape since the control region is different
        if (self._shape) :
            cb = ''
        else :
            cb = '_cb'
        # XJ: doing cb as shape was remocing that prefix again !  
        if 'sf_0j' in channel : cb = '_cb'
        if 'sf_1j' in channel : cb = '_cb'
        print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! TEMP FIX !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ',cb,channel
        mapping = {
            'WW'      : ( jetcat+cb,  ['WW','ggWW'] ),
            'Top'     : ( jetcat+cb,  ['Top']       ),
            'DYLL'    : ( jetcat+cb,  ['DYLL']      ),
            'DYee'    : ( channel+cb, ['DYee']      ),
            'DYmm'    : ( channel+cb, ['DYmm']      ),
            'DYee05'  : ( channel+cb, ['DYee05']      ),
            'DYmm05'  : ( channel+cb, ['DYmm05']      ),
        }

        # see if there are MC extrapolation scale factors needed
        MCextrapFile = 'ScaleFactors.py'
        if os.path.exists(MCextrapFile):
            handle = open(MCextrapFile,'r')
            scaleFactor = {}
            exec(handle)
            handle.close()

        eff_bin1_tmpl = 'CMS{0}_hww_{1}_{2}_stat_bin1'
        for tag,(context, processes) in mapping.iteritems(): 
            extr_uncorr_entries = {}
            extr_corr_entries = {}
            extr_entries = {}
            stat_entries = {}

            if (tag=="WW" and (jetcat=="0j" or jetcat=="1j")) :
                eff_extr    = 'CMS{0}_hww_{1}_extr'.format(suffix,tag)
            else :
                eff_extr    = 'CMS{0}_hww_{1}_{2}_extr'.format(suffix,tag,context)
            eff_stat        = 'CMS{0}_hww_{1}_{2}_stat'.format(suffix,tag,context)
            eff_extr_corr   = 'CMS{0}_hww_{1}_{2}_extr_corr'.format(suffix,tag,context)
            eff_extr_uncorr = 'CMS{0}_hww_{1}_{2}_extr_uncorr'.format(suffix,tag,channel)

            available = [ p for p in processes if p in estimates ]
            if not available: continue

            # check the dd to have the same events in the ctr region before associating them
            listNctr = [ estimates[p].Nctr for p in available ]

            if len(available) != listNctr.count(estimates[available[0]].Nctr):
                raise RuntimeError('Mismatch between Nctr in the same systematic: '+', '.join([ '{0}{1}'.format(n[0],n[1]) for n in zip(available, listNctr) ]) )

            flagdoextracorr = 0
            flagdoextrauncorr = 0

            for process in available:
                e = estimates[process]

                doneMCextrap = False
                if 'MCextrap' in opts:
                  # MC extrapolation is needed for some dd
                  for nameNuis,nameNominal,nameSimilTemplate in opts['MCextrap'] :
                    # check if the name of the nuisance is correct
                    #print " ::::::::: nameNuis = ",nameNuis,"   :: eff_stat = ",eff_stat
                    if (nameNuis == eff_stat) :
                      # read from file the scale factor
                      # e.g.: scaleFactor.update({110: {'CHITOP-Top': 0.02029}})
                      #       MCextrap = [('CMS_8TeV_hww_Top_2j_stat',  'Top',      'CHITOP')]
                      valueScaleFactor = scaleFactor[mass]['%s-' %nameSimilTemplate + '%s' %nameNominal]
                      #print valueScaleFactor
                      e.alphaPrime = e.alpha * valueScaleFactor
                      doneMCextrap = True

                extrUnc = 1+e.delta/e.alpha if pdf != 'gmN' else e.delta/e.alpha

                if e.deltaUnCorr != 0:
                    extr_uncorr_entries[process] = 1. + e.deltaUnCorr/e.alpha
                if e.deltaCorr != 0: 
                    extr_corr_entries[process] = 1. + e.deltaCorr/e.alpha
#                 if jetcat == '2j' and tag == 'Top' :
#                      if e.deltaCorr != 0: 
#                          extr_corr_entries[process] = 1. + e.deltaCorr/e.alpha
#                          flagdoextracorr = 1
                extr_entries[process] = extrUnc
                if (e.alphaPrime < 0) :
                  stat_entries[process] = e.alpha
                else :
                  stat_entries[process] = e.alphaPrime  # in case of MC extrapolation

                eff_bin1 = eff_bin1_tmpl.format(suffix,process,channel)
                if eff_bin1 in nuisances and not doneMCextrap:
                    # only if not bin-by-bin, then remove statistical uncertainty for datadriven samples
                    # for bbb it the single bin variation has already been normalized to the nominal
                    if self._statmode != 'bybin':
                        del nuisances[eff_bin1]

                if not doneMCextrap and 'CMS%s' % suffix +'_eff_e' in nuisances and process == 'Top':
                  del nuisances['CMS%s' % suffix +'_eff_e'][1][process]
                if not doneMCextrap and 'CMS%s' % suffix +'_eff_m' in nuisances and process == 'Top':
                  del nuisances['CMS%s' % suffix +'_eff_m'][1][process]
                # for Top no b-mistag error (if added before)
                if 'CMS'+suffix+'hww2j_misb' in nuisances and process == 'Top':
                  del nuisances['CMS'+suffix+'hww2j_misb'][1][process]

#             if jetcat == '2j' and tag == 'Top' :
#                 if flagdoextracorr == 1 :
#                     nuisances[eff_extr_corr] = ([pdf], extr_corr_entries )

            if len(extr_corr_entries) > 0:
                nuisances[eff_extr_corr] = ([pdf], extr_corr_entries )
            else :
                if (tag=="WW" and (jetcat=="0j" or jetcat=="1j")) :
                    eff_extr    = 'CMS{0}_hww_{1}_extr'.format(suffix,tag)
                else :
                   eff_extr    = 'CMS{0}_hww_{1}_{2}_{3}_extr'.format(suffix,tag,context,channel)
                eff_stat        = 'CMS{0}_hww_{1}_{2}_{3}_stat'.format(suffix,tag,context,channel)


            if len(extr_uncorr_entries) > 0:
                nuisances[eff_extr_uncorr] = ([pdf], extr_uncorr_entries )
            else :
                if (tag=="WW" and (jetcat=="0j" or jetcat=="1j")) :
                    eff_extr    = 'CMS{0}_hww_{1}_extr'.format(suffix,tag)
                else :
                   eff_extr    = 'CMS{0}_hww_{1}_{2}_{3}_extr'.format(suffix,tag,context,channel)
                eff_stat        = 'CMS{0}_hww_{1}_{2}_{3}_stat'.format(suffix,tag,context,channel)


            nuisances[eff_extr] = ([pdf], extr_entries )
            nuisances[eff_stat] = (['gmN',e.Nctr], stat_entries)



    def _addStatisticalNuisances(self,nuisances, yields,channel,suffix=''):
        for p,y in yields.iteritems():
            if p == 'Data':
                continue
            name  = 'CMS{0}_hww_{1}_{2}_stat_bin1'.format(suffix,p,channel)
            if y._entries == 0.:
                continue
            value = 1+(1./ROOT.TMath.Sqrt(y._entries) if y._entries > 0 else 0.)
            nuisances[name] = ( ['lnN'], dict({p:value}) )

    def _addWWShapeNuisances(self,nuisances, effects):
        '''Generator relates shape nuisances'''
        wwRegex  = re.compile('Gen_(.+)$')
        for eff,processes in effects.iteritems():
            # select the experimental effects only (starting with gen)
            if not wwRegex.match(eff):
                continue

            tag = eff
            if tag in nuisances: del nuisances[tag]
            nuisances[tag] = (['shapeN2'],dict([ (p,1) for p in processes]) )

    def _addInterfShapeNuisances(self,nuisances, effects):
        '''Interference related shape nuisances'''
        wwRegex  = re.compile('interf_(.+)$')
        for eff,processes in effects.iteritems():
            # select the experimental effects only (starting with gen)
            if not wwRegex.match(eff):
                continue

            tag = eff
            if tag in nuisances: del nuisances[tag]
            nuisances[tag] = (['shapeN2'],dict([ (p,1) for p in processes]) )

    def _addExperimentalShapeNuisances(self, nuisances, effects, suffix, yields):
        '''Experimental Shape-based nuisances'''
        # expr for CMS nuisances
        expRegex  = re.compile('CMS_(.+)')
        # expr for statistical nuisances
        statRegex = re.compile('CMS_hww_([^_]+)_.+_stat_shape')

#         mask = ['Vg','DYLL','DYTT']#'WJet',]#'Vg','DYLL','DYTT',]#]#,'Top',]#'WW','ggWW','VV',]#'ggH','vbfH']
        for eff in sorted(effects):
            # select the experimental effects only (starting with CMS)
            if not expRegex.match(eff):
                continue

            m = statRegex.match(eff)
#             if m:
#                 print m.group(1), self.statShapeVeto
            if m and m.group(1) in self.statShapeVeto:
                self._log.info( 'Skipping %s (vetoed, data driven)', eff )
                continue

            tag = eff
            if tag in nuisances: del nuisances[tag]
          # nuisances[tag] = (['shapeN2'],dict([ (p,1) for p in effects[eff] if p not in self.expShapeVeto[tag]]) )
          # nuisances[tag] = (['shapeN2'],dict([ (p,1) for p in effects[eff] if p not in self.expShapeVeto.get(tag,[])]) )
          #  nuisances[tag] = (['shapeN2'],dict([ (p,1) for p in effects[eff] if (not (tag in self.expShapeVeto) or p not in self.expShapeVeto[tag]) ]) )
          #  nuisances[tag] = (['shapeN2'],dict([ (p,1) for p in effects[eff] if ((not (tag in self.expShapeVeto) or p not in self.expShapeVeto[tag])) and ( yields[p] is not None and yields[p]._N()!=0 )  ]) )
            names = []
            for tempnames, tempvalue in yields.iteritems():
              names.append(tempnames)

          # remove nuisance if 0 entries in nominal! "Bogus norm" error in combine
            nuisances[tag] = (['shapeN2'],dict([ (p,1) for p in effects[eff] if ((not (tag in self.expShapeVeto) or p not in self.expShapeVeto[tag])) and ( p in names and yields[p]._N!=0 )  ]) )

    def _addShapeNuisances(self, nuisances, effects, opts, suffix, yields):
        # local copy
        shapeNu = OrderedDict()

        self._addWWShapeNuisances(shapeNu, effects)
        self._addInterfShapeNuisances(shapeNu, effects)
        self._addExperimentalShapeNuisances(shapeNu, effects, suffix, yields)

        if 'shapeFlags' not in opts:
            sys.exit(-1)
        flags = opts['shapeFlags']

        nus = set(shapeNu.keys())
        dummy = nus.copy()
        for exp,flag in flags:
            subset = set(fnmatch.filter(nus,exp))
            if flag:
                dummy |= subset
            else:
                dummy -= subset

        for eff in shapeNu:
            if eff not in dummy: continue
            if eff in nuisances: del nuisances[eff]
            nuisances[eff] = shapeNu[eff]

    #  _  _      _                          
    # | \| |_  _(_)___ __ _ _ _  __ ___ ___
    # | .` | || | (_-</ _` | ' \/ _/ -_|_-<
    # |_|\_|\_,_|_/__/\__,_|_||_\__\___/__/
    #                                      
    def nuisances(self, yields, effects, mass, channel, jetcat, flavor, opts ):
        '''Add the nuisances according to the options'''
        allNus = OrderedDict()

        optMatt = mattOpts()
        optMatt.WJadd = 0.36
        optMatt.WJsub = 0.0

        qqWWfromData = self._wwddfilter.haswwdd(mass, channel)

        # vh and vbf and wwewk mapped to "2j" category
        if (jetcat == 'vh2j' or jetcat == 'whsc' or jetcat == '2jtche05' or jetcat == '2jtche05CJ' or jetcat == '2jtche05FJ') :
           jetcat = '2j'

        # vh : remove some nuisances, typical of vbf only
        if (jetcat == 'vh2j' or jetcat == 'whsc') :
           optMatt.VH = 1
        else :
           optMatt.VH = 0
        if jetcat not in ['0j','1j','2j','2jex'] and 'pth' not in jetcat: raise ValueError('Unsupported jet category found: %s')

#         suffix = '_8TeV'
#         if '2011' in opt.dataset: suffix = '_7TeV'

        suffix = '_'+opt.energy
        njett = jetcat[0] if 'pth' not in jetcat else 0
        CutBased = getCommonSysts(int(mass),flavor,int(njett),qqWWfromData, self._shape, optMatt, suffix, self._isssactive, opt.energy,opts['newInterf'],opt.YRSysVer,opt.mHSM)
        if self._shape:
            # float WW+ggWW background normalisation float together
#             for p in opts['floatN'].split(' '):
            for p in opts['floatN']:
                print p
                floatN = floatNorm(p,jetcat)
                CutBased.update( floatN )

        common = OrderedDict()
        for k in sorted(CutBased):
            common[k] = CutBased[k]
        allNus.update( common )


        # only if not bin-by-bin, then add statistical uncertainty
        # for bbb it is already included
        if self._statmode != 'bybin':
            self._addStatisticalNuisances(allNus, yields, channel, suffix)

        self._addDataDrivenNuisances(allNus, yields, mass, channel, jetcat, suffix, opts)

        if self._shape:
            self._addShapeNuisances(allNus,effects, opts, suffix, yields)

        if 'nuisFlags' not in opts:
            raise RuntimeError('nuisFlags not found among the allNus options')

        flags = opts['nuisFlags']

        finalNuisances = OrderedDict()
        nus = set(allNus.keys())
        dummy = nus.copy()
        for exp,flag in flags:
            subset = set(fnmatch.filter(nus,exp))
            if flag:
                dummy |= subset
            else:
                dummy -= subset

        nuisances = OrderedDict()
        for eff in allNus:
            if eff not in dummy: continue
            nuisances[eff] = allNus[eff]

        return nuisances

def incexc(option, opt_str, value, parser):
    if not hasattr(parser.values,'shapeFlags'):
        setattr(parser.values,'shapeFlags',[])
    if not hasattr(parser.values,'nuisFlags'):
        setattr(parser.values,'nuisFlags',[])

    if not hasattr(parser.values,'MCextrap'):
        setattr(parser.values,'MCextrap',[])

    optarray = str(option).split('/')
    print optarray
    if '--Ish' in optarray:
        parser.values.shapeFlags.append((value,True))
    elif '--Xsh' in optarray:
        parser.values.shapeFlags.append((value,False))
    elif '-I' in optarray:
        parser.values.nuisFlags.append((value,True))
    elif '-X' in optarray:
        parser.values.nuisFlags.append((value,False))
    
class mattOpts: pass

if __name__ == '__main__':
    print '''
.------..------..------.       .------..------..------.       .------..------..------.
|B.--. ||E.--. ||T.--. | .-.   |T.--. ||H.--. ||E.--. | .-.   |P.--. ||O.--. ||T.--. |
| :(): || (\/) || :/\: |((5))  | :/\: || :/\: || (\/) |((5))  | :/\: || :/\: || :/\: |
| ()() || :\/: || (__) | '-.-. | (__) || (__) || :\/: | '-.-. | (__) || :\/: || (__) |
| '--'B|| '--'E|| '--'T|  ((1))| '--'T|| '--'H|| '--'E|  ((1))| '--'P|| '--'O|| '--'T|
`------'`------'`------'   '-' `------'`------'`------'   '-' `------'`------'`------'
'''

    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(usage)
    parser.add_option('-p', '--prefix'  , dest='prefix'      , help='Datacard directory prefix'           , default=None)
    parser.add_option('--cutbased'      , dest='shape'       , help='Make cutbased datacards (no shapes)' , default=True , action='store_false' )
    parser.add_option('--no_wwdd_above' , dest='noWWddAbove' , help='No WW dd above this mass'            , default=None   , type='int'     )
    parser.add_option('--dataset'       , dest='dataset'     , help='Dataset to process'                  , default=None)
    parser.add_option('--statmode'      , dest='statmode'    , help='Production mode for stat-shapes (default = %default)', default='unified')
    parser.set_defaults(MCextrap=[])
    parser.set_defaults(shapeFlags=[])
    parser.set_defaults(nuisFlags=[])
    parser.add_option('--Xsh','--excludeShape', dest='shapeFlags'        , help='exclude shapes nuisances matching the expression', action='callback', type='string', callback=incexc)
    parser.add_option('--Ish','--includeShape', dest='shapeFlags'        , help='include shapes nuisances matching the expression', action='callback', type='string', callback=incexc)
    parser.add_option('-X','--exclude',         dest='nuisFlags'         , help='exclude nuisances matching the expression',        action='callback', type='string', callback=incexc)
    parser.add_option('-I','--include',         dest='nuisFlags'         , help='include nuisances matching the expression',        action='callback', type='string', callback=incexc)
    parser.add_option('-M','--MCextrap',        dest='MCextrap'          , help='For MC extrapolation: gmN nuisance to be scaled',  action='callback', type='string', callback=incexc)
    parser.add_option('--path_dd'           ,   dest='path_dd'           , help='Data driven path'                 , default=None)
    parser.add_option('--path_shape_merged' ,   dest='path_shape_merged' , help='Destination directory for merged' , default=None)
#     parser.add_option('--floatN',               dest='floatN'            , help='float normalisation of particular processes, separate by space ', default=' ')
    parser.add_option('--isssactive',           dest='isssactive'        , help='Is samesign datacard available'                           , default=False)
    parser.add_option('--floatN',               dest='floatN'            , help='float normalisation of particular processes, separate by space',  default=[] , type='string' , action='callback' , callback=hwwtools.list_maker('floatN'))
    parser.set_defaults(listSignals=[])
    parser.add_option('--lSg','--listSignals',  dest='listSignals'       , help='list of signal samples', action='callback', type='string', callback=incexc)


    parser.add_option('--newcps',        dest='newcps',  help='On/Off New CPS weights',               default=False , action='store_true')
    # EWK Doublet Model
    parser.add_option('--ewksinglet',    dest='ewksinglet',  help='On/Off EWK singlet model',           default=False , action='store_true')   
    parser.add_option('--cprimesq'  ,    dest='cprimesq',    help='EWK singlet C\'**2 mixing value',    default=[1.]  , type='string'  , action='callback' , callback=hwwtools.list_maker('cprimesq',',',float))
    parser.add_option('--brnew'     ,    dest='brnew'   ,    help='EWK singlet BRNew values',           default=[0.]  , type='string'  , action='callback' , callback=hwwtools.list_maker('brnew',',',float))
    parser.add_option('--YRSysVer'  ,    dest='YRSysVer',    help='Yellow Report Version (Syst)',       default=3     , type='int' )   
    parser.add_option('--mHSM'      ,    dest='mHSM',        help='Mass of the SM Higgs boson@125',     default=125.6 , type='float')
    hwwtools.addOptions(parser)
    hwwtools.loadOptDefaults(parser)

    (opt, args) = parser.parse_args()
    print 'ShapeFlags: ',opt.shapeFlags
    print 'NuisFlags:  ',opt.nuisFlags
    print 'noWWddAbove:',opt.noWWddAbove
    print 'dataset:    ',opt.dataset
    print 'isssactive: ',opt.isssactive
    print 'MCextrap:   ',opt.MCextrap
    print 'listSignals:',opt.listSignals


    # checks
    if not opt.variable or not opt.lumi:
        parser.error('The variable and the luminosty must be defined')
    var = opt.variable

    if not opt.debug:
        pass
    elif opt.debug > 0:
        logging.basicConfig(level=logging.DEBUG)

    sys.argv.append('-b')
    ROOT.gROOT.SetBatch()

#     masses = hwwinfo.masses[:] if opt.mass == 0 else [opt.mass]
    masses = opt.mass
    channels =  dict([ (k,v) for k,v in hwwinfo.channels.iteritems() if k in opt.chans])

    print channels

    mergedPath = opt.path_shape_merged
    outPath    = 'datacards/'
    if opt.prefix:
        if opt.prefix[0] == '/':
            raise NameError('prefix: Only subdirectories are supported')
        outPath = (opt.prefix if opt.prefix[-1] == '/' else opt.prefix+'/')+outPath
    shapeSubDir = 'shapes/'

    shapeDir = os.path.join(outPath,shapeSubDir[:-1])

    os.system('mkdir -p '+outPath)
    if os.path.exists(shapeDir):
        os.unlink(shapeDir)
    os.symlink(os.path.abspath(mergedPath), shapeDir)

    optsNuis = {}
    optsNuis['MCextrap'] = opt.MCextrap
    optsNuis['shapeFlags'] = opt.shapeFlags
    optsNuis['nuisFlags'] = opt.nuisFlags
    optsNuis['floatN'] = opt.floatN
    optsNuis['newInterf'] = opt.newcps
    lumistr = '{0:.2f}'.format(opt.lumi)


    nModel = 1
    if opt.ewksinglet : nModel = len(opt.cprimesq)*len(opt.brnew)
    for iModel in xrange(0,nModel):
        iCP2 = iModel%len(opt.cprimesq)
        iBRn = (int(iModel/len(opt.cprimesq)))

        if opt.ewksinglet:
          shapeTmpl = os.path.join(mergedPath,'hww-'+lumistr+'fb.mH{mass}.{channel}.EWKSinglet_CP2_'+str(opt.cprimesq[iCP2]).replace('.','d')+'_BRnew_'+str(opt.brnew[iBRn]).replace('.','d')+'_shape.root')
        else:
          shapeTmpl = os.path.join(mergedPath,'hww-'+lumistr+'fb.mH{mass}.{channel}_shape.root')
        #mask = ['Vg','DYLL','DYTT']
        mask = ['DYLL']
    
        maskVeto = {
           'CMS_8TeV_p_scale_j':['DYTT'],
           'CMS_8TeV_puModel'  :['DYTT'],
           }
    
    
    
        builder = NuisanceMapBuilder( opt.path_dd, opt.noWWddAbove, opt.shape, opt.isssactive, opt.statmode)
        builder.statShapeVeto = mask
        builder.expShapeVeto  = maskVeto
    
        for mass in masses:
            if '2011' in opt.dataset and (mass==145 or mass==155): continue
            for ch,(jcat,fl) in channels.iteritems():
    
    #         for jets in jetBins:
    #             for flavor in flavors:
                print '- Processing',mass, ch
                loader = ShapeLoader(shapeTmpl.format(mass = mass, channel=ch) ) 
                loader.load()
    
                writer = ShapeDatacardWriter( mass, ch, opt.shape, opt.dataset )
                print '   + loading yields'
                yields = loader.yields()
    
                # reshuffle the order
                #order = [ 'vbfH', 'ggH', 'wzttH', 'ggWW', 'Vg', 'WJet', 'Top', 'WW', 'DYLL', 'VV', 'DYTT', 'Data']
                order = [ 'ggH', 'ggHBin0','ggHBin1','ggHBin2','ggHBin3','ggHBin4','ggHBin5', 'ggH_ALT','qqH', 'qqHBin0', 'qqHBin1', 'qqHBin2', 'qqHBin3', 'qqHBin4', 'qqHBin5', 'qqH_ALT', 'wzttH','wzttH_ALT', 'WH', 'WHBin0', 'WHBin1', 'WHBin2', 'WHBin3', 'WHBin4', 'WHBin5', 'ZH', 'ZHBin0', 'ZHBin1', 'ZHBin2', 'ZHBin3', 'ZHBin4', 'ZHBin5', 'ttH', 'ggWW', 'VgS', 'Vg', 'WJet', 'Top', 'Top0jet', 'Topge1jet', 'Topge1jetCtrl', 'Top0jet_nowe', 'Topge1jet_nowe', 'TopPt0', 'TopPt1', 'TopPt2', 'TopPt3', 'TopPt4', 'TopPt5', 'TopPt6', 'TopPt7', 'TopPt8', 'WW', 'WWewk', 'DYLL', 'VV', 'DYTT', 'DYee', 'DYmm', 'DYee05', 'DYmm05', 'Other', 'VVV', 'Data','ggH_SM', 'qqH_SM', 'WH_SM','ZH_SM' , 'wzttH_SM', 'ggH_sbi', 'ggH_s', 'ggH_b', 'qqH_sbi', 'qqH_s', 'qqH_b', 'WWBin0', 'WWBin1', 'WWBin2', 'WWBin3', 'WWBin4', 'WWBin5',]
    
   
                oldYields = yields.copy()
                yields = OrderedDict([ (k,oldYields[k]) for k in order if k in oldYields])
                
                # lista systematiche sperimentali (dal file. root)
                effects = loader.effects()

                print '   + making nuisance map'
                nuisances = builder.nuisances( yields, effects , mass, ch, jcat, fl, optsNuis)
    
                for n,(pdf, eff) in nuisances.iteritems():
                    if 'ggH' in eff and 'shape' not in pdf[0] and 'stat_bin' not in n :
                        eff['ggH_ALT'] =  eff['ggH']
                    if 'qqH' in eff and 'shape' not in pdf[0] and 'stat_bin' not in n :
                        eff['qqH_ALT'] =  eff['qqH']
                    if 'wzttH' in eff and 'shape' not in pdf[0] and 'stat_bin' not in n :
                        eff['wzttH_ALT'] =  eff['wzttH']
    
                #basename = 'hww-'+lumistr+'fb.mH{mass}.{bin}_shape'
                if opt.ewksinglet:
                  basename = 'hww-'+lumistr+'fb.mH{mass}.{bin}.EWKSinglet_CP2_'+str(opt.cprimesq[iCP2]).replace('.','d')+'_BRnew_'+str(opt.brnew[iBRn]).replace('.','d')
                else:
                  basename = 'hww-'+lumistr+'fb.mH{mass}.{bin}'
                if opt.shape :
                     basename  = basename + '_shape'
                print '   + dumping all to file'
                if opt.listSignals==[] :
                     writer.write(yields,nuisances,outPath+basename+'.txt',shapeSubDir+basename+'.root')
                else :
                     writer.write(yields,nuisances,outPath+basename+'.txt',shapeSubDir+basename+'.root',opt.listSignals)



