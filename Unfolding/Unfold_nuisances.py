#!/usr/bin/env python

from ROOT import *
from ROOT import RooUnfoldResponse
from ROOT import RooUnfold
from ROOT import RooUnfoldBayes
from ROOT import RooUnfoldSvd
# from ROOT import RooUnfoldTUnfold
from array import *
from math import *

#sample="latino_1125_ggToH125toWWTo2LAndTau2Nu.root"
sample="latino_2125_vbfToH125toWWTo2LAndTau2Nu.root"

out_file = TFile("syst_ggH.root","recreate") if "1125" in sample else TFile("syst_vbf.root","recreate")
### File with signal extracted from the fit for each nuisance up/down variation
syst_file = TFile("plotsFromFit.root")
### File with the response martices for the systematics which need them
matrix_file = TFile("ggHresponseMatrices.root") if "1125" in sample else TFile("vbfresponseMatrices.root")

pthbins = array("d",[0,15,45,87,125,162,200])

### Build standard response matrix
file = TFile("samples/nominals/"+sample)
tree = file.Get("latino")

hMeas = TH1F("hMeas central","pTH RECO central",len(pthbins)-1,pthbins)
hTrue = TH1F("hTrue central ","pTH GEN central",len(pthbins)-1,pthbins)

response_central = RooUnfoldResponse(hMeas,hTrue,"central","central")

### Start loop
iEvt=0
for e in tree :
  iEvt+=1
#    if iEvt==1000 : break
  if iEvt%10000==0 :
    print "Event ",iEvt

  weight = e.puW*e.effW*e.triggW
  
  pTH_reco = sqrt( (e.pt1*cos(e.phi1)+e.pt2*cos(e.phi2)+e.pfmet*cos(e.pfmetphi))**2 + (e.pt1*sin(e.phi1)+e.pt2*sin(e.phi2)+e.pfmet*sin(e.pfmetphi))**2 )

  pTH_gen = sqrt( (e.leptonGenpt1*cos(e.leptonGenphi1)+e.leptonGenpt2*cos(e.leptonGenphi2)+e.neutrinoGenpt1*cos(e.neutrinoGenphi1)+e.neutrinoGenpt2*cos(e.neutrinoGenphi2))**2 + (e.leptonGenpt1*sin(e.leptonGenphi1)+e.leptonGenpt2*sin(e.leptonGenphi2)+e.neutrinoGenpt1*sin(e.neutrinoGenphi1)+e.neutrinoGenpt2*sin(e.neutrinoGenphi2))**2  )

  pT_nn = sqrt((((e.neutrinoGenpt1*cos(e.neutrinoGenphi1))+(e.neutrinoGenpt2*cos(e.neutrinoGenphi2)))*((e.neutrinoGenpt1*cos(e.neutrinoGenphi1))+(e.neutrinoGenpt2*cos(e.neutrinoGenphi2))))+(((e.neutrinoGenpt1*sin(e.neutrinoGenphi1))+(e.neutrinoGenpt2*sin(e.neutrinoGenphi2)))*((e.neutrinoGenpt1*sin(e.neutrinoGenphi1))+(e.neutrinoGenpt2*sin(e.neutrinoGenphi2)))))

    ### Acceptance selection
  if ( e.leptonGenpt1>20. and e.leptonGenpt2>10 and abs(e.leptonGeneta1)<2.5 and abs(e.leptonGeneta2)<2.5 and pT_nn>20 ):

    ### Analysis selection
    if ( ((e.ptll>30 and e.mth>60 and e.mth<280 and e.mll<200 and e.trigger==1. and e.pfmet>20. and e.mll>12 and e.mpmet>20. and e.nextra==0 and e.pt1>20 and e.pt2>10 and ((e.ch1)*(e.ch2))<0 and (e.zveto==1 or (not e.sameflav)) and (e.njet==0 or e.njet==1 or (e.dphilljetjet<3.14/180.*165. or (not e.sameflav) ) ) and ( (not e.sameflav) or ( ( e.njet!=0 or e.dymva1>0.88 or e.mpmet>35) and (e.njet!=1 or e.dymva1>0.84 or e.mpmet>35) and ( e.njet==0 or e.njet==1 or (e.pfmet > 45.0)) ) ))and((not e.sameflav) and (((( e.jetbjpb1<1.4 or e.jetpt1<30) and ( e.jetbjpb2<1.4 or e.jetpt2<30) and ( e.jetbjpb3<1.4 or e.jetpt3<30) and ( e.jetbjpb4<1.4 or e.jetpt4<30)) and e.njet>0) or (e.bveto_mu==1 and e.bveto_ip==1 and e.njet==0))))  ): 

      response_central.Fill(min(pTH_reco,167.), min(pTH_gen,167.),weight)
      response_central.Miss(min(pTH_gen,167.),1-weight)

    else: response_central.Miss(min(pTH_gen,167.),1)

