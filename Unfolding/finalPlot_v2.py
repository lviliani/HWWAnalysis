#!/usr/bin/env python

from ROOT import *
from array import *
from math import *

gInterpreter.ExecuteMacro("/afs/cern.ch/work/l/lviliani/DatacardFramework/CMSSW_6_1_1/src/HWWAnalysis/ShapeAnalysis/macros/LatinoStyle2.C")

lumi = 19.468

in_file = TFile("syst_tot_cov.root")
#file_ggH = TFile("syst_ggH_NEW.root")
#file_vbf = TFile("syst_vbf_NEW.root")
file_truth = TFile("the_total_truth.root")

pthbins = array("d",[7.5,30,66,106,143.5,181])
err_pth = array("d",[7.5,15,21,19,18.5,19])
zero = array("d",[0,0,0,0,0,0])
central_value_tot = array("d")
syst_up_tot = array("d")
syst_down_tot = array("d")
up_tot = array("d")
down_tot = array("d")
truth_tot = array("d")


syst = ["up","down","btagsf","eff_l","met","p_res_e","p_scale_e","p_scale_j","p_scale_m","p_scale_met"]

for bin in range(1,7):
  err_up = 0
  err_down = 0

  central_value = in_file.Get("central").GetBinContent(bin)
  stat = in_file.Get("central").GetBinError(bin)
  
  print "bin ",bin," = ", central_value," +/- ", stat

  truth = file_truth.Get("hTrue").GetBinContent(bin)

  print "truth = ",truth

  for s in syst:
    if "up" in s or "down" in s:
      up = in_file.Get(s).GetBinContent(bin)
      down = in_file.Get(s).GetBinContent(bin)
    else:
      up = in_file.Get(s+"Up").GetBinContent(bin)
      down = in_file.Get(s+"Down").GetBinContent(bin)
  
    print "up = ",up, " down = ",down, " central = ", central_value

    if ( (up > central_value) and (down < central_value) ) :
      err_up += (up-central_value)**2
      err_down += (down - central_value)**2
    elif ( (up < central_value) and (down > central_value) ) :
      err_up += (down-central_value)**2
      err_down += (up - central_value)**2
    elif ( (up > central_value) and (down > central_value) ) :
      err_up += max((up-central_value)**2, (down - central_value)**2)
      err_down += 0
    elif ( (up < central_value) and (down < central_value) ) :
      err_up += 0
      err_down += max((up-central_value)**2, (down - central_value)**2)
    elif ( (up == central_value) and (down > central_value) ) :
      err_up += (down-central_value)**2
      err_down += 0
    elif ( (up == central_value) and (down < central_value)  ) :
      err_up += 0
      err_down += (down - central_value)**2
    elif ( (up > central_value) and (down == central_value) ) :
      err_up += (up-central_value)**2
      err_down += 0
    elif (  (up < central_value) and (down == central_value) ) :
      err_up += 0
      err_down += (up-central_value)**2
    else :
      print " ggH SYSTEMATIC ERROR...:)"
      break
  
  central_value_tot.append((central_value)/(err_pth[bin-1]*2*lumi))

  print "central tot = ", (central_value)/(err_pth[bin-1]*2*lumi)
  
  syst_up_tot.append( sqrt( err_up )/(err_pth[bin-1]*2*lumi) )
  syst_down_tot.append( sqrt( err_down )/(err_pth[bin-1]*2*lumi) )


  up_tot.append( sqrt( err_up  + (stat)**2  )/(err_pth[bin-1]*2*lumi) )
  down_tot.append( sqrt( err_down + (stat)**2 )/(err_pth[bin-1]*2*lumi) )
 
  truth_tot.append(truth/(err_pth[bin-1]*2*lumi))
  
#  print truth/(err_pth[bin-1]*2*lumi)

print up_tot, down_tot

gsyst = TGraphAsymmErrors(6, pthbins, central_value_tot, err_pth, err_pth, syst_down_tot, syst_up_tot)
gtot = TGraphAsymmErrors(6, pthbins, central_value_tot, err_pth, err_pth, down_tot, up_tot)
gtruth = TGraphErrors(6, pthbins, truth_tot, err_pth, zero)

gtot.SetTitle("")
gtot.SetLineColor(2)
gtot.SetLineWidth(3) 
gtot.SetFillColor(2) 
gtot.SetFillStyle(3001) 
#gtot.SetTitle("Differential_cross_section") 
gtot.GetYaxis().SetTitle("#frac{d#sigma}{dp_{T}^{H}} [#frac{fb}{GeV}]") 
gtot.GetXaxis().SetRangeUser(0,200)
gtot.GetXaxis().SetTitle("p_{T}^{H} [GeV]") 
gtot.Draw("AP2") 

gsyst.SetLineColor(4) 
gsyst.SetFillColor(4) 
gsyst.SetFillStyle(3001) 
gsyst.SetLineWidth(3) 
gsyst.Draw("P2") 
gtot.Draw("P")
gsyst.Draw("P")

gtruth.SetLineColor(kGreen)
gtruth.SetLineWidth(3)
gtruth.Draw("P")

leg = TLegend(0.7,0.65,0.4,0.3)
leg.SetTextFont(72) 
leg.SetTextSize(0.04) 
leg.AddEntry(gtot,"Stat+Syst error","F") 
leg.AddEntry(gsyst,"Syst error","F") 
leg.AddEntry(gtruth,"MC truth","L")
leg.Draw() 

a=raw_input()
