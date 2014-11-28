#!/usr/bin/env python

## Example:
## ./scaleAndSmearTree.py -i H140_ll.root -o blu/bla/bli.root -t latino -a leptonEfficiency -d down


## auto:
#ls --color=none nominals/ | grep .root | awk '{print "scaleAndSmearTree.py -i nominals/"$1" -o jetEnergyScale_up/"$1"    -a jetEnergyScale -v up"}'  | /bin/sh
#ls --color=none nominals/ | grep .root | awk '{print "scaleAndSmearTree.py -i nominals/"$1" -o jetEnergyScale_down/"$1"  -a jetEnergyScale -v down"}'| /bin/sh

#ls --color=none nominals/ | grep .root | awk '{print "scaleAndSmearTree.py -i nominals/"$1" -o electronScale_up/"$1"    -a electronScale -v up"}'| /bin/sh
#ls --color=none nominals/ | grep .root | awk '{print "scaleAndSmearTree.py -i nominals/"$1" -o electronScale_down/"$1"  -a electronScale -v down"}'| /bin/sh

#ls --color=none nominals/ | grep .root | awk '{print "scaleAndSmearTree.py -i nominals/"$1" -o muonScale_up/"$1"    -a muonScale -v up"}'| /bin/sh
#ls --color=none nominals/ | grep .root | awk '{print "scaleAndSmearTree.py -i nominals/"$1" -o muonScale_down/"$1"  -a muonScale -v down"}'| /bin/sh

#ls --color=none nominals/ | grep .root | awk '{print "scaleAndSmearTree.py -i nominals/"$1" -o metResolution/"$1"         -a metResolution"}'| /bin/sh
#ls --color=none nominals/ | grep .root | awk '{print "scaleAndSmearTree.py -i nominals/"$1" -o electronResolution/"$1"    -a electronResolution"}'| /bin/sh




## FIXME:
## 1) make an n events argument... it's hardcoded at the moment...
## 2) lepton efficiency are at the moment moved up / down for electrons and muosn simultaneously


import optparse
import os
import ROOT
import numpy
from math import *
import math
# from ROOT import *
 
from math import sqrt, cos

## MET resolution sigma for gaussian smearing (fraction of x- and y- component)
## mean is x- and y- component
metSigma = 0.1 
## muon resolution sigma
muonSigmaMB = 0.01 # pT dependent
muonSigmaME = 0.02 # pT dependent
## electron resolution sigma 
electronSigmaEB = 0.02 # abseta < 1.5
electronSigmaEE = 0.04 # abseta > 1.5
electronSigmaEB2012 = 0.015 # 0.0 < abseta < 1.0
electronSigmaET2012 = 0.025 # 1.0 < abseta < 2.0
electronSigmaEE2012 = 0.035 # abseta > 2.0
## muon scale uncertainty
muonUncertainty = 0.01
muonUncertaintyMB2012 = 0.005 # abseta < 2.2
muonUncertaintyME2012 = 0.015 # abseta > 2.2
## electron scale uncertainty
electronUncertaintyEB = 0.02 # abseta < 1.5
electronUncertaintyEE = 0.04 # abseta > 1.5
electronUncertaintyEB2012 = 0.01 # abseta < 2.0
electronUncertaintyEE2012 = 0.02 # abseta > 2.0

## charge mismeasurement
# in MC mischarge   = 4.45 / 10^4
# in DATA mischarge = 5.55 / 10^4
# absolute difference is 1.1 / 10^4
#

sigmaChargeElectron = (0.000240123, 7.55615e-05, 0.000144796, 2.52092e-05, 0.00120842, 0.00236264)
sigmaChargeMuon     = 0.0002

## JER: jet energy resolution
#sigmaJetResolution = (0.0390, 0.0427, 0.0601, 0.0675, 0.1090 )   # from WZ

sigmaJetResolution     = (0.0342, 0.0363, 0.0504, 0.0534, 0.0898 )   # from WW    nominal
sigmaJetResolutionDown = (0.0000, 0.0047, 0.0286, 0.0293, 0.0477 )   # from WW    down
sigmaJetResolutionUp   = (0.0516, 0.0521, 0.0663, 0.0712, 0.1220 )   # from WW    up


## pu uncertainty
puUp   = "puDATAup.root"
puDown = "puDATAdown.root"
puMC   = "puMC.root"
weightNamePU = "puW"

#verbose = False
mZ = 91.1876
to = ' -> '

def openTFile(path, option=''):
    f =  ROOT.TFile.Open(path,option)
    if not f.__nonzero__() or not f.IsOpen():
        raise NameError('File '+path+' not open')
    return f

def getHist(file, hist):
    h = file.Get(hist)
    if not h.__nonzero__():
        raise NameError('Histogram '+hist+' doesn\'t exist in '+str(file))
    return h

def invariantMass(l1,l2):
    mll = (l1+l2).M()
    return mll

def dileptonPt(l1, l2):
    ptll = (l1+l2).Pt()
    return ptll

def deltaPhi(l1,l2):
    radToDeg = 180./math.pi
##     dphi = abs(l1.DeltaPhi(l2))*radToDeg
    dphi = abs(l1.DeltaPhi(l2))
    return dphi

def transverseMass(p,m):
    mt = sqrt( 2* p.Pt() * m.Pt() * (1 - cos(p.DeltaPhi(m))))
    return mt

def correctMet(met, j1_hold, j2_hold, j1, j2):
    met = met + j1_hold - j1 + j2_hold - j2
    return met

def smearMET(met,sigma):
    metpx = met.Px()
    metpy = met.Py()
    ## throw the dices
    newpx = ROOT.gRandom.Gaus(metpx, sigma*metpx)
    newpy = ROOT.gRandom.Gaus(metpy, sigma*metpy)
    ## and replace the vector
    met.SetPxPyPzE(newpx, newpy,0,0)
    return met

def smearJet(pt,eta,nominal):
    if nominal==0:
      if abs(eta)<=0.5 :
        sigma = sigmaJetResolution[0]
      if abs(eta)>0.5 and abs(eta)<=1.1 :
        sigma = sigmaJetResolution[1]
      if abs(eta)>1.1 and abs(eta)<=1.7 :
        sigma = sigmaJetResolution[2]
      if abs(eta)>1.7 and abs(eta)<=2.3 :
        sigma = sigmaJetResolution[3]
      if abs(eta)>2.3 :
        sigma = sigmaJetResolution[4]

    if nominal==-1:
      if abs(eta)<=0.5 :
        sigma = sigmaJetResolutionDown[0]
      if abs(eta)>0.5 and abs(eta)<=1.1 :
        sigma = sigmaJetResolutionDown[1]
      if abs(eta)>1.1 and abs(eta)<=1.7 :
        sigma = sigmaJetResolutionDown[2]
      if abs(eta)>1.7 and abs(eta)<=2.3 :
        sigma = sigmaJetResolutionDown[3]
      if abs(eta)>2.3 :
        sigma = sigmaJetResolutionDown[4]

    if nominal==1:
      if abs(eta)<=0.5 :
        sigma = sigmaJetResolutionUp[0]
      if abs(eta)>0.5 and abs(eta)<=1.1 :
        sigma = sigmaJetResolutionUp[1]
      if abs(eta)>1.1 and abs(eta)<=1.7 :
        sigma = sigmaJetResolutionUp[2]
      if abs(eta)>1.7 and abs(eta)<=2.3 :
        sigma = sigmaJetResolutionUp[3]
      if abs(eta)>2.3 :
        sigma = sigmaJetResolutionUp[4]

    scale = -1
    while scale < 0  :
      scale = ROOT.gRandom.Gaus(1, sigma)

    newpt = pt
    if pt > 0 :
     newpt = scale * pt

    return newpt


def smearPt(pt, sigma):
    pt = ROOT.gRandom.Gaus(pt, sigma*pt)
    return pt

def smearCharge(sigma):
    change = ROOT.gRandom.Uniform(0, 1)
    if change < sigma :
       return -1
    else :
       return 1

def electronPtScale(pt, eta, dataset):
    
    par0 = 0
    par1 = 0
    par2 = 0
    if dataset == '2012':
        if   abs(eta) < 0.8 :
            par0 = -2.27e-02
            par1 = -7.01e-02
            par2 = -3.71e-04
        elif abs(eta) < 1.5 :
            par0 = -2.92e-02
            par1 = -6.59e-02
            par2 = -7.22e-04
        else :
            par0 = -2.27e-02
            par1 = -7.01e-02
            par2 = -3.71e-04

    scale = par0 * math.exp(par1 * pt) + par2
    return abs(scale)

def calculateGammaMRStar(ja, jb):
##def gammaMRstar(ja, jb):
    A = ja.P()
    B = jb.P()
    az = ja.Pz()
    bz = jb.Pz()
    jaT = ROOT.TVector3()
    jbT = ROOT.TVector3()
    jaT.SetXYZ(ja.Px(),ja.Py(),0.0)
    jbT.SetXYZ(jb.Px(),jb.Py(),0.0)
    ATBT = (jaT+jbT).Mag2()

    temp = sqrt((A+B)*(A+B)-(az+bz)*(az+bz)-(jbT.Dot(jbT)-jaT.Dot(jaT))*(jbT.Dot(jbT)-jaT.Dot(jaT))/(jaT+jbT).Mag2())
    mybeta = (jbT.Dot(jbT)-jaT.Dot(jaT))/sqrt(ATBT*((A+B)*(A+B)-(az+bz)*(az+bz)))
    mygamma = 1./sqrt(1.-mybeta*mybeta)
    ## gamma times MRstar
    temp *= mygamma
    return temp

def checkZveto(mll, channel):
    zveto = 0
    if abs(mll - mZ) > 15 or channel > 1:
        zveto = 1
    return zveto


# pass eta and pt from a jet plus the list containing the uncertaibties
# from Emanueles file to extract the uncertainty as function of pt and eta
def getJEUFactor(pt, eta, jeuList):
    scale = -1
    ## if there is no jet there is also no uncertainty defined...
    if pt < 0:
        scale = 0
        return scale
    ## loop over the table and find the matching uncertainty!
    for s in jeuList:
        if eta > float(s[0]) and eta <= float(s[1]):
            for p in xrange(len(s)):
                if p%3 != 0:
                    continue
                ## uncertainties have some minimum pt, set to the  lowest defined value if pt is too small...
                if pt <  float(s[3]): # 3 = minimum pt in table
                    scale = float(s[4]) # 4 = corresponding smallest uncertainty
##                     print ' ----------------------------------'
##                     print 'Jet has too low pt: '+str(pt)+' << '+s[3]
##                     print 'Setting uncertainty to minimum pt uncertainty: '+str(scale)
##                     print 'pseudorapidity: '+str(eta)
                    break
                if pt > float(s[p]):
                    scale = float(s[p+1])
                else:
                    break
    ##scale = 0.
    return scale

# calculate projected MET
def projectMET(lep1, lep2, met):
    dphi1 = abs(lep1.DeltaPhi(met))
    dphi2 = abs(lep2.DeltaPhi(met))
    dphimin = min( dphi1, dphi2 )
    pmet = met.Pt()
    if dphimin < 0.5*math.pi:
        pmet *= math.sin(dphimin)
    return pmet

    
###############################################################################################
##                 _                        _                                 
##                | |                      | |                                
##  ___  ___  __ _| | ___    __ _ _ __   __| |  ___ _ __ ___   ___  __ _ _ __ 
## / __|/ __|/ _` | |/ _ \  / _` | '_ \ / _` | / __| '_ ` _ \ / _ \/ _` | '__|
## \__ \ (__| (_| | |  __/ | (_| | | | | (_| | \__ \ | | | | |  __/ (_| | |   
## |___/\___|\__,_|_|\___|  \__,_|_| |_|\__,_| |___/_| |_| |_|\___|\__,_|_|   
##                                                                           
##                                                                           
class scaleAndSmear:

    def __init__(self):
        self.inputFileName = ''
        self.outputFileName = ''
        self.path = ''
        self.inFile = None
        self.outFile = None
        self.treeDir = ''
        self.ttree = None
        self.oldttree = None
        self.nentries = 0
        self.systArgument = ''
        self.direction = ''
        self.strength = -99.
        self.correctMETwithJES = False
        self.dataset = ''
        
        self.pt1 = numpy.zeros(1, dtype=numpy.float32)
        self.pt2 = numpy.zeros(1, dtype=numpy.float32)
        self.mll = numpy.zeros(1, dtype=numpy.float32)
        self.ptll = numpy.zeros(1, dtype=numpy.float32)
        ## self.dphill = numpy.zeros(1, dtype=numpy.float32)
        self.dphilljet = numpy.zeros(1, dtype=numpy.float32)
        self.gammaMRStar = numpy.zeros(1, dtype=numpy.float32)
        self.zveto = numpy.zeros(1, dtype=int)

        self.jetpt1 = numpy.zeros(1, dtype=numpy.float32)
        self.jetpt2 = numpy.zeros(1, dtype=numpy.float32)
        self.njet = numpy.zeros(1, dtype=numpy.float32)
        self.dphilljetjet = numpy.zeros(1, dtype=numpy.float32)
        self.mjj = numpy.zeros(1, dtype=numpy.float32)
        self.cjetpt1 = numpy.zeros(1, dtype=numpy.float32)
        self.cjetpt2 = numpy.zeros(1, dtype=numpy.float32)
        self.njetvbf = numpy.zeros(1, dtype=numpy.float32)
        
        self.dphillmet = numpy.zeros(1, dtype=numpy.float32)
        self.dphilmet = numpy.zeros(1, dtype=numpy.float32)
        self.dphilmet1 = numpy.zeros(1, dtype=numpy.float32)
        self.dphilmet2 = numpy.zeros(1, dtype=numpy.float32)
        self.mth = numpy.zeros(1, dtype=numpy.float32)
        self.mtw1 = numpy.zeros(1, dtype=numpy.float32)
        self.mtw2 = numpy.zeros(1, dtype=numpy.float32)
        self.pfmet = numpy.zeros(1, dtype=numpy.float32)
        self.pfmetphi = numpy.zeros(1, dtype=numpy.float32)
        self.chmet = numpy.zeros(1, dtype=numpy.float32)
        self.chmetphi = numpy.zeros(1, dtype=numpy.float32)
        ## self.tcmet = numpy.zeros(1, dtype=numpy.float32)
        ## self.tcmetphi = numpy.zeros(1, dtype=numpy.float32)
        self.ppfmet = numpy.zeros(1, dtype=numpy.float32)
        self.pchmet = numpy.zeros(1, dtype=numpy.float32)
        ## self.ptcmet = numpy.zeros(1, dtype=numpy.float32)
        self.mpmet = numpy.zeros(1, dtype=numpy.float32)
        self.pfmetSignificance = numpy.zeros(1, dtype=numpy.float32)
        self.pfmetMEtSig = numpy.zeros(1, dtype=numpy.float32)
        self.dphilljet1  = numpy.ones(1, dtype=numpy.float32)
        self.dphimetjet1 = numpy.zeros(1, dtype=numpy.float32)
        self.recoil = numpy.zeros(1, dtype=numpy.float32)
        
        self.getDYMVAV0j0 = None
        self.getDYMVAV0j1 = None
        self.getDYMVAV0j0 = None
        self.getDYMVAV1j1 = None
        self.var1 = numpy.ones(1, dtype=numpy.float32)
        self.var2 = numpy.ones(1, dtype=numpy.float32)
        self.var3 = numpy.ones(1, dtype=numpy.float32)
        self.var4 = numpy.ones(1, dtype=numpy.float32)
        self.var5 = numpy.ones(1, dtype=numpy.float32)
        self.var6 = numpy.ones(1, dtype=numpy.float32)
        self.var7 = numpy.ones(1, dtype=numpy.float32)
        self.var8 = numpy.ones(1, dtype=numpy.float32)
        self.var9 = numpy.ones(1, dtype=numpy.float32)
        self.var10 = numpy.ones(1, dtype=numpy.float32)
        self.var11 = numpy.ones(1, dtype=numpy.float32)


    def __del__(self):
        if self.outFile:
            self.outFile.Write()
            self.outFile.Close()



    def openOriginalTFile(self):
        filename = self.inputFileName
        print 'opening file: '+filename
        self.inFile = ROOT.TFile.Open(filename)

    def openOutputTFile(self):
        filename = self.outputFileName
        dir = os.path.dirname(filename)
        if not os.path.exists(dir):
            print 'directory does not exist yet...'
            print 'creating output directory: '+dir
            os.system('mkdir -p '+dir)
        print 'creating output file: '+filename
        self.outFile = ROOT.TFile.Open(filename,'recreate')

