#!/bin/env python

import pdb

import sys
import os.path
import hwwtools
import logging
import array
import re
import math
import copy
import numpy as np
import HWWAnalysis.Misc.odict as odict


from HiggsAnalysis.CombinedLimit.DatacardParser import *
from HiggsAnalysis.CombinedLimit.ShapeTools import *
from HWWAnalysis.Misc.ROOTAndUtils import TH1AddDirSentry

import ROOT

#---
def getnorms(pdf, obs, norms = None ):
    '''helper function to exctact the normalisation factors'''

    out = norms if norms!=None else {}

#     logging.debug('searching norms in class: %s' % pdf.__class__.__name__ )

    if isinstance(pdf,ROOT.RooSimultaneous):
        cat = pdf.indexCat()
        idx = cat.getIndex()
        for i in xrange(cat.numBins('')):
            cat.setBin(i)
            pdfi = pdf.getPdf(cat.getLabel());
            if pdfi.__nonzero__(): getnorms(pdfi, obs, out);
        # restore the old index
        cat.setIndex(idx)
        #pass


    if isinstance(pdf,ROOT.RooProdPdf):
        pdfs = ROOT.RooArgList(pdf.pdfList())
        for pdfi in roofiter(pdfs):
            if pdfi.dependsOn(obs): getnorms(pdfi,obs,out)

    if isinstance(pdf,ROOT.RooAddPdf):
        coefs = ROOT.RooArgList(pdf.coefList())
        for c in roofiter(coefs):
            out[c.GetName()] =  c.getVal(obs)

    return out

#---
class roofiter:
    def __init__(self,collection):
        self._iter = collection.fwdIterator()

    def __iter__(self):
        return self

    def next(self):
        o = self._iter.next()
        if not o: raise StopIteration
        return o

# ---
class Coroner(object):
    '''Class to recompose a histograms-base combined model into drawable objects'''
    _log = logging.getLogger('Coroner')
    def __init__(self, bin, DC, MB, ws, fit): 
        self._DC = DC
        self._MB = MB
        # todo: what is the role of the bin in the multibin case?
        self._bin = bin
        self._ws = ws
        # TODO, rearrange this fit information
        self._fit = fit
        self._model    = fit[0]  
        self._fitpars  = fit[1]
        self._fitnorms = fit[2]

        self._build()

        # set the default error calc function
        self.errmode  = 'errorband'

    @property
    def errmode(self): return self._errmode
    
    @errmode.setter
    def errmode(self, mode):
        if   mode == 'errorband':
            self._computeerrors = self._errorband
        elif mode == 'rawerrors':
            self._computeerrors = self._rawerrors
        else:
            raise ValueError('Unknown error mode: %s [allowed errorband,rawerrors]' % mode)

        self._errmode = mode


    #---
    def _build(self):
        '''Fill up the objects'''

        hdata = self._MB.getShape(self._bin,'data_obs')

        # the Xaxis label has to be cheked
        self._template = hdata.Clone('shape_template')
        self._template.SetTitle('shape_template')
        self._template.Reset()

        # keep a pointer to the data object
        self._data  = self._ws.data('data_obs')

        # keep a pointer to the category
        self._cat   = self._ws.cat('CMS_channel')
        self._cat.setLabel(self._bin)

        # keep a pointer to the x-variable as well
        self._x = self._ws.var('CMS_th1x')

        # count the expected number of bins for this bin
        itdata = self._data.sliceIterator(self._x,ROOT.RooArgSet(self._cat))
        i = 0
        while itdata.Next():
            i += 1
        self._nentries = i
        if self._nentries > self._template.GetNbinsX():
            self._log.warn('The bins in shape template do not match the workspace dataset, for bin %s: %d != %d' % (self._bin, self._nentries, self._template.GetNbinsX()) )
            self._nentries = self._template.GetNbinsX()
        elif self._nentries < self._template.GetNbinsX():
            raise ValueError('There are less entries than template bins, for bin %s: %d != %d ' % (self._bin, self._nentries, self._template.GetNbinsX()) )


        self._log.info('Will make shapes with %d entries (aka histogram bins)' % self._nentries )

        # list the processes with non 0 yield
        self._processes = []
        for p,y in self._DC.exp[self._bin].iteritems():
            if y > 0.: self._processes.append(p)
            else: self._log.info('Process %s has 0 yield in bin %s', p,self._bin )

        # double check the pdfs of the model
