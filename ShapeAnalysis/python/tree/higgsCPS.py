from tree.gardening import TreeCloner
import ctypes
import optparse
import os
import ROOT

from ctypes import c_int,c_double,c_float,cdll,byref

class HiggsCPSWeightAdder(TreeCloner):

    _masses = {
        250  : 250,
        300  : 300,
        350  : 350,
        400  : 400,
        450  : 450,
        500  : 500,
        550  : 550,
        600  : 600,
        650  : 650,
        700  : 700,
        750  : 750,
        800  : 800,
        850  : 850,
        900  : 900,
        950  : 950,
        1000 : 1000,
    }

    #---

    def GetBinWithContent(self, histo, value) :
        bin = -1
        data_nBin     = histo.GetNbinsX()
        data_minValue = histo.GetXaxis().GetXmin()
        data_maxValue = histo.GetXaxis().GetXmax()
        data_dValue   = (data_maxValue - data_minValue) / data_nBin

        bin = int ((value - data_minValue) / data_dValue)
        return bin

    #---

    def GetValueBinWithContent(self, histo, value) :
        bin = -1
        bin = self.GetBinWithContent (histo,value)
        integral = histo.Integral()
        if integral != 0 :
          return ( histo.GetBinContent(bin) / integral)
        else :
          return 1.


    #---
    def __init__(self):
        self._mass = None

    #---
    def help(self):
        return 'Add the lineshape weight to higgs sample'

    #---
    def addOptions(self, parser):
        description=self.help()
        group = optparse.OptionGroup(parser,self.label, description)
        group.add_option('-w', '--weightfile',dest='weightfile',  help='Name of the file with histograms weights (default = %default)', default='mHist.root')
        group.add_option('-b', '--branch',    dest='branch',      help='Name of the higgs CPS weight branch (default = %default)', default='kHcps')
        group.add_option('-p', '--process',   dest='process',     help='Scale factor to add to the weight (default = %default)', default='ggH')
        group.add_option('-m', '--mass',      dest='mass',        type='int', help='Higgs Mass to reweight to', default=0)
        group.add_option('-k', '--kind',      dest='kind',        help='Name of the kind of ration to calculate: (default = %default), e.g. pow2new, old2new, pow2old', default='pow2new')
        parser.add_option_group(group)
        return group

    #---
    def checkOptions(self,opts):
        if not hasattr(opts,'mass'):
            raise RuntimeError('Higgs Mass must be defined!')

        masses = sorted(HiggsCPSWeightAdder._masses.keys())
        if opts.mass not in masses:
            raise ValueError('Supported mass values are %s (found %d)' % (','.join([str(m) for m in masses]), opts.mass) )

        if opts.process not in ['ggH','qqH']:
            raise ValueError('Process mus be ggH or qqH (found %d)' % opts.process)

        self._mass       = opts.mass
        self._weightfile = opts.weightfile
        self._branch     = opts.branch
        self._process    = opts.process
        self._kind       = opts.kind
        print " do: ",self._kind

    #---
    def process(self, **kwargs):

        # get histograms
        oldcpshistname = "mH"+str(self._mass)+"_cpsOld_8TeV_"+self._process
        newcpshistname = "mH"+str(self._mass)+"_cpsNew_8TeV_"+self._process
        powcpshistname = "mH"+str(self._mass)+"_Powheg_8TeV_"+self._process
        print "oldcpshistname =",oldcpshistname
        print "newcpshistname =",newcpshistname
        print "powcpshistname =",powcpshistname

        self.infileWeight = self._openRootFile(self._weightfile)
        self.oldcps = self._getRootObj(self.infileWeight,oldcpshistname)
        self.newcps = self._getRootObj(self.infileWeight,newcpshistname)
        self.powcps = self._getRootObj(self.infileWeight,powcpshistname)


        tree  = kwargs['tree']
        input = kwargs['input']
        output = kwargs['output']

        self.connect(tree,input)
        self.clone(output,[self._branch])


        weight = c_float(5.)
        self.otree.Branch(self._branch, weight, '%s/F' % self._branch )

        nentries = self.itree.GetEntries()
        print 'Total number of entries: ',nentries 

        # avoid dots to go faster
        itree     = self.itree
        otree     = self.otree


        cl = self.__class__

        m  = c_double(0.)

        step = 5000
        for i in xrange(nentries):
            if i > 0 and i%step == 0:
                print i,' events processed.'

            itree.GetEntry(i)
            m.value  = getattr(itree,'MHiggs') 

            pow_value = self.GetValueBinWithContent(self.powcps, m.value)
            old_value = self.GetValueBinWithContent(self.oldcps, m.value)
            new_value = self.GetValueBinWithContent(self.newcps, m.value)

            # calculate weight
            if self._kind == "old2new" :
              if (old_value != 0) :
                weight.value = new_value / old_value
              else :
                weight.value = 1.
            elif self._kind == "pow2new" :
              if (pow_value != 0) :
                weight.value = new_value / pow_value
              else :
                weight.value = 1.
            elif self._kind == "pow2old" :
              if (pow_value != 0) :
                weight.value = old_value / pow_value
              else :
                weight.value = 1.

            otree.Fill()

        self.disconnect()
        print '- Eventloop completed'


