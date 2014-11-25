from tree.gardening import TreeCloner


import optparse
import os
import sys
import ROOT
import numpy
import re
import warnings
import os.path
from math import *
import math


#
#
#    |   |                _)      |  |    |           \  | \ \     /  \        \ \     /  \      _ \
#    |   |     \ \  \   /  |   _` |  __|  __ \       |\/ |  \ \   /  _ \        \ \   /  _ \    |   |
#    ___ |      \ \  \ /   |  (   |  |    | | |      |   |   \ \ /  ___ \        \ \ /  ___ \   __ <
#   _|  _|       \_/\_/   _| \__,_| \__| _| |_|     _|  _|    \_/ _/    _\        \_/ _/    _\ _| \_\
#
#

class HwidthMVAVarFiller(TreeCloner):

    def __init__(self):
        pass


    def createHwidthMVA(self):
        self.getHwidthMVA = ROOT.TMVA.Reader();


        self.getHwidthMVA.AddVariable("mll",         (self.var1))
        self.getHwidthMVA.AddVariable("mth",         (self.var2))
        self.getHwidthMVA.AddVariable("ptll",        (self.var3))
        self.getHwidthMVA.AddVariable("pt1",         (self.var4))
        self.getHwidthMVA.AddVariable("pt2",         (self.var5))
        self.getHwidthMVA.AddVariable("dphill",      (self.var6))
        self.getHwidthMVA.AddVariable("pfmet",       (self.var7))

        baseCMSSW = os.getenv('CMSSW_BASE')

        if self.kindOfMVA == 0 :
          self.getHwidthMVA.BookMVA("BDTG",baseCMSSW+"/src/HwidthMvaInCMSSW/GetHwidthMVA/data/TMVA_Hwidth_ggH_BDTG.weights.xml")
        else :
          self.getHwidthMVA.BookMVA("BDTG",baseCMSSW+"/src/HwidthMvaInCMSSW/GetHwidthMVA/data/TMVA_Hwidth_bkg_BDTG.weights.xml")


    def help(self):
        return '''Add wwewk mva variables'''


    def addOptions(self,parser):
        description = self.help()
        group = optparse.OptionGroup(parser,self.label, description)
        group.add_option('-k', '--kindOfMVA',   dest='kindOfMVA', type='int', help='kind of sample: 0 = off-shell vs on-shell, 1 = off-shell vs background', default=0)
        parser.add_option_group(group)
        return group


    def checkOptions(self,opts):
        self.kindOfMVA     = opts.kindOfMVA
        print "it's all ok ..."


    def process(self,**kwargs):

        self.getHwidthMVA = None
        self.var1  = numpy.ones(1, dtype=numpy.float32)
        self.var2  = numpy.ones(1, dtype=numpy.float32)
        self.var3  = numpy.ones(1, dtype=numpy.float32)
        self.var4  = numpy.ones(1, dtype=numpy.float32)
        self.var5  = numpy.ones(1, dtype=numpy.float32)
        self.var6  = numpy.ones(1, dtype=numpy.float32)
        self.var7  = numpy.ones(1, dtype=numpy.float32)

        tree  = kwargs['tree']
        input = kwargs['input']
        output = kwargs['output']

        self.connect(tree,input)

        print "self.kindOfMVA = ", self.kindOfMVA

        if self.kindOfMVA == 0 :
          newbranches = ['HwidthMVAggH']
        else :
          newbranches = ['HwidthMVAbkg']

        self.clone(output,newbranches)

        HwidthMVA = numpy.ones(1, dtype=numpy.float32)

        if self.kindOfMVA == 0 :
          self.otree.Branch('HwidthMVAggH',  HwidthMVA,  'HwidthMVAggH/F')
        else :
          self.otree.Branch('HwidthMVAbkg',  HwidthMVA,  'HwidthMVAbkg/F')

        self.createHwidthMVA()

        nentries = self.itree.GetEntries()
        print 'Total number of entries: ',nentries 

        # avoid dots to go faster
        itree     = self.itree
        otree     = self.otree


        print '- Starting eventloop'
        step = 5000
        for i in xrange(nentries):
            itree.GetEntry(i)

            ## print event count
            if i > 0 and i%step == 0.:
                print i,'events processed.'

            self.var1[0]  =  itree.mll
            self.var2[0]  =  itree.mth
            self.var3[0]  =  itree.ptll
            self.var4[0]  =  itree.pt1
            self.var5[0]  =  itree.pt2
            self.var6[0]  =  itree.dphill
            self.var7[0]  =  itree.pfmet


            HwidthMVA[0] = self.getHwidthMVA.EvaluateMVA("BDTG")

            otree.Fill()
        self.disconnect()
        print '- Eventloop completed'