#         norms = self._getnormalisations(self._model)
#         
#         missing = set([ p for p in self._processes if p not in norms ])
#         # check if this is the background only mode
#         if missing <= set(self._DC.signals):
#             self._log.debug('Some missing processes, but they are all signals. Bkg only mode')
#             for p in missing:
#                 self._processes.remove(p)

        # make the nus <-> pars maps
        self._makenumaps()
        
        # finally store the list of pdfs
        self._pdfs = self._getpdfs()


    #---
    def _makenumaps(self):
        # make a map of the variables (nuisances+r) associated to each process per bin
        # used for filtering later
        # this is list comprehension madness
        # slimmed to nuisance->processes map
        # the forula is v != 0 ( and not v > 0) to include cases where v is a list (asym errors)
        nu2procs = odict.OrderedDict([ (n,[ p for p,v in e[self._bin].iteritems() if v != 0. ]) for (n,nf,pf,a,e) in self._DC.systs])

        # init the new array
        proc2nus = odict.OrderedDict([ (p,[]) for p in self._processes])
        for (n,nf,pf,a,e) in self._DC.systs:
            try:
                for p,val in e[self._bin].iteritems():
                    # if the variation is not 0, append the nuisance to the process
                    # could be a  non-zer0 float or a list. What if it is none?
                    if val != 0: proc2nus[p].append(n)
            except KeyError:
                self._log.debug('No processes in bin %s for nuisance %s' % (self._bin, n) )
                continue

        
        # filter out the 
        self._nu2procs = {}
        for n,ps in nu2procs.iteritems():
            if len(ps) != 0:
                self._nu2procs[n] = ps
            else:
                self._log.debug('Nuisance %s does not affect bin %s',n,self._bin)
        # add the signal strength
        self._nu2procs['r'] = self._DC.signals
        self._proc2nus = proc2nus

        # add the signal strength to the parameters
        for s in self._DC.signals:
            if s in self._proc2nus:
                self._proc2nus[s].append('r')


    #---
    def _getpdfs( self ):
        '''Extract the process pdfs from the ws.'''

        pdfs = {}
        for process in self._processes:
            tag = 'Sig' if process in self._DC.signals else 'Bkg'

            mname  = 'shape{0}_{1}_{2}_morph'.format(tag,self._bin,process)
            sname  = 'shape{0}_{2}_{1}Pdf'.format(tag,self._bin,process)
            morph  = self._ws.pdf('shape{0}_{1}_{2}_morph'.format(tag,self._bin,process))
            static = self._ws.pdf('shape{0}_{2}_{1}Pdf'.format(tag,self._bin,process))

            if morph.__nonzero__():
                shape = morph
            elif static.__nonzero__():
                shape = static
            else:
                self._ws.allPdfs().Print('V')
                print morph.__nonzero__(),morph, mname
                print static.__nonzero__(),static, sname
                raise ValueError('Can\'t find the nether the morph nor the shape!!! '+process)

            pdfs[process] = shape
        if self._log.isEnabledFor(logging.DEBUG):
            self._log.debug('List of PDF extracted from the ws')
            for p,pdf in pdfs.iteritems():
                self._log.debug('%-10s %s',p,pdf)


            
        return pdfs

    #---
    def _getnormalisations( self, pdf ):
        '''Retrieve the normalisations from a pdf'''
        pdf_obs  = pdf.getObservables(self._data)
        roonorms = getnorms(pdf, pdf_obs)

        # debuginfo
#         if self._log.isEnabledFor(logging.DEBUG):
#             self._log.debug('List of normalisation coefficients from %s', pdf.GetName())
#             for t,v in roonorms.iteritems():
#                 self._log.debug('%-30s %f',t,v)

        norms = {}
        notfound = []
        for process in self._processes:
            # search for a normalisation with the right name
            n = roonorms.get( 'n_exp_bin%s_proc_%s' % (self._bin, process) )
            if n is None: n = roonorms.get( 'n_exp_final_bin%s_proc_%s' % (self._bin, process) )

            # fill it up only if the process exists in the model
            if n is None: 
                notfound.append(process)
                continue

            norms[process] = n

        if len(notfound):
            self._log.debug('The normalisation of the following processes were not found: %s', ', '.join(notfound))
            if not len(norms):
                # if no normalisation were matched, something is wrong
                raise RuntimeError('No normalisations were matched: %s' % ( ', '.join(roonorms) ) )
        return norms

    #---
    def _makeHisto(self, name, title):
        sentry = TH1AddDirSentry()
        h = self._template.Clone(name)
        h.SetTitle(title)

        return h

    #---
    def _array2TH1(self, name, array, title=None):
        if len(array) != self._template.GetNbinsX():
            raise ValueError('Mismatching bin array length and histogram bins: %d %d' % (len(array), self._template.GetNbinsX()) )

        if title==None: title = name
        h = self._makeHisto( name, title )
  

        for i,c in enumerate(array):
            h.SetBinContent(i+1,c)
        
        print "histo ",name,"has integral",h.Integral()

        return h

    #---
    def _roo2array(self, pdf, pars=None, norm=None):
        '''Converts a pdf into a numpy array
        The pdf is plotted against the data stored in the builder
        A custom set of parameters and normalisation can be applied'''

        data = self._data

        pdf_obs  = pdf.getObservables(data)
        pdf_pars = pdf.getParameters(data)

        # make 1 double (float32) array
