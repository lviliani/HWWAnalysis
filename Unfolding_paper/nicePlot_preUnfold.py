#!/usr/bin/env python

from ROOT import *
from array import *
from math import *
import CMS_lumi, tdrstyle

#gInterpreter.ExecuteMacro("/afs/cern.ch/work/l/lviliani/DatacardFramework/CMSSW_6_1_1/src/HWWAnalysis/ShapeAnalysis/macros/LatinoStyle2.C")

#set the tdr style
tdrstyle.setTDRStyle()

#change the CMS_lumi variables (see CMS_lumi.py)
CMS_lumi.lumi_8TeV = "19.4 fb^{-1}"
CMS_lumi.writeExtraText = 0
CMS_lumi.extraText = "Preliminary"

iPos = 1

H_ref = 600
W_ref = 800 
W = W_ref
H  = H_ref

# references for T, B, L, R
T = 0.08*H_ref
B = 0.12*H_ref 
L = 0.14*W_ref
R = 0.04*W_ref

#canvas = TCanvas("c2","c2",50,50,W,H)
canvas = TCanvas("c2","c2")
canvas.SetFillColor(0)
canvas.SetBorderMode(0)
canvas.SetFrameFillStyle(0)
canvas.SetFrameBorderMode(0)
canvas.SetLeftMargin( L/W )
canvas.SetRightMargin( R/W )
canvas.SetTopMargin( T/H )
canvas.SetBottomMargin( B/H )
canvas.SetTickx(0)
canvas.SetTicky(0)
canvas.SetGrid()

lumi = 19.468
in_file = TFile("plotsFromFit_ggWWscale.root")
file_truth = TFile("TheMeasure.root")
file_fakes = TFile("fakes_reco.root")
file_fakes_XH = TFile("fakes_reco_XH.root")
file_VH = TFile("TheMeasureVH.root")

pthbins = array("d",[7.5,30,65,105,145,182.5])
err_pth = array("d",[7.5,15,20,20,20,17.5])
zero = array("d",[0,0,0,0,0,0])
central_value_tot = array("d")
syst_up_tot = array("d")
syst_down_tot = array("d")
up_tot = array("d")
down_tot = array("d")
truth_tot = array("d")
truth_XH_tot = array("d")
truth_scaleup = array("d")
truth_scaledown = array("d")
stat_error_tot = array("d")

XH_bins = array("d",[0,15,45,85,125,165,200])
h_XH = TH1F("hXH","hXH",len(XH_bins)-1,XH_bins)

syst = ["btagsf","eff_l","met","p_res_e","p_scale_e","p_scale_j","p_scale_m","p_scale_met"]

textable=""
textable+="\\begin{tabular}{c|ccccc}\n"
textable+="Bin & Unfolded value & Total error & Stat error & Syst error & MC truth \\\ \n"
textable+="\hline \n\hline \n"


for bin in range(1,7):
  err_up = 0
  err_down = 0

  central_value = in_file.Get("HcentralStat").GetBinContent(bin)
  syst_no_matrix = in_file.Get("HcentralNotChangingRM").GetBinError(bin)
  
  stat_error = in_file.Get("HcentralStat").GetBinError(bin)

  truth = file_truth.Get("hMeas").GetBinContent(bin) - file_fakes.Get("hfake").GetBinContent(bin)
  truth_XH = file_VH.Get("hMeas").GetBinContent(bin) - file_fakes_XH.Get("hFakes").GetBinContent(bin)

  for s in syst:
    up = in_file.Get("HCMS_8TeV_"+s+"Up").GetBinContent(bin)
    down = in_file.Get("HCMS_8TeV_"+s+"Down").GetBinContent(bin)
  
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

 # print "central tot = ", (central_value)/(err_pth[bin-1]*2*lumi)
  

  up_tot.append( sqrt( err_up  + (syst_no_matrix)**2  )/(err_pth[bin-1]*2*lumi) )
  down_tot.append( sqrt( err_down + (syst_no_matrix)**2 )/(err_pth[bin-1]*2*lumi) )
 
  stat_error_tot.append(stat_error/(err_pth[bin-1]*2*lumi))

  truth_tot.append(truth/(err_pth[bin-1]*2*lumi))
  truth_scaleup.append( (truth/(err_pth[bin-1]*2*lumi))*(0.1) )
  truth_scaledown.append( (truth/(err_pth[bin-1]*2*lumi))*(0.1) )

  h_XH.SetBinContent(bin,(truth_XH)/(err_pth[bin-1]*2*lumi)) 

#  print "###### BIN ",bin
#  print "central tot = ", (central_value)/(err_pth[bin-1]*2*lumi)
#  print "Truth = ", truth/(err_pth[bin-1]*2*lumi)
#  print "Err up = ",up_tot, " Err down = ", down_tot
#  print "Stat error = ", stat_error_tot
#  string = "%1.2f" %central_value_tot[bin-1]
#  textable+=str(bin)+" & $%1.2f^{+%1.1f}_{-%1.1f}$ & %1.2f \\\ \n" %(central_value_tot[bin-1], (100*up_tot[bin-1]/central_value_tot[bin-1]), (100*down_tot[bin-1]/central_value_tot[bin-1]), truth_tot[bin-1])
  textable+=str(bin)+" & $%1.2f & +%1.1f/-%1.1f & \pm%1.1f & +%1.1f/-%1.1f  &  %1.2f \\\ \n" %(central_value_tot[bin-1], (100*up_tot[bin-1]/central_value_tot[bin-1]), (100*down_tot[bin-1]/central_value_tot[bin-1]), (100*stat_error_tot[bin-1]/central_value_tot[bin-1]), 100*(sqrt(up_tot[bin-1]**2 - stat_error_tot[bin-1]**2)/central_value_tot[bin-1]), 100*(sqrt(down_tot[bin-1]**2 - stat_error_tot[bin-1]**2)/central_value_tot[bin-1]), truth_tot[bin-1])
