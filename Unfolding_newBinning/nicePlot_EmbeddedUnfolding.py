#!/usr/bin/env python

from ROOT import *
from array import *
from math import *
import CMS_lumi, tdrstyle

#gInterpreter.ExecuteMacro("/afs/cern.ch/work/l/lviliani/DatacardFramework/CMSSW_6_1_1/src/HWWAnalysis/ShapeAnalysis/macros/LatinoStyle2.C")

#set the tdr style
tdrstyle.setTDRStyle()

#change the CMS_lumi variables (see CMS_lumi.py)
CMS_lumi.lumi_8TeV = "19.47 fb^{-1}"
CMS_lumi.writeExtraText = 1
CMS_lumi.extraText = "Preliminary"

iPos = 33

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


lumi = 19.468
in_file = TFile("plotsFromFit_embeddedUnfolding.root")
file_truth = TFile("TheTruth.root")

pthbins = array("d",[7.5,30,65,105,145,182.5])
err_pth = array("d",[7.5,15,20,20,20,17.5])
zero = array("d",[0,0,0,0,0,0])
central_value_tot = array("d")
syst_up_tot = array("d")
syst_down_tot = array("d")
up_tot = array("d")
down_tot = array("d")
truth_tot = array("d")
stat_error_tot = array("d")

syst = []

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

  truth = file_truth.Get("hTrue").GetBinContent(bin)

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

x_pth = array("d",[7.5*0.5,15*0.5,20*0.5,20*0.5,20*0.5,17.5*0.5])


gsyst = TGraphAsymmErrors(6, pthbins, central_value_tot, x_pth, x_pth, syst_down_tot, syst_up_tot)
gtot = TGraphAsymmErrors(6, pthbins, central_value_tot, zero, zero, down_tot, up_tot)
gtruth = TGraphErrors(6, pthbins, truth_tot, err_pth, zero)
gstat = TGraphErrors(6, pthbins, central_value_tot, x_pth, stat_error_tot)

gtot.SetTitle("")
gtot.SetLineColor(kBlack)
gtot.SetLineWidth(2) 
#gtot.SetFillColor(2) 
#gtot.SetFillStyle(3002) 
#gtot.SetTitle("Differential_cross_section") 
gtot.GetYaxis().SetTitle("d#sigma/dp_{T,reco}^{H} #left[#frac{fb}{GeV}#right]") 
gtot.GetYaxis().SetLabelSize(0.04)
gtot.GetYaxis().SetTitleSize(0.04)
gtot.GetYaxis().SetTitleOffset(1.5)
gtot.GetXaxis().SetRangeUser(0,200)
gtot.GetXaxis().SetTitle("p_{T,reco}^{H} [GeV]") 
gtot.GetXaxis().SetLabelSize(0.04)
gtot.GetXaxis().SetTitleSize(0.04)
gtot.GetXaxis().SetTitleOffset(1.2)
gtot.Draw("AP") 

#gstat.SetLineColor(kBlack) 
gstat.SetFillColor(kAzure-8) 
#gstat.SetFillStyle(3002) 
gstat.SetLineWidth(1) 
gstat.Draw("P2Z") 
gtot.Draw("PZ")

#gsyst.SetLineColor(4) 
#gsyst.SetFillColor(4) 
gsyst.SetFillStyle(3004) 
gsyst.SetLineWidth(1) 
gsyst.Draw("P2Z") 


gtruth.SetMarkerSize(0)
gtruth.SetLineColor(kGreen)
gtruth.SetLineWidth(3)
#gtruth.SetLineStyle(7)
gtruth.Draw("PZ")
gtot.Draw("PZ")


leg = TLegend(0.4,0.6,0.6,0.8)
leg.SetBorderSize(0)
leg.SetFillColor(kWhite)
#leg.SetTextFont(72) 
leg.SetTextSize(0.04)
leg.AddEntry(gtot,"Data","lep") 
leg.AddEntry(gstat,"statistical uncertainty","F")
leg.AddEntry(gsyst,"systematic uncertainty","F")
leg.AddEntry(gtruth,"POWHEG","l")
leg.Draw() 

CMS_lumi.CMS_lumi(canvas, 2, iPos)

a=raw_input()
