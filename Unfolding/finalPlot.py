#!/usr/bin/env python

from ROOT import *
from array import *
from math import *

gInterpreter.ExecuteMacro("/afs/cern.ch/work/l/lviliani/DatacardFramework/CMSSW_6_1_1/src/HWWAnalysis/ShapeAnalysis/macros/LatinoStyle2.C")

lumi = 19.468

file_ggH = TFile("syst_ggH_NEW.root")
file_vbf = TFile("syst_vbf_NEW.root")
file_truth = TFile("TRUTH.root")

pthbins = array("d",[7.5,30,66,106,143.5,181])
err_pth = array("d",[7.5,15,21,19,18.5,19])
zero = array("d",[0,0,0,0,0,0])
central_tot = array("d")
syst_up_tot = array("d")
syst_down_tot = array("d")
up_tot = array("d")
down_tot = array("d")
truth_tot = array("d")


syst = ["CMS_8TeV_hww_FakeRate","CMS_8TeV_norm_DYTT","CMS_8TeV_norm_Vg","QCDscale_VV","QCDscale_VVV","QCDscale_VgS","QCDscale_WW","QCDscale_WW1in","QCDscale_ggWW","lumi_8TeV","pdf_gg_ACCEPT","pdf_qqbar_ACCEPT","CMS_8TeV_btagsf","CMS_8TeV_eff_l","CMS_8TeV_met","CMS_8TeV_p_res_e","CMS_8TeV_p_scale_e","CMS_8TeV_p_scale_j","CMS_8TeV_p_scale_m","CMS_8TeV_p_scale_met"]

for bin in range(1,7):
  err_up_ggH = 0
  err_down_ggH = 0
  err_up_vbf = 0
  err_down_vbf = 0
    

  central_ggH = file_ggH.Get("central").GetBinContent(bin)
  stat_ggH = file_ggH.Get("central").GetBinError(bin)
  
  print "ggH bin ",bin," = ", central_ggH," +/- ", stat_ggH

  central_vbf = file_vbf.Get("central").GetBinContent(bin)
  stat_vbf = file_vbf.Get("central").GetBinError(bin)

  print "vbf bin ",bin," = ", central_vbf," +/- ", stat_vbf

  truth = file_truth.Get("hTrue").GetBinContent(bin)

  print "truth = ",truth

  for s in syst:
    up_ggH = file_ggH.Get(s+"Up").GetBinContent(bin)
    down_ggH = file_ggH.Get(s+"Down").GetBinContent(bin)
    up_vbf = file_vbf.Get(s+"Up").GetBinContent(bin)
    down_vbf = file_vbf.Get(s+"Down").GetBinContent(bin)
  
    print "up ggH = ",up_ggH, " down ggH = ",down_ggH, " central = ", central_ggH

    if ( (up_ggH > central_ggH) and (down_ggH < central_ggH) ) :
      err_up_ggH += (up_ggH-central_ggH)**2
      err_down_ggH += (down_ggH - central_ggH)**2
    elif ( (up_ggH < central_ggH) and (down_ggH > central_ggH) ) :
      err_up_ggH += (down_ggH-central_ggH)**2
      err_down_ggH += (up_ggH - central_ggH)**2
    elif ( (up_ggH > central_ggH) and (down_ggH > central_ggH) ) :
      err_up_ggH += max((up_ggH-central_ggH)**2, (down_ggH - central_ggH)**2)
      err_down_ggH += 0
    elif ( (up_ggH < central_ggH) and (down_ggH < central_ggH) ) :
      err_up_ggH += 0
      err_down_ggH += max((up_ggH-central_ggH)**2, (down_ggH - central_ggH)**2)
    elif ( (up_ggH == central_ggH) and (down_ggH > central_ggH) ) :
      err_up_ggH += (down_ggH-central_ggH)**2
      err_down_ggH += 0
    elif ( (up_ggH == central_ggH) and (down_ggH < central_ggH)  ) :
      err_up_ggH += 0
      err_down_ggH += (down_ggH - central_ggH)**2
    elif ( (up_ggH > central_ggH) and (down_ggH == central_ggH) ) :
      err_up_ggH += (up_ggH-central_ggH)**2
      err_down_ggH += 0
    elif (  (up_ggH < central_ggH) and (down_ggH == central_ggH) ) :
      err_up_ggH += 0
      err_down_ggH += (up_ggH-central_ggH)**2
    else :
      print " ggH SYSTEMATIC ERROR...:)"
      break

    if ( (up_vbf > central_vbf) and (down_vbf < central_vbf) ) :
      err_up_vbf += (up_vbf-central_vbf)**2
      err_down_vbf += (down_vbf - central_vbf)**2
    elif ( (up_vbf < central_vbf) and (down_vbf > central_vbf) ) :
      err_up_vbf += (down_vbf-central_vbf)**2
      err_down_vbf += (up_vbf - central_vbf)**2
    elif ( (up_vbf > central_vbf) and (down_vbf > central_vbf) ) :
      err_up_vbf += max((up_vbf-central_vbf)**2, (down_vbf - central_vbf)**2)
      err_down_vbf += 0
    elif ( (up_vbf < central_vbf) and (down_vbf < central_vbf) ) :
      err_up_vbf += 0
      err_down_vbf += max((up_vbf-central_vbf)**2, (down_vbf - central_vbf)**2)
    elif ( (up_vbf == central_vbf) and (down_vbf > central_vbf) ) :
      err_up_vbf += (down_vbf-central_vbf)**2
      err_down_vbf += 0
    elif ( (up_vbf == central_vbf) and (down_vbf < central_vbf)  ) :
      err_up_vbf += 0
      err_down_vbf += (down_vbf - central_vbf)**2
    elif (  (up_vbf > central_vbf) and (down_vbf == central_vbf) ) :
      err_up_vbf += (up_vbf-central_vbf)**2
      err_down_vbf += 0
    elif (  (up_vbf < central_vbf) and (down_vbf == central_vbf) ) :
      err_up_vbf += 0
      err_down_vbf += (up_vbf-central_vbf)**2

    else :
      print " VBF SYSTEMATIC ERROR...:)"
      break
  