###############################################################################################
##  _____ _                    _____             
## /  __ \ |                  |_   _|            
## | /  \/ | ___  _ __   ___    | |_ __ ___  ___ 
## | |   | |/ _ \| '_ \ / _ \   | | '__/ _ \/ _ \
## | \__/\ | (_) | | | |  __/   | | | |  __/  __/
##  \____/_|\___/|_| |_|\___|   \_/_|  \___|\___|
##                                              
    def cloneTree(self):
        ## clone the tree
        self.inFile.ls()
        oldTree = self.inFile.Get(self.treeDir)
        ## do not clone the branches which we want to drop for systematics ntuples
        ## i.e. set status to 0

        #oldTree.SetBranchStatus('bdt1'           ,0)
        #oldTree.SetBranchStatus('bdt2'           ,0)
        #oldTree.SetBranchStatus('cjeteta1'       ,0)
        #oldTree.SetBranchStatus('cjeteta2'       ,0)
        #oldTree.SetBranchStatus('cjetid1'        ,0)
        #oldTree.SetBranchStatus('cjetid2'        ,0)
        #oldTree.SetBranchStatus('cjetmva1'       ,0)
        #oldTree.SetBranchStatus('cjetmva2'       ,0)
        #oldTree.SetBranchStatus('cjetphi1'       ,0)
        #oldTree.SetBranchStatus('cjetphi2'       ,0)
        #oldTree.SetBranchStatus('cjetpt1'        ,0)
        #oldTree.SetBranchStatus('cjetpt2'        ,0)
        #oldTree.SetBranchStatus('effAW'          ,0)
        #oldTree.SetBranchStatus('effBW'          ,0)
        #oldTree.SetBranchStatus('fakeAW'         ,0)
        #oldTree.SetBranchStatus('fakeBW'         ,0)
        #oldTree.SetBranchStatus('imet'           ,0)
        #oldTree.SetBranchStatus('iso1'           ,0)
        #oldTree.SetBranchStatus('iso2'           ,0)
        #oldTree.SetBranchStatus('jetbjpb1'       ,0)
        #oldTree.SetBranchStatus('jetbjpb2'       ,0)
        #oldTree.SetBranchStatus('jetbjpb3'       ,0)
        #oldTree.SetBranchStatus('jetid1'         ,0)
        #oldTree.SetBranchStatus('jetid2'         ,0)
        #oldTree.SetBranchStatus('jetid3'         ,0)
        #oldTree.SetBranchStatus('jetid4'         ,0)
        #oldTree.SetBranchStatus('jetmva1'        ,0)
        #oldTree.SetBranchStatus('jetmva2'        ,0)
        #oldTree.SetBranchStatus('jetmva3'        ,0)
        #oldTree.SetBranchStatus('jetmva4'        ,0)
        #oldTree.SetBranchStatus('jettche1'       ,0)
        #oldTree.SetBranchStatus('jettche2'       ,0)
        #oldTree.SetBranchStatus('jettche3'       ,0)
        #oldTree.SetBranchStatus('jettchp1'       ,0)
        #oldTree.SetBranchStatus('jettchp2'       ,0)
        #oldTree.SetBranchStatus('jettchp3'       ,0)
        #oldTree.SetBranchStatus('lh1'            ,0)
        #oldTree.SetBranchStatus('lh2'            ,0)
        #oldTree.SetBranchStatus('nbrem1'         ,0)
        #oldTree.SetBranchStatus('nbrem2'         ,0)
        #oldTree.SetBranchStatus('sceta1'         ,0)
        #oldTree.SetBranchStatus('sceta2'         ,0)
        #oldTree.SetBranchStatus('triggAW'        ,0)
        #oldTree.SetBranchStatus('triggBW'        ,0)
        #oldTree.SetBranchStatus('bveto_munj'     ,0)
        #oldTree.SetBranchStatus('bveto_munj05'   ,0)
        #oldTree.SetBranchStatus('bveto_munj30'   ,0)
        #oldTree.SetBranchStatus('bveto_munj3005' ,0)
        #oldTree.SetBranchStatus('bveto_nj'       ,0)
        #oldTree.SetBranchStatus('bveto_nj05'     ,0)
        #oldTree.SetBranchStatus('bveto_nj30'     ,0)
        #oldTree.SetBranchStatus('bveto_nj3005'   ,0)
        oldTree.SetBranchStatus('puWsmurf'       ,0)
        oldTree.SetBranchStatus('puWABtrue'      ,0)
        oldTree.SetBranchStatus('puWCtrue'       ,0)
        oldTree.SetBranchStatus('puWABCtrue'     ,0)
        oldTree.SetBranchStatus('puW120AB'       ,0)
        oldTree.SetBranchStatus('puW600AB'       ,0)
        oldTree.SetBranchStatus('puW120C'        ,0)
        oldTree.SetBranchStatus('puW600C'        ,0)
        oldTree.SetBranchStatus('puW120ABC'      ,0)
        oldTree.SetBranchStatus('puW600ABC'      ,0)

        ## do not clone the branches which should be scaled
        ## i.e. set status to 0
        if self.systArgument == 'leptonEfficiency':
            oldTree.SetBranchStatus('effW'      ,0)
            oldTree.SetBranchStatus('effAW'     ,0)
            oldTree.SetBranchStatus('effBW'     ,0)
            
        elif self.systArgument == 'puscale':
            oldTree.SetBranchStatus('puW'       ,0)
            
        elif self.systArgument == 'chargeResolution':
            oldTree.SetBranchStatus('ch1'       ,0)
            oldTree.SetBranchStatus('ch2'       ,0)

        else:
        ## by default, re-assign all these variables
        ## currently not needed for JEC, but for everything else
            oldTree.SetBranchStatus('pt1'       ,0)
            oldTree.SetBranchStatus('pt2'       ,0)
            oldTree.SetBranchStatus('mll'       ,0)
            oldTree.SetBranchStatus('ptll'      ,0)
            ## oldTree.SetBranchStatus('dphill'    ,0)
            oldTree.SetBranchStatus('dphilljet' ,0)
            oldTree.SetBranchStatus('gammaMRStar',0)
            oldTree.SetBranchStatus('zveto'     ,0)

            oldTree.SetBranchStatus('jetpt1'    ,0)
            oldTree.SetBranchStatus('jetpt2'    ,0)
            oldTree.SetBranchStatus('njet'      ,0)
            oldTree.SetBranchStatus('mjj'       ,0)
            oldTree.SetBranchStatus('dphilljetjet' ,0)
            oldTree.SetBranchStatus('cjetpt1'   ,0)
            oldTree.SetBranchStatus('cjetpt2'   ,0)
            oldTree.SetBranchStatus('njetvbf'   ,0)
                                                                                                                        
            oldTree.SetBranchStatus('pfmet'     ,0)
            oldTree.SetBranchStatus('pfmetphi'  ,0)
            oldTree.SetBranchStatus('chmet'     ,0)
            oldTree.SetBranchStatus('chmetphi'  ,0)
            ## oldTree.SetBranchStatus('tcmet'     ,0)
            ## oldTree.SetBranchStatus('tcmetphi'  ,0)
            oldTree.SetBranchStatus('dphillmet' ,0)
            oldTree.SetBranchStatus('dphilmet'  ,0)
            oldTree.SetBranchStatus('dphilmet1' ,0)
            oldTree.SetBranchStatus('dphilmet2' ,0)
            oldTree.SetBranchStatus('mth'       ,0)
            oldTree.SetBranchStatus('mtw1'      ,0)
            oldTree.SetBranchStatus('mtw2'      ,0)
            oldTree.SetBranchStatus('ppfmet'    ,0)
            oldTree.SetBranchStatus('pchmet'    ,0)
            ## oldTree.SetBranchStatus('ptcmet'    ,0)
            oldTree.SetBranchStatus('mpmet'     ,0)
            oldTree.SetBranchStatus('pfmetSignificance', 0)
            oldTree.SetBranchStatus('pfmetMEtSig',0)
            oldTree.SetBranchStatus('dphilljet1',0)
            oldTree.SetBranchStatus('dphimetjet1',0)
            oldTree.SetBranchStatus('recoil'    ,0)
                        

        newTree = oldTree.CloneTree(0)
        nentries = oldTree.GetEntriesFast()
        print 'Tree with '+str(nentries)+' entries cloned...'
        self.nentries = nentries
        
        self.ttree = newTree
        ## BUT keep all branches "active" in the old tree
        oldTree.SetBranchStatus('*'  ,1)

        self.oldttree = oldTree
        for branch in self.ttree.GetListOfBranches():
            print branch

## define variables to recompute
    def defineVariables(self):

        self.ttree.Branch('pt1',self.pt1,'pt1/F')
        self.ttree.Branch('pt2',self.pt2,'pt2/F')
        self.ttree.Branch('mll',self.mll,'mll/F')
        self.ttree.Branch('ptll',self.ptll,'ptll/F')
        ##         self.ttree.Branch('dphill',self.dphill,'dphill/F')
        self.ttree.Branch('dphilljet',self.dphilljet,'dphilljet/F')
        self.ttree.Branch('gammaMRStar',self.gammaMRStar,'gammaMRStar/F')
        self.ttree.Branch('zveto',self.zveto,'zveto/I')
        
        self.ttree.Branch('jetpt1',self.jetpt1,'jetpt1/F')
        self.ttree.Branch('jetpt2',self.jetpt2,'jetpt2/F')
        self.ttree.Branch('njet',self.njet,'njet/F')
        self.ttree.Branch('mjj',self.mjj,'mjj/F')
        self.ttree.Branch('dphilljetjet',self.dphilljetjet,'dphilljetjet/F')
        self.ttree.Branch('cjetpt1',self.cjetpt1,'cjetpt1/F')
        self.ttree.Branch('cjetpt2',self.cjetpt2,'cjetpt2/F')
        self.ttree.Branch('njetvbf',self.njetvbf,'njetvbf/F')
    
        self.ttree.Branch('dphillmet',self.dphillmet,'dphillmet/F')
        self.ttree.Branch('dphilmet',self.dphilmet,'dphilmet/F')
        self.ttree.Branch('dphilmet1',self.dphilmet1,'dphilmet1/F')
        self.ttree.Branch('dphilmet2',self.dphilmet2,'dphilmet2/F')
        self.ttree.Branch('mth',self.mth,'mth/F')
        self.ttree.Branch('mtw1',self.mtw1,'mtw1/F')
        self.ttree.Branch('mtw2',self.mtw2,'mtw2/F')
        self.ttree.Branch('pfmet',self.pfmet,'pfmet/F')
        self.ttree.Branch('pfmetphi',self.pfmetphi,'pfmetphi/F')
        self.ttree.Branch('chmet',self.chmet,'chmet/F')
        self.ttree.Branch('chmetphi',self.chmetphi,'chmetphi/F')
        ## self.ttree.Branch('tcmet',self.tcmet,'tcmet/F')
        ## self.ttree.Branch('tcmetphi',self.tcmetphi,'tcmetphi/F')
        self.ttree.Branch('ppfmet',self.ppfmet,'ppfmet/F')
        self.ttree.Branch('pchmet',self.pchmet,'pchmet/F')
        ## self.ttree.Branch('ptcmet',self.ptcmet,'ptcmet/F')
        self.ttree.Branch('mpmet',self.mpmet,'mpmet/F')
        self.ttree.Branch('pfmetSignificance',self.pfmetSignificance,'pfmetSignificance/F')
        self.ttree.Branch('pfmetMEtSig',self.pfmetMEtSig,'pfmetMEtSig/F')
        self.ttree.Branch('dphimetjet1',self.dphimetjet1,'dphimetjet1/F')
        self.ttree.Branch('dphilljet1',self.dphilljet1,'dphilljet1/F')
        self.ttree.Branch('recoil',self.recoil,'recoil/F')


## get old values from original tree
    def getOriginalVariables(self):
        
        self.pt1[0] = self.oldttree.pt1
        self.pt2[0] = self.oldttree.pt2
        #print 'original '+str(tree.pt1)+' '+str(tree.pt2)
        #print 'original '+str(self.pt1)+' '+str(self.pt2)
        self.mll[0] = self.oldttree.mll
        self.ptll[0] = self.oldttree.ptll
        ## self.dphill[0] = self.oldttree.dphill
        self.dphilljet[0] = self.oldttree.dphilljet
        self.gammaMRStar[0] = self.oldttree.gammaMRStar
        self.zveto[0] = self.oldttree.zveto
        
        self.jetpt1[0] = self.oldttree.jetpt1
        self.jetpt2[0] = self.oldttree.jetpt2
        self.njet[0] = self.oldttree.njet
        self.dphilljetjet[0] = self.oldttree.dphilljetjet
        self.mjj[0] = self.oldttree.mjj
        self.cjetpt1[0] = self.oldttree.cjetpt1
        self.cjetpt2[0] = self.oldttree.cjetpt2
        self.njetvbf[0] = self.oldttree.njetvbf
        
        self.dphillmet[0] = self.oldttree.dphillmet
        self.dphilmet[0] = self.oldttree.dphilmet
        self.dphilmet1[0] = self.oldttree.dphilmet1
        self.dphilmet2[0] = self.oldttree.dphilmet2
        self.mth[0] = self.oldttree.mth
        self.mtw1[0] = self.oldttree.mtw1
        self.mtw2[0] = self.oldttree.mtw2
        self.pfmet[0] = self.oldttree.pfmet
        self.pfmetphi[0] = self.oldttree.pfmetphi
        self.chmet[0] = self.oldttree.chmet
        self.chmetphi[0] = self.oldttree.chmetphi
        ## self.tcmet[0] = self.oldttree.tchmet
        ## self.tcmetphi[0] = self.oldttree.tcmetphi
        self.ppfmet[0] = self.oldttree.ppfmet
        self.pchmet[0] = self.oldttree.pchmet
        ## self.ptcmet[0] = self.oldttree.ptcmet
        self.mpmet[0] = self.oldttree.mpmet
        self.pfmetSignificance[0] = self.oldttree.pfmetSignificance
        self.pfmetMEtSig[0] = self.oldttree.pfmetMEtSig

        # these variables were not defined in a previous version of the ntuples, then default values needed
        if hasattr(self.oldttree, 'dphimetjet1') :
          self.dphimetjet1[0] = self.oldttree.dphimetjet1   #-999 #self.oldttree.dphimetjet1
        else :
          self.dphimetjet1[0] = -999

        if hasattr(self.oldttree, 'dphilljet1') :
          self.dphilljet1[0] = self.oldttree.dphilljet1   #-999 #self.oldttree.dphimetjet1
        else :
          self.dphilljet1[0] = -999

        if hasattr(self.oldttree, 'recoil') :
          self.recoil[0] = self.oldttree.recoil   #-999 #self.oldttree.dphimetjet1
        else :
          self.recoil[0] = -999