#         bins = np.zeros(data.numEntries(),dtype=np.float32)
        bins = np.zeros(self._nentries,dtype=np.float32)

        if pars:
            pdf_pars.__assign__(ROOT.RooArgSet(pars))

        # take a slice of the data corresponding to the current category
        itdata = data.sliceIterator(self._x,ROOT.RooArgSet(self._cat))
        i = 0
        while itdata.Next():
#         for i in xrange(data.numEntries()):
            pdf_obs.__assign__(data.get())
            bins[i] = pdf.getVal(pdf_obs)
            i += 1
            if i>= self._nentries: break

        # the pdf should have area equal 1
        if norm or norm == 0:
            bins *= norm
        elif norm==None:
            pass

        return bins

    #---
    def _rooPdf2TH1(self, name, pdf, pars=None, norm=None, title=None):
        ''' '''

        contents = self._roo2array(pdf,pars)

        h = self._array2TH1(name, contents, title)

        if norm:
            if isinstance(norm,ROOT.RooAbsReal):
                norm = norm.getVal()
            self._log.debug('pdf %s, h %s, Normalization %f -> %f',pdf.GetName(), h.GetName(),h.Integral(), norm)
            h.Scale(norm/h.Integral())
        elif norm==0:
            # just in case we are normalizing a 0 integral to 0 (0/0 is bad)
            h.Scale(0)
        elif norm==None:
            print 'No norm'
        
        return h

    #---
    def _model2arrays(self,pars,processes=None):
        '''Turns the array into '''

        data  = self._data
        model = self._model
        pdfs  = self._pdfs

        # convert the model to array (this applies the params)
        model_array = self._roo2array(model,pars)

        # then get the list of normalisations
        norms = self._getnormalisations( model )
        
        # normalise the arrary to the sum of the components
        model_array *= sum(norms.itervalues())

        #loop over the processes
        arrays = {}

        for p,s in pdfs.iteritems():
            if processes and p not in processes: continue
            # here is an extra-check for coherency
            if p not in norms:
                # it can happen for signal pdfs for the background-only model
                if p not in self._DC.signals:
                    raise RuntimeError('Normalisation not found for process %s. This is not right' % p)
                continue

            # here I can avoid pars, but it might not make any difference,
            # as the operation to copy the pars is quick. Maybe
            x = self._roo2array(s,pars)
            # normalise the process pdf to the yields
            x *= norms[p]
            arrays[p] = x

        arrays['model'] = model_array
        
        return arrays

    #---
    def _model2TH1(self,pars,processes=None):
        
        arrays = self._model2arrays(pars,processes)
        
        #convert the model array into the histogram
        hists = dict( [ ( p,self._array2TH1('histo_'+p, a, title=p) ) for p,a in arrays.iteritems() ] )

        return hists

    # bin
    def nuisances(self):
        return self._nu2procs.keys()

    #---
    def perform(self):
        hists = {}
        errs = {}
        hists,errs = self._sewmc()
        hists['Data'] = self._sewdata()
        return hists,errs

        
    #---
    def _sewdata(self):
        from math import sqrt
        h = self._makeHisto('histo_Data','Data')

        data = self._data

        # take a slice of the data corresponding to the current category
        itdata = data.sliceIterator(self._x,ROOT.RooArgSet(self._cat))
        i = 0
        while itdata.Next():
#             x = data.get()
#             j = data.getIndex(x)
#             if i < 10:
#                 print i,j,x.getCatIndex('CMS_channel'),x.getRealValue('CMS_th1x')
            h.SetBinContent(i+1,data.weight())
            h.SetBinError(i+1,sqrt(data.weight()))
            i += 1

        
        return h

    #---
    def _chknorms(self, A, norms):
        pdf_obs  = self._model.getObservables(self._data)
        ns = getnorms(self._model,pdf_obs)
        I = J = 0

        print '-'*80
        print '%-10s %-10s %-10s %-10s' % ('Process','frompdf','fromfit','datacard')
        print '-'*80
        fn = {}
        if norms:
            for n in roofiter(norms):
                fn[n.GetName()] = n.getVal()
                J+=n.getVal()

        for p,v in sorted(self._DC.exp[self._bin].iteritems()):
            # associate the normalization to the process
            endswith = re.compile('%s_proc_%s$' % (self._bin,p) )
            matches = [ n for n in ns if endswith.search(n)]
            if not matches: continue
            if len(matches) != 1:
                raise RuntimeError('Can\'t match normalisation to process: %s,%s' % (p,matches))
            n = matches[0]

            print '%-10s %10.3f %s %10.3f' % (p,ns[n],'%10.3f' % fn[n] if fn and (n in fn) else '%10s' % 'x',v)
            I += ns[n]

        print '-'*80

        print 'Integrals:'
        print ' - expected from DC: %10.3f' % sum(self._DC.exp[self._bin].itervalues())
        print ' - from fit results: %10.3f' % J
        print ' - from pdf norms  : %10.3f' % I
        print ' - observed data   : %10.3f' % A

        print '-'*80

    #---
    def _sewmc(self):
        self._ws.loadSnapshot('clean')
        # clean the parameters
        model, pars, norms = self._fit
        
        # deal with the 2 cases. Fit 
        if norms: 
            # now the real thing
            pars = pars.snapshot()

            # normalize to data
