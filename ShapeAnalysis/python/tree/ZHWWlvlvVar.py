##############################################
#
# Written and designed by M. Franke 04-04-14
# Northeastern University
#
##############################################


#change path structure!


from tree.gardening import TreeCloner
import numpy
import ROOT
import sys
import optparse
import re
import warnings
import os.path
from array import array;

class ZhwwlvlvVarFiller(TreeCloner):
    def __init__(self):
       pass

    def help(self):
        return '''Add new variables to HiggsZto4l'''

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
        newbranches = ['MllZ', 'DphiZ', 'FlZ','PTZ','MllWW', 'DphiWW', 'FlWW','PTWW','DphiZ1','DphiZ2','M4l']
        self.clone(output,newbranches)
        
        MllZ    = numpy.ones(1, dtype=numpy.float32)
        DphiZ   = numpy.ones(1, dtype=numpy.float32)
        FlZ     = numpy.ones(1, dtype=numpy.float32)
        PTZ     = numpy.ones(1, dtype=numpy.float32)
        MllWW   = numpy.ones(1, dtype=numpy.float32)
        DphiWW  = numpy.ones(1, dtype=numpy.float32)
        FlWW    = numpy.ones(1, dtype=numpy.float32)
        PTWW    = numpy.ones(1, dtype=numpy.float32)
        DphiZ1  = numpy.ones(1, dtype=numpy.float32)
        DphiZ2  = numpy.ones(1, dtype=numpy.float32)
        M4l     = numpy.ones(1, dtype=numpy.float32)
       
        self.otree.Branch('MllZ'  , MllZ  , 'MllZ/F')
        self.otree.Branch('DphiZ' , DphiZ , 'DphiZ/F')
        self.otree.Branch('FlZ'   , FlZ   , 'FlZ/F')
        self.otree.Branch('PTZ'   , PTZ   , 'PTZ/F')
        self.otree.Branch('MllWW' , MllWW , 'MllWW/F')
        self.otree.Branch('DphiWW', DphiWW, 'DphiWW/F')
        self.otree.Branch('FlWW'  , FlWW  , 'FlWW/F')
        self.otree.Branch('PTWW'  , PTWW  , 'PTWW/F')
        self.otree.Branch('DphiZ1', DphiZ1, 'DphiZ1/F')
        self.otree.Branch('DphiZ2', DphiZ2, 'DphiZ2/F')
        self.otree.Branch('M4l'   , M4l   , 'M4l/F')

        nentries = self.itree.GetEntries()
        print 'Total number of entries: ',nentries 

        #what is self.itree? what is self.otree?
        itree     = self.itree
        otree     = self.otree

        # change this part into correct path structure... 
        cmssw_base = os.getenv('CMSSW_BASE')
        try:
            ROOT.gROOT.LoadMacro(cmssw_base+'/src/HWWAnalysis/ShapeAnalysis/python/tree/ZHWWlvlvVar.C+g')
        except RuntimeError:
            ROOT.gROOT.LoadMacro(cmssw_base+'/src/HWWAnalysis/ShapeAnalysis/python/tree/ZHWWlvlvVar.C++g')
        #----------------------------------------------------------------------------------------------------
        print '- Starting eventloop'
        step = 5000
        for i in xrange(nentries):
            itree.GetEntry(i)

            if i > 0 and i%step == 0.:
                print i,'events processed.'

            pt1 = itree.pt1
            pt2 = itree.pt2
            pt3 = itree.pt3
            pt4 = itree.pt4
            eta1 = itree.eta1
            eta2 = itree.eta2
            eta3 = itree.eta3
            eta4 = itree.eta4
            phi1 = itree.phi1
            phi2 = itree.phi2
            phi3 = itree.phi3
            phi4 = itree.phi4
            ch1 = itree.ch1
            ch2 = itree.ch2
            ch3 = itree.ch3
            ch4 = itree.ch4
            fl1 = ROOT.TMath.Abs(itree.pdgid1)
            fl2 = ROOT.TMath.Abs(itree.pdgid2)
            fl3 = ROOT.TMath.Abs(itree.pdgid3)
            fl4 = ROOT.TMath.Abs(itree.pdgid4)

            ZHWW4lvari = ROOT.ZHWW4lvari(pt1, pt2, pt3, pt4, eta1, eta2, eta3, eta4, phi1, phi2, phi3, phi4, ch1, ch2, ch3, ch4, fl1, fl2, fl3, fl4)

            MllZ[0]  = ZHWW4lvari.GetMllZ()
            DphiZ[0] = ZHWW4lvari.GetDphiZ()
            FlZ[0]   = ZHWW4lvari.GetFlZ()
            PTZ[0]   = ZHWW4lvari.GetPTZ()
            MllWW[0] = ZHWW4lvari.GetMllWW()
            DphiWW[0]= ZHWW4lvari.GetDphiWW()
            FlWW[0]  = ZHWW4lvari.GetFlWW()
            PTWW[0]  = ZHWW4lvari.GetPTWW()
            DphiZ1[0]= ZHWW4lvari.GetDphiZ1()
            DphiZ2[0]= ZHWW4lvari.GetDphiZ2()
            M4l[0]   = ZHWW4lvari.GetM4l()
        
            otree.Fill()

        self.disconnect()
        print '- Eventloop completed'