#  central_tot = central_ggH+central_vbf
  central_tot.append((central_ggH+central_vbf)/(err_pth[bin-1]*2*lumi))

  print "central tot = ", (central_ggH+central_vbf)/(err_pth[bin-1]*2*lumi)
  
#  syst_up_tot = (sqrt( err_up_ggH ) + sqrt( err_up_vbf ))/(err_pth[bin]*2*lumi)
#  syst_down_tot = (sqrt( err_down_ggH ) + sqrt( err_down_vbf ))/(err_pth[bin]*2*lumi)
  syst_up_tot.append((sqrt( err_up_ggH ) + sqrt( err_up_vbf ))/(err_pth[bin-1]*2*lumi))
  syst_down_tot.append(( sqrt( err_down_ggH ) +sqrt(  err_down_vbf))/(err_pth[bin-1]*2*lumi))

#  stat_tot = (stat_ggH+stat_vbf)/(err_pth[bin]*2*lumi)

#  up_tot = sqrt( (sqrt( err_up_ggH ) + sqrt( err_up_vbf ))**2 + (stat_ggH+stat_vbf)**2  )/(err_pth[bin]*2*lumi)
#  down_tot = sqrt( (sqrt( err_down_ggH ) + sqrt( err_down_vbf ))**2 + (stat_ggH+stat_vbf)**2  )/(err_pth[bin]*2*lumi)

  up_tot.append( sqrt( (sqrt( err_up_ggH ) + sqrt( err_up_vbf ))**2 + (stat_ggH+stat_vbf)**2  )/(err_pth[bin-1]*2*lumi) )
  down_tot.append( sqrt( (sqrt( err_down_ggH ) + sqrt( err_down_vbf ))**2 + (stat_ggH+stat_vbf)**2  )/(err_pth[bin-1]*2*lumi) )

#  up_tot.append( sqrt(  err_up_ggH  + err_up_vbf + stat_ggH**2 + stat_vbf**2  )/(err_pth[bin-1]*2*lumi))
#  down_tot.append( sqrt(  err_down_ggH + err_down_vbf + stat_ggH**2 + stat_vbf**2  )/(err_pth[bin-1]*2*lumi))
 
  truth_tot.append(truth/(err_pth[bin-1]*lumi))
  
#  print truth/(err_pth[bin-1]*2*lumi)

print up_tot, down_tot

gsyst = TGraphAsymmErrors(6, pthbins, central_tot, err_pth, err_pth, syst_down_tot, syst_up_tot)
gtot = TGraphAsymmErrors(6, pthbins, central_tot, err_pth, err_pth, down_tot, up_tot)
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
