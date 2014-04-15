from tree.gardening import TreeCloner


import optparse
import sys
import ROOT
import numpy
import re
import warnings
import os.path
from math import *
from array import array;




#    ____|       |               __ )                |                                          |
#    |     _` |  |  /   _ \      __ \    _` |   __|  |  /   _` |   __|  _ \   |   |  __ \    _` |
#    __|  (   |    <    __/      |   |  (   |  (       <   (   |  |    (   |  |   |  |   |  (   |
#   _|   \__,_| _|\_\ \___|     ____/  \__,_| \___| _|\_\ \__, | _|   \___/  \__,_| _|  _| \__,_|
#                                                         |___/
#

#
# Examples:
#
#  cd /HWWAnalysis/ShapeAnalysis
# source test/env.sh
#
# gardener.py  fakeWVar -m /data2/amassiro/VBF/Data/All21Aug2012_temp_1/latino_085_WgammaToLNuG.root  /data2/amassiro/VBF/Data/All21Aug2012_temp_2/latino_085_WgammaToLNuG_TESTIFITWORKS.root 
#
#    -m if it's a MC sample
#    -d if it's a "data" sample
#


class FakeWVarFiller(TreeCloner):

    def __init__(self):
        pass

    def help(self):
        return '''Add new unboosted variables'''


    def addOptions(self,parser):
        description = self.help()
        group = optparse.OptionGroup(parser,self.label, description)
        group.add_option('-m', '--mc',   dest='mc', help='Check if it is a MC   sample', default=0)
        #group.add_option('-d', '--dt',   dest='dt', help='Check if it is a Data sample', default=1)
        parser.add_option_group(group)
        return group
        #pass


    def checkOptions(self,opts):
        self._mc     = opts.mc
        #self._dt     = opts.dt
        pass


    def process(self,**kwargs):
        tree  = kwargs['tree']
        input = kwargs['input']
        output = kwargs['output']

        self.connect(tree,input)
        newbranches = ['newFakeW', 'newFakeWup']
        self.clone(output,newbranches)

        newFakeW      = numpy.ones(1, dtype=numpy.float32)
        newFakeWup    = numpy.ones(1, dtype=numpy.float32)

        self.otree.Branch('newFakeW'    ,  newFakeW    ,  'newFakeW/F'    )
        self.otree.Branch('newFakeWup'  ,  newFakeWup  ,  'newFakeWup/F'  )

        nentries = self.itree.GetEntries()
        print 'Total number of entries: ',nentries 

        if self._mc :
            print 'it is MC'
        else :
            print 'it is DATA'

        # avoid dots to go faster
        itree     = self.itree
        otree     = self.otree


        cmssw_base = os.getenv('CMSSW_BASE')
        try:
            ROOT.gROOT.LoadMacro(cmssw_base+'/src/HWWAnalysis/ShapeAnalysis/python/tree/fakeW.C+g')
        except RuntimeError:
            ROOT.gROOT.LoadMacro(cmssw_base+'/src/HWWAnalysis/ShapeAnalysis/python/tree/fakeW.C++g')


        print '- Starting eventloop'
        step = 5000
        for i in xrange(nentries):
            itree.GetEntry(i)

            ## print event count
            if i > 0 and i%step == 0.:
                print i,'events processed.'

            #                                  <----          l1          --->  <----          l2          --->   <----          l3          --->   <----          l4          --->
#           FakeProb = ROOT.FakeProbabilities(itree.pt1, itree.eta1, itree.id1, itree.pt2, itree.eta2, itree.id2, itree.pt3, itree.eta3, itree.id3, itree.pt4, itree.eta4, itree.id4 )
            FakeProb = ROOT.FakeProbabilities(itree.pt1, itree.eta1, 0        , itree.pt2, itree.eta2,       0  , itree.pt3, itree.eta3,       0  , itree.pt4, itree.eta4, 0         )

            newFakeW[0] = FakeProb.FakeW4l()

            otree.Fill()

        self.disconnect()
        print '- Eventloop completed'






