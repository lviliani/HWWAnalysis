#!/usr/bin/env python

from ROOT import *
from ROOT import RooUnfoldResponse
from ROOT import RooUnfold
from ROOT import RooUnfoldBayes
from ROOT import RooUnfoldSvd
# from ROOT import RooUnfoldTUnfold
from array import *
from math import *

lumi = 19.468

out_file = TFile("syst_tot_cov.root","recreate")
#out_file = TFile("prova.root","recreate")

### File with signal extracted from the fit for each nuisance up/down variation
syst_file = TFile("plotsFromFit_cov.root")
### File with the response martices for the systematics which need them
matrix_file = TFile("responseMatrices.root")

pthbins = array("d",[0,15,45,87,125,162,200])

### First of all get the central distribution and unfold with central, up and down matrices, corresponding to the ggH/VBF ratio variation
h = syst_file.Get("Hcentral")

list = ["central","up","down"]
print "==================================== UNFOLD CENTRAL ==================================="

for l in list :
  response = matrix_file.Get(l)
  unfold = RooUnfoldSvd(response, h, 3)

  cov_matrix = syst_file.Get("Hcentral_covariance")
  cov_matrix.Print()

  unfold.SetMeasuredCov(cov_matrix)
  hReco = unfold.Hreco(2)
  hReco.SetNameTitle(l,l)
  out_file.cd()
  hReco.Write()

### Now unfold the distributions corresponding to the up/down nuisance variations that affect the response matrix
syst = ["btagsfUp","btagsfDown","eff_lUp","eff_lDown","metUp","metDown","p_res_eUp","p_res_eDown","p_scale_eUp","p_scale_eDown","p_scale_mUp","p_scale_mDown","p_scale_metUp","p_scale_metDown","p_scale_jUp","p_scale_jDown"]

for s in syst:
  print "==================================== UNFOLD ",s," ==================================="
  h = syst_file.Get("HCMS_8TeV_"+s)
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
  elif "m_scale_eUp" in s:
    matrix = matrix_file.Get("muonScale_up")
  elif "m_scale_eDown" in s:
    matrix = matrix_file.Get("muonScale_down")
  elif "j_scale_eUp" in s:
    matrix = matrix_file.Get("jetEnergyScale_up")
  elif "j_scale_eDown" in s:
    matrix = matrix_file.Get("jetEnergyScale_down")

  unfold = RooUnfoldSvd(response, h, 3)

#  cov_matrix = syst_file.Get("Hcentral_covariance")
#  cov_matrix.Print()
#  unfold.SetMeasuredCov(cov_matrix)
  hReco = unfold.Hreco(2)
  unfold.GetMeasuredCov().Print()
  
  hReco.SetNameTitle(s,s)
  out_file.cd()
  hReco.Write()

out_file.Close()