## recompute lepton related variables from already corrected leptons
    def computeLeptonVariables(self,l1,l2):

        self.mll[0]  = invariantMass(l1, l2)
        self.ptll[0] = dileptonPt(l1, l2)
        ## self.dphill[0] =  deltaPhi(l1,l2)
        
        self.gammaMRStar[0] = calculateGammaMRStar(l1,l2)
        self.zveto[0] = checkZveto(self.mll, self.oldttree.channel)

        j1 = ROOT.TLorentzVector()
        j1.SetPtEtaPhiM(self.jetpt1[0], self.oldttree.jeteta1, self.oldttree.jetphi1, 0)
        self.dphilljet[0] = deltaPhi(l1+l2,j1)

## recompute met related variables from already corrected lepton and pfmet/chmet
    def computeMETVariables(self,l1,l2,pf,ch):
    
        ## correct projected MET
        self.ppfmet[0] = projectMET(l1, l2, pf)
        self.pchmet[0] = projectMET(l1, l2, ch)
        self.mpmet[0] = min( self.ppfmet, self.pchmet )

        self.dphillmet[0] =  deltaPhi(l1+l2,pf)
        self.dphilmet1[0] =  deltaPhi(l1,pf)
        self.dphilmet2[0] =  deltaPhi(l2,pf)
        self.dphilmet[0]  =  min(self.dphilmet1, self.dphilmet2)
        
        self.mth[0]  = transverseMass((l1+l2),pf)
        self.mtw1[0] = transverseMass((l1),pf)
        self.mtw2[0] = transverseMass((l2),pf)

        jpt1 = self.jetpt1[0]
        if self.jetpt1[0] < 15 :
            jpt1 = 15
            self.dphilljet1[0]  = -0.1;
            self.dphimetjet1[0] = -0.1;
        else :
            jet1 = ROOT.TLorentzVector()
            jet1.SetPtEtaPhiM(self.jetpt1[0], self.oldttree.jeteta1, self.oldttree.jetphi1, 0)
            self.dphilljet1[0]  = deltaPhi(l1+l2,jet1)
            self.dphimetjet1[0] = deltaPhi(pf,jet1)

        #self.pfmetSignificance[0] = self.pfmet[0] / self.oldttree.pfmet * self.oldttree.pfmetSignificance
        self.pfmetMEtSig[0] = self.pfmet[0] / self.oldttree.pfmet * self.oldttree.pfmetMEtSig
        
        px_rec = pf.Pt() * cos(pf.Phi()) + (l1+l2).Px()
        py_rec = pf.Pt() * sin(pf.Phi()) + (l1+l2).Py()
        self.recoil[0] = sqrt(px_rec*px_rec + py_rec*py_rec)
                                
        

## print values before and after
    def printVariables(self):

        print 'channel: '+str(self.oldttree.channel)
        print 'pt1: '+str(self.oldttree.pt1)+' -> '+ str(self.pt1[0])
        print 'pt2: '+str(self.oldttree.pt2)+' -> '+ str(self.pt2[0])
        print 'mll: '    + str(self.oldttree.mll)    +to+ str(self.mll[0])
        print 'ptll: '   + str(self.oldttree.ptll)   +to+ str(self.ptll[0])
        ##                 print 'dphill: ' + str(self.oldttree.dphill) +to+ str(self.dphill[0])  
        print 'gammaMRStar: '    +str(self.oldttree.gammaMRStar)    +to+str(self.gammaMRStar[0])
        print 'zveto: '    +str(self.oldttree.zveto)    +to+str(self.zveto[0])
        print 'pfmet: '    +str(self.oldttree.pfmet)    +to+str(self.pfmet[0])
        print 'pfmetphi: ' +str(self.oldttree.pfmetphi) +to+str(self.pfmetphi[0])
        print 'chmet: '    +str(self.oldttree.chmet)    +to+str(self.chmet[0])
        print 'chmetphi: ' +str(self.oldttree.chmetphi) +to+str(self.chmetphi[0])
        ## print 'tcmet: '    +str(self.oldttree.tcmet)    +to+str(self.tcmet[0])
        ## print 'tcmetphi: ' +str(self.oldttree.tcmetphi) +to+str(self.tcmetphi[0])
        print 'dphillmet: ' + str(self.oldttree.dphillmet) +to+ str(self.dphillmet[0])
        print 'dphilmet: ' + str(self.oldttree.dphilmet) +to+ str(self.dphilmet[0])
        print 'dphilljet: ' + str(self.oldttree.dphilljet) +to+ str(self.dphilljet[0])
        print 'dphilmet1: ' + str(self.oldttree.dphilmet1) +to+ str(self.dphilmet1[0])
        print 'dphilmet2: ' + str(self.oldttree.dphilmet2) +to+ str(self.dphilmet2[0])
        print 'mth: ' + str(self.oldttree.mth) +to+ str(self.mth[0])
        print 'mtw1: ' + str(self.oldttree.mtw1) +to+ str(self.mtw1[0])
        print 'mtw2: ' + str(self.oldttree.mtw2) +to+ str(self.mtw2[0])
        print 'ppfmet: '    +str(self.oldttree.ppfmet)    +to+str(self.ppfmet[0])
        print 'pchmet: '    +str(self.oldttree.pchmet)    +to+str(self.pchmet[0])
        ## print 'ptcmet: '    +str(self.oldttree.ptcmet)    +to+str(self.ptcmet[0])
        print 'mpmet: '    +str(self.oldttree.mpmet)    +to+str(self.mpmet[0])
        print 'jetpt1: '+str(self.oldttree.jetpt1)+' -> '+ str(self.jetpt1[0])
        print 'jetpt2: '+str(self.oldttree.jetpt2)+' -> '+ str(self.jetpt2[0])
        print 'cjetpt1: '+str(self.oldttree.cjetpt1)+' -> '+ str(self.cjetpt1[0])
        print 'cjetpt2: '+str(self.oldttree.cjetpt2)+' -> '+ str(self.cjetpt2[0])
        print 'njet: '  +str(self.oldttree.njet)        +to+str(self.njet[0])
        print 'njetvbf: '  +str(self.oldttree.njetvbf)        +to+str(self.njetvbf[0])
        print 'mjj: ' + str(self.oldttree.mjj) +to+ str(self.mjj[0])
        

    def createDYMVA(self):
        self.getDYMVAV0j0 = ROOT.TMVA.Reader();
        self.getDYMVAV0j1 = ROOT.TMVA.Reader();
        self.getDYMVAV1j0 = ROOT.TMVA.Reader();
        self.getDYMVAV1j1 = ROOT.TMVA.Reader();
        
        self.getDYMVAV0j0.AddVariable("met",           (self.var1))
        self.getDYMVAV0j0.AddVariable("trackMet",      (self.var2))
        self.getDYMVAV0j0.AddVariable("jet1pt",        (self.var3))
        self.getDYMVAV0j0.AddVariable("metSig",        (self.var4))
        self.getDYMVAV0j0.AddVariable("dPhiDiLepJet1", (self.var5))
        self.getDYMVAV0j0.AddVariable("dPhiJet1MET",   (self.var6))
        self.getDYMVAV0j0.AddVariable("mt",            (self.var7))
        
        self.getDYMVAV0j1.AddVariable("met",           (self.var1))
        self.getDYMVAV0j1.AddVariable("trackMet",      (self.var2))
        self.getDYMVAV0j1.AddVariable("jet1pt",        (self.var3))
        self.getDYMVAV0j1.AddVariable("metSig",        (self.var4))
        self.getDYMVAV0j1.AddVariable("dPhiDiLepJet1", (self.var5))
        self.getDYMVAV0j1.AddVariable("dPhiJet1MET",   (self.var6))
        self.getDYMVAV0j1.AddVariable("mt",            (self.var7))
        
        self.getDYMVAV1j0.AddVariable("pmet",           (self.var1))
        self.getDYMVAV1j0.AddVariable("pTrackMet",      (self.var2))
        self.getDYMVAV1j0.AddVariable("nvtx",           (self.var3))
        self.getDYMVAV1j0.AddVariable("dilpt",          (self.var4))
        self.getDYMVAV1j0.AddVariable("jet1pt",         (self.var5))
        self.getDYMVAV1j0.AddVariable("metSig",         (self.var6))
        self.getDYMVAV1j0.AddVariable("dPhiDiLepJet1",  (self.var7))
        self.getDYMVAV1j0.AddVariable("dPhiDiLepMET",   (self.var8))
        self.getDYMVAV1j0.AddVariable("dPhiJet1MET",    (self.var9))
        self.getDYMVAV1j0.AddVariable("recoil",         (self.var10))
        self.getDYMVAV1j0.AddVariable("mt",             (self.var11))
        
        self.getDYMVAV1j1.AddVariable("pmet",           (self.var1))
        self.getDYMVAV1j1.AddVariable("pTrackMet",      (self.var2))
        self.getDYMVAV1j1.AddVariable("nvtx",           (self.var3))
        self.getDYMVAV1j1.AddVariable("dilpt",          (self.var4))
        self.getDYMVAV1j1.AddVariable("jet1pt",         (self.var5))
        self.getDYMVAV1j1.AddVariable("metSig",         (self.var6))
        self.getDYMVAV1j1.AddVariable("dPhiDiLepJet1",  (self.var7))
        self.getDYMVAV1j1.AddVariable("dPhiDiLepMET",   (self.var8))
        self.getDYMVAV1j1.AddVariable("dPhiJet1MET",    (self.var9))
        self.getDYMVAV1j1.AddVariable("recoil",         (self.var10))
        self.getDYMVAV1j1.AddVariable("mt",             (self.var11))
        
        
        #baseCMSSW = string(getenv("CMSSW_BASE"))
        #self.getDYMVAV0j0.BookMVA("BDTB",baseCMSSW+string("/src/DYMvaInCMSSW/GetDYMVA/data/TMVA_0j_BDTB.weights.xml"))
        #self.getDYMVAV0j1.BookMVA("BDTB",baseCMSSW+string("/src/DYMvaInCMSSW/GetDYMVA/data/TMVA_1j_BDTB.weights.xml"))
        #self.getDYMVAV1j0.BookMVA("BDTG",baseCMSSW+string("/src/DYMvaInCMSSW/GetDYMVA/data/TMVA_BDTG_0j_MCtrain.weights.xml"))
        #self.getDYMVAV1j1.BookMVA("BDTG",baseCMSSW+string("/src/DYMvaInCMSSW/GetDYMVA/data/TMVA_BDTG_1j_MCtrain.weights.xml"))
        
        #baseCMSSW = os.getenv('CMSSW_BASE')
        #self.getDYMVAV0j0.BookMVA("BDTB",baseCMSSW+"/src/DYMvaInCMSSW/GetDYMVA/data/TMVA_0j_BDTB.weights.xml")
        #self.getDYMVAV0j1.BookMVA("BDTB",baseCMSSW+"/src/DYMvaInCMSSW/GetDYMVA/data/TMVA_1j_BDTB.weights.xml")
        #self.getDYMVAV1j0.BookMVA("BDTG",baseCMSSW+"/src/DYMvaInCMSSW/GetDYMVA/data/TMVA_BDTG_0j_MCtrain.weights.xml")
        #self.getDYMVAV1j1.BookMVA("BDTG",baseCMSSW+"/src/DYMvaInCMSSW/GetDYMVA/data/TMVA_BDTG_1j_MCtrain.weights.xml")
        
        # new dymva trainined xml
        baseCMSSW = os.getenv('CMSSW_BASE')
        self.getDYMVAV0j0.BookMVA("BDTB",baseCMSSW+"/src/DYMvaInCMSSW/GetDYMVA/data/TMVA_0j_BDTB.weights.xml")
        self.getDYMVAV0j1.BookMVA("BDTB",baseCMSSW+"/src/DYMvaInCMSSW/GetDYMVA/data/TMVA_1j_BDTB.weights.xml")
        self.getDYMVAV1j0.BookMVA("BDTG",baseCMSSW+"/src/DYMvaInCMSSW/GetDYMVA/data/TMVA_0j_metshift_BDTG.weights.xml")
        self.getDYMVAV1j1.BookMVA("BDTG",baseCMSSW+"/src/DYMvaInCMSSW/GetDYMVA/data/TMVA_1j_metshift_BDTG.weights.xml")
        
        
    def computeDYMVA(self, algo, nj, l1, l2, met):

        dymva = -999

        if algo == 0:
            
            self.var1[0] =  self.pfmet[0]
            self.var2[0] =  self.chmet[0]
            self.var3[0] =  self.jetpt1[0]
            self.var4[0] =  self.pfmetSignificance[0]
            self.var5[0] =  self.dphilljet1[0]
            self.var6[0] =  self.dphimetjet1[0]
            self.var7[0] =  self.mth[0]
            
            if nj == 0:
                dymva = self.getDYMVAV0j0.EvaluateMVA("BDTB")
            elif nj == 1:
                dymva = self.getDYMVAV0j1.EvaluateMVA("BDTB")
            else :
                dymva = -999

        if algo == 1:
            self.var1[0]  =  self.ppfmet[0]
            self.var2[0]  =  self.pchmet[0]
            self.var3[0]  =  self.oldttree.nvtx
            self.var4[0]  =  self.ptll[0]
            self.var5[0]  =  self.jetpt1[0]
            self.var6[0]  =  self.pfmetMEtSig[0]
            self.var7[0]  =  self.dphilljet1[0]
            self.var8[0]  =  self.dphillmet[0]
            self.var9[0]  =  self.dphimetjet1[0]
            self.var10[0] =  self.recoil[0]
            self.var11[0] =  self.mth[0]
        
            if nj == 0:
                dymva = self.getDYMVAV1j0.EvaluateMVA("BDTG")
            elif nj == 1:
                dymva = self.getDYMVAV1j1.EvaluateMVA("BDTG")
            else :
                dymva = -999

            #print 'dymva '+str(self.oldttree.dymva1)+' '+str(dymva)

        return dymva
    
        