out_file.cd()

h_central = syst_file.Get("ggHcentral") if "1125" in sample else syst_file.Get("otherHcentral")
print "==================================== UNFOLD CENTRAL ==================================="
unfold_central = RooUnfoldBayes(response_central, h_central, 4)
hReco_central = unfold_central.Hreco()
hReco_central.Write()

syst = ["CMS_8TeV_hww_FakeRateUp","CMS_8TeV_norm_DYTTUp","CMS_8TeV_norm_VgUp","QCDscale_VVUp","QCDscale_VVVUp","QCDscale_VgSUp","QCDscale_WWUp","QCDscale_WW1inUp","QCDscale_ggWWUp","lumi_8TeVUp","pdf_ggUp","pdf_qqbarUp","CMS_8TeV_btagsfUp","CMS_8TeV_eff_lUp","CMS_8TeV_metUp","CMS_8TeV_p_res_eUp","CMS_8TeV_p_scale_eUp","CMS_8TeV_p_scale_jUp","CMS_8TeV_p_scale_mUp","CMS_8TeV_p_scale_metUp","CMS_8TeV_hww_FakeRateDown","CMS_8TeV_norm_DYTTDown","CMS_8TeV_norm_VgDown","QCDscale_VVDown","QCDscale_VVVDown","QCDscale_VgSDown","QCDscale_WWDown","QCDscale_WW1inDown","QCDscale_ggWWDown","lumi_8TeVDown","pdf_ggDown","pdf_qqbarDown","CMS_8TeV_btagsfDown","CMS_8TeV_eff_lDown","CMS_8TeV_metDown","CMS_8TeV_p_res_eDown","CMS_8TeV_p_scale_eDown","CMS_8TeV_p_scale_jDown","CMS_8TeV_p_scale_mDown","CMS_8TeV_p_scale_metDown"]

for s in syst:
  print "==================================== UNFOLD ",s," ==================================="
  h = syst_file.Get("ggH"+s) if "1125" in sample else syst_file.Get("otherH"+s)
  if "btagsfUp" in s:
    matrix = matrix_file.Get("btagsf_up")
  elif "btagsfDown" in s:
    matrix = matrix_file.Get("btagsf_down")
  elif "CMS_8TeV_eff_lUp" in s:
    matrix = matrix_file.Get("leptonEfficiency_up")
  elif "CMS_8TeV_eff_lDown" in s:
    matrix = matrix_file.Get("leptonEfficiency_down")
  elif "CMS_8TeV_metUp" in s:
    matrix = matrix_file.Get("metResolution")
  elif "CMS_8TeV_p_res_eUp" in s:
    matrix = matrix_file.Get("electronResolution")
  elif "CMS_8TeV_p_scale_metUp" in s:
    matrix = matrix_file.Get("metScale_up")
  elif "CMS_8TeV_p_scale_metDown" in s:
    matrix = matrix_file.Get("metScale_down")
  else:
    matrix = response_central

  unfold = RooUnfoldBayes(matrix, h, 4)
  hReco = unfold.Hreco()
  hReco.SetNameTitle(s,s)
  hReco.Write()

out_file.Close()

