#!/usr/bin/env python

from ROOT import *
from array import *
from math import *


def finalPlot(input_file, truth_file):

  #gInterpreter.ExecuteMacro("/afs/cern.ch/work/l/lviliani/DatacardFramework/CMSSW_6_1_1/src/HWWAnalysis/ShapeAnalysis/macros/LatinoStyle2.C")

  #gStyle.SetHatchesSpacing(0.6)
  #gStyle.SetHatchesLineWidth(2)

  lumi = 19.468
  in_file = TFile(input_file)
  file_truth = TFile(truth_file)

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

  syst = ["up","down","btagsf","eff_l","met","p_res_e","p_scale_e","p_scale_j","p_scale_m","p_scale_met"]

  textable=""
  textable+="\\begin{tabular}{c|ccccc}\n"
  textable+="Bin & Unfolded value & Total error & Stat error & Syst error & MC truth \\\ \n"
  textable+="\hline \n\hline \n"


  for bin in range(1,7):
    err_up = 0
    err_down = 0
  
    central_value = in_file.Get("central").GetBinContent(bin)
    syst_no_matrix = in_file.Get("central").GetBinError(bin)
    
    stat_error = in_file.Get("statOnly").GetBinError(bin)
  
    truth = file_truth.Get("hTrue").GetBinContent(bin)
  
    for s in syst:
      if "up" in s or "down" in s:
        up = in_file.Get(s).GetBinContent(bin)
        down = in_file.Get(s).GetBinContent(bin)
      else:
        up = in_file.Get(s+"Up").GetBinContent(bin)
        down = in_file.Get(s+"Down").GetBinContent(bin)

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
  #  textable+=str(bin)+" & "+str((central_value)/(err_pth[bin-1]*2*lumi))^{+"+"+str(up_tot[bin-1])+"}_{-"+str(down_tot[bin-1])+"} & "+str(truth/(err_pth[bin-1]*2*lumi))+"\\\ \n"
  textable+="\hline \n"
  textable+="\end{tabular}\n"

  print textable

  gtot = TGraphAsymmErrors(6, pthbins, central_value_tot, err_pth, err_pth, down_tot, up_tot)
  gtruth = TGraphErrors(6, pthbins, truth_tot, err_pth, zero)
  gstat = TGraphErrors(6, pthbins, central_value_tot, err_pth, stat_error_tot)

#  gtot.SetTitle("k_{reg} = 5")
  gtot.SetLineColor(2)
  gtot.SetLineWidth(3) 
  gtot.SetFillColor(2) 
  gtot.SetFillStyle(3002) 
  gtot.GetYaxis().SetTitle("#frac{d#sigma}{dp_{T}^{H}} #left[#frac{fb}{GeV}#right]") 
  gtot.GetXaxis().SetRangeUser(0,200)
  gtot.GetXaxis().SetTitle("p_{T}^{H} [GeV]") 
  gtot.Draw("AP2") 

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

  leg = TLegend(0.6,0.6,0.9,0.9)
  leg.SetFillColor(kWhite)
#  leg.SetBorderSize(0)
  leg.SetTextFont(72) 
  leg.SetTextSize(0.04) 
  leg.AddEntry(gtot,"Total uncertainty","F") 
  leg.AddEntry(gstat,"Statistical uncertainty","F") 
  leg.AddEntry(gtruth,"MC truth","L")
  leg.Draw() 

  a=raw_input()