###############################################################################################
##     
##     
##        _ \   |   |                         _)         |   _)               
##       |   |  |   |     \ \   /  _` |   __|  |   _` |  __|  |   _ \   __ \  
##       ___/   |   |      \ \ /  (   |  |     |  (   |  |    |  (   |  |   | 
##      _|     \___/        \_/  \__,_| _|    _| \__,_| \__| _| \___/  _|  _| 
##                                                                            
##     

    def puVariation(self):
        from ROOT import std
 
        ## define a new branch
        print 'PU scaling'
        puW = numpy.ones(1, dtype=numpy.float32)
        self.ttree.Branch(weightNamePU,puW,weightNamePU+"/F")


        inDATAFileUp   = openTFile('data/'+puUp)
        inDATAFileDown = openTFile('data/'+puDown)
        inMCFile       = openTFile('data/'+puMC)


        puScaleDATAhistoUp   = getHist(inDATAFileUp,"pileup")
        puScaleDATAhistoDown = getHist(inDATAFileDown,"pileup")
        puScaleMChisto       = getHist(inMCFile,"pileup")


        dataUp_nBin = puScaleDATAhistoUp.GetNbinsX()
        dataUp_minValue = puScaleDATAhistoUp.GetXaxis().GetXmin()
        dataUp_maxValue = puScaleDATAhistoUp.GetXaxis().GetXmax()
        dataUp_dValue = (dataUp_maxValue - dataUp_minValue) / dataUp_nBin

        dataDown_nBin = puScaleDATAhistoDown.GetNbinsX()
        dataDown_minValue = puScaleDATAhistoDown.GetXaxis().GetXmin()
        dataDown_maxValue = puScaleDATAhistoDown.GetXaxis().GetXmax()
        dataDown_dValue = (dataDown_maxValue - dataDown_minValue) / dataDown_nBin

        mc_nBin = puScaleMChisto.GetNbinsX()
        mc_minValue = puScaleMChisto.GetXaxis().GetXmin()
        mc_maxValue = puScaleMChisto.GetXaxis().GetXmax()
        mc_dValue = (mc_maxValue - mc_minValue) / mc_nBin
  
        ratioUp = mc_dValue/dataUp_dValue
        nBinUp = dataUp_nBin
        minValueUp = dataUp_minValue
        maxValueUp = dataUp_maxValue
        dValueUp = dataUp_dValue

        ratioDown = mc_dValue/dataDown_dValue
        nBinDown = dataDown_nBin
        minValueDown = dataDown_minValue
        maxValueDown = dataDown_maxValue
        dValueDown = dataDown_dValue
      
        if (mc_dValue/dataUp_dValue - (int) (mc_dValue/dataUp_dValue)) != 0 :
          print " ERROR:: incompatible intervals!  Up"
          exit(0);
        
        if (mc_dValue/dataDown_dValue - (int) (mc_dValue/dataDown_dValue)) != 0 :
          print " ERROR:: incompatible intervals!  Down"
          exit(0);
 
        puScaleDATAUp   = std.vector(float)()
        puScaleDATADown = std.vector(float)()
        puScaleMCtemp   = std.vector(float)()
        puScaleMC       = std.vector(float)()

        ################
        nBin = nBinUp
        # remove last bin -> peak in DATA distribution
        nBin = nBin-1
        ################   

        for iBin in range(0, nBin):
            puScaleDATAUp.push_back(puScaleDATAhistoUp.GetBinContent(iBin+1))
            puScaleDATADown.push_back(puScaleDATAhistoDown.GetBinContent(iBin+1))
            mcbin = int(floor(iBin / ratioUp))
            puScaleMCtemp.push_back(puScaleMChisto.GetBinContent(mcbin+1))

 
        integralDATA = 0.
        integralMC   = 0.
 
        for iBin in range(0, nBin):
            integralDATA += puScaleDATAUp.at(iBin)
            integralMC   += puScaleMCtemp.at(iBin)

        print " integralDATA = " + "%.3f" %integralDATA
        print " integralMC   = " + "%.3f" %integralMC
 
        for iBin in range(0, nBin):
            puScaleMC.push_back( puScaleMCtemp.at(iBin) * integralDATA / integralMC) 


 
        nentries = self.nentries
        print 'total number of entries: '+str(nentries)
        i = 0
        for ientry in range(0,nentries):
            i+=1
            self.oldttree.GetEntry(ientry)

            ## print event count
            step = 50000
            if i > 0 and i%step == 0.:
                print str(i)+' events processed.'

            puW[0] = 1.
            
            
            if self.direction == 'up':
                ibin = int(self.oldttree.trpu / dValueUp)
                if ibin < puScaleDATAUp.size() :
                   if puScaleMC.at(ibin) != 0 :
                      puW[0] = 1. * puScaleDATAUp.at(ibin) / puScaleMC.at(ibin)
                   else :
                      puW[0] = 1.
                else :
                   ibin = puScaleDATAUp.size()-1
                   if puScaleMC.at(ibin) != 0 :
                      puW[0] = 1. * puScaleDATAUp.at(ibin) / puScaleMC.at(ibin)
                   else :
                      puW[0] = 1.


            if self.direction == 'down':
                ibin = int(self.oldttree.trpu / dValueDown)
                if ibin < puScaleDATADown.size() :
                   if puScaleMC.at(ibin) != 0 :
                      puW[0] = 1. * puScaleDATADown.at(ibin) / puScaleMC.at(ibin)
                   else :
                      puW[0] = 1.
                else :
                   ibin = puScaleDATADown.size()-1
                   if puScaleMC.at(ibin) != 0 :
                      puW[0] = 1. * puScaleDATADown.at(ibin) / puScaleMC.at(ibin)
                   else :
                      puW[0] = 1.

            if self.verbose is True:
                print '-----------------------------------'
                print 'puW: '+str(puW[0])


            # fill old and new values
            self.ttree.Fill()







###############################################################################################
## ___  ___                    _____            _      
## |  \/  |                   /  ___|          | |     
## | .  . |_   _  ___  _ __   \ `--.  ___  __ _| | ___ 
## | |\/| | | | |/ _ \| '_ \   `--. \/ __|/ _` | |/ _ \
## | |  | | |_| | (_) | | | | /\__/ / (__| (_| | |  __/
## \_|  |_/\__,_|\___/|_| |_| \____/ \___|\__,_|_|\___|
##                                                    
    def muonScale(self):
##        uncertainty = 0.02
        uncertaintyMB = muonUncertainty
        uncertaintyME = muonUncertainty
        boundaryMBME = 1.5
        if self.dataset == '2012' :
            uncertaintyMB = muonUncertaintyMB2012
            uncertaintyME = muonUncertaintyME2012
            boundaryMBME = 2.2
                                                        
        if self.direction == 'up':
            direction = self.strength
        if self.direction == 'down':
            direction = self.strength
        scaleMB = uncertaintyMB * direction
        scaleME = uncertaintyME * direction

        ## define a new branch
        self.defineVariables()

        nentries = self.nentries
        print 'total number of entries: '+str(nentries)
        i=0
        for ientry in xrange(0,nentries):
            i+=1
            self.oldttree.GetEntry(ientry)

            ## print event count
            step = 10000
            if i > 0 and i%step == 0:
                print str(i)+' events processed.'
                
            ## by default set all values to original tree
            self.getOriginalVariables()

            # get the "old" lepton pt
            pt1_hold  = self.oldttree.pt1
            eta1_hold = self.oldttree.eta1
            phi1_hold = self.oldttree.phi1
            pt2_hold  = self.oldttree.pt2
            eta2_hold = self.oldttree.eta2
            phi2_hold = self.oldttree.phi2
            
            ## scale the lepton pt
            ## muon-muon channel
            if self.oldttree.channel == 0:
                if   abs(self.oldttree.eta1) < boundaryMBME:
                    self.pt1[0] = pt1_hold + pt1_hold * scaleMB
                else :
                    self.pt1[0] = pt1_hold + pt1_hold * scaleME
                if   abs(self.oldttree.eta2) < boundaryMBME:
                    self.pt2[0] = pt2_hold + pt2_hold * scaleMB
                else :
                    self.pt2[0] = pt2_hold + pt2_hold * scaleME
            ## electron-electron channel
            ## dont scale at all
            if self.oldttree.channel == 1:
                self.pt1[0] = pt1_hold  ## do not scale electrons here
                self.pt2[0] = pt2_hold  ## independent of "up" or "down"
            ## electron-muon channel
            if self.oldttree.channel == 2:
                self.pt1[0] = pt1_hold
                if   abs(self.oldttree.eta2) < boundaryMBME:
                    self.pt2[0] = pt2_hold + pt2_hold * scaleMB
                else :
                    self.pt2[0] = pt2_hold + pt2_hold * scaleME
            ## muon-electron channel
            if self.oldttree.channel == 3:
                if   abs(self.oldttree.eta1) < boundaryMBME:
                    self.pt1[0] = pt1_hold + pt1_hold * scaleMB
                else :
                    self.pt1[0] = pt1_hold + pt1_hold * scaleME
                self.pt2[0] = pt2_hold


            ## FIXME: after the scaling one has to recalculate some variables
            ##        like invariant mass etc...
            ##        does delta phi, eta change? guess not...

            l1 = ROOT.TLorentzVector()
            l2 = ROOT.TLorentzVector()
            l1_hold = ROOT.TLorentzVector()
            l2_hold = ROOT.TLorentzVector()
            l1_hold.SetPtEtaPhiM(pt1_hold, eta1_hold, phi1_hold, 0)
            l2_hold.SetPtEtaPhiM(pt2_hold, eta2_hold, phi2_hold, 0)
            l1.SetPtEtaPhiM(self.pt1[0], eta1_hold, phi1_hold, 0)
            l2.SetPtEtaPhiM(self.pt2[0], eta2_hold, phi2_hold, 0)
            
            # recompute lepton variables
            self.computeLeptonVariables(l1, l2)
            
            # recompute met variables
            ## - pfmet
            met = ROOT.TLorentzVector()
            met.SetPtEtaPhiM(self.oldttree.pfmet, 0, self.oldttree.pfmetphi, 0)
            met = correctMet(met, l1_hold, l2_hold, l1, l2)
            self.pfmet[0] = met.Pt()
            self.pfmetphi[0] = met.Phi()
            ## - chmet
            chmet4 = ROOT.TLorentzVector()
            chmet4.SetPtEtaPhiM(self.oldttree.chmet, 0, self.oldttree.chmetphi, 0)
            chmet4 = correctMet(chmet4, l1_hold, l2_hold, l1, l2)
            self.chmet[0] = chmet4.Pt()
            self.chmetphi[0] = chmet4.Phi()
            ## ## - tcmet
            ## tcmet4 = ROOT.TLorentzVector()
            ## tcmet4.SetPtEtaPhiM(self.oldttree.tcmet, 0, self.oldttree.tcmetphi, 0)
            ## tcmet4 = correctMet(tcmet4, l1_hold, l2_hold, l1, l2)
            ## tcmet[0] = tcmet4.Pt()
            ## tcmetphi[0] = tcmet4.Phi()
            
            self.computeMETVariables(l1, l2, met, chmet4)
                        
            if self.verbose is True:
                print '-----------------------------------'
                print 'event: '+str(i)
                print 'scale MB '+str(scaleMB)
                print 'scale ME '+str(scaleME)
                self.printVariables()
            
            # fill old and new values
            self.ttree.Fill()


###############################################################################################
##  _____ _           _                     _____            _      
## |  ___| |         | |                   /  ___|          | |     
## | |__ | | ___  ___| |_ _ __ ___  _ __   \ `--.  ___  __ _| | ___ 
## |  __|| |/ _ \/ __| __| '__/ _ \| '_ \   `--. \/ __|/ _` | |/ _ \
## | |___| |  __/ (__| |_| | | (_) | | | | /\__/ / (__| (_| | |  __/
## \____/|_|\___|\___|\__|_|  \___/|_| |_| \____/ \___|\__,_|_|\___|
##                                                                 

    def electronScale(self):
        uncertaintyEB = electronUncertaintyEB
        uncertaintyEE = electronUncertaintyEE
        boundaryEBEE = 1.5
        if self.dataset == '2012' :
            uncertaintyEB = electronUncertaintyEB2012
            uncertaintyEE = electronUncertaintyEE2012
            boundaryEBEE = 2.0
        if self.direction == 'up':
            direction = self.strength
        if self.direction == 'down':
            direction = self.strength
        scaleEB = uncertaintyEB * direction
        scaleEE = uncertaintyEE * direction
                
        ## define a new branch
        self.defineVariables()
        
        nentries = self.nentries
        print 'total number of entries: '+str(nentries)
        i=0
        for ientry in xrange(0,nentries):
            i+=1
            self.oldttree.GetEntry(ientry)

            ## print event count
            step = 10000
            if i > 0 and i%step == 0:
                print str(i)+' events processed.'

            ## by default set all values to original tree
            self.getOriginalVariables()
                            
            # get the "old" lepton pt
            pt1_hold  = self.oldttree.pt1
            eta1_hold = self.oldttree.eta1
            phi1_hold = self.oldttree.phi1
            pt2_hold  = self.oldttree.pt2
            eta2_hold = self.oldttree.eta2
            phi2_hold = self.oldttree.phi2

            ## scale the lepton pt
            ## muon-muon channel
            ## dont scale at all
            if self.oldttree.channel == 0:
                self.pt1[0] = pt1_hold           ## do not scale electrons here  
                self.pt2[0] = pt2_hold           ## independent of "up" or "down"
            ## electron-electron channel    
            if self.oldttree.channel == 1:
                scale = direction * electronPtScale(pt1_hold, eta1_hold, self.dataset)
                if abs(self.oldttree.eta1) < boundaryEBEE:
                    scale += scaleEB
                if abs(self.oldttree.eta1) >= boundaryEBEE:
                    scale += scaleEE
                self.pt1[0] = pt1_hold + pt1_hold * scale

                scale = direction * electronPtScale(pt2_hold, eta2_hold, self.dataset)
                if abs(self.oldttree.eta2) < boundaryEBEE:
                    scale += scaleEB
                if abs(self.oldttree.eta2) >= boundaryEBEE:
                    scale += scaleEE
                self.pt2[0] = pt2_hold + pt2_hold * scale

            ## electron-muon channel
            if self.oldttree.channel == 2:
                scale = direction * electronPtScale(pt1_hold, eta1_hold, self.dataset)
                if abs(self.oldttree.eta1) < boundaryEBEE:
                    scale += scaleEB
                if abs(self.oldttree.eta1) >= boundaryEBEE:
                    scale += scaleEE
                self.pt1[0] = pt1_hold + pt1_hold * scale
                self.pt2[0] = pt2_hold

            ## muon-electron channel    
            if self.oldttree.channel == 3:
                self.pt1[0] = pt1_hold
                scale =direction * electronPtScale(pt2_hold, eta2_hold, self.dataset)
                if abs(self.oldttree.eta2) < boundaryEBEE:
                    scale += scaleEB
                if abs(self.oldttree.eta2) >= boundaryEBEE:
                    scale += scaleEE
                self.pt2[0] = pt2_hold + pt2_hold * scale
                

            
