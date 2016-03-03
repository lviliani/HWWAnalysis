#!/usr/bin/env python

from ROOT import *
from ROOT import RooUnfoldResponse
from ROOT import RooUnfold
from array import *
from math import *
import sys

lumi = 19.47

base="/afs/cern.ch/work/l/lviliani/DatacardFramework/CMSSW_7_1_5/src/Unfolding/"

sample_ggh="latino_1125_ggToH125toWWTo2LAndTau2Nu.root"
sample_vbf="latino_2125_vbfToH125toWWTo2LAndTau2Nu.root"
sample_wzh="latino_3125_wzttH125ToWW.root"

pthbins = array("d",[0,15,45,85,125,165,200])

file_out = TFile("responseMatrix_up.root","recreate")

#ggH_up = 0.00741055018132
#ggH_down = 0.00626155125022 
#vbf_up = 0.0764639370037
#vbf_down = 0.0904951216692

ggH_up = 0.22
ggH_down = 0.19
vbf_up = 0.32
vbf_down = 0.29

#list = ["central","up","down","metScale_up","metScale_down","jetEnergyScale_up","jetEnergyScale_down","electronScale_up","electronScale_down","muonScale_up","muonScale_down","metResolution","electronResolution","leptonEfficiency_up","leptonEfficiency_down","btagsf_up","btagsf_down"]  
#list = ["central"]
list=[]
for arg in sys.argv:
  list.append(arg)
list.pop(0)

for l in list:

  print l

  chain = TChain("latino")
 
  if "btagsf" in l or "leptonEfficiency" in l:
    chain.Add(base+"samples/nominals/"+sample_ggh.replace(".root","_weights.root"))
    chain.Add(base+"samples/nominals/"+sample_vbf.replace(".root","_weights.root"))
    chain.Add(base+"samples/nominals/"+sample_wzh.replace(".root","_weights.root"))
  elif "central" in l or "up" in l or "down" in l:
    chain.Add(base+"samples/nominals/"+sample_ggh)
    chain.Add(base+"samples/nominals/"+sample_vbf)
    chain.Add(base+"samples/nominals/"+sample_wzh)
  else:
    chain.Add(base+"samples/"+l+"/"+sample_ggh)
    chain.Add(base+"samples/"+l+"/"+sample_vbf)
    chain.Add(base+"samples/"+l+"/"+sample_wzh)

  hMeas = TH1F("hMeas "+l,"pTH RECO "+l,len(pthbins)-1,pthbins)
  hTrue = TH1F("hTrue "+l,"pTH GEN "+l,len(pthbins)-1,pthbins)

  response = RooUnfoldResponse(hMeas,hTrue,l,l)
  
  print chain

  sel_and_acc=0.
  not_sel_and_acc=0.
  sel_and_not_acc=0.
  acc=0.

  # Start loop
  iEvt=0
  for e in chain :
    iEvt+=1