#           A = self._data.sum(False)
            A = self._data.sum(ROOT.RooArgSet(self._x),ROOT.RooArgSet(self._cat),False)
        else:
            # here we can use w.set('nuisances') :D
            pars = pars.snapshot()
            
            # set the errors to 1. sigma for the priors
            for arg in roofiter(pars):
                name = arg.GetName()
                # don't add errors to the signal strength
                if name == 'r': continue
                # find the functional form
                ptype = None
                for (n,nf,p,a,e) in self._DC.systs:
                    if n==name:
                        ptype = p
                        break
                
                # add errors
                if   ptype == 'lnN' or ptype == 'lnU' or 'shape' in ptype:
                    # +/- 1 for lnN (and shapes)
                    arg.setError(1.)
                elif ptype == 'gmN':
                    # +/- sqrt(N) for gmN
                    arg.setError(math.sqrt(arg.getVal()))
                else:
                    raise ValueError('Pdf type %s not known',ptype)

            # normalize to the expected from the DC
            A = sum(self._DC.exp[self._bin].itervalues())


        # take ebin centers
        ax      = self._template.GetXaxis()
        nbins   = ax.GetNbins()
        xs      = np.array( [ ax.GetBinCenter(i) for i in xrange(1,nbins+1) ], np.float32)
        wu      = np.array( [ ax.GetBinUpEdge(i)-ax.GetBinCenter(i)  for i in xrange(1,nbins+1) ], np.float32)
        wd      = np.array( [ ax.GetBinCenter(i)-ax.GetBinLowEdge(i) for i in xrange(1,nbins+1) ], np.float32)
        
        # sort the nuisances
        shapes = [n for (n,nf,p,a,e) in self._DC.systs if 'shape' in p]

        # split shape and normalisation nuisances
        nushapes = [ arg.GetName() for arg in roofiter(pars) if arg.GetName() in shapes]
        nunorms  = [ arg.GetName() for arg in roofiter(pars) if not arg.GetName() in shapes ]

        # groups the nuis to float: all norms together, shapes 1 by
        # and filter on the nuisances which are actually affecting this datacard
        # grouping = dict([('norms',nunorms)] + [ (arg,[arg]) for arg in nushapes] )
        grouping = dict([ (arg,[arg]) for arg in (nushapes+nunorms) if arg in self._nu2procs])
#         grouping = {'CMS_norm_WW':['CMS_norm_WW']}

        # print some stats
        self._chknorms(A, norms)

        # now produce the arrays for everything
        nmarrays =  self._model2arrays( pars )

        mega = {}
        
        # now the variations
        print 'Scanning the nuisance space'
        for nu,group in grouping.iteritems():
            self._log.debug(' - %s',nu)
            try:
                nuvars = self._variatemodel(pars,group)
            except RuntimeWarning as re:
                self._log.debug( re )
                continue

            # store the variation by process
            for p,v in nuvars.iteritems():
                if not p in mega: mega[p] = {}
                mega[p][nu] = v

        # loop over processes to calculate the square sum of the nuisances
        print 'Calculating the nuisances envelope'
        for p,nus in mega.iteritems():
            self._log.debug(' - %s',p)
            
            uperrs = np.zeros(nbins, np.float32)
            dwerrs = np.zeros(nbins, np.float32)

            for n,(ups,dws) in nus.iteritems(): 
                uperrs += np.square(ups)
                dwerrs += np.square(dws)

