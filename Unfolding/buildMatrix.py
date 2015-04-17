#!/usr/bin/env python

from ROOT import *
from ROOT import RooUnfoldResponse
from ROOT import RooUnfold
from ROOT import RooUnfoldBayes
# from ROOT import RooUnfoldSvd
# from ROOT import RooUnfoldTUnfold
from array import *
from math import *

lumi = 19.47

#sample="latino_1125_ggToH125toWWTo2LAndTau2Nu.root"
sample="latino_2125_vbfToH125toWWTo2LAndTau2Nu.root"

pthbins = array("d",[0,15,45,87,125,162,200])

#file_out = TFile("ggHresponseMatrices.root","recreate")
file_out = TFile("vbfresponseMatrices.root","recreate")

syst = ["metScale_up","metScale_down","jetEnergyScale_up","jetEnergyScale_down","electronScale_up","electronScale_down","muonScale_up","muonScale_down","metResolution","electronResolution","leptonEfficiency_up","leptonEfficiency_down","btagsf_up","btagsf_down"]

for s in syst :
  print s
  # btagsf nuisance needs a different sample with special weights
  # leptonEfficiency up/down variations are just two weights
  if "btagsf" in s or "leptonEfficiency" in s:
    file = TFile("samples/nominals/"+sample.replace(".root","_weights.root"))
  else :
    file = TFile("samples/"+s+"/"+sample)

  print file
  tree = file.Get("latino")

  hMeas = TH1F("hMeas "+s,"pTH RECO "+s,len(pthbins)-1,pthbins)
  hTrue = TH1F("hTrue "+s,"pTH GEN "+s,len(pthbins)-1,pthbins)

  response = RooUnfoldResponse(hMeas,hTrue,s,s)
  
  # Start loop
  iEvt=0
  for e in tree :
    iEvt+=1
#    if iEvt==1000 : break
    if iEvt%10000==0 : 
      print "Event ",iEvt
    
    if "btagsf_up" in s :
      weight = ( ( (e.weightBtagSigUp/e.weightBtagSig)*(e.jetbjpb1<1.4) + (e.weightBtagCtrlUp/e.weightBtagCtrl)*(e.jetbjpb1>1.4) ) if ( ((e.dataset>=10 and e.dataset<=19) or e.dataset==1125 or e.dataset==2125 or e.dataset==3125 ) and (e.njet>0)) else 1.)*e.puW*e.effW*e.triggW
    elif "btagsf_down" in s :
      weight = ( ( (e.weightBtagSigDown/e.weightBtagSig)*(e.jetbjpb1<1.4) + (e.weightBtagCtrlDown/e.weightBtagCtrl)*(e.jetbjpb1>1.4) ) if ( ((e.dataset>=10 and e.dataset<=19) or e.dataset==1125 or e.dataset==2125 or e.dataset==3125 ) and (e.njet>0)) else 1.)*e.puW*e.effW*e.triggW
    elif "leptonEfficiency_up" in s :
      weight = e.puW*e.effW*e.triggW*e.effWUp/e.effW
    elif "leptonEfficiency_down" in s :
      weight = e.puW*e.effW*e.triggW*e.effWDown/e.effW
    else:
      weight = e.puW*e.effW*e.triggW

    # Reconstructed Higgs transverse momentum
    pTH_reco = sqrt( (e.pt1*cos(e.phi1)+e.pt2*cos(e.phi2)+e.pfmet*cos(e.pfmetphi))**2 + (e.pt1*sin(e.phi1)+e.pt2*sin(e.phi2)+e.pfmet*sin(e.pfmetphi))**2 ) 

    # Generated Higgs transverse momentum
    pTH_gen = sqrt( (e.leptonGenpt1*cos(e.leptonGenphi1)+e.leptonGenpt2*cos(e.leptonGenphi2)+e.neutrinoGenpt1*cos(e.neutrinoGenphi1)+e.neutrinoGenpt2*cos(e.neutrinoGenphi2))**2 + (e.leptonGenpt1*sin(e.leptonGenphi1)+e.leptonGenpt2*sin(e.leptonGenphi2)+e.neutrinoGenpt1*sin(e.neutrinoGenphi1)+e.neutrinoGenpt2*sin(e.neutrinoGenphi2))**2  )  

    pT_nn = sqrt((((e.neutrinoGenpt1*cos(e.neutrinoGenphi1))+(e.neutrinoGenpt2*cos(e.neutrinoGenphi2)))*((e.neutrinoGenpt1*cos(e.neutrinoGenphi1))+(e.neutrinoGenpt2*cos(e.neutrinoGenphi2))))+(((e.neutrinoGenpt1*sin(e.neutrinoGenphi1))+(e.neutrinoGenpt2*sin(e.neutrinoGenphi2)))*((e.neutrinoGenpt1*sin(e.neutrinoGenphi1))+(e.neutrinoGenpt2*sin(e.neutrinoGenphi2)))))

    ### Acceptance selection
    if ( e.leptonGenpt1>20. and e.leptonGenpt2>10 and abs(e.leptonGeneta1)<2.5 and abs(e.leptonGeneta2)<2.5 and pT_nn>20 ):

      ### Analysis selection
      if ( ((e.ptll>30 and e.mth>60 and e.mth<280 and e.mll<200 and e.trigger==1. and e.pfmet>20. and e.mll>12 and e.mpmet>20. and e.nextra==0 and e.pt1>20 and e.pt2>10 and ((e.ch1)*(e.ch2))<0 and (e.zveto==1 or (not e.sameflav)) and (e.njet==0 or e.njet==1 or (e.dphilljetjet<3.14/180.*165. or (not e.sameflav) ) ) and ( (not e.sameflav) or ( ( e.njet!=0 or e.dymva1>0.88 or e.mpmet>35) and (e.njet!=1 or e.dymva1>0.84 or e.mpmet>35) and ( e.njet==0 or e.njet==1 or (e.pfmet > 45.0)) ) ))and((not e.sameflav) and (((( e.jetbjpb1<1.4 or e.jetpt1<30) and ( e.jetbjpb2<1.4 or e.jetpt2<30) and ( e.jetbjpb3<1.4 or e.jetpt3<30) and ( e.jetbjpb4<1.4 or e.jetpt4<30)) and e.njet>0) or (e.bveto_mu==1 and e.bveto_ip==1 and e.njet==0))))  ):         
        response.Fill(min(pTH_reco,167.), min(pTH_gen,167.),weight)
        response.Miss(min(pTH_gen,167.),1-weight)
#        hMeas.Fill(min(pTH_reco,167.),e.puW*e.effW*e.triggW*e.baseW*lumi)

      else: response.Miss(min(pTH_gen,167.),1)

  file_out.cd()
  response.Write()

file_out.Write()
file_out.Close()

