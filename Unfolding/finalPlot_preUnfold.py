#!/usr/bin/env python

from ROOT import *
from array import *
from math import *

gInterpreter.ExecuteMacro("/afs/cern.ch/work/l/lviliani/DatacardFramework/CMSSW_6_1_1/src/HWWAnalysis/ShapeAnalysis/macros/LatinoStyle2.C")

lumi = 19.468
in_file = TFile("plotsFromFit_20150604.root")
file_truth = TFile("TheMeasure.root")

pthbins = array("d",[7.5,30,66,106,143.5,181])
err_pth = array("d",[7.5,15,21,19,18.5,19])
zero = array("d",[0,0,0,0,0,0])
central_value_tot = array("d")
syst_up_tot = array("d")
syst_down_tot = array("d")
up_tot = array("d")
down_tot = array("d")
truth_tot = array("d")
stat_error_tot = array("d")

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


#  print "bin ",bin," = ", central_value," +/- ", stat

  truth = file_truth.Get("hMeas").GetBinContent(bin)

  for s in syst:
    up = in_file.Get("HCMS_8TeV_"+s+"Up").GetBinContent(bin)
    down = in_file.Get("HCMS_8TeV_"+s+"Down").GetBinContent(bin)
  
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


  up_tot.append( sqrt( err_up  + (syst_no_matrix)**2  )/(err_pth[bin-1]*2*lumi) )
  down_tot.append( sqrt( err_down + (syst_no_matrix)**2 )/(err_pth[bin-1]*2*lumi) )
 
  stat_error_tot.append(stat_error/(err_pth[bin-1]*2*lumi))

  truth_tot.append(truth/(err_pth[bin-1]*2*lumi))

  print "###### BIN ",bin
  print "central tot = ", (central_value)/(err_pth[bin-1]*2*lumi)
  print "Truth = ", truth/(err_pth[bin-1]*2*lumi)
  print "Err up = ",up_tot, " Err down = ", down_tot
#  string = "%1.2f" %central_value_tot[bin-1]
#  textable+=str(bin)+" & $%1.2f^{+%1.1f}_{-%1.1f}$ & %1.2f \\\ \n" %(central_value_tot[bin-1], (100*up_tot[bin-1]/central_value_tot[bin-1]), (100*down_tot[bin-1]/central_value_tot[bin-1]), truth_tot[bin-1])
  textable+=str(bin)+" & $%1.2f & +%1.1f/-%1.1f & \pm%1.1f & +%1.1f/-%1.1f  &  %1.2f \\\ \n" %(central_value_tot[bin-1], (100*up_tot[bin-1]/central_value_tot[bin-1]), (100*down_tot[bin-1]/central_value_tot[bin-1]), (100*stat_error_tot[bin-1]/central_value_tot[bin-1]), 100*(sqrt(up_tot[bin-1]**2 - stat_error_tot[bin-1]**2)/central_value_tot[bin-1]), 100*(sqrt(down_tot[bin-1]**2 - stat_error_tot[bin-1]**2)/central_value_tot[bin-1]), truth_tot[bin-1])
textable+="\hline \n"
textable+="\end{tabular}\n"
  
print textable


#gsyst = TGraphAsymmErrors(6, pthbins, central_value_tot, err_pth, err_pth, syst_down_tot, syst_up_tot)
gtot = TGraphAsymmErrors(6, pthbins, central_value_tot, err_pth, err_pth, down_tot, up_tot)
gtruth = TGraphErrors(6, pthbins, truth_tot, err_pth, zero)
gstat = TGraphErrors(6, pthbins, central_value_tot, err_pth, stat_error_tot)

gtot.SetTitle("")
gtot.SetLineColor(2)
gtot.SetLineWidth(3) 
gtot.SetFillColor(2) 
gtot.SetFillStyle(3002) 
#gtot.SetTitle("Differential_cross_section") 
gtot.GetYaxis().SetTitle("#frac{d#sigma}{dp_{T,reco}^{H}} #left[#frac{fb}{GeV}#right]") 
gtot.GetXaxis().SetRangeUser(0,200)
gtot.GetXaxis().SetTitle("p_{T,reco}^{H} [GeV]") 
gtot.Draw("AP2") 

#gsyst.SetLineColor(4) 
#gsyst.SetFillColor(4) 
#gsyst.SetFillStyle(3001) 
#gsyst.SetLineWidth(3) 
#gsyst.Draw("P2") 
#gtot.Draw("P")
#gsyst.Draw("P")

gstat.SetLineColor(4) 
gstat.SetFillColor(4) 
gstat.SetFillStyle(3002) 
gstat.SetLineWidth(3) 
gstat.Draw("P2") 
gtot.Draw("P")
gstat.Draw("P")

gtruth.SetLineColor(kGreen)
gtruth.SetLineWidth(3)
gtruth.Draw("P")

leg = TLegend(0.7,0.65,0.4,0.3)
leg.SetTextFont(72) 
leg.SetTextSize(0.04) 
leg.AddEntry(gtot,"Total uncertainty","F") 
leg.AddEntry(gstat,"Statistical uncertainty","F") 
leg.AddEntry(gtruth,"MC truth","L")
leg.Draw() 

a=raw_input()
