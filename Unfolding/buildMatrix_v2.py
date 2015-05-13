#!/usr/bin/env python

from ROOT import *
from ROOT import RooUnfoldResponse
from ROOT import RooUnfold
from array import *
from math import *

lumi = 19.47

base="/afs/cern.ch/work/l/lviliani/DatacardFramework/CMSSW_7_1_5/src/Unfolding/"

sample_ggh="latino_1125_ggToH125toWWTo2LAndTau2Nu.root"
sample_vbf="latino_2125_vbfToH125toWWTo2LAndTau2Nu.root"

pthbins = array("d",[0,15,45,87,125,162,200])

file_out = TFile("responseMatrices.root","recreate")

ggH_up = 0.00741055018132
ggH_down = 0.00626155125022 
vbf_up = 0.0764639370037
vbf_down = 0.0904951216692

list = ["central","up","down","metScale_up","metScale_down","jetEnergyScale_up","jetEnergyScale_down","electronScale_up","electronScale_down","muonScale_up","muonScale_down","metResolution","electronResolution","leptonEfficiency_up","leptonEfficiency_down","btagsf_up","btagsf_down"]  

for l in list:

  print l

  chain = TChain("latino")
 
  if "btagsf" in l or "leptonEfficiency" in l:
    chain.Add(base+"samples/nominals/"+sample_ggh.replace(".root","_weights.root"))
    chain.Add(base+"samples/nominals/"+sample_vbf.replace(".root","_weights.root"))
  elif "central" in l or "up" in l or "down" in l:
    chain.Add(base+"samples/nominals/"+sample_ggh)
    chain.Add(base+"samples/nominals/"+sample_vbf)
  else:
    chain.Add(base+"samples/"+l+"/"+sample_ggh)
    chain.Add(base+"samples/"+l+"/"+sample_vbf)

  hMeas = TH1F("hMeas "+l,"pTH RECO "+l,len(pthbins)-1,pthbins)
  hTrue = TH1F("hTrue "+l,"pTH GEN "+l,len(pthbins)-1,pthbins)

  response = RooUnfoldResponse(hMeas,hTrue,l,l)

  print chain

  # Start loop
  iEvt=0
  for e in chain :
    iEvt+=1
#    if iEvt==1000 : break
    if iEvt%10000==0 : 
      print "Event ",iEvt
 
    current_file = chain.GetFile().GetName() 
    
    if l=="up":
      weight = e.puW*e.effW*e.triggW*(1-ggH_down) if "1125" in current_file else e.puW*e.effW*e.triggW*(1+vbf_up)
    elif l=="down":
      weight = e.puW*e.effW*e.triggW*(1+ggH_up) if "1125" in current_file else e.puW*e.effW*e.triggW*(1-vbf_down)
    elif "btagsf_up" in l:
      print e.weightBtagSigUp
      weight = ( ( (e.weightBtagSigUp/e.weightBtagSig)*(e.jetbjpb1<1.4) + (e.weightBtagCtrlUp/e.weightBtagCtrl)*(e.jetbjpb1>1.4) ) if ( ((e.dataset>=10 and e.dataset<=19) or e.dataset==1125 or e.dataset==2125 or e.dataset==3125 ) and (e.njet>0)) else 1.)*e.puW*e.effW*e.triggW
    elif "btagsf_down" in l :
      weight = ( ( (e.weightBtagSigDown/e.weightBtagSig)*(e.jetbjpb1<1.4) + (e.weightBtagCtrlDown/e.weightBtagCtrl)*(e.jetbjpb1>1.4) ) if ( ((e.dataset>=10 and e.dataset<=19) or e.dataset==1125 or e.dataset==2125 or e.dataset==3125 ) and (e.njet>0)) else 1.)*e.puW*e.effW*e.triggW
    elif "leptonEfficiency_up" in l :
      weight = e.puW*e.effW*e.triggW*e.effWUp/e.effW
    elif "leptonEfficiency_down" in l :
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
        response.Fill(min(pTH_reco,167.), min(pTH_gen,167.),weight*e.baseW*lumi)
        response.Miss(min(pTH_gen,167.),(1-weight)*e.baseW*lumi)
#        hMeas.Fill(min(pTH_reco,167.),e.puW*e.effW*e.triggW*e.e.baseW*lumi)

      else: response.Miss(min(pTH_gen,167.),e.baseW*lumi)

  matrix = response.Hresponse()
  matrix.SetNameTitle("matrix_"+l,"matrix_"+l)

  file_out.cd()
  response.Write()
  matrix.Write()


file_out.Close()