#             if p == 'model':
#                 for n in sorted(nus): 
#                     (ups,dws) = nus[n]
#                     print 'g %40s: sumup %15.6f | sumdw %15.6f'  % (n,sum(ups),sum(dws))


            uperrs = np.sqrt(uperrs)
            dwerrs = np.sqrt(dwerrs)

            nus['all'] = (uperrs,dwerrs)


        # turn them into TGraphs
        print 'Creating the ROOT objects'

        # convert the shapes into histograms
        hists = dict( [
            (p,self._array2TH1('histo_'+p, a, title=p)) for p,a in nmarrays.iteritems()
        ] )
        #hists = { p:self._array2TH1('histo_'+p, a, title=p) for p,a in nmarrays.iteritems() }

        errs = {}

        for p,nus in mega.iteritems():
            self._log.debug(' - %s',p)
            # ensure the sub-dictionary
            if not p in errs: errs[p] = {}

            # take the nominal
            nmarray = nmarrays[p]

            for n,(uperrs,dwerrs) in nus.iteritems():
                errgraph = ROOT.TGraphAsymmErrors(len(xs),xs,nmarray,wd,wu,dwerrs,uperrs)
                nametitle = '%s_errs_%s' % (p,n)
                errgraph.SetNameTitle(nametitle, nametitle)
                
                errs[p][n] = errgraph

        return hists,errs

    #---
    def _dovariations(self,nmarray,uparray,dwarray):

#         nentries = self._data.numEntries()

        upfloat = np.zeros(self._nentries, np.float32)
        dwfloat = np.zeros(self._nentries, np.float32)

        # and calculate the fluctuations in terms of the model
        for i in xrange(self._nentries):
            u =  max(uparray[i],dwarray[i])-nmarray[i]
            d = -min(uparray[i],dwarray[i])+nmarray[i]
            upfloat[i] = u if u > 0 else 0
            dwfloat[i] = d if d > 0 else 0

        return (upfloat,dwfloat)

    #---
    def _errorband(self,nmarray,uparray,dwarray):

#         nentries = self._data.numEntries()

        upfloat = np.zeros(self._nentries, np.float32)
        dwfloat = np.zeros(self._nentries, np.float32)

        # and calculate the fluctuations in terms of the model
        for i in xrange(self._nentries):
            upfloat[i] =  max(uparray[i],dwarray[i],nmarray[i])-nmarray[i]
            dwfloat[i] = -min(uparray[i],dwarray[i],nmarray[i])+nmarray[i]
#             upfloat[i] = u if u > 0 else 0
#             dwfloat[i] = d if d > 0 else 0

        return (upfloat,dwfloat)

    #---
    def _rawerrors(self,nmarray,uparray,dwarray):

#         nentries = self._data.numEntries()

        upfloat = np.zeros(self._nentries, np.float32)
        dwfloat = np.zeros(self._nentries, np.float32)

        # and calculate the fluctuations in terms of the model
        for i in xrange(self._nentries):
            upfloat[i] =  uparray[i]-nmarray[i]
            dwfloat[i] = -dwarray[i]+nmarray[i]

        return (upfloat,dwfloat)


    #---
    def _variatemodel(self,pars,nuistofloat):
        '''variates a subgroup of nuisances by their error and calculate the fluctuation from the nominal value
        
        - pars is the set of variables the model depends on
        - tofloat are the nuisances to shift
        - processes is the list of processes for which to calculate the variations
        '''
        ups = pars.snapshot()
        dws = pars.snapshot()

        procs2save = set()
        for nu in nuistofloat:
            # prepare the up & downs parameter sets
            up = ups.find(nu) 
            up.setVal(up.getVal()+up.getError())
            dw = dws.find(nu) 
            dw.setVal(dw.getVal()-dw.getError())
        
            # add the processes affected by this nuisance
            try:
                procs2save.update( self._nu2procs[nu] )
            except KeyError:
                self._log.debug('XXXXXXXXXXXX  No processes for %s',nu)

        self._log.debug('Preparing variations for nuisance %s on processes %s' % (','.join(nuistofloat), ','.join(procs2save) ) )

        if len(procs2save) == 0:
            raise RuntimeWarning('No processes found to variate in %s for nuisances %s' % (self._bin, ', '.join(nuistofloat)))

        # model+pars -> 
        nmarrays =  self._model2arrays( pars, procs2save )
        uparrays =  self._model2arrays( ups,  procs2save )
        dwarrays =  self._model2arrays( dws,  procs2save )

        # transform the fluctuations in differences
        # filter those which do not differ from the nominal
        vararrays = []
        for p in nmarrays.iterkeys():
            if p not in uparrays: raise KeyError('Process %s not found among the up-variation', p)
            if p not in dwarrays: raise KeyError('Process %s not found among the dw-variation', p)

            if (nmarrays[p] == uparrays[p]).all() and (nmarrays[p] == dwarrays[p]).all(): 
                self._log.warn('Pdf %s: No changes in bin %s when %s were varied. Is it OK?',p, self._bin, ', '.join(nuistofloat))
                continue
#             vararrays.append( ( p, self._dovariations(nmarrays[p],uparrays[p],dwarrays[p])) )
            vararrays.append( ( p, self._computeerrors(nmarrays[p],uparrays[p],dwarrays[p])) )

        variations = dict(vararrays)
            

        return variations