## FIXME: after the scaling one has to recalculate some variables
##        like invariant mass etc...
##        does delta phi, eta change? guess not...

            l1 = ROOT.TLorentzVector()
            l2 = ROOT.TLorentzVector()
            l1_hold = ROOT.TLorentzVector()
            l2_hold = ROOT.TLorentzVector()
            l1_hold.SetPtEtaPhiM(pt1_hold, eta1_hold, phi1_hold, 0)
            l2_hold.SetPtEtaPhiM(pt2_hold, eta2_hold, phi2_hold, 0)
            l1.SetPtEtaPhiM(self.pt1[0], eta1_hold, phi1_hold, 0)
            l2.SetPtEtaPhiM(self.pt2[0], eta2_hold, phi2_hold, 0)

            # recompute lepton variables
            self.computeLeptonVariables(l1, l2)

            # recompute met variables
            ## - pfmet
            met = ROOT.TLorentzVector()
            met.SetPtEtaPhiM(self.oldttree.pfmet, 0, self.oldttree.pfmetphi, 0)
            met = correctMet(met, l1_hold, l2_hold, l1, l2)
            self.pfmet[0] = met.Pt()
            self.pfmetphi[0] = met.Phi()
            ## - chmet
            chmet4 = ROOT.TLorentzVector()
            chmet4.SetPtEtaPhiM(self.oldttree.chmet, 0, self.oldttree.chmetphi, 0)
            chmet4 = correctMet(chmet4, l1_hold, l2_hold, l1, l2)
            self.chmet[0] = chmet4.Pt()
            self.chmetphi[0] = chmet4.Phi()
            ## ## - tcmet
            ## tcmet4 = ROOT.TLorentzVector()
            ## tcmet4.SetPtEtaPhiM(self.oldttree.tcmet, 0, self.oldttree.tcmetphi, 0)
            ## tcmet4 = correctMet(tcmet4, l1_hold, l2_hold, l1, l2)
            ## tcmet[0] = tcmet4.Pt()
            ## tcmetphi[0] = tcmet4.Phi()
            
            self.computeMETVariables(l1, l2, met, chmet4)

            if self.verbose is True:
                print '-----------------------------------'
                print 'event: '+str(i)
                print 'scale MB '+str(scaleMB)
                print 'scale ME '+str(scaleME)
                self.printVariables()
                
            # fill old and new values
            self.ttree.Fill()

        


###############################################################################################
##    ___      _     _____                              _____            _      
##   |_  |    | |   |  ___|                            /  ___|          | |     
##     | | ___| |_  | |__  _ __   ___ _ __ __ _ _   _  \ `--.  ___  __ _| | ___ 
##     | |/ _ \ __| |  __|| '_ \ / _ \ '__/ _` | | | |  `--. \/ __|/ _` | |/ _ \
## /\__/ /  __/ |_  | |___| | | |  __/ | | (_| | |_| | /\__/ / (__| (_| | |  __/
## \____/ \___|\__| \____/|_| |_|\___|_|  \__, |\__, | \____/ \___|\__,_|_|\___|
##                                         __/ | __/ |                          
##                                        |___/ |___/                           
##
    def jetEnergyScale(self):

        jetthreshold = 30.
        if self.direction == 'up':
            direction = self.strength
        if self.direction == 'down':
            direction = self.strength

        ## read the JES corrections
        jeu = []
        base_path = os.path.join(os.getenv('CMSSW_BASE'),'src/HWWAnalysis/ShapeAnalysis/data/')
        #file = open(base_path+'START38_V13_AK5PF_Uncertainty.txt')
        #file = open(base_path+'Fall12_V7_DATA_AK5PF_Uncertainty.txt')
        print self.dataset
        if   (self.dataset=='2012rereco') :
            file = open(base_path+'FT_53_V21_AN3_Uncertainty_AK5PF.txt')
        elif (self.dataset=='2012') :
            file = open(base_path+'START53_V15_Uncertainty_AK5PF.txt')
        elif (self.dataset=='2011') :
            file = open(base_path+'GR_R_42_V19_AK5PF_Uncertainty.txt')
        else :
            print 'dataset option has to be 2011, 2012 or 2012rereco'
            return  

        for line in file:
            if (line[0] == '#' or line[0] == '{'):
                continue
            s = line.split(None)
            #print s[0],s[1],s[2],s[3]
            #print s
            jeu.append(s)

        ## define a new branch
        self.defineVariables()
        
        nentries = self.nentries
        print 'total number of entries: '+str(nentries)
        i=0
        for ientry in xrange(0,nentries):
            i+=1
## FIXME: load tree envirenement like Chiara does?
##             j = loadTree(i)
##             if j < 0:
##                 break
            self.oldttree.GetEntry(ientry)

            ## print event count
            step = 10000
            if i > 0 and i%step == 0:
                print str(i)+' events processed.'

            ## by default set all values to original tree
            self.getOriginalVariables()
                            
            ## calculate the scaled pt
            scale1 = -1. ## a dummy value...
            scale2 = -1.
            scale3 = -1.
            scale4 = -1.

            ## get pt and eta of the jets
            jpt1  = self.oldttree.jetpt1
            jeta1 = self.oldttree.jeteta1
            jphi1 = self.oldttree.jetphi1
            jpt2  = self.oldttree.jetpt2
            jeta2 = self.oldttree.jeteta2
            jphi2 = self.oldttree.jetphi2

            cpt1  = self.oldttree.cjetpt1
            ceta1 = self.oldttree.cjeteta1
            cphi1 = self.oldttree.cjetphi1
            cpt2  = self.oldttree.cjetpt2
            ceta2 = self.oldttree.cjeteta2
            cphi2 = self.oldttree.cjetphi2

 

            ## get the scale factor - i.e. this is the relative uncertainty!
            scale1 = getJEUFactor(jpt1, jeta1, jeu) * direction
            scale2 = getJEUFactor(jpt2, jeta2, jeu) * direction
            cscale1 = getJEUFactor(cpt1, ceta1, jeu) * direction
            cscale2 = getJEUFactor(cpt2, ceta2, jeu) * direction


            # get the "old" jet pt
            jetpt1_hold = self.oldttree.jetpt1
            jetpt2_hold = self.oldttree.jetpt2
            cjetpt1_hold = self.oldttree.cjetpt1
            cjetpt2_hold = self.oldttree.cjetpt2

            ## do not scale "no jet"
            if jetpt1_hold < 0:
                scale1 = 0
            if jetpt2_hold < 0: 
                scale2 = 0
            if cjetpt1_hold < 0:
                cscale1 = 0
            if cjetpt2_hold < 0: 
                cscale2 = 0

            # scale the jet pt
            self.jetpt1[0] = jetpt1_hold + jetpt1_hold * scale1
            self.jetpt2[0] = jetpt2_hold + jetpt2_hold * scale2
            self.cjetpt1[0] = cjetpt1_hold + cjetpt1_hold * scale1
            self.cjetpt2[0] = cjetpt2_hold + cjetpt2_hold * scale2

##             print '---------------------'
##             print str(jetpt1_hold)+' -> '+str( jetpt1[0])
##             print str(jetpt2_hold)+' -> '+str( jetpt2[0])
            
            # calculate the number of jets
            # we only have bin migration, so check if a jet "walks" over the threshold
            # we can not gain a potential third jet!!
            # remind the vbf analysis people of that
##             n = self.oldttree.njet
##             if jetpt1_hold < jetthreshold and jetpt1[0] > jetthreshold:
##                 n+=1
##             if jetpt2_hold < jetthreshold and jetpt2[0] > jetthreshold:
##                 n+=1
##             if jetpt1_hold > jetthreshold and jetpt1[0] < jetthreshold:
##                 n-=1
##             if jetpt2_hold > jetthreshold and jetpt2[0] < jetthreshold:
##                 n-=1
##             njet[0] = n

            nJetOverThreshold = 0
            if self.jetpt1[0] > jetthreshold :
                nJetOverThreshold+=1
            if self.jetpt2[0] > jetthreshold :
                nJetOverThreshold+=1
            self.njet[0] = nJetOverThreshold

            # calculate the number of jets between tag jets (NB: no jet order inversion is considered!)
            newnjetvbf = 0
            if self.cjetpt1[0] > jetthreshold :
                newnjetvbf+=1
            if self.cjetpt2[0] > jetthreshold :
                newnjetvbf+=1
            self.njetvbf[0] = newnjetvbf


            ## set hardbdisc and soft...
            #if njet[0] == 2:
            #    hardbdisctche[0] = max(self.oldttree.jettche1, self.oldttree.jettche2)
            #if njet[0] == 1:
            #    hardbdiscrche[0] = self.oldttree.jettche1
            #    softbdisctche[0] = max(self.oldttree.jettche2, self.oldttree.softbdisc)
            #if njet[0] == 0:
            #    hardbdisctche[0] = -9999.9
            #    softbdisctche[0] = max(max(self.oldttree.jettche1, self.oldttree.jettche2),self.oldttree.softbdisc)
                
            
            ## correct MET
            ## get "old" and "new" jets as TLorentzVectors
            j1_hold = ROOT.TLorentzVector()
            j1_hold.SetPtEtaPhiM(0, 0, 0, 0) ## make sure that no jet is no jet
            j2_hold = ROOT.TLorentzVector()
            j2_hold.SetPtEtaPhiM(0, 0, 0, 0)
            j1 = ROOT.TLorentzVector()
            j1.SetPtEtaPhiM(0, 0, 0, 0)
            j2 = ROOT.TLorentzVector()
            j2.SetPtEtaPhiM(0, 0, 0, 0)

            j3_hold = ROOT.TLorentzVector()
            j3_hold.SetPtEtaPhiM(0, 0, 0, 0) ## make sure that no jet is no jet
            j4_hold = ROOT.TLorentzVector()
            j4_hold.SetPtEtaPhiM(0, 0, 0, 0)
            j3 = ROOT.TLorentzVector()
            j3.SetPtEtaPhiM(0, 0, 0, 0)
            j4 = ROOT.TLorentzVector()
            j4.SetPtEtaPhiM(0, 0, 0, 0)

            if jetpt1_hold > 0:
                j1_hold.SetPtEtaPhiM(jetpt1_hold, jeta1, jphi1, 0)
            if jetpt2_hold > 0:
                j2_hold.SetPtEtaPhiM(jetpt2_hold, jeta2, jphi2, 0)
            if self.jetpt1[0] > 0:
                j1.SetPtEtaPhiM(self.jetpt1[0], jeta1, jphi1, 0)
            if self.jetpt2[0] > 0:
                j2.SetPtEtaPhiM(self.jetpt2[0], jeta2, jphi2, 0)
            

            
            l1 = ROOT.TLorentzVector()
            l2 = ROOT.TLorentzVector()
            l1.SetPtEtaPhiM(self.oldttree.pt1, self.oldttree.eta1, self.oldttree.phi1, 0)
            l2.SetPtEtaPhiM(self.oldttree.pt2, self.oldttree.eta2, self.oldttree.phi2, 0)
            
            self.dphilljet[0] = deltaPhi(l1+l2,j1)
            self.dphilljetjet[0] =  deltaPhi(l1+l2,j1+j2)
            self.mjj[0] = invariantMass(j1,j2)

            if self.correctMETwithJES :
               ## PFMET:
               met = ROOT.TLorentzVector()
               met.SetPtEtaPhiM(self.oldttree.pfmet, 0, self.oldttree.pfmetphi, 0)           
               ## FIXME: cross-check this!!
               ## add "old jets" and subtract the "new" ones:
               #met = met + j1_hold - j1 + j2_hold - j2
               met = correctMet(met, j1_hold, j2_hold, j1, j2)
               met = correctMet(met, j3_hold, j4_hold, j3, j4)            
               ## substitute the values
               self.pfmet[0] = met.Pt()
               self.pfmetphi[0] = met.Phi()
               ## - chmet
               chmet4 = ROOT.TLorentzVector()
               chmet4.SetPtEtaPhiM(self.oldttree.chmet, 0, self.oldttree.chmetphi, 0)
               chmet4 = correctMet(chmet4, j1_hold, j2_hold, j1, j2)
               chmet4 = correctMet(chmet4, j3_hold, j4_hold, j3, j4)
               self.chmet[0] = chmet4.Pt()
               self.chmetphi[0] = chmet4.Phi()
               ## ## - tcmet
               ## tcmet4 = ROOT.TLorentzVector()
               ## tcmet4.SetPtEtaPhiM(self.oldttree.tcmet, 0, self.oldttree.tcmetphi, 0)
               ## tcmet4 = correctMet(tcmet4, j1_hold, j2_hold, j1, j2)
               ## tcmet4 = correctMet(tcmet4, j3_hold, j4_hold, j3, j4)
               ## tcmet[0] = tcmet4.Pt()
               ## tcmetphi[0] = tcmet4.Phi()  
               
               self.computeMETVariables(l1, l2, met, chmet4)


            if self.verbose is True:
                print '-----------------------------------'
                print 'event: '+str(i)
                print 'scale1: '+str(scale1)
                print 'scale2: '+str(scale2)
                self.printVariables()
                                                
            # fill old and new values            
            self.ttree.Fill()







###############################################################################################
## jet energy resolution, a.k.a. JER



    def jetEnergyResolution(self):

        ## define a new branch
        self.defineVariables()

        jetthreshold = 30.

        #nentries = self.ttree.GetEntriesFast()
        nentries = self.nentries
        print 'total number of entries: '+str(nentries)
        i=0
        for ientry in xrange(0,nentries):
            i+=1
            self.oldttree.GetEntry(ientry)
            ## print event count
            step = 10000
            if i > 0 and i%step == 0:
                print str(i)+' events processed.'

            ## by default set all values to original tree
            self.getOriginalVariables()

            nuisance = 0.
            if self.direction == 'up':
              nuisance = 1.
            if self.direction == 'down':
              nuisance = -1.
            ## get the variables
            tmp_jetpt1 = smearJet(self.oldttree.jetpt1,self.oldttree.jeteta1,nuisance)
            tmp_jetpt2 = smearJet(self.oldttree.jetpt2,self.oldttree.jeteta2,nuisance)

            # re-order the jets
            # FIXME
            # neglected as for the JES
            self.jetpt1[0] = tmp_jetpt1
            self.jetpt2[0] = tmp_jetpt2

            # fill new values
            #
            nJetOverThreshold = 0
            if self.jetpt1[0] > jetthreshold :
                nJetOverThreshold+=1
            if self.jetpt2[0] > jetthreshold :
                nJetOverThreshold+=1
            self.njet[0] = nJetOverThreshold
            # no more than 4 considered
            # calculate the number of jets between tag jets (NB: no jet order inversion is considered!)
            newnjetvbf = 0
            if self.cjetpt1[0] > jetthreshold :
                newnjetvbf+=1
            if self.cjetpt2[0] > jetthreshold :
                newnjetvbf+=1
            self.njetvbf[0] = newnjetvbf

            # fill old and new values
            self.ttree.Fill()






###############################################################################################
## met scale

    def metScale(self):

        # offset seen at ~1 GeV at MET = 20GeV and ~0.5 GeV at MET = 40 GeV
        metUncertainty = 1.0 # GeV
        if self.direction == 'up':
            direction = self.strength
        if self.direction == 'down':
            direction = self.strength
        scale = direction*metUncertainty

        ## define a new branch
        self.defineVariables()
        
        #nentries = self.ttree.GetEntriesFast()
        nentries = self.nentries
        print 'total number of entries: '+str(nentries)
        i=0
        for ientry in xrange(0,nentries):
            i+=1
            self.oldttree.GetEntry(ientry)
            ## print event count
            step = 10000
            if i > 0 and i%step == 0:
                print str(i)+' events processed.'
                
            ## by default set all values to original tree
            self.getOriginalVariables()
                            
            ## get the "old" met vector and smear px and py
            ## PFMET:
            met = ROOT.TLorentzVector()
            met.SetPtEtaPhiM(self.oldttree.pfmet, 0, self.oldttree.pfmetphi, 0)
            met.SetPtEtaPhiM(self.oldttree.pfmet+scale, 0, self.oldttree.pfmetphi, 0)
            ## CHMET:
            chmet4 = ROOT.TLorentzVector()
            chmet4.SetPtEtaPhiM(self.oldttree.chmet, 0, self.oldttree.chmetphi, 0)
            chmet4.SetPtEtaPhiM(self.oldttree.chmet+scale, 0, self.oldttree.chmetphi, 0)
            ## ## TCMET:
            ## tcmet4 = ROOT.TLorentzVector()
            ## tcmet4.SetPtEtaPhiM(self.oldttree.tcmet, 0, self.oldttree.tcmetphi, 0)
            ## tcmet4 = smearMET(tcmet4, sigma)
            
                
            ## get the variables
            self.pfmet[0] = met.Pt()
            self.pfmetphi[0] = met.Phi()
            self.chmet[0] = chmet4.Pt()
            self.chmetphi[0] = chmet4.Phi()
            ## self.tcmet[0] = tcmet4.Pt()
            ## self.tcmetphi[0] = tcmet4.Phi()

            l1 = ROOT.TLorentzVector()
            l2 = ROOT.TLorentzVector()
            l1.SetPtEtaPhiM(self.oldttree.pt1, self.oldttree.eta1, self.oldttree.phi1, 0)
            l2.SetPtEtaPhiM(self.oldttree.pt2, self.oldttree.eta2, self.oldttree.phi2, 0)

            self.computeMETVariables(l1, l2, met, chmet4)
                        
            if self.verbose is True:
                print '-----------------------------------'
                print 'event: '    +str(i)
                print 'scale: '    +str(scale)
                self.printVariables()
                    
                    
            # fill old and new values
            self.ttree.Fill()

                    