#    if iEvt==1000 : break
    if iEvt%10000==0 : 
      print "Event ",iEvt
 
    current_file = chain.GetFile().GetName() 
    
    if l=="up":
      weight = e.puW*e.effW*e.triggW*(1-ggH_down) if "1125" in current_file else e.puW*e.effW*e.triggW*(1+vbf_up) if "2125" in current_file else e.puW*e.effW*e.triggW

    elif l=="down":
      weight = e.puW*e.effW*e.triggW*(1+ggH_up) if "1125" in current_file else e.puW*e.effW*e.triggW*(1-vbf_down) if "2125" in current_file else e.puW*e.effW*e.triggW

    elif "btagsf_up" in l:
      weight = ( ( (e.weightBtagSigUp/e.weightBtagSig)*(e.jetbjpb1<1.4) + (e.weightBtagCtrlUp/e.weightBtagCtrl)*(e.jetbjpb1>1.4) ) if ( ((e.dataset>=10 and e.dataset<=19) or e.dataset==1125 or e.dataset==2125 or e.dataset==3125 ) and (e.njet>0)) else 1.)*e.puW*e.effW*e.triggW

    elif "btagsf_down" in l :
      weight = ( ( (e.weightBtagSigUp/e.weightBtagSig)*(e.jetbjpb1<1.4) + (e.weightBtagCtrlUp/e.weightBtagCtrl)*(e.jetbjpb1>1.4) ) if ( ((e.dataset>=10 and e.dataset<=19) or e.dataset==1125 or e.dataset==2125 or e.dataset==3125 ) and (e.njet>0)) else 1.)*e.puW*e.effW*e.triggW

    elif "leptonEfficiency_up" in l :
      weight = e.puW*e.effW*e.triggW*e.effWUp/e.effW

    elif "leptonEfficiency_down" in l :
      weight = e.puW*e.effW*e.triggW*e.effWDown/e.effW

    else:
      weight = e.puW*e.effW*e.triggW

    # Reconstructed Higgs transverse momentum
    pTH_reco = sqrt( (e.pt1*cos(e.phi1)+e.pt2*cos(e.phi2)+e.pfmet*cos(e.pfmetphi))**2 + (e.pt1*sin(e.phi1)+e.pt2*sin(e.phi2)+e.pfmet*sin(e.pfmetphi))**2 ) 

    pl1 = TLorentzVector()
    pl2 = TLorentzVector()
    pn1 = TLorentzVector()
    pn2 = TLorentzVector()


    if abs(e.leptonGenpid1)==13: 
      pl1.SetPtEtaPhiM(e.leptonGenpt1,e.leptonGeneta1,e.leptonGenphi1,0.1056)
    elif abs(e.leptonGenpid1)==11:  
      pl1.SetPtEtaPhiM(e.leptonGenpt1,e.leptonGeneta1,e.leptonGenphi1,0.000511)
    else:
      pl1.SetPtEtaPhiM(e.leptonGenpt1,e.leptonGeneta1,e.leptonGenphi1,1.777)

    if abs(e.leptonGenpid2)==13:
      pl2.SetPtEtaPhiM(e.leptonGenpt2,e.leptonGeneta2,e.leptonGenphi2,0.1056)
    elif abs(e.leptonGenpid1)==11:
      pl2.SetPtEtaPhiM(e.leptonGenpt2,e.leptonGeneta2,e.leptonGenphi2,0.000511)
    else:
      pl2.SetPtEtaPhiM(e.leptonGenpt2,e.leptonGeneta2,e.leptonGenphi2,1.777)


    pn1.SetPtEtaPhiM(e.neutrinoGenpt1,e.neutrinoGeneta1,e.neutrinoGenphi1,0)
    pn2.SetPtEtaPhiM(e.neutrinoGenpt2,e.neutrinoGeneta2,e.neutrinoGenphi2,0)


    pTll_gen = (pl1+pl2).Perp()
#    pTll_gen = sqrt((((e.leptonGenpt1*cos(e.leptonGenphi1))+(e.leptonGenpt2*cos(e.leptonGenphi2)))*((e.leptonGenpt1*cos(e.leptonGenphi1))+(e.leptonGenpt2*cos(e.leptonGenphi2))))+(((e.leptonGenpt1*sin(e.leptonGenphi1))+(e.leptonGenpt2*sin(e.leptonGenphi2)))*((e.leptonGenpt1*sin(e.leptonGenphi1))+(e.leptonGenpt2*sin(e.leptonGenphi2)))))

    pTnn_gen = (pn1+pn2).Perp()
#    pTnn_gen = sqrt((((e.neutrinoGenpt1*cos(e.neutrinoGenphi1))+(e.neutrinoGenpt2*cos(e.neutrinoGenphi2)))*((e.neutrinoGenpt1*cos(e.neutrinoGenphi1))+(e.neutrinoGenpt2*cos(e.neutrinoGenphi2))))+(((e.neutrinoGenpt1*sin(e.neutrinoGenphi1))+(e.neutrinoGenpt2*sin(e.neutrinoGenphi2)))*((e.neutrinoGenpt1*sin(e.neutrinoGenphi1))+(e.neutrinoGenpt2*sin(e.neutrinoGenphi2)))))
  
    mll_gen = (pl1+pl2).M()
#    mll_gen_v2 = sqrt(2*e.leptonGenpt1*e.leptonGenpt2*(cosh(e.leptonGeneta1 - e.leptonGeneta2 ) - cos(e.leptonGenphi1 - e.leptonGenphi2)))

