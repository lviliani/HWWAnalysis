#!/usr/bin/env python

from ROOT import *
from ROOT import RooUnfoldResponse
from ROOT import RooUnfold
from ROOT import RooUnfoldBinByBin
from array import *
from math import *
import finalPlot
import nicePlot_unfolded

lumi = 19.468

out_file = TFile("unfoldedBinByBin.root","recreate")

### File with signal extracted from the fit for each nuisance up/down variation
syst_file = TFile("plotsFromFit_20150604.root")

### File with the response martices for the systematics which need them
#matrix_file = TFile("responseMatricesWithFakesAndWZttH.root")

### First of all get the central distribution and unfold with central, up and down matrices, corresponding to the ggH/VBF ratio variation
h = syst_file.Get("HcentralNotChangingRM")

list = ["central","up","down"]
print "==================================== UNFOLD CENTRAL ==================================="

for l in list :
  matrix_file = TFile("responseMatrices/responseMatrix_"+str(l)+".root")
  response = matrix_file.Get(l)
  unfold = RooUnfoldBinByBin(response, h)

  cov_matrix = syst_file.Get("Hcentral_covariance")
  cov_matrix.Print()

  unfold.SetMeasuredCov(cov_matrix)
  hReco = unfold.Hreco(2)
  hReco.SetNameTitle(l,l)
  out_file.cd()
  hReco.Write()

### Now unfold the distributions corresponding to the up/down nuisance variations that affect the response matrix
syst = ["statOnly","btagsfUp","btagsfDown","eff_lUp","eff_lDown","metUp","metDown","p_res_eUp","p_res_eDown","p_scale_eUp","p_scale_eDown","p_scale_mUp","p_scale_mDown","p_scale_metUp","p_scale_metDown","p_scale_jUp","p_scale_jDown"]
#syst = ["btagsfUp","btagsfDown","eff_lUp","eff_lDown","metUp","metDown","p_res_eUp","p_res_eDown","p_scale_eUp","p_scale_eDown","p_scale_mUp","p_scale_mDown","p_scale_metUp","p_scale_metDown","p_scale_jUp","p_scale_jDown"]


for s in syst:
  print "==================================== UNFOLD ",s," ==================================="
  h = syst_file.Get("HCMS_8TeV_"+s)
  matrix_file = TFile("responseMatrices/responseMatrix_"+str(l)+".root")

  if "btagsfUp" in s:
    matrix = matrix_file.Get("btagsf_up")
  elif "btagsfDown" in s:
    matrix = matrix_file.Get("btagsf_down")
  elif "eff_lUp" in s:
    matrix = matrix_file.Get("leptonEfficiency_up")
  elif "eff_lDown" in s:
    matrix = matrix_file.Get("leptonEfficiency_down")
  elif "metUp" in s or "metDown" in s:
    matrix = matrix_file.Get("metResolution")
  elif "p_res_e" in s:
    matrix = matrix_file.Get("electronResolution")
  elif "p_scale_metUp" in s:
    matrix = matrix_file.Get("metScale_up")
  elif "p_scale_metDown" in s:
    matrix = matrix_file.Get("metScale_down")
  elif "p_scale_eUp" in s:
    matrix = matrix_file.Get("electronScale_up")
  elif "p_scale_eDown" in s:
    matrix = matrix_file.Get("electronScale_down")
  elif "p_scale_mUp" in s:
    matrix = matrix_file.Get("muonScale_up")
  elif "p_scale_mDown" in s:
    matrix = matrix_file.Get("muonScale_down")
  elif "p_scale_jUp" in s:
    matrix = matrix_file.Get("jetEnergyScale_up")
  elif "p_scale_jDown" in s:
    matrix = matrix_file.Get("jetEnergyScale_down")
  elif "statOnly" in s:
    matrix_file = TFile("responseMatrix_central.root")
    h = syst_file.Get("HcentralStat")
    matrix = matrix_file.Get("central")
  else: 
    print "####################### Error!!!"
    break

  unfold = RooUnfoldBinByBin(response, h)

  hReco = unfold.Hreco(2)
  unfold.GetMeasuredCov().Print()
  
  hReco.SetNameTitle(s,s)
  out_file.cd()
  hReco.Write()

out_file.Close()

print "Plotting the unfolded spectrum..."

plot_file = "unfoldedBinByBin.root"
truth_file = "TheTruth.root"

nicePlot_unfolded.finalPlot(plot_file, truth_file)