def THSum( shapes, labels, name=None, title=None):

    labels = [ p for p in shapes.iterkeys() if p in labels ]
    if not labels: return None

    sentry = TH1AddDirSentry()
    h = shapes[labels[0]].Clone()

    for l in labels[1:]:
        h.Add(shapes[l])

    if name: h.SetName(name)
    if title: h.SetName(title)

    return h


def fitAndPlot( dcpath, opts ):
    '''
1. read the datacard
2. convert to ws
3. run combine
4. open get the mlfit rootfile

1-4 don't need to know the content of the card, only to check that there are shapes inside

'''

    remass = re.compile('mH(\d*)')
    m = remass.search(dcpath)
    if not m: raise ValueError('Mass not found! Name your datacards properly!')

    print 'Mass',m.group(1)
    opt.mass = int(m.group(1))

    shapepath = os.path.join(os.getenv('CMSSW_BASE'),'src/HWWAnalysis/ShapeAnalysis')
    print 'Shape directory is',shapepath
    ROOT.gInterpreter.ExecuteMacro(shapepath+'/macros/LatinoStyle2.C')

    # 1. load the datacard
    dcfile = open(dcpath,'r')
    
    class DCOptions: pass
    options = DCOptions()
    options.stat = False
    options.bin = True
    options.noJMax = False
    options.nuisancesToExclude = []
    options.nuisancesToRescale = []

    options.fileName = dcpath
    options.out = None
    options.cexpr = False
    options.fixpars = False
    options.libs = []
    options.verbose = 0
    options.poisson = 0
    options.mass = opt.mass

    DC = parseCard(dcfile, options)

    if not DC.hasShapes:
        print 'This datacard has no shapes!'
        print dcpath
        sys.exit(-1)