###############################################################################################
##  
## ___  ___ _____ _____  ______                _       _   _             
## |  \/  ||  ___|_   _| | ___ \              | |     | | (_)            
## | .  . || |__   | |   | |_/ /___  ___  ___ | |_   _| |_ _  ___  _ __  
## | |\/| ||  __|  | |   |    // _ \/ __|/ _ \| | | | | __| |/ _ \| '_ \ 
## | |  | || |___  | |   | |\ \  __/\__ \ (_) | | |_| | |_| | (_) | | | |
## \_|  |_/\____/  \_/   \_| \_\___||___/\___/|_|\__,_|\__|_|\___/|_| |_|
##    
##


    def metResolution(self):

        sigma = metSigma # for 2012 dataset, use 1 GeV

        ## define a new branch
        self.defineVariables()

        #nentries = self.ttree.GetEntriesFast()
        nentries = self.nentries
        print 'total number of entries: '+str(nentries)
        i=0
        for ientry in xrange(0,nentries):
            i+=1
            self.oldttree.GetEntry(ientry)
            ## print event count
            step = 10000
            if i > 0 and i%step == 0:
                print str(i)+' events processed.'
                

            ## by default set all values to original tree
            self.getOriginalVariables()
                            
            ## get the "old" met vector and smear px and py
            ## PFMET:
            met = ROOT.TLorentzVector()
            met.SetPtEtaPhiM(self.oldttree.pfmet, 0, self.oldttree.pfmetphi, 0)
            #if self.dataset == '2012' : sigma = 1./met.Pt()
            met = smearMET(met, sigma)
            ## CHMET:
            chmet4 = ROOT.TLorentzVector()
            chmet4.SetPtEtaPhiM(self.oldttree.chmet, 0, self.oldttree.chmetphi, 0)
            #if self.dataset == '2012' : sigma = 1./chmet4.Pt()
            chmet4 = smearMET(chmet4, sigma)
            ## ## TCMET:
            ## tcmet4 = ROOT.TLorentzVector()
            ## tcmet4.SetPtEtaPhiM(self.oldttree.tcmet, 0, self.oldttree.tcmetphi, 0)         
            ## tcmet4 = smearMET(tcmet4, sigma)


            ## get the variables
            self.pfmet[0] = met.Pt()
            self.pfmetphi[0] = met.Phi()
            self.chmet[0] = chmet4.Pt()
            self.chmetphi[0] = chmet4.Phi()
            ## self.tcmet[0] = tcmet4.Pt()
            ## self.tcmetphi[0] = tcmet4.Phi()

            l1 = ROOT.TLorentzVector()
            l2 = ROOT.TLorentzVector()
            l1.SetPtEtaPhiM(self.oldttree.pt1, self.oldttree.eta1, self.oldttree.phi1, 0)
            l2.SetPtEtaPhiM(self.oldttree.pt2, self.oldttree.eta2, self.oldttree.phi2, 0)

            self.computeMETVariables(l1, l2, met, chmet4)
            
            if self.verbose is True:
                print '-----------------------------------'
                print 'event: '+str(i)
                print 'sigma: '    +str(sigma)
                self.printVariables()


            # fill old and new values            
            self.ttree.Fill()


###############################################################################################
##      _     _____                    _       _       
##     | |   |_   _|                  | |     | |      
##   __| |_   _| | ___ _ __ ___  _ __ | | __ _| |_ ___ 
##  / _` | | | | |/ _ \ '_ ` _ \| '_ \| |/ _` | __/ _ \
## | (_| | |_| | |  __/ | | | | | |_) | | (_| | ||  __/
##  \__,_|\__, \_/\___|_| |_| |_| .__/|_|\__,_|\__\___|
##         __/ |                | |                    
##        |___/                 |_|                    


    def dyTemplate(self):

        ## define a new branch
        self.defineVariables()
        
        #nentries = self.ttree.GetEntriesFast()
        nentries = self.nentries
        print 'total number of entries: '+str(nentries)
        i=0
        for ientry in xrange(0,nentries):
            i+=1
            self.oldttree.GetEntry(ientry)
            ## print event count
            step = 10000
            if i > 0 and i%step == 0:
                print str(i)+' events processed.'

            ## by default set all values to original tree
            self.getOriginalVariables()
                            
            self.dyW[0]=1.
            self.dyWUp[0]=1.

            if self.oldttree.channel < 1.5:

                # reweighting as a function of ptll
                # preliminary (almost random) implementation for test
                ptll_temp = self.oldttree.ptll
                self.dyWUp[0] = 1.
                self.dyW[0]   = 1.1*ptll_temp*(1./400.)
            
                # get the "old" met
                pfmet_hold  = self.oldttree.pfmet
                chmet_hold  = self.oldttree.chmet
                ## tcmet_hold  = self.oldttree.tcmet

                self.pfmet[0] = pfmet_hold + 25 
                self.chmet[0] = chmet_hold + 25
                ## tcmet[0] = tcmet_hold + 25

                met = ROOT.TLorentzVector()
                met.SetPtEtaPhiM(self.pfmet[0], 0, self.oldttree.pfmetphi, 0)
                chmet4 = ROOT.TLorentzVector()
                chmet4.SetPtEtaPhiM(self.chmet[0], 0, self.oldttree.chmetphi, 0)
                ## tcmet4 = ROOT.TLorentzVector()
                ## tcmet4.SetPtEtaPhiM(tcmet[0], 0, self.oldttree.tcmetphi, 0)
                
                ## changing MET means also changing transverse masses...
                l1 = ROOT.TLorentzVector()
                l2 = ROOT.TLorentzVector()
                l1.SetPtEtaPhiM(self.oldttree.pt1, self.oldttree.eta1, self.oldttree.phi1, 0)
                l2.SetPtEtaPhiM(self.oldttree.pt2, self.oldttree.eta2, self.oldttree.phi2, 0)

                self.computeMETVariables(l1, l2, met, chmet4)            
                
                ## fix met related variables
                # get the "old" met
                ppfmet_hold  = self.oldttree.ppfmet
                pchmet_hold  = self.oldttree.pchmet
                ## ptcmet_hold  = self.oldttree.ptcmet
                self.ppfmet[0] = ppfmet_hold * (self.pfmet[0] / pfmet_hold)
                self.pchmet[0] = pchmet_hold * (self.chmet[0] / chmet_hold)
                ## self.ptcmet[0] = ptcmet_hold * (self.tcmet[0] / tcmet_hold)

                #self.mpmet[0] = min( self.ppfmet[0], self.pchmet[0] )
                self.mpmet_hold  = self.oldttree.mpmet
                self.mpmet[0] = mpmet_hold + 25;

                self.dymva0[0] = self.mpmet[0]>20;
                self.dymva1[0] = self.mpmet[0]>20;

            if self.verbose is True:
                print '-----------------------------------'
                print 'event: '+str(i)
                self.printVariables()
        

            # fill old and new values            
            self.ttree.Fill()







###############################################################################################
##
##   \  | _)         ___|  |                                                           |         |   _)
##  |\/ |  |   __|  |      __ \    _` |   __|  _` |   _ \       __|  _ \   __|   _ \   |  |   |  __|  |   _ \   __ \
##  |   |  | \__ \  |      | | |  (   |  |    (   |   __/      |     __/ \__ \  (   |  |  |   |  |    |  (   |  |   |
## _|  _| _| ____/ \____| _| |_| \__,_| _|   \__, | \___|     _|   \___| ____/ \___/  _| \__,_| \__| _| \___/  _|  _|
##                                           |___/
##
###############################################################################################

    def chargeResolution(self):

        ## define a new branch
        ch1 = numpy.zeros(1, dtype=numpy.float32)
        ch2 = numpy.zeros(1, dtype=numpy.float32)
        self.ttree.Branch('ch1',ch1,'ch1/F')
        self.ttree.Branch('ch2',ch2,'ch2/F')

        nentries = self.nentries
        print 'total number of entries: '+str(nentries)
        i=0
        for ientry in xrange(0,nentries):
            i+=1
            self.oldttree.GetEntry(ientry)

            ## print event count
            step = 10000
            if i > 0 and i%step == 0:
                print str(i)+' events processed.'

            ## muon-muon channel
            if self.oldttree.channel == 0:
               ch1[0] = self.oldttree.ch1 * smearCharge(sigmaChargeMuon)
               ch2[0] = self.oldttree.ch2 * smearCharge(sigmaChargeMuon)

            ## electron-muon electron
            if self.oldttree.channel == 1:
               if ( self.oldttree.pt1 < 30) :
                  if ( math.fabs(self.oldttree.eta1) < 1.5) :
                      ch1[0] = self.oldttree.ch1 * smearCharge(sigmaChargeElectron[0])
               if ( self.oldttree.pt1 >= 30 and self.oldttree.pt1 < 50) :
                  if ( math.fabs(self.oldttree.eta1) < 1.5) :
                      ch1[0] = self.oldttree.ch1 * smearCharge(sigmaChargeElectron[1])
               if ( self.oldttree.pt1 >= 50) :
                  if ( math.fabs(self.oldttree.eta1) < 1.5) :
                      ch1[0] = self.oldttree.ch1 * smearCharge(sigmaChargeElectron[2])
               if ( self.oldttree.pt1 < 30) :
                  if ( math.fabs(self.oldttree.eta1) >= 1.5) :
                      ch1[0] = self.oldttree.ch1 * smearCharge(sigmaChargeElectron[3])
               if ( self.oldttree.pt1 >= 30 and self.oldttree.pt1 < 50) :
                  if ( math.fabs(self.oldttree.eta1) >= 1.5) :
                      ch1[0] = self.oldttree.ch1 * smearCharge(sigmaChargeElectron[4])
               if ( self.oldttree.pt1 >= 50) :
                  if ( math.fabs(self.oldttree.eta1) >= 1.5) :
                      ch1[0] = self.oldttree.ch1 * smearCharge(sigmaChargeElectron[5])

               if ( self.oldttree.pt2 < 30) :
                  if ( math.fabs(self.oldttree.eta2) < 1.5) :
                      ch2[0] = self.oldttree.ch2 * smearCharge(sigmaChargeElectron[0])
               if ( self.oldttree.pt2 >= 30 and self.oldttree.pt2 < 50) :
                  if ( math.fabs(self.oldttree.eta2) < 1.5) :
                      ch2[0] = self.oldttree.ch2 * smearCharge(sigmaChargeElectron[1])
               if ( self.oldttree.pt2 >= 50) :
                  if ( math.fabs(self.oldttree.eta2) < 1.5) :
                      ch2[0] = self.oldttree.ch2 * smearCharge(sigmaChargeElectron[2])
               if ( self.oldttree.pt2 < 30) :
                  if ( math.fabs(self.oldttree.eta2) >= 1.5) :
                      ch2[0] = self.oldttree.ch2 * smearCharge(sigmaChargeElectron[3])
               if ( self.oldttree.pt2 >= 30 and self.oldttree.pt2 < 50) :
                  if ( math.fabs(self.oldttree.eta2) >= 1.5) :
                      ch2[0] = self.oldttree.ch2 * smearCharge(sigmaChargeElectron[4])
               if ( self.oldttree.pt2 >= 50) :
                  if ( math.fabs(self.oldttree.eta2) >= 1.5) :
                      ch2[0] = self.oldttree.ch2 * smearCharge(sigmaChargeElectron[5])

            ## electron-muon channel
            if self.oldttree.channel == 2:
               if ( self.oldttree.pt1 < 30) :
                  if ( math.fabs(self.oldttree.eta1) < 1.5) :
                      ch1[0] = self.oldttree.ch1 * smearCharge(sigmaChargeElectron[0])
               if ( self.oldttree.pt1 >= 30 and self.oldttree.pt1 < 50) :
                  if ( math.fabs(self.oldttree.eta1) < 1.5) :
                      ch1[0] = self.oldttree.ch1 * smearCharge(sigmaChargeElectron[1])
               if ( self.oldttree.pt1 >= 50) :
                  if ( math.fabs(self.oldttree.eta1) < 1.5) :
                      ch1[0] = self.oldttree.ch1 * smearCharge(sigmaChargeElectron[2])
               if ( self.oldttree.pt1 < 30) :
                  if ( math.fabs(self.oldttree.eta1) >= 1.5) :
                      ch1[0] = self.oldttree.ch1 * smearCharge(sigmaChargeElectron[3])
               if ( self.oldttree.pt1 >= 30 and self.oldttree.pt1 < 50) :
                  if ( math.fabs(self.oldttree.eta1) >= 1.5) :
                      ch1[0] = self.oldttree.ch1 * smearCharge(sigmaChargeElectron[4])
               if ( self.oldttree.pt1 >= 50) :
                  if ( math.fabs(self.oldttree.eta1) >= 1.5) :
                      ch1[0] = self.oldttree.ch1 * smearCharge(sigmaChargeElectron[5])
               ch2[0] = self.oldttree.ch2 * smearCharge(sigmaChargeMuon)

            ## muon-electron channel
            if self.oldttree.channel == 3:
               ch1[0] = self.oldttree.ch1 * smearCharge(sigmaChargeMuon)
               if ( self.oldttree.pt2 < 30) :
                  if ( math.fabs(self.oldttree.eta2) < 1.5) :
                      ch2[0] = self.oldttree.ch2 * smearCharge(sigmaChargeElectron[0])
               if ( self.oldttree.pt2 >= 30 and self.oldttree.pt2 < 50) :
                  if ( math.fabs(self.oldttree.eta2) < 1.5) :
                      ch2[0] = self.oldttree.ch2 * smearCharge(sigmaChargeElectron[1])
               if ( self.oldttree.pt2 >= 50) :
                  if ( math.fabs(self.oldttree.eta2) < 1.5) :
                      ch2[0] = self.oldttree.ch2 * smearCharge(sigmaChargeElectron[2])
               if ( self.oldttree.pt2 < 30) :
                  if ( math.fabs(self.oldttree.eta2) >= 1.5) :
                      ch2[0] = self.oldttree.ch2 * smearCharge(sigmaChargeElectron[3])
               if ( self.oldttree.pt2 >= 30 and self.oldttree.pt2 < 50) :
                  if ( math.fabs(self.oldttree.eta2) >= 1.5) :
                      ch2[0] = self.oldttree.ch2 * smearCharge(sigmaChargeElectron[4])
               if ( self.oldttree.pt2 >= 50) :
                  if ( math.fabs(self.oldttree.eta2) >= 1.5) :
                      ch2[0] = self.oldttree.ch2 * smearCharge(sigmaChargeElectron[5])


            # fill old and new values
            self.ttree.Fill()



