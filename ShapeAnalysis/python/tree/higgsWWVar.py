#
#
#    |   | _)                         \ \        / \ \        /
#    |   |  |   _` |   _` |   __|      \ \  \   /   \ \  \   /
#    ___ |  |  (   |  (   | \__ \       \ \  \ /     \ \  \ /
#   _|  _| _| \__, | \__, | ____/        \_/\_/       \_/\_/
#             |___/  |___/
#
#
#


from tree.gardening import TreeCloner
import numpy
import ROOT
import sys
import optparse
import re
import warnings
import os.path
from array import array;

class higgsWWVarFiller(TreeCloner):
    def __init__(self):
       pass

    def help(self):
        return '''Add new variables for hWW'''

    def addOptions(self,parser):
        pass

    def checkOptions(self,opts):
        pass

    def process(self,**kwargs):
        tree  = kwargs['tree']
        input = kwargs['input']
        output = kwargs['output']

        # does that work so easily and give new variable itree and otree?
        self.connect(tree,input)
        newbranches = ['mWW']
        self.clone(output,newbranches)

        mWW          = numpy.ones(1, dtype=numpy.float32)

        self.otree.Branch('mWW'  , mWW  , 'mWW/F')

        nentries = self.itree.GetEntries()
        print 'Total number of entries: ',nentries 

        #what is self.itree? what is self.otree?
        itree     = self.itree
        otree     = self.otree

        # change this part into correct path structure... 
        cmssw_base = os.getenv('CMSSW_BASE')
        try:
            ROOT.gROOT.LoadMacro(cmssw_base+'/src/HWWAnalysis/ShapeAnalysis/python/tree/higgsWWVar.C+g')
        except RuntimeError:
            ROOT.gROOT.LoadMacro(cmssw_base+'/src/HWWAnalysis/ShapeAnalysis/python/tree/higgsWWVar.C++g')
        #----------------------------------------------------------------------------------------------------
        print '- Starting eventloop'
        step = 5000

        for i in xrange(nentries):

            itree.GetEntry(i)

            if i > 0 and i%step == 0.:
                print i,'events processed.'

            pt1 = itree.leptonGenpt1
            pt2 = itree.leptonGenpt2
            eta1 = itree.leptonGeneta1
            eta2 = itree.leptonGeneta2
            phi1 = itree.leptonGenphi1
            phi2 = itree.leptonGenphi2

            vpt1 = itree.neutrinoGenpt1
            vpt2 = itree.neutrinoGenpt2
            veta1 = itree.neutrinoGeneta1
            veta2 = itree.neutrinoGeneta2
            vphi1 = itree.neutrinoGenphi1
            vphi2 = itree.neutrinoGenphi2

            higgsWW = ROOT.higgsWW(pt1, pt2, eta1, eta2, phi1, phi2,    vpt1, vpt2, veta1, veta2, vphi1, vphi2 )

            mWW[0]   = higgsWW.mWW()

            otree.Fill()

        self.disconnect()
        print '- Eventloop completed'
