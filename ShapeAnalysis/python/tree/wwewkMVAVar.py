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
#   \ \        / \ \        /                       |          \  | \ \     /  \
#    \ \  \   /   \ \  \   /        _ \ \ \  \   /  |  /      |\/ |  \ \   /  _ \
#     \ \  \ /     \ \  \ /         __/  \ \  \ /     <       |   |   \ \ /  ___ \
#      \_/\_/       \_/\_/        \___|   \_/\_/   _|\_\     _|  _|    \_/ _/    _\
#
#
#

class WWewkMVAVarFiller(TreeCloner):

    def __init__(self):
        pass


    def createWWewkMVA(self):
        self.getWWewkMVA = ROOT.TMVA.Reader();

        self.getWWewkMVA.AddVariable("jetpt1",                  (self.var1))
        self.getWWewkMVA.AddVariable("jetpt2",                  (self.var2))
        self.getWWewkMVA.AddVariable("detajj",                  (self.var3))
        self.getWWewkMVA.AddVariable("log(mjj)",                (self.var4))
        #self.getWWewkMVA.AddVariable("pt1",                     (self.var5))
        #self.getWWewkMVA.AddVariable("pt2",                     (self.var6))
        #self.getWWewkMVA.AddVariable("ptll",                    (self.var7))
        self.getWWewkMVA.AddVariable("abs(eta1-(jeteta1+jeteta2)/2)/detajj",            (self.var8))
        self.getWWewkMVA.AddVariable("abs(eta2-(jeteta1+jeteta2)/2)/detajj",            (self.var9))
        #self.getWWewkMVA.AddVariable("abs(yll-(jeteta1+jeteta2)/2)/detajj",             (self.var10))
        #self.getWWewkMVA.AddVariable("dphilljetjet",            (self.var11))

        self.getWWewkMVA.AddVariable("sqrt((Ml1j1-100)*(Ml1j1-100)+(Ml1j2-100)*(Ml1j2-100))",             (self.var12))
        self.getWWewkMVA.AddVariable("sqrt((Ml2j1-100)*(Ml2j1-100)+(Ml2j2-100)*(Ml2j2-100))",             (self.var13))


        baseCMSSW = os.getenv('CMSSW_BASE')
        self.getWWewkMVA.BookMVA("BDTG",baseCMSSW+"/src/WWewkMvaInCMSSW/GetWWewkMVA/data/TMVA_WWewk_BDTG.weights.xml")
        #self.getWWewkMVA.BookMVA("MLP",baseCMSSW+"/src/WWewkMvaInCMSSW/GetWWewkMVA/data/TMVA_WWewk_MLP.weights.xml")


    def help(self):
        return '''Add wwewk mva variables'''


    def addOptions(self,parser):
        description = self.help()
        group = optparse.OptionGroup(parser,self.label, description)
        #group.add_option('-k', '--kindMCDATA',   dest='kindMCDATA', help='kind of sample: MC2011, MC2012, DATA2011, DATA2012', default='MC2012')
        parser.add_option_group(group)
        return group


    def checkOptions(self,opts):
        #if not (hasattr(opts,'kindMCDATA')) :
            #raise RuntimeError('Missing parameter')
        #self.kindMCDATA     = opts.kindMCDATA
        print "it's all ok ..."


    def process(self,**kwargs):

        self.getWWewkMVA = None
        self.var1  = numpy.ones(1, dtype=numpy.float32)
        self.var2  = numpy.ones(1, dtype=numpy.float32)
        self.var3  = numpy.ones(1, dtype=numpy.float32)
        self.var4  = numpy.ones(1, dtype=numpy.float32)
        self.var5  = numpy.ones(1, dtype=numpy.float32)
        self.var6  = numpy.ones(1, dtype=numpy.float32)
        self.var7  = numpy.ones(1, dtype=numpy.float32)
        self.var8  = numpy.ones(1, dtype=numpy.float32)
        self.var9  = numpy.ones(1, dtype=numpy.float32)
        self.var10 = numpy.ones(1, dtype=numpy.float32)
        self.var11 = numpy.ones(1, dtype=numpy.float32)
        self.var12 = numpy.ones(1, dtype=numpy.float32)
        self.var13 = numpy.ones(1, dtype=numpy.float32)

        tree  = kwargs['tree']
        input = kwargs['input']
        output = kwargs['output']

        self.connect(tree,input)

        newbranches = ['WWewkMVABDTG']
        self.clone(output,newbranches)

        WWewkMVABDTG = numpy.ones(1, dtype=numpy.float32)

        self.otree.Branch('WWewkMVABDTG',  WWewkMVABDTG,  'WWewkMVABDTG/F')

        self.createWWewkMVA()

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

            self.var1[0]  =  itree.jetpt1
            self.var2[0]  =  itree.jetpt2
            self.var3[0]  =  itree.detajj
            if (itree.mjj>100) :   self.var4[0] =  math.log(itree.mjj)
            else :                 self.var4[0] =  math.log(100)
            self.var5[0]  =  itree.pt1
            self.var6[0]  =  itree.pt2
            self.var7[0]  =  itree.ptll
            if (itree.detajj > 0.01) :
                self.var8[0]  =  fabs(itree.eta1-(itree.jeteta1+itree.jeteta2)/2)/itree.detajj
                self.var9[0]  =  fabs(itree.eta2-(itree.jeteta1+itree.jeteta2)/2)/itree.detajj
                self.var10[0] =  fabs(itree.yll-(itree.jeteta1+itree.jeteta2)/2)/itree.detajj
            else :
                self.var8[0]  =  0.
                self.var9[0]  =  0.
                self.var10[0] =  0.
            self.var11[0] =  itree.dphilljetjet
            self.var12[0] =  sqrt((itree.Ml1j1-100)*(itree.Ml1j1-100)+(itree.Ml1j2-100)*(itree.Ml1j2-100))
            self.var13[0] =  sqrt((itree.Ml2j1-100)*(itree.Ml2j1-100)+(itree.Ml2j2-100)*(itree.Ml2j2-100))


            if  itree.njet>=2 :
                WWewkMVABDTG[0] = self.getWWewkMVA.EvaluateMVA("BDTG")
                #WWewkMVABDTG[0] = self.getWWewkMVA.EvaluateMVA("MLP")
            else :
                WWewkMVABDTG[0] = -999.

            otree.Fill()
        self.disconnect()
        print '- Eventloop completed'