###############################################################################################
# muon resolution

    def muonResolution(self):
        
        ## define a new branch
        self.defineVariables()
        
        nentries = self.nentries
        print 'total number of entries: '+str(nentries)
        i=0
        for ientry in xrange(0,nentries):
            i+=1
            self.oldttree.GetEntry(ientry)
            
            ## print event count
            step = 10000
            if i > 0 and i%step == 0:
                print str(i)+' events processed.'

            ## by default set all values to original tree
            self.getOriginalVariables()

            ## scale the lepton pt
            ## muon-muon channel
            ## dont scale at all
            if self.oldttree.channel == 0:
                self.pt1[0] = smearPt(self.oldttree.pt1,(0.00017*self.oldttree.pt1+0.002))
                self.pt2[0] = smearPt(self.oldttree.pt2,(0.00017*self.oldttree.pt1+0.002))
            ## electron-electron channel
            if self.oldttree.channel == 1:
                self.pt1[0] = self.oldttree.pt1                  ## do not scale electrons here
                self.pt2[0] = self.oldttree.pt2                  ## independent of "up" or "down"
            ## electron-muon channel
            if self.oldttree.channel == 2:
                self.pt1[0] = self.oldttree.pt1
                self.pt2[0] = smearPt(self.oldttree.pt2,(0.00017*self.oldttree.pt1+0.002))
            ## muon-electron channel
            if self.oldttree.channel == 3:
                self.pt1[0] = smearPt(self.oldttree.pt1,(0.00017*self.oldttree.pt1+0.002))
                self.pt2[0] = self.oldttree.pt2
                    
                    
## FIXME: after the scaling one has to recalculate some variables
##        like invariant mass etc...
##        does delta phi, eta change? guess not...

            l1 = ROOT.TLorentzVector()
            l2 = ROOT.TLorentzVector()
            l1_hold = ROOT.TLorentzVector()
            l2_hold = ROOT.TLorentzVector()
            l1_hold.SetPtEtaPhiM(self.oldttree.pt1, self.oldttree.eta1, self.oldttree.phi1, 0)
            l2_hold.SetPtEtaPhiM(self.oldttree.pt2, self.oldttree.eta2, self.oldttree.phi2, 0)
            l1.SetPtEtaPhiM(self.pt1[0], self.oldttree.eta1, self.oldttree.phi1, 0)
            l2.SetPtEtaPhiM(self.pt2[0], self.oldttree.eta2, self.oldttree.phi2, 0)

            # recompute lepton variables
            self.computeLeptonVariables(l1, l2)
            
            # recompute met variables
            ## - pfmet
            met = ROOT.TLorentzVector()
            met.SetPtEtaPhiM(self.oldttree.pfmet, 0, self.oldttree.pfmetphi, 0)
            met = correctMet(met, l1_hold, l2_hold, l1, l2)
            self.pfmet[0] = met.Pt()
            self.pfmetphi[0] = met.Phi()
            ## - chmet
            chmet4 = ROOT.TLorentzVector()
            chmet4.SetPtEtaPhiM(self.oldttree.chmet, 0, self.oldttree.chmetphi, 0)
            chmet4 = correctMet(chmet4, l1_hold, l2_hold, l1, l2)
            self.chmet[0] = chmet4.Pt()
            self.chmetphi[0] = chmet4.Phi()
            ## ## - tcmet
            ## tcmet4 = ROOT.TLorentzVector()
            ## tcmet4.SetPtEtaPhiM(self.oldttree.tcmet, 0, self.oldttree.tcmetphi, 0)
            ## tcmet4 = correctMet(tcmet4, l1_hold, l2_hold, l1, l2)
            ## self.tcmet[0] = tcmet4.Pt()
            ## self.tcmetphi[0] = tcmet4.Phi()
            
            self.computeMETVariables(l1, l2, met, chmet4)

            
            if self.verbose is True:
                print '-----------------------------------'
                print 'event: '+str(i)
                self.printVariables()
                
                
            # fill old and new values
            self.ttree.Fill()
                
                
        
###############################################################################################
##  _____ _           _                    ______                _       _   _             
## |  ___| |         | |                   | ___ \              | |     | | (_)            
## | |__ | | ___  ___| |_ _ __ ___  _ __   | |_/ /___  ___  ___ | |_   _| |_ _  ___  _ __  
## |  __|| |/ _ \/ __| __| '__/ _ \| '_ \  |    // _ \/ __|/ _ \| | | | | __| |/ _ \| '_ \ 
## | |___| |  __/ (__| |_| | | (_) | | | | | |\ \  __/\__ \ (_) | | |_| | |_| | (_) | | | |
## \____/|_|\___|\___|\__|_|  \___/|_| |_| \_| \_\___||___/\___/|_|\__,_|\__|_|\___/|_| |_|
##                                                                                       
##                                      

    def electronResolution(self):
        
        sigmaEB = electronSigmaEB
        sigmaET = electronSigmaEE
        sigmaEE = 0.
        boundary1 = 1.5
        boundary2 = 5.0
        if self.dataset == '2012' :
            sigmaEB = electronSigmaEB2012
            sigmaET = electronSigmaET2012
            sigmaEE = electronSigmaEE2012
            boundary1 = 1.0
            boundary2 = 2.0

        ## define a new branch
        self.defineVariables()
        
        nentries = self.nentries
        print 'total number of entries: '+str(nentries)
        i=0
        for ientry in xrange(0,nentries):
            i+=1
            self.oldttree.GetEntry(ientry)

            ## print event count
            step = 10000
            if i > 0 and i%step == 0:
                print str(i)+' events processed.'

            ## by default set all values to original tree
            self.getOriginalVariables()

            ## scale the lepton pt
            ## muon-muon channel
            ## dont scale at all
            if self.oldttree.channel == 0:
                self.pt1[0] = self.oldttree.pt1                  ## do not scale electrons here  
                self.pt2[0] = self.oldttree.pt2                  ## independent of "up" or "down"
            ## electron-electron channel    
            if self.oldttree.channel == 1:
                if   abs(self.oldttree.eta1) < boundary1:
                    self.pt1[0] = smearPt(self.oldttree.pt1,sigmaEB)
                elif abs(self.oldttree.eta1) < boundary2:
                    self.pt1[0] = smearPt(self.oldttree.pt1,sigmaET)
                elif abs(self.oldttree.eta1) >= boundary2:
                    self.pt1[0] = smearPt(self.oldttree.pt1,sigmaEE)
                if   abs(self.oldttree.eta2) < boundary1:
                    self.pt2[0] = smearPt(self.oldttree.pt2,sigmaEB)
                elif abs(self.oldttree.eta2) < boundary2:
                    self.pt2[0] = smearPt(self.oldttree.pt2,sigmaET)
                elif abs(self.oldttree.eta2) >= boundary2:
                    self.pt2[0] = smearPt(self.oldttree.pt2,sigmaEE)
                                        
            ## electron-muon channel
            if self.oldttree.channel == 2:
                if   abs(self.oldttree.eta1) < boundary1:
                    self.pt1[0] = smearPt(self.oldttree.pt1,sigmaEB)
                elif abs(self.oldttree.eta1) < boundary2:
                    self.pt1[0] = smearPt(self.oldttree.pt1,sigmaET)
                elif abs(self.oldttree.eta1) >= boundary2:
                    self.pt1[0] = smearPt(self.oldttree.pt1,sigmaEE)
                self.pt2[0] = self.oldttree.pt2
            ## muon-electron channel    
            if self.oldttree.channel == 3:
                self.pt1[0] = self.oldttree.pt1
                if   abs(self.oldttree.eta2) < boundary1:
                    self.pt2[0] = smearPt(self.oldttree.pt2,sigmaEB)
                elif abs(self.oldttree.eta2) < boundary2:
                    self.pt2[0] = smearPt(self.oldttree.pt2,sigmaET)
                elif abs(self.oldttree.eta2) >= boundary2:
                    self.pt2[0] = smearPt(self.oldttree.pt2,sigmaEE)

        
## FIXME: after the scaling one has to recalculate some variables
##        like invariant mass etc...
##        does delta phi, eta change? guess not...

            l1 = ROOT.TLorentzVector()
            l2 = ROOT.TLorentzVector()
            l1_hold = ROOT.TLorentzVector()
            l2_hold = ROOT.TLorentzVector()
            l1_hold.SetPtEtaPhiM(self.oldttree.pt1, self.oldttree.eta1, self.oldttree.phi1, 0)
            l2_hold.SetPtEtaPhiM(self.oldttree.pt2, self.oldttree.eta2, self.oldttree.phi2, 0)
            l1.SetPtEtaPhiM(self.pt1[0], self.oldttree.eta1, self.oldttree.phi1, 0)
            l2.SetPtEtaPhiM(self.pt2[0], self.oldttree.eta2, self.oldttree.phi2, 0)

            # recompute lepton variables
            self.computeLeptonVariables(l1, l2)

            # recompute met variables
            ## - pfmet
            met = ROOT.TLorentzVector()
            met.SetPtEtaPhiM(self.oldttree.pfmet, 0, self.oldttree.pfmetphi, 0)
            met = correctMet(met, l1_hold, l2_hold, l1, l2)
            self.pfmet[0] = met.Pt()
            self.pfmetphi[0] = met.Phi()
            ## - chmet
            chmet4 = ROOT.TLorentzVector()
            chmet4.SetPtEtaPhiM(self.oldttree.chmet, 0, self.oldttree.chmetphi, 0)
            chmet4 = correctMet(chmet4, l1_hold, l2_hold, l1, l2)
            self.chmet[0] = chmet4.Pt()
            self.chmetphi[0] = chmet4.Phi()
            ## ## - tcmet
            ## tcmet4 = ROOT.TLorentzVector()
            ## tcmet4.SetPtEtaPhiM(self.oldttree.tcmet, 0, self.oldttree.tcmetphi, 0)
            ## tcmet4 = correctMet(tcmet4, l1_hold, l2_hold, l1, l2)
            ## self.tcmet[0] = tcmet4.Pt()
            ## self.tcmetphi[0] = tcmet4.Phi()
            
            self.computeMETVariables(l1, l2, met, chmet4)

            if self.verbose is True:
                print '-----------------------------------'
                print 'event: '+str(i)
                print 'sigmaEB: '+str(sigmaEB)
                print 'sigmaET: '+str(sigmaET)
                print 'sigmaEE: '+str(sigmaEE)
                self.printVariables()

            # fill old and new values
            self.ttree.Fill()
                

###############################################################################################
##  _                 _                 _____  __  __ _      _                 _          
## | |               | |               |  ___|/ _|/ _(_)    (_)               (_)         
## | |      ___ _ __ | |_  ___  _ __   | |__ | |_| |_ _  ___ _  ___ _ __   ___ _  ___ ___ 
## | |     / _ \ '_ \| __|/ _ \| '_ \  |  __||  _|  _| |/ __| |/ _ \ '_ \ / __| |/ _ | __|
## | |____|  __/ |_) | |_| (_) | | | | | |___| | | | | | (__| |  __/ | | | (__| |  __|__ \
## \_____/ \___| .__/ \__|\___/|_| |_| \____/|_| |_| |_|\___|_|\___|_| |_|\___|_|\___|___/
##             | |                                                                        
##             |_|                                                                        
##
    def leptonEfficiency(self):
        print 'lepton efficiency'

        effW = numpy.zeros(1, dtype=numpy.float32)
        effAW = numpy.zeros(1, dtype=numpy.float32)
        effBW = numpy.zeros(1, dtype=numpy.float32)
        self.ttree.Branch('effW',effW,'effW/F')
        self.ttree.Branch('effAW',effAW,'effAW/F')
        self.ttree.Branch('effBW',effBW,'effBW/F')

## this are the 1stNov efficiency weights:
        base_path = os.path.join(os.getenv('CMSSW_BASE'),'src/HWWAnalysis/ShapeAnalysis/data/')
##         base_path = '/shome/jueugste/HWWSystematics/leptonEfficiencies/'
##         mA_path = base_path+'OutputScaleFactorMap_Run2011AData_vs_42XMC.root'
##         mB_path = base_path+'OutputScaleFactorMap_Run2011BData_vs_42XMC.root'
##         eA_path = base_path+'OutputScaleFactorMap_DATA_Run2011A_MC_42X_BDTID.root'
##         eB_path = base_path+'OutputScaleFactorMap_DATA_Run2011B_MC_42X_BDTID.root'
        mA_path = base_path+'m_OutputScaleFactorMap_MC42X_2011AReweighted.root'
        mB_path = base_path+'m_OutputScaleFactorMap_MC42X_2011BReweighted.root'
        eA_path = base_path+'e_OutputScaleFactorMap_MC42X_2011AReweighted.root'
        eB_path = base_path+'e_OutputScaleFactorMap_MC42X_2011BReweighted.root'
        lumiA = 2.118
        #lumiB = 1.841
        lumiB = 2.511

        
##         # open the root files containing the weights and errors...
##         base_path = '/shome/jueugste/HWWSystematics/leptonEfficiencies/'
## ##         m_path = base_path+'Muons_vpvPlusExpo_OutputScaleFactorMap.root'
##         m_path = base_path+'OutputScaleFactorMap_MuonEfficiencies_DataRun2011A_vs_MC42X.root'
## ##        m_path = base_path+'AbsEta-Pt_Histrogram_2011AData_MuonPRcenario2_MAP.root'
## ##         e_path = base_path+'Electrons_vpvPlusExpo_OutputScaleFactorMap.root'
##         e_path = base_path+'electronEff_CutID_SFmap_Run2011A.root'
## ##        e_path = base_path+'OutputScaleFactorMap_Scenario4_BDTElectrons_Run2011A_MC42X.root'


        fA_muon = openTFile(mA_path)
        fB_muon = openTFile(mB_path)
        fA_ele  = openTFile(eA_path)
        fB_ele  = openTFile(eB_path)
##         f_muon = openTFile(m_path)
##         f_ele  = openTFile(e_path)
        hA_muon = getHist(fA_muon,'hScaleFactorMap')
        hB_muon = getHist(fB_muon,'hScaleFactorMap')
        hA_ele  = getHist(fA_ele,'hScaleFactorMap')
        hB_ele  = getHist(fB_ele,'hScaleFactorMap')