textable+="\hline \n"
textable+="\end{tabular}\n"
  
print textable

for bin in range(6): 
  syst_up_tot.append( sqrt(up_tot[bin]**2 - stat_error_tot[bin]**2) )
  syst_down_tot.append( sqrt(down_tot[bin]**2 - stat_error_tot[bin]**2) )

#x_pth_stat = array("d",[7.5*0.2,15*0.2,20*0.2,20*0.2,20*0.2,17.5*0.2])
x_pth_stat = array("d",[4,4,4,4,4,4])

#x_pth_syst = array("d",[7.5*0.1,15*0.1,20*0.1,20*0.1,20*0.1,17.5*0.1])
x_pth_syst = array("d",[2,2,2,2,2,2])

gsyst = TGraphAsymmErrors(6, pthbins, central_value_tot, x_pth_syst, x_pth_syst, syst_down_tot, syst_up_tot)
gtot = TGraphAsymmErrors(6, pthbins, central_value_tot, zero, zero, down_tot, up_tot)
gtruth = TGraphErrors(6, pthbins, truth_tot, err_pth, zero)
gtruth_scale = TGraphAsymmErrors(6, pthbins, truth_tot, err_pth, err_pth, truth_scaleup, truth_scaledown)
gstat = TGraphErrors(6, pthbins, central_value_tot, x_pth_stat, stat_error_tot)

gtot.SetTitle("")
gtot.SetLineColor(kBlack)
gtot.SetLineWidth(2) 
#gtot.SetFillColor(2) 
#gtot.SetFillStyle(3002) 
#gtot.SetTitle("Differential_cross_section") 
#gtot.GetYaxis().SetTitle("d#sigma/dp_{T,reco}^{H} #left[#frac{fb}{GeV}#right]") 
gtot.GetYaxis().SetTitle("d#sigma/dp_{T,reco}^{H} [fb/GeV]")
gtot.GetYaxis().SetLabelSize(0.04)
gtot.GetYaxis().SetTitleSize(0.04)
gtot.GetYaxis().SetTitleOffset(1.5)
gtot.GetXaxis().SetRangeUser(0,200)
gtot.GetYaxis().SetRangeUser(-0.02,0.4)
gtot.GetXaxis().SetTitle("p_{T,reco}^{H} [GeV]") 
gtot.GetXaxis().SetLabelSize(0.04)
gtot.GetXaxis().SetTitleSize(0.04)
gtot.GetXaxis().SetTitleOffset(1.2)
gtot.Draw("AP") 

gstat.SetLineColor(kWhite) 
gstat.SetFillColor(kAzure-8) 
#gstat.SetFillStyle(3002) 
gstat.SetLineWidth(1) 
#gstat.Draw("P2Z") 

gsyst.SetLineColor(kWhite) 
#gsyst.SetFillColor(4) 
#gsyst.SetFillStyle(3004) 
gsyst.SetFillColor(kGray)
gsyst.SetLineWidth(1) 
#gsyst.Draw("P2Z") 

gStyle.SetHatchesSpacing(0.5)
gStyle.SetHatchesLineWidth(2)

gtruth.SetMarkerSize(0)
gtruth.SetLineColor(kGreen+1)
gtruth.SetLineWidth(3)
#gtruth.SetLineStyle(7)

gtruth_scale.SetFillStyle(3354)
gtruth_scale.SetLineWidth(3)
gtruth_scale.SetLineColor(kGreen+1)
gtruth_scale.SetFillColor(kGreen)


h_XH.SetMarkerSize(0)
h_XH.SetLineWidth(2)
h_XH.SetLineColor(kTeal-7)
h_XH.SetFillColor(kTeal-8)
h_XH.Draw("HISTsame")

gtruth_scale.Draw("2Z")
gtruth.Draw("PZ")
gstat.Draw("P2Z")
gsyst.Draw("P2Z")
gtot.Draw("PZ")

gPad.RedrawAxis()


leg = TLegend(0.45,0.45,0.9,0.9)
leg.SetBorderSize(0)
leg.SetFillStyle(0)
#leg.SetFillColor(kWhite)
#leg.SetTextFont(72) 
#leg.SetTextSize(0.04)
leg.AddEntry(gtot,"Data","lep") 
leg.AddEntry(gstat,"Statistical uncertainty","F")
leg.AddEntry(gsyst,"Systematic uncertainty","F")
leg.AddEntry(gtruth_scale,"ggH (PowhegV1) + XH","FL")
leg.AddEntry(h_XH, "XH = VBF + VH","F")

leg.Draw() 

CMS_lumi.CMS_lumi(canvas, 2, iPos)

a=raw_input()