#    mth_gen_v1 = sqrt((pl1+pl2+pn1+pn2).E()*(pl1+pl2+pn1+pn2).E() - (pl1+pl2+pn1+pn2).Perp()*(pl1+pl2+pn1+pn2).Perp())
    if ( ( pTll_gen + pTnn_gen  )**2 < ( ( e.leptonGenpt1*cos(e.leptonGenphi1) + e.leptonGenpt2*cos(e.leptonGenphi2) + e.neutrinoGenpt1*cos(e.neutrinoGenphi1) + e.neutrinoGenpt2*cos(e.neutrinoGenphi2) )**2 + ( e.leptonGenpt1*sin(e.leptonGenphi1) + e.leptonGenpt2*sin(e.leptonGenphi2) + e.neutrinoGenpt1*sin(e.neutrinoGenphi1) + e.neutrinoGenpt2*sin(e.neutrinoGenphi2)  )**2 ) ):
      continue
    else:
      mth_gen = sqrt( ( pTll_gen + pTnn_gen  )**2 - ( ( e.leptonGenpt1*cos(e.leptonGenphi1) + e.leptonGenpt2*cos(e.leptonGenphi2) + e.neutrinoGenpt1*cos(e.neutrinoGenphi1) + e.neutrinoGenpt2*cos(e.neutrinoGenphi2) )**2 + ( e.leptonGenpt1*sin(e.leptonGenphi1) + e.leptonGenpt2*sin(e.leptonGenphi2) + e.neutrinoGenpt1*sin(e.neutrinoGenphi1) + e.neutrinoGenpt2*sin(e.neutrinoGenphi2)  )**2 ) ) 

#    pTll_gen = (pl1+pl2).Perp() 
#    pTll_gen_v2 = sqrt((((e.leptonGenpt1*cos(e.leptonGenphi1))+(e.leptonGenpt2*cos(e.leptonGenphi2)))*((e.leptonGenpt1*cos(e.leptonGenphi1))+(e.leptonGenpt2*cos(e.leptonGenphi2))))+(((e.leptonGenpt1*sin(e.leptonGenphi1))+(e.leptonGenpt2*sin(e.leptonGenphi2)))*((e.leptonGenpt1*sin(e.leptonGenphi1))+(e.leptonGenpt2*sin(e.leptonGenphi2)))))

#    pTnn_gen = (pn1+pn2).Perp()
#    pTnn_gen_v2 = sqrt((((e.neutrinoGenpt1*cos(e.neutrinoGenphi1))+(e.neutrinoGenpt2*cos(e.neutrinoGenphi2)))*((e.neutrinoGenpt1*cos(e.neutrinoGenphi1))+(e.neutrinoGenpt2*cos(e.neutrinoGenphi2))))+(((e.neutrinoGenpt1*sin(e.neutrinoGenphi1))+(e.neutrinoGenpt2*sin(e.neutrinoGenphi2)))*((e.neutrinoGenpt1*sin(e.neutrinoGenphi1))+(e.neutrinoGenpt2*sin(e.neutrinoGenphi2)))))

#    pTH_gen = e.PtHiggs
    pTH_gen = (pl1+pl2+pn1+pn2).Perp()
#    pTH_gen_v2 = sqrt( (e.leptonGenpt1*cos(e.leptonGenphi1)+e.leptonGenpt2*cos(e.leptonGenphi2)+e.neutrinoGenpt1*cos(e.neutrinoGenphi1)+e.neutrinoGenpt2*cos(e.neutrinoGenphi2))**2 + (e.leptonGenpt1*sin(e.leptonGenphi1)+e.leptonGenpt2*sin(e.leptonGenphi2)+e.neutrinoGenpt1*sin(e.neutrinoGenphi1)+e.neutrinoGenpt2*sin(e.neutrinoGenphi2))**2  )  

    of_gen = ( (abs(e.leptonGenpid1)==11 and abs(e.leptonGenpid2)==13) or (abs(e.leptonGenpid1)==13 and abs(e.leptonGenpid2)==11) )

    if e.dataset==3125:
      wzemu_gen = ( (e.mctruth==24 or e.mctruth==26)*(e.dataset==3125)*(e.mcHWWdecay==3)*(e.leptonGenpt3<0)*(e.neutrinoGenpt3<0) )
    else :
      wzemu_gen=1

#    acceptance = e.leptonGenpt1>18. and e.leptonGenpt2>8. and abs(e.leptonGeneta1)<2.5 and abs(e.leptonGeneta2)<2.5 and pTnn_gen>15. and pTll_gen>25. and mll_gen>12. and mth_gen>50. and of_gen and wzemu_gen