#     if len(DC.bins) != 1:
#         raise ValueError('Only 1 bin datacards supported at the moment: '+', '.join(DC.bins))
        

    # 2. convert to ws
    wspath = os.path.splitext(dcpath)[0]+'_workspace.root'
    logging.debug('Working with workspace %s',wspath)

    mkws = (not os.path.exists(wspath) or
            os.path.getmtime(wspath) < os.path.getmtime(dcpath) or
            opts.clean)
    if mkws:
        # workspace + parameters = shapes
        print 'Making the workspace...',
        sys.stdout.flush()
        cmd = 'text2workspace.py %s -o %s' % (dcpath,wspath)
        if opts.model != None:
           cmd = 'text2workspace.py %s -o %s -P %s' % (dcpath,wspath, opts.model)
        print cmd   
        os.system( cmd )
        print 'done.'

    ROOT.gSystem.Load('libHiggsAnalysisCombinedLimit')
    wsfile = ROOT.TFile.Open(wspath)
    if not wsfile.__nonzero__():
        raise IOError('Could not open '+wspath)
    
    w = wsfile.Get('w')
    w.saveSnapshot('clean',w.allVars())

    # run combine if requested
    if opt.usefit:
        mlfpath = opt.usefit
        print '-'*80
        print 'Using results in',mlfpath
        print '-'*80
        if not os.path.exists(mlfpath):
            raise IOError('Fit result file %s not found.' % mlfpath )
    else:
        # 3.0 prepare the temp direcotry
        import tempfile
        mlfdir = opt.tmpdir if opt.tmpdir else tempfile.mkdtemp(prefix='mlfit_')
        hwwtools.ensuredir(mlfdir)
        # 3.1 go to the tmp dir 
        here = os.getcwd()
        os.chdir(mlfdir)
        # 3.2
        mlcmd = ' '
        if opts.injectionSignal == False :
          mlcmd = 'combine --saveWorkspace -M '+ opts.fitmode +' '+os.path.join(here,wspath)
        else :
          mlcmd = 'combine --saveWorkspace --expectSignal=1 -t -1 -M '+opts.fitmode+' '+os.path.join(here,wspath)
        if opts.fitmode == "MultiDimFit":
          mlcmd += ' --algo=singles'
        logging.debug(mlcmd)
        print 'do: ',mlcmd
        print 'Fitting the workspace...',
        sys.stdout.flush()
        if opts.fit: os.system(mlcmd)
        os.chdir(here)
        print 'done.'

        # 3.3 set the max-like fit results path
        mlfpath = os.path.join(mlfdir,'mlfit.root')

    # 4. open the output and get the normalizations
    model_s = w.pdf('model_s')
    model_b = w.pdf('model_b')
    mlffile = ROOT.TFile.Open(mlfpath)
    if not mlffile.__nonzero__():
      raise IOError('Could not open '+mlfpath)

    res_s=None
    res_b=None
    sig_fit=None
    bkg_fit=None
    modes=None
    if opts.fitmode == "MaxLikelyhoodFit":
      res_s   = mlffile.Get('fit_s')
      res_b   = mlffile.Get('fit_b')
      sig_fit = ( model_s, res_s.floatParsFinal(), mlffile.Get('norm_fit_s'), )
      bkg_fit = ( model_b, res_b.floatParsFinal(), mlffile.Get('norm_fit_b'), )

      print 'List of bins found',', '.join(DC.bins)
      bin = DC.bins[0]

      modes = odict.OrderedDict([
        ('init',(model_s,res_s.floatParsInit(),None)), #(None, None, model_s)
        ('bkg' ,bkg_fit),
        ('sig' ,sig_fit),
      ])
    else:
      res_s   = mlffile.Get('fit_s')
      sig_fit = ( model_s, res_s.floatParsFinal(), mlffile.Get('norm_fit_s'), )
      modes = odict.OrderedDict([
        ('sig', sig_fit )
      ])  
      #sig_fit = 
    # experimental
    MB = ShapeBuilder(DC, options)

    allshapes = {}
    nuisancemap = {}
    for mode,fit in modes.iteritems():
        print 'Analysing model:',mode
        logging.debug('Plotting %s', fit)

        allshapes[mode] = {}

        for bin in DC.bins:
            print ' - Bin:',bin
            coroner = Coroner(bin, DC, MB, w, fit)
            coroner.errmode = opt.errmode
            shapes,errs = coroner.perform()
            nuisancemap[bin] = coroner.nuisances()

            if opts.output:
                printshapes(shapes, errs, mode, opts, bin, DC.signals, DC.processes)

            allshapes[mode][bin] = (shapes,errs)
    
    if opts.dump:
        logging.debug('Dumping histograms to %s',opts.dump)
        dumpdir = os.path.dirname(opt.dump)
        # open rootfile
        if dumpdir: hwwtools.ensuredir(dumpdir)
        dump = ROOT.TFile.Open(opts.dump,'recreate')
        here = ROOT.gDirectory.func()
        dump.cd()

        idir = dump.mkdir('info')
        idir.cd()
        # save the list of nuisances
        nuisances = ROOT.TObjArray() #ROOT.std.vector('string')()
        for (n,nf,pf,a,e) in DC.systs: nuisances.Add( ROOT.TObjString(n) )
        nuisances.Write('nuisances', ROOT.TObject.kSingleKey)
        # save the list of processes
        processes = ROOT.TObjArray() #ROOT.std.vector('string')()
        for p in DC.processes: processes.Add( ROOT.TObjString(p) )
        processes.Write('processes', ROOT.TObject.kSingleKey)
        # save the list of signals
        signals = ROOT.TObjArray() #ROOT.std.vector('string')()
        for s in DC.signals: signals.Add( ROOT.TObjString(s) )
        signals.Write('signals', ROOT.TObject.kSingleKey)

        # save the list of nuisances per bin
        nuisbybin = ROOT.TMap()
        for bin,nuis in nuisancemap.iteritems():
            tnuis = ROOT.TObjArray()
            for n in nuis: tnuis.Add( ROOT.TObjString(n) )
            nuisbybin.Add(ROOT.TObjString(bin),tnuis)
        nuisbybin.Write('map_binnuisances', ROOT.TObject.kSingleKey)

        for mode,allbins in allshapes.iteritems():
            # make the main directory
            mdir = dump.mkdir(mode)
            mdir.cd()
            
            # info directory
            idir = mdir.mkdir('info')
            idir.cd()

            # save the fit parameters
            model,pars,norms = modes[mode] 
            pars.Write('parameters')

            # save the list of signals

            # save the bin plots
            for bin,(shapes,errs) in allbins.iteritems():
                # bin directory
                bdir = mdir.mkdir(bin) 
                bdir.cd()
                for s in shapes.itervalues():
#                     print s
                    s.Write()

                for p,nugs in errs.iteritems():
                    dp = bdir.mkdir(p)
                    dp.cd()
                    for g in nugs.itervalues(): g.Write()
                    bdir.cd()

                
                try:
                    modelall = errs['model']['all'].Clone('model_errs')
                    modelall.SetTitle('model_errs')
                    modelall.Write()
                except:
                    logging.warn('Error graph model:err not found')

                mdir.cd()



        dump.Write()
        dump.Close()
        here.cd()



#---
def printshapes( shapes, errs, mode, opts, bin, signals, processes ):

    # deep copy?
    shapes2plot = copy.deepcopy(shapes)

    import hwwplot
    plot = hwwplot.HWWPlot()
    plot.setautosort()

    plot.setdata(shapes2plot['Data'])


    for p in processes:
        if p not in shapes: continue
        if p in signals:
            print "p = ",p
            plot.addsig(p,shapes2plot[p], label=plot.properties[p]['label']+'^{ %.0f}'%opt.mass)
        else:
            plot.addbkg(p,shapes2plot[p])

    ## 1 = signal over background , 0 = signal on its own
    plot.set_addSignalOnBackground(1);

    ## 1 = merge signal in 1 bin, 0 = let different signals as it is
