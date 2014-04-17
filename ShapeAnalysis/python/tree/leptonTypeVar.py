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




#    |                   |                     __ __|
#    |       _ \  __ \   __|   _ \   __ \         |  |   |  __ \    _ \
#    |       __/  |   |  |    (   |  |   |        |  |   |  |   |   __/
#   _____| \___|  .__/  \__| \___/  _|  _|       _| \__, |  .__/  \___|
#                _|                                 ____/  _|


#
# Examples:
#
#  cd /HWWAnalysis/ShapeAnalysis
# source test/env.sh
#
# gardener.py  LeptonTypeVar /data2/amassiro/VBF/Data/All21Aug2012_temp_1/latino_085_WgammaToLNuG.root  /data2/amassiro/VBF/Data/All21Aug2012_temp_2/latino_085_WgammaToLNuG_TESTIFITWORKS.root 
#



class LeptonTypeVarFiller(TreeCloner):

    def __init__(self):
        pass

    def help(self):
        return '''Add new unboosted variables'''


    def addOptions(self,parser):
        #description = self.help()
        #group = optparse.OptionGroup(parser,self.label, description)
        #parser.add_option_group(group)
        #return group
        pass


    def checkOptions(self,opts):
        #self._mc     = opts.mc
        #self._dt     = opts.dt
        pass

    #                        e/mu                <- iso ->   e    mu
    def IsLeptonTight(self, lepid, pt, eta, phi, iso, mva, scEta, d0) :
        passed = 0
        # electron
        if abs(lepid) == 11 :
            passed = 1
            ele_eta = fabs(scEta)

            mvaCut = 999.
            if (pt < 20) :
                if (ele_eta <= 0.8) :
                    mvaCut = 0.00
                elif (ele_eta > 0.8 and ele_eta <= 1.479) :
                    mvaCut = 0.10
                else :
                    mvaCut = 0.62

            else :
                if (ele_eta <= 0.8) :
                    mvaCut = 0.94
                elif (ele_eta > 0.8 and ele_eta <= 1.479 ) :
                    mvaCut = 0.85
                else :
                    mvaCut = 0.92

            if (mva > mvaCut) :
                relIso = iso / pt
                if (relIso < 0.15) :
                    passed = 1


        # muon
        if abs(lepid) == 13 :
            isoCut = -1;
            if (pt <= 20) : 
                if (fabs(eta) < 1.479) :
                    isoCut = 0.86 
                else :
                    isoCut = 0.82
            else :
                if (fabs(eta) < 1.479) :
                    isoCut = 0.82 
                else :
                    isoCut = 0.86

            if ( mva > isoCut ) :
                if (pt < 20) :
                    MaxMuIP = 0.01
                else : 
                    MaxMuIP = 0.02
                if fabs(d0) < MaxMuIP :
                    passed = 1

        return passed




    def process(self,**kwargs):

        tree  = kwargs['tree']
        input = kwargs['input']
        output = kwargs['output']

        self.connect(tree,input)
        newbranches = ['type1', 'type2', 'type3', 'type4']
        self.clone(output,newbranches)

        type1 = numpy.ones(1, dtype=numpy.float32)
        type2 = numpy.ones(1, dtype=numpy.float32)
        type3 = numpy.ones(1, dtype=numpy.float32)
        type4 = numpy.ones(1, dtype=numpy.float32)

        self.otree.Branch('type1'      ,  type1      ,  'type1/F'  )
        self.otree.Branch('type2'      ,  type2      ,  'type2/F'  )
        self.otree.Branch('type3'      ,  type3      ,  'type3/F'  )
        self.otree.Branch('type4'      ,  type4      ,  'type4/F'  )

        nentries = self.itree.GetEntries()
        print 'Total number of entries: ',nentries 

        if self._mc :
            print 'it is MC'
        else :
            print 'it is DATA'

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

            # initialize to "fail"
            type1 = 0
            type2 = 0
            type3 = 0
            type4 = 0

            ##                        e/mu                <- iso ->   e    mu
            #def IsLeptonTight(self, lepid, pt, eta, phi, iso, mva, scEta, d0) :

            type1 = self.IsLeptonTight (itree.id1, itree.pt1, itree.eta1, itree.phi1,    iso1       , itree.mvaIso1,  sceta1,     d0)
            type2 = self.IsLeptonTight (itree.id2, itree.pt2, itree.eta2, itree.phi2,    iso2       , itree.mvaIso2,  sceta2,     d0)
            type3 = self.IsLeptonTight (itree.id3, itree.pt3, itree.eta3, itree.phi3,    iso3       , itree.mvaIso3,  sceta3,     d0)
            type4 = self.IsLeptonTight (itree.id4, itree.pt4, itree.eta4, itree.phi4,    iso4       , itree.mvaIso4,  sceta4,     d0)

            otree.Fill()

        self.disconnect()
        print '- Eventloop completed'