### Optimized acceptance
    acceptance = e.leptonGenpt1>20. and e.leptonGenpt2>10. and abs(e.leptonGeneta1)<2.5 and abs(e.leptonGeneta2)<2.5 and pTll_gen>30. and mll_gen>12. and mth_gen>50. and of_gen and wzemu_gen

    ### Acceptance selection
    if ( acceptance ):
      acc+=e.baseW*lumi
      ### Analysis selection
      if ( ((e.ptll>30 and e.mth>60 and e.mth<280 and e.mll<200 and e.trigger==1. and e.pfmet>20. and e.mll>12 and e.mpmet>20. and e.nextra==0 and e.pt1>20 and e.pt2>10 and ((e.ch1)*(e.ch2))<0 and (e.zveto==1 or (not e.sameflav)) and (e.njet==0 or e.njet==1 or (e.dphilljetjet<3.14/180.*165. or (not e.sameflav) ) ) and ( (not e.sameflav) or ( ( e.njet!=0 or e.dymva1>0.88 or e.mpmet>35) and (e.njet!=1 or e.dymva1>0.84 or e.mpmet>35) and ( e.njet==0 or e.njet==1 or (e.pfmet > 45.0)) ) ))and((not e.sameflav) and (((( e.jetbjpb1<1.4 or e.jetpt1<30) and ( e.jetbjpb2<1.4 or e.jetpt2<30) and ( e.jetbjpb3<1.4 or e.jetpt3<30) and ( e.jetbjpb4<1.4 or e.jetpt4<30)) and e.njet>0) or (e.bveto_mu==1 and e.bveto_ip==1 and e.njet==0))))  ):         
        response.Fill(min(pTH_reco,167.), min(pTH_gen,167.),weight*e.baseW*lumi)
        response.Miss(min(pTH_gen,167.),(1-weight)*e.baseW*lumi)
	sel_and_acc+=weight*e.baseW*lumi       

      else: 
        if l=="up":
          w = (1-ggH_down) if "1125" in current_file else (1+vbf_up) if "2125" in current_file else 1
          response.Miss(min(pTH_gen,167.),e.baseW*lumi*w)
          not_sel_and_acc+=e.baseW*lumi*w
        elif l=="down":
          w = (1+ggH_up) if "1125" in current_file else (1-vbf_down) if "2125" in current_file else 1
          response.Miss(min(pTH_gen,167.),e.baseW*lumi*w)
          not_sel_and_acc+=e.baseW*lumi*w
        else:
   	  response.Miss(min(pTH_gen,167.),e.baseW*lumi)
    	  not_sel_and_acc+=e.baseW*lumi

    else:
      ### Analysis selection
      if ( ((e.ptll>30 and e.mth>60 and e.mth<280 and e.mll<200 and e.trigger==1. and e.pfmet>20. and e.mll>12 and e.mpmet>20. and e.nextra==0 and e.pt1>20 and e.pt2>10 and ((e.ch1)*(e.ch2))<0 and (e.zveto==1 or (not e.sameflav)) and (e.njet==0 or e.njet==1 or (e.dphilljetjet<3.14/180.*165. or (not e.sameflav) ) ) and ( (not e.sameflav) or ( ( e.njet!=0 or e.dymva1>0.88 or e.mpmet>35) and (e.njet!=1 or e.dymva1>0.84 or e.mpmet>35) and ( e.njet==0 or e.njet==1 or (e.pfmet > 45.0)) ) ))and((not e.sameflav) and (((( e.jetbjpb1<1.4 or e.jetpt1<30) and ( e.jetbjpb2<1.4 or e.jetpt2<30) and ( e.jetbjpb3<1.4 or e.jetpt3<30) and ( e.jetbjpb4<1.4 or e.jetpt4<30)) and e.njet>0) or (e.bveto_mu==1 and e.bveto_ip==1 and e.njet==0))))  ):
        #response.Fake(min(pTH_reco,167.), weight*e.baseW*lumi)
	sel_and_not_acc += weight*e.baseW*lumi
  matrix = response.Hresponse()
  matrix.SetNameTitle("matrix_"+l,"matrix_"+l)

  file_out.cd()
  response.Write()
  matrix.Write()
  print "############# Events passing the selection and the acceptance = ", sel_and_acc
  print "############# Events passing the acceptance = ", acc  
  print "############# Events passing the acceptance but not the selection = ", not_sel_and_acc
  print "############# Events passing the selection but not the acceptance = ", sel_and_not_acc



file_out.Close()

