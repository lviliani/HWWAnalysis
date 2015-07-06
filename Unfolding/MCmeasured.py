#!/usr/bin/env python

from ROOT import *
from array import *
from math import *

lumi = 19.468

base="/afs/cern.ch/work/l/lviliani/DatacardFramework/CMSSW_7_1_5/src/Unfolding/"

sample_ggH="latino_1125_ggToH125toWWTo2LAndTau2Nu.root"
sample_VBF="latino_2125_vbfToH125toWWTo2LAndTau2Nu.root"
sample_WZH="latino_3125_wzttH125ToWW.root"

pthbins = array("d",[0,15,45,85,125,165,200])

chain = TChain("latino")
chain.Add(base+"samples/nominals/"+sample_ggH)
chain.Add(base+"samples/nominals/"+sample_VBF)
chain.Add(base+"samples/nominals/"+sample_WZH)

hMeas = TH1F("hMeas ","pTH RECO ",len(pthbins)-1,pthbins)

# Start loop
iEvt=0
for e in chain :
  iEvt+=1
#   if iEvt==1000 : break
  if iEvt%10000==0 : 
    print "Event ",iEvt
    
  pTH_reco = sqrt( (e.pt1*cos(e.phi1)+e.pt2*cos(e.phi2)+e.pfmet*cos(e.pfmetphi))**2 + (e.pt1*sin(e.phi1)+e.pt2*sin(e.phi2)+e.pfmet*sin(e.pfmetphi))**2 )

  # Generated Higgs transverse momentum
  pTH_gen = sqrt( (e.leptonGenpt1*cos(e.leptonGenphi1)+e.leptonGenpt2*cos(e.leptonGenphi2)+e.neutrinoGenpt1*cos(e.neutrinoGenphi1)+e.neutrinoGenpt2*cos(e.neutrinoGenphi2))**2 + (e.leptonGenpt1*sin(e.leptonGenphi1)+e.leptonGenpt2*sin(e.leptonGenphi2)+e.neutrinoGenpt1*sin(e.neutrinoGenphi1)+e.neutrinoGenpt2*sin(e.neutrinoGenphi2))**2  )  

  pT_nn = sqrt((((e.neutrinoGenpt1*cos(e.neutrinoGenphi1))+(e.neutrinoGenpt2*cos(e.neutrinoGenphi2)))*((e.neutrinoGenpt1*cos(e.neutrinoGenphi1))+(e.neutrinoGenpt2*cos(e.neutrinoGenphi2))))+(((e.neutrinoGenpt1*sin(e.neutrinoGenphi1))+(e.neutrinoGenpt2*sin(e.neutrinoGenphi2)))*((e.neutrinoGenpt1*sin(e.neutrinoGenphi1))+(e.neutrinoGenpt2*sin(e.neutrinoGenphi2)))))

      ### Analysis selection
  if ( ((e.ptll>30 and e.mth>60 and e.mth<280 and e.mll<200 and e.trigger==1. and e.pfmet>20. and e.mll>12 and e.mpmet>20. and e.nextra==0 and e.pt1>20 and e.pt2>10 and ((e.ch1)*(e.ch2))<0 and (e.zveto==1 or (not e.sameflav)) and (e.njet==0 or e.njet==1 or (e.dphilljetjet<3.14/180.*165. or (not e.sameflav) ) ) and ( (not e.sameflav) or ( ( e.njet!=0 or e.dymva1>0.88 or e.mpmet>35) and (e.njet!=1 or e.dymva1>0.84 or e.mpmet>35) and ( e.njet==0 or e.njet==1 or (e.pfmet > 45.0)) ) ))and((not e.sameflav) and (((( e.jetbjpb1<1.4 or e.jetpt1<30) and ( e.jetbjpb2<1.4 or e.jetpt2<30) and ( e.jetbjpb3<1.4 or e.jetpt3<30) and ( e.jetbjpb4<1.4 or e.jetpt4<30)) and e.njet>0) or (e.bveto_mu==1 and e.bveto_ip==1 and e.njet==0))))  ):
    hMeas.Fill(min(pTH_reco,167.),e.puW*e.effW*e.triggW*e.baseW*lumi)

file_out = TFile("TheMeasure.root","recreate")
file_out.cd()
hMeas.Write()
file_out.Close()