##         h_muon = getHist(f_muon,'hScaleFactorMap')
##         h_ele  = getHist(f_ele,'pt_abseta_PLOT')

        nentries = self.nentries
        print 'total number of entries: '+str(nentries)
        i = 0
        for ientry in xrange(0,nentries):
            i+=1
            self.oldttree.GetEntry(ientry)

            ## print event count
            step = 10000
            if i > 0 and i%step == 0.:
                print str(i)+' events processed.'

            # get the bin coordinates
            cpt1 = 1
            cpt2 = 1
            ceta1 = 1
            ceta2 = 1
            lpt1 = self.oldttree.pt1
            lpt2 = self.oldttree.pt2
            leta1 = self.oldttree.eta1
            leta2 = self.oldttree.eta2
            if lpt1 < 15:
                cpt1 = 1
            if lpt1 >= 15 and lpt1 < 20:
                cpt1 = 2
            if lpt1 >= 20 and lpt1 < 50:
                cpt1 = 3
            if lpt1 >= 50:
                cpt1 = 4
            if lpt2 < 15:
                cpt2 = 1
            if lpt2 >= 15 and lpt2 < 20:
                cpt2 = 2
            if lpt2 >= 20 and lpt2 < 50:
                cpt2 = 3
            if lpt2 >= 50:
                cpt2 = 4
            if abs(leta1) > 1.48:
                ceta1 = 2
            if abs(leta2) > 1.48:
                ceta2 = 2

            ## muon-muon channel
            if self.oldttree.channel == 0:
                valA1 = hA_muon.GetBinContent(cpt1,ceta1)
                valA2 = hA_muon.GetBinContent(cpt2,ceta2)
                errA1 = hA_muon.GetBinError(cpt1,ceta1)
                errA2 = hA_muon.GetBinError(cpt2,ceta2)

                valB1 = hB_muon.GetBinContent(cpt1,ceta1)
                valB2 = hB_muon.GetBinContent(cpt2,ceta2)
                errB1 = hB_muon.GetBinError(cpt1,ceta1)
                errB2 = hB_muon.GetBinError(cpt2,ceta2)
##                 val1 = h_muon.GetBinContent(cpt1,ceta1)
##                 val2 = h_muon.GetBinContent(cpt2,ceta2)
##                 err1 = h_muon.GetBinError(cpt1,ceta1)
##                 err2 = h_muon.GetBinError(cpt2,ceta2)

            ## electron-electron channel    
            if self.oldttree.channel == 1:
                if lpt1 < 15:
                    cpt1 = 1
                if lpt1 >= 15 and lpt1 < 20:
                    cpt1 = 2
                if lpt1 >= 20 and lpt1 < 25:
                    cpt1 = 3
                if lpt1 >= 25 and lpt1 < 50:
                    cpt1 = 4
                if lpt1 >= 50:
                    cpt1 = 5
                if lpt2 < 15:
                    cpt2 = 1
                if lpt2 >= 15 and lpt2 < 20:
                    cpt2 = 2
                if lpt2 >= 20 and lpt2 < 25:
                    cpt2 = 3
                if lpt2 >= 25 and lpt2 < 50:
                    cpt2 = 4
                if lpt2 >= 50:
                    cpt2 = 5
                if abs(leta1) <= 1.4442:
                    ceta1 = 1
                if abs(leta1) > 1.4442 and abs(leta1) <1.556:
                    ceta1 = 2
                if abs(leta1) >= 1.556:
                    ceta1 = 3
                if abs(leta2) <= 1.4442:
                    ceta2 = 1
                if abs(leta2) > 1.4442 and abs(leta2) <1.556:
                    ceta2 = 2
                if abs(leta2) >= 1.556:
                    ceta2 = 3
                
                valA1 = hA_ele.GetBinContent(cpt1,ceta1)
                valA2 = hA_ele.GetBinContent(cpt2,ceta2)
                errA1 = hA_ele.GetBinError(cpt1,ceta1)
                errA2 = hA_ele.GetBinError(cpt2,ceta2)

                valB1 = hB_ele.GetBinContent(cpt1,ceta1)
                valB2 = hB_ele.GetBinContent(cpt2,ceta2)
                errB1 = hB_ele.GetBinError(cpt1,ceta1)
                errB2 = hB_ele.GetBinError(cpt2,ceta2)

##                 val1 = h_ele.GetBinContent(cpt1,ceta1)
##                 val2 = h_ele.GetBinContent(cpt2,ceta2)
##                 err1 = h_ele.GetBinError(cpt1,ceta1)
##                 err2 = h_ele.GetBinError(cpt2,ceta2)

            ## electron-muon channel
            if self.oldttree.channel == 2:
                if lpt1 < 15:
                    cpt1 = 1
                if lpt1 >= 15 and lpt1 < 20:
                    cpt1 = 2
                if lpt1 >= 20 and lpt1 < 25:
                    cpt1 = 3
                if lpt1 >= 25 and lpt1 < 50:
                    cpt1 = 4
                if lpt1 >= 50:
                    cpt1 = 5
                if abs(leta1) <= 1.4442:
                    ceta1 = 1
                if abs(leta1) > 1.4442 and abs(leta1) <1.556:
                    ceta1 = 2
                if abs(leta1) >= 1.556:
                    ceta1 = 3

                valA1 = hA_ele.GetBinContent(cpt1,ceta1)
                valA2 = hA_muon.GetBinContent(cpt2,ceta2)
                errA1 = hA_ele.GetBinError(cpt1,ceta1)
                errA2 = hA_muon.GetBinError(cpt2,ceta2)

                valB1 = hB_ele.GetBinContent(cpt1,ceta1)
                valB2 = hB_muon.GetBinContent(cpt2,ceta2)
                errB1 = hB_ele.GetBinError(cpt1,ceta1)
                errB2 = hB_muon.GetBinError(cpt2,ceta2)

##                 val1 = h_ele.GetBinContent(cpt1,ceta1)
##                 val2 = h_muon.GetBinContent(cpt2,ceta2)
##                 err1 = h_ele.GetBinError(cpt1,ceta1)
##                 err2 = h_muon.GetBinError(cpt2,ceta2)

            ## muon-electron channel    
            if self.oldttree.channel == 3:
                if lpt2 < 15:
                    cpt2 = 1
                if lpt2 >= 15 and lpt2 < 20:
                    cpt2 = 2
                if lpt2 >= 20 and lpt2 < 25:
                    cpt2 = 3
                if lpt2 >= 25 and lpt2 < 50:
                    cpt2 = 4
                if lpt2 >= 50:
                    cpt2 = 5
                if abs(leta2) <= 1.4442:
                    ceta2 = 1
                if abs(leta2) > 1.4442 and abs(leta2) <1.556:
                    ceta2 = 2
                if abs(leta2) >= 1.556:
                    ceta2 = 3
                    
                valA1 = hA_muon.GetBinContent(cpt1,ceta1)
                valA2 = hA_ele.GetBinContent(cpt2,ceta2)
                errA1 = hA_muon.GetBinError(cpt1,ceta1)
                errA2 = hA_ele.GetBinError(cpt2,ceta2)

                valB1 = hB_muon.GetBinContent(cpt1,ceta1)
                valB2 = hB_ele.GetBinContent(cpt2,ceta2)
                errB1 = hB_muon.GetBinError(cpt1,ceta1)
                errB2 = hB_ele.GetBinError(cpt2,ceta2)

                ## constrain the error from wild values...
                if errA1 > 0.03:
                    errA1 = 0.03
                if errA2 > 0.03:
                    errA2 = 0.03
                if errB1 > 0.03:
                    errB1 = 0.03
                if errB2 > 0.03:
                    errB2 = 0.03
                ## ... and set the lower limit to 1%
                if errA1 < 0.01:
                    errA1 = 0.01
                if errA2 < 0.01:
                    errA2 = 0.01
                if errB1 < 0.01:
                    errB1 = 0.01
                if errB2 < 0.01:
                    errB2 = 0.01
                    
##                 val1 = h_muon.GetBinContent(cpt1,ceta1)
##                 val2 = h_ele.GetBinContent(cpt2,ceta2)
##                 err1 = h_muon.GetBinError(cpt1,ceta1)
##                 err2 = h_ele.GetBinError(cpt2,ceta2)

            ## add the statistical error
            ##effW_sup = (val1+err2)*(val2+err2)
            ##effW_sdown = (val1-err2)*(val2-err2)
            effAW_sup = (valA1+errA1)*(valA2+errA2)
            effAW_sdown = (valA1-errA1)*(valA2-errA2)

            effBW_sup = (valB1+errB1)*(valB2+errB2)
            effBW_sdown = (valB1-errB1)*(valB2-errB2)

            effW_sup   = (effAW_sup*lumiA + effBW_sup*lumiB) / (lumiA + lumiB)
            effW_sdown = (effAW_sdown*lumiA + effBW_sdown*lumiB) / (lumiA + lumiB) 

##             ## just replace the "old" value with the one from the root files
##             ##effW_sup   = val1*val2
##             ##effW_sdown = val1*val2
##             effAW_sup   = valA1*valA2
##             effAW_sdown = valA1*valA2
##             effBW_sup   = valB1*valB2
##             effBW_sdown = valB1*valB2

##             effW_sup   = (effAW_sup*lumiA + effBW_sup*lumiB) / (lumiA + lumiB)
##             effW_sdown = (effAW_sdown*lumiA + effBW_sdown*lumiB) / (lumiA + lumiB) 


##Some printouts to check that I am doing the right thing...        
#             print '------------------------'
#             print self.oldttree.channel
#             print lpt1, leta1, valA1, valB1,'\n' 
#             print lpt2, leta2, valA2, valB2,'\n' 
#             print 'err1: ', errA1, errB1
#             print 'err2: ', errA2, errB2


##             #print 'up  : '+str(effW_sup)
##             print 'val : '+str(val1*val2)
##             #print 'down: '+str(effW_sdown)
##             print 'effW: '+str(self.oldttree.effW)
            
            if self.direction == 'up':
                effAW[0] = effAW_sup
                effBW[0] = effBW_sup
                effW[0] = effW_sup
            if self.direction == 'down':
                effAW[0] = effAW_sdown
                effBW[0] = effBW_sdown
                effW[0] = effW_sdown

#             print effAW_sup, effAW_sdown
#             print effBW_sup, effBW_sdown

#             print effW[4], effAW[0], effBW[0]

##            print self.direction+' : '+str(effW[0])
            # fill old and new values
            self.ttree.Fill()

    def addOptions(self,parser):
        parser.add_option('-i', '--inputFileName',      dest='inputFileName',   help='Name of the input *.root file.',)
        parser.add_option('-o', '--outputFileName',     dest='outputFileName',  help='Name of the output *.root file.',)
        parser.add_option('-a', '--systematicArgument', dest='systArgument',    help='Argument to specify systematic (possible arguments are: "muonScale","electronScale","leptonEfficiency","jetEnergyScale","metScale","metResolution","muonResolution","electronResolution","dyTemplate","puVariation","chargeResolution",)',)
        parser.add_option('-v', '--variation',          dest='variation',       help='Direction of the scale variation ("up"/"down") or type of DY template ("temp"/"syst"), works only in combination with "-a dyTemplate". In the case of "metResolution" and "muonResolution" and "electronResolution" and "chargeResolution" this is ommitted.',)
        parser.add_option('-t', '--treeDir',            dest='treeDir',         help='TDirectry structure to the tree to scale and smear.',)
        #    parser.add_option('-n', '--nEvents',           dest='nEvents',         help='Number of events to run over',)
        parser.add_option('-d', '--debug',              dest='debug',           help='Switch to debug mode',default=False, action='store_true')



###############################################################################################
##                  _       
##                 (_)      
##  _ __ ___   __ _ _ _ __  
## | '_ ` _ \ / _` | | '_ \ 
## | | | | | | (_| | | | | |
## |_| |_| |_|\__,_|_|_| |_|
##                         
def main():
    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(usage)
    
    parser.set_defaults(overwrite=False)
    
    parser.add_option('-i', '--inputFileName',      dest='inputFileName',   help='Name of the input *.root file.',)
    parser.add_option('-o', '--outputFileName',     dest='outputFileName',  help='Name of the output *.root file.',)
    parser.add_option('-a', '--systematicArgument', dest='systArgument',    help='Argument to specify systematic (possible arguments are: "muonScale","electronScale","leptonEfficiency","jetEnergyScale","metScale","metResolution","muonResolution","electronResolution","dyTemplate","puVariation","chargeResolution",)',)
    parser.add_option('-v', '--variation',          dest='variation',       help='Direction of the scale variation ("up"/"down") or type of DY template ("temp"/"syst"), works only in combination with "-a dyTemplate". In the case of "metResolution" and "muonResolution" and "electronResolution" and "chargeResolution" this is ommitted.',)
    parser.add_option('-s', '--strength',           dest='strength',  type="float",    help='Intensity of the scale variation (1 = "up", -1 = "down", 0.5, 0.6, ...)', default=-99.)
    parser.add_option('-t', '--treeDir',            dest='treeDir',         help='TDirectry structure to the tree to scale and smear.',default="latino")
#    parser.add_option('-n', '--nEvents',           dest='nEvents',         help='Number of events to run over',)
    parser.add_option('-y', '--dataset',            dest='dataset',         help='dataset: 2011, 2012 or 2012rereco', default='2012')
    parser.add_option('-d', '--debug',              dest='debug',           help='Switch to debug mode',default=False, action='store_true')


    (opt, args) = parser.parse_args()

    if opt.inputFileName is None:
        parser.error('No input file defined')
    if opt.outputFileName is None:
        parser.error('No output file defined')
    if opt.systArgument is None:
        parser.error('No systematic argument given')
    possibleSystArguments = ['muonScale','electronScale','leptonEfficiency','jetEnergyScale','jetEnergyResolution','metScale','metResolution','muonResolution','electronResolution','dyTemplate','puVariation','chargeResolution']
    if opt.systArgument not in possibleSystArguments:
        parser.error('Wrong systematic argument')        
    possibleDirections = ['up','down','temp','syst']
    needdir = ["muonScale","electronScale","leptonEfficiency","jetEnergyScale","metScale","dyTemplate","puVariation"]
    if opt.systArgument in needdir and opt.variation not in possibleDirections:
        parser.error('No direction of the systematic variation given')
    if opt.treeDir is None:
        parser.error('No path to the tree specyfied')
    if opt.systArgument == 'dyTemplate' and opt.variation not in ['temp','syst']:
        parser.error('template and syst only allowed for dyTemplate')
    if opt.systArgument == 'dyTemplate' and opt.variation in ['up','down']:
        parser.error('"up" or "down" not allowed for "dyTemplate"')

#    verbose = opt.debug

##     sys.argv.append('-b')
##     ROOT.gROOT.SetBatch()

    s = scaleAndSmear()
    s.inputFileName = opt.inputFileName
    s.outputFileName = opt.outputFileName
    s.treeDir = opt.treeDir
    s.systArgument = opt.systArgument
    s.direction = opt.variation
    s.strength = opt.strength
    s.verbose = opt.debug
    s.dataset = opt.dataset

    if s.strength == -99.:
      if s.direction == 'up':
        s.strength = 1.
      if s.direction == 'down':
        s.strength = -1.

    print s.systArgument
    print s.strength

    s.openOriginalTFile()
    s.openOutputTFile()
    s.cloneTree()

    # dymva
    s.createDYMVA()

    if s.systArgument == 'muonScale':
        s.muonScale()
    if s.systArgument == 'electronScale':
        s.electronScale()
    if s.systArgument == 'leptonEfficiency':
        s.leptonEfficiency()
    if s.systArgument == 'jetEnergyScale':
        s.jetEnergyScale()
    if s.systArgument == 'jetEnergyResolution':
        s.jetEnergyResolution()
    if s.systArgument == 'metScale':
        s.metScale()
    if s.systArgument == 'metResolution':
        s.metResolution()
    if s.systArgument == 'muonResolution':
        s.muonResolution()
    if s.systArgument == 'electronResolution':
        s.electronResolution()
    if s.systArgument == 'dyTemplate':
        s.dyTemplate()
    if s.systArgument == 'puVariation':
        s.puVariation()
    if s.systArgument == 'chargeResolution':
        s.chargeResolution()
    
    print 'Job finished...'


if __name__ == '__main__':
    main()
