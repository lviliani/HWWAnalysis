#!/usr/bin/env python

from ROOT import *
from ROOT import RooUnfoldResponse
from ROOT import RooUnfold
#from ROOT import RooUnfoldBayes
from ROOT import RooUnfoldSvd
# from ROOT import RooUnfoldTUnfold
from array import *
from math import *
import nicePlot_unfolded


lumi = 19.468
kreg=4

out_file = TFile("unfolded.root","recreate")

### File with signal extracted from the fit for each nuisance up/down variation
syst_file = TFile("plotsFromFit.root")

### File with the response martices for the systematics which need them
#matrix_file = TFile("responseMatricesPreAppWithFakesAndWZttH.root")

### First of all get the central distribution and unfold with central, up and down matrices, corresponding to the ggH/VBF ratio variation
h = syst_file.Get("HcentralNotChangingRM")

list = ["central","up","down"]
print "==================================== UNFOLD CENTRAL ==================================="

for l in list :
  matrix_file = TFile("responseMatricesPreApp/responseMatrix_"+str(l)+".root")
  response = matrix_file.Get(l)
  unfold = RooUnfoldSvd(response, h, kreg)

  cov_matrix = syst_file.Get("Hcentral_covariance")
  cov_matrix.Print()

  if "central" in l: unfolded_cov_matrix = unfold.Ereco()

  unfold.SetMeasuredCov(cov_matrix)
  hReco = unfold.Hreco(2)
  hReco.SetNameTitle(l,l)
  out_file.cd()
  hReco.Write()

### Now unfold the distributions corresponding to the up/down nuisance variations that affect the response matrix
syst = ["statOnly","btagsfUp","btagsfDown","eff_lUp","eff_lDown","metUp","metDown","p_res_eUp","p_res_eDown","p_scale_eUp","p_scale_eDown","p_scale_mUp","p_scale_mDown","p_scale_metUp","p_scale_metDown","p_scale_jUp","p_scale_jDown"]
#syst = ["statOnly","btagsf_up","btagsf_down","leptonEfficiency_up","leptonEfficiency_up","metResolution","electronResolution","electronScale_up","electronScale_down","muonScale_up","muonScale_down","metScale_up","metScale_down","jetEnergyScale_up","jetEnergyScale_down"]


for s in syst:
  print "==================================== UNFOLD ",s," ==================================="
  h = syst_file.Get("HCMS_8TeV_"+s)
#  matrix_file = TFile("responseMatricesPreApp/responseMatrix_"+str(s)+".root") if not "statOnly" in s else TFile("responseMatricesPreApp/responseMatrix_central.root")

  if "btagsfUp" in s:
    matrix_file = TFile("responseMatricesPreApp/responseMatrix_btagsf_up.root")
    matrix = matrix_file.Get("btagsf_up")
    print matrix_file
#    matrix_file.Close()
  elif "btagsfDown" in s:
    matrix_file = TFile("responseMatricesPreApp/responseMatrix_btagsf_down.root")
    matrix = matrix_file.Get("btagsf_down")
    print matrix_file
#    matrix_file.Close()
  elif "eff_lUp" in s:
    matrix_file = TFile("responseMatricesPreApp/responseMatrix_leptonEfficiency_up.root")
    matrix = matrix_file.Get("leptonEfficiency_up")
#    matrix_file.Close()
  elif "eff_lDown" in s:
    matrix_file = TFile("responseMatricesPreApp/responseMatrix_leptonEfficiency_down.root")
    matrix = matrix_file.Get("leptonEfficiency_down")
#    matrix_file.Close()
  elif "metUp" in s or "metDown" in s:
    matrix_file = TFile("responseMatricesPreApp/responseMatrix_metResolution.root")
    matrix = matrix_file.Get("metResolution")
#    matrix_file.Close()
  elif "p_res_e" in s:
    matrix_file = TFile("responseMatricesPreApp/responseMatrix_electronResolution.root")
    matrix = matrix_file.Get("electronResolution")
#    matrix_file.Close()
  elif "p_scale_metUp" in s:
    matrix_file = TFile("responseMatricesPreApp/responseMatrix_metScale_up.root")
    matrix = matrix_file.Get("metScale_up")
#    matrix_file.Close()
  elif "p_scale_metDown" in s:
    matrix_file = TFile("responseMatricesPreApp/responseMatrix_metScale_down.root")
    matrix = matrix_file.Get("metScale_down")
#    matrix_file.Close()
  elif "p_scale_eUp" in s:
    matrix_file = TFile("responseMatricesPreApp/responseMatrix_electronScale_up.root")
    matrix = matrix_file.Get("electronScale_up")
#    matrix_file.Close()
  elif "p_scale_eDown" in s:
    matrix_file = TFile("responseMatricesPreApp/responseMatrix_electronScale_down.root")
    matrix = matrix_file.Get("electronScale_down")
#    matrix_file.Close()
  elif "p_scale_mUp" in s:
    matrix_file = TFile("responseMatricesPreApp/responseMatrix_muonScale_up.root")
    matrix = matrix_file.Get("muonScale_up")
#    matrix_file.Close()
  elif "p_scale_mDown" in s:
    matrix_file = TFile("responseMatricesPreApp/responseMatrix_muonScale_down.root")
    matrix = matrix_file.Get("muonScale_down")
#    matrix_file.Close()
  elif "p_scale_jUp" in s:
    matrix_file = TFile("responseMatricesPreApp/responseMatrix_jetEnergyScale_up.root")
    matrix = matrix_file.Get("jetEnergyScale_up")
#    matrix_file.Close()
  elif "p_scale_jDown" in s:
    matrix_file = TFile("responseMatricesPreApp/responseMatrix_jetEnergyScale_down.root")
    matrix = matrix_file.Get("jetEnergyScale_down")
#    matrix_file.Close()
  elif "statOnly" in s:
    matrix_file = TFile("responseMatricesPreApp/responseMatrix_central.root")
    h = syst_file.Get("HcentralStat")
    matrix = matrix_file.Get("central")
#    matrix_file.Close()
  else: 
    print "####################### Error!!!"
    break

  unfold = RooUnfoldSvd(matrix, h, kreg)

  hReco = unfold.Hreco(2)
  unfold.GetMeasuredCov().Print()
  
  hReco.SetNameTitle(s,s)
  out_file.cd()
  hReco.Write()

out_file.Close()

gStyle.SetPalette(1)
cov_matrix = TH2D("cov_matrix","Covariance matrix, kreg = "+str(kreg),6,0,6,6,0,6)

for row in range(6):
  for column in range(6):
    cov_matrix.SetBinContent(row+1,column+1, unfolded_cov_matrix[row][column]/sqrt(unfolded_cov_matrix[row][row])/sqrt(unfolded_cov_matrix[column][column]))

ccov = TCanvas("","")
ccov.cd()
cov_matrix.SetStats(0)
cov_matrix.SetTitle("")
cov_matrix.SetMarkerSize(1.5)
cov_matrix.GetXaxis().SetTitle("i")
cov_matrix.GetYaxis().SetTitle("j")
#cov_matrix.GetZaxis().SetTitle("#sigma_{ij}/#sigma_{i}#sigma_{j}")
cov_matrix.Draw("COLZ text")
ccov.Print("covariance_"+str(kreg)+".eps")

print "Plotting the unfolded spectrum..."

plot_file = "unfolded.root"
truth_file = "TheTruth.root"

nicePlot_unfolded.finalPlot(plot_file, truth_file)
