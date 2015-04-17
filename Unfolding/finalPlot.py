#!/usr/bin/env python

from ROOT import *
from array import *
from math import *

lumi = 19.468

file_ggH = TFile("syst_ggH.root")
file_vbf = TFile("syst_vbf.root")

pthbins = array("d",[7.5,30,66,106,143.5,181])
err_pth = array("d",[7.5,15,21,19,18.5,19])
central_tot = array("d")
syst_up_tot = array("d")
syst_down_tot = array("d")
up_tot = array("d")
down_tot = array("d")



syst = ["CMS_8TeV_hww_FakeRate","CMS_8TeV_norm_DYTT","CMS_8TeV_norm_Vg","QCDscale_VV","QCDscale_VVV","QCDscale_VgS","QCDscale_WW","QCDscale_WW1in","QCDscale_ggWW","lumi_8TeV","pdf_gg","pdf_qqbar","CMS_8TeV_btagsf","CMS_8TeV_eff_l","CMS_8TeV_met","CMS_8TeV_p_res_e","CMS_8TeV_p_scale_e","CMS_8TeV_p_scale_j","CMS_8TeV_p_scale_m","CMS_8TeV_p_scale_met"]

for bin in range(1,7):
  err_up_ggH = 0
  err_down_ggH = 0
  err_up_vbf = 0
  err_down_vbf = 0
 
  

  central_ggH = file_ggH.Get("central").GetBinContent(bin)
  stat_ggH = file_ggH.Get("central").GetBinError(bin)
  
  central_vbf = file_vbf.Get("central").GetBinContent(bin)
  stat_vbf = file_vbf.Get("central").GetBinError(bin)


  for s in syst:
    up_ggH = file_ggH.Get(s+"Up").GetBinContent(bin)
    down_ggH = file_ggH.Get(s+"Down").GetBinContent(bin)
    up_vbf = file_vbf.Get(s+"Up").GetBinContent(bin)
    down_vbf = file_vbf.Get(s+"Down").GetBinContent(bin)

    if ( up_ggH > central_ggH and down_ggH < central_ggH) :
      err_up_ggH += (up_ggH-central_ggH)**2
      err_down_ggH += (down_ggH - central_ggH)**2
    elif ( up_ggH < central_ggH and down_ggH > central_ggH) :
      err_up_ggH += (down_ggH-central_ggH)**2
      err_down_ggH += (up_ggH - central_ggH)**2
    elif ( up_ggH > central_ggH and down_ggH > central_ggH) :
      err_up_ggH += max((up_ggH-central_ggH)**2, (down_ggH - central_ggH)**2)
      err_down_ggH += 0
    elif ( up_ggH < central_ggH and down_ggH < central_ggH) :
      err_up_ggH += 0
      err_down_ggH += max((up_ggH-central_ggH)**2, (down_ggH - central_ggH)**2)
    else :
      print "SYSTEMATIC ERROR...:)"
      break

    if ( up_vbf > central_vbf and down_vbf < central_vbf) :
      err_up_vbf += (up_vbf-central_vbf)**2
      err_down_vbf += (down_vbf - central_vbf)**2
    elif ( up_vbf < central_vbf and down_vbf > central_vbf) :
      err_up_vbf += (down_vbf-central_vbf)**2
      err_down_vbf += (up_vbf - central_vbf)**2
    elif ( up_vbf > central_vbf and down_vbf > central_vbf) :
      err_up_vbf += max((up_vbf-central_vbf)**2, (down_vbf - central_vbf)**2)
      err_down_vbf += 0
    elif ( up_vbf < central_vbf and down_vbf < central_vbf) :
      err_up_vbf += 0
      err_down_vbf += max((up_vbf-central_vbf)**2, (down_vbf - central_vbf)**2)
    else :
      print "SYSTEMATIC ERROR...:)"
      break
  
#  central_tot = central_ggH+central_vbf
  central_tot.append((central_ggH+central_vbf)/(err_pth[bin-1]*2*lumi))
  
#  syst_up_tot = (sqrt( err_up_ggH ) + sqrt( err_up_vbf ))/(err_pth[bin]*2*lumi)
#  syst_down_tot = (sqrt( err_down_ggH ) + sqrt( err_down_vbf ))/(err_pth[bin]*2*lumi)
  syst_up_tot.append((sqrt( err_up_ggH ) + sqrt( err_up_vbf ))/(err_pth[bin-1]*2*lumi))
  syst_down_tot.append((sqrt( err_down_ggH ) + sqrt( err_down_vbf ))/(err_pth[bin-1]*2*lumi))

#  stat_tot = (stat_ggH+stat_vbf)/(err_pth[bin]*2*lumi)

#  up_tot = sqrt( (sqrt( err_up_ggH ) + sqrt( err_up_vbf ))**2 + (stat_ggH+stat_vbf)**2  )/(err_pth[bin]*2*lumi)
#  down_tot = sqrt( (sqrt( err_down_ggH ) + sqrt( err_down_vbf ))**2 + (stat_ggH+stat_vbf)**2  )/(err_pth[bin]*2*lumi)

  up_tot.append( sqrt( (sqrt( err_up_ggH ) + sqrt( err_up_vbf ))**2 + (stat_ggH+stat_vbf)**2  )/(err_pth[bin-1]*2*lumi))
  down_tot.append(sqrt( (sqrt( err_down_ggH ) + sqrt( err_down_vbf ))**2 + (stat_ggH+stat_vbf)**2  )/(err_pth[bin-1]*2*lumi))
 
gsyst = TGraphAsymmErrors(6, pthbins, central_tot, err_pth, err_pth, syst_down_tot, syst_up_tot)
gtot = TGraphAsymmErrors(6, pthbins, central_tot, err_pth, err_pth, down_tot, up_tot)

gtot.SetLineColor(2)
gtot.SetLineWidth(3) 
gtot.SetFillColor(2) 
gtot.SetFillStyle(3001) 
gtot.SetTitle("Differential_cross_section") 
gtot.GetYaxis().SetTitle("frac{d#sigma}{dp_{t}^{H}} [#frac{fb}{GeV}]") 
gtot.GetXaxis().SetTitle("p_{t}^{H} [GeV]") 
gtot.Draw("AP2") 

gsyst.SetLineColor(4) 
gsyst.SetFillColor(4) 
gsyst.SetFillStyle(3001) 
gsyst.SetLineWidth(3) 
gsyst.Draw("P2") 
gtot.Draw("P")
gsyst.Draw("P")

leg = TLegend(0.7,0.65,0.4,0.3)
leg.SetTextFont(72) 
leg.SetTextSize(0.04) 
leg.AddEntry(gtot,"Stat+Syst error","F") 
leg.AddEntry(gsyst,"Syst error","F") 
leg.Draw() 

a=raw_input()