#     plot.set_mergeSignal(1);

    plot.setMass(opt.mass); 
#     plot.setLabel('m_{T}^{ll-E_{T}^{miss}} [GeV]')
#     plot.addLabel('#sqrt{s} = 8TeV')

    plot.prepare()

    plot.mergeSamples() #---- merge trees with the same name! ---- to be called after "prepare"

    cName = 'c_fitshapes_'+mode
    ratio = opts.ratio
    errband = False

    if ratio: w = 500; h = 700
    else:     w = 500; h = 500

#     if opts.stretch:
#         plot.stretch(opts.stretch)
#         w = int(w*opts.stretch)

    c = ROOT.TCanvas(cName,cName, w+4, h+28) 

#     plot.setMass(opts.mass)
    plot.setLumi(opts.lumi if opt.lumi else 0)
    if opt.xlabel: plot.setLabel(opts.xlabel)
#     plot.setRatioRange(0.,2.)

    def _print(c, p, e, l):
        plot.seterror(e)

        if not e:
            e = 0x0

        plot.set_ErrorBand(e)

        c.Clear()
    
        p.Draw(c,1,ratio,errband)

        c.Modified()
        c.Update()
    
        hwwtools.ensuredir(opts.output)

        outbasename = os.path.join(opts.output,'fitshapes_mH%d_%s_%s' % (opt.mass,bin,mode))
        if l: 
            outbasename += '_' + l

        c.Print(outbasename+'.pdf')
        c.Print(outbasename+'.png')


    if errs:
        ename = 'all'
        _print(c,plot,errs['model'][ename],ename) 

    del c


#---
def addOptions( parser ):
    
    parser.add_option('-o' , '--output'    , dest='output'         , help='Output directory (%default)'     , default=None)
    parser.add_option('-x' , '--xlabel'    , dest='xlabel'         , help='X-axis label'                    , default='')
    parser.add_option('-r' , '--ratio'     , dest='ratio'          , help='Plot the data/mc ration'         , default=True       , action='store_false')
    parser.add_option('--errormode'        , dest='errmode'        , help='Algo to calculate the errors'    , default='errorband')
    parser.add_option('--nofit'            , dest='fit'            , help='Don\'t fit'                      , default=True       , action='store_false')
    parser.add_option('--clean'            , dest='clean'          , help='Clean the ws (regenerate)'       , default=False      , action='store_true')
    parser.add_option('--dump'             , dest='dump'           , help='Dump the histograms to file'     , default=None)
    parser.add_option('--tmpdir'           , dest='tmpdir'         , help='Temporary directory'             , default=None)
    parser.add_option('--usefit'           , dest='usefit'         , help='Do not fit, use an external file', default=None)
    parser.add_option('--stretch'          , dest='stretch'        , help='Stretch'                         , default=None, type='float')
    parser.add_option('--injectionSignal'  , dest='injectionSignal', help='Signal injection'                , default=False     , action='store_true')
    parser.add_option('--model'  , dest='model', help='signal model'                , default=None     , action='store')
    parser.add_option('--fitmode'  , dest='fitmode', help='fit mode, MaxLikelihoodFit or MultiDimFit', default='MaxLikelihoodFit', action='store')

    hwwtools.addOptions(parser)
    hwwtools.loadOptDefaults(parser)

#---
def parseOptions(parser):
    (opt, args) = parser.parse_args()
    sys.argv.append('-b')

    if not opt.debug:
        pass
    elif opt.debug >= 2:
        print 'Logging level set to DEBUG (%d)' % opt.debug
        logging.basicConfig(level=logging.DEBUG)
    elif opt.debug == 1:
        print 'Logging level set to INFO (%d)' % opt.debug
        logging.basicConfig(level=logging.INFO)

    return (opt,args)


if __name__ == '__main__':
    import optparse
    ## option parser
    usage = 'usage: %prog [options] datacard'
    parser = optparse.OptionParser(usage)

    addOptions(parser)
    (opt, args) = parseOptions(parser)

    import bdb
    try:
        dcpath = args[0]
    except IndexError:
        parser.print_usage()
        sys.exit(0)
    
    try:
        fitAndPlot(dcpath, opt)
    except SystemExit:
        pass
    except bdb.BdbQuit:
        pass
    except:
        import traceback
        exc_type, exc_value, exc_traceback = sys.exc_info()

        print '-'*80
        print '--> Exception'
        print
        print "*** print_exc:"
        traceback.print_exc()
        print "*** format_exc, first and last line:"
        formatted_lines = traceback.format_exc().splitlines()
        print formatted_lines[0]
        print formatted_lines[-1]
        print "*** format_exception:"
        print repr(traceback.format_exception(exc_type, exc_value,
                                              exc_traceback))
