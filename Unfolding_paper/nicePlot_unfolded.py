#!/usr/bin/env python

from ROOT import *
from array import *
from math import *
import CMS_lumi, tdrstyle
def finalPlot(input_file):

  #set the tdr style
  tdrstyle.setTDRStyle()

  #change the CMS_lumi variables (see CMS_lumi.py)
  CMS_lumi.lumi_8TeV = "19.4 fb^{-1}"
  CMS_lumi.writeExtraText = 0
  CMS_lumi.extraText = "Preliminary"

  #iPos = 33
  iPos = 8

  H_ref = 600
  W_ref = 800
  W = W_ref
  H  = H_ref

  # references for T, B, L, R
  T = 0.08*H_ref
  B = 0.12*H_ref
  L = 0.14*W_ref
  R = 0.04*W_ref

#  canvas = TCanvas("c2","c2",50,50,W,H)
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

  #gStyle.SetHatchesSpacing(0.6)
  #gStyle.SetHatchesLineWidth(2)

  lumi = 19.468
  in_file = TFile(input_file)
  #file_truth = TFile(truth_file)
  file_powhegV2_central = TFile("powhegV2_central.root")
  file_powhegV2_scaleup = TFile("powhegV2_scaleup.root")
  file_powhegV2_scaledown = TFile("powhegV2_scaledown.root")
  file_XH = TFile("TheTruthXH.root")

  pthbins = array("d",[7.5,30,65,105,145,182.5])
  err_pth = array("d",[7.5,15,20,20,20,17.5])
  zero = array("d",[0,0,0,0,0,0])
  central_value_tot = array("d")
  syst_up_tot = array("d")
  syst_down_tot = array("d")
  up_tot = array("d")
  down_tot = array("d")
  up_theo = array("d")
  down_theo = array("d")
  syst_no_matrix_tot = array("d")
  #truth_tot = array("d")
  powhegV2_central_tot = array("d")
  powhegV2_scaleup_tot = array("d")
  powhegV2_scaledown_tot = array("d")
  stat_error_tot = array("d")
  XH_tot = array("d")

  powheg_bins = array("d")
  hres_bins = array("d")
  powheg_err = array("d")
  hres_err = array("d")

  for i in range(6):
    powheg_bins.append(pthbins[i] - err_pth[i]/2)
    powheg_err.append(err_pth[i]/5)
    hres_bins.append(pthbins[i] + err_pth[i]/2)
    hres_err.append(err_pth[i]/5)

##################################################
############## HRes --- Hardcoded ################
##################################################
  hres_central = array("d", [0.342830, 0.268013, 0.820749E-01, 0.271278E-01, 0.116930E-01, 0.144969E-02])
  hres_stat = array("d", [0.553522E-02, 0.298860E-02, 0.249445E-02, 0.131942E-02, 0.269466E-03, 0.199257E-05])
  hres_scaleup = array("d", [0.322700, 0.244752, 0.713427E-01, 0.225048E-01, 0.927317E-02, 0.117876E-02])
  hres_scaledown = array("d", [0.380556, 0.292041, 0.920276E-01, 0.321461E-01, 0.144447E-01, 0.170412E-02])

  print "##################################################"
  print "############## HRes --- Hardcoded ################"
  print "##################################################"
  print "CENTRAL VALUES: ", hres_central
  print "SCALE UP VALUES: ", hres_scaleup
  print "SCALE DONW VALUES: ", hres_scaledown

  syst = ["up","down","btagsf","eff_l","met","p_res_e","p_scale_e","p_scale_j","p_scale_m","p_scale_met"]

  textable=""
  textable+="\\begin{tabular}{c|cccccc}\n"
  textable+="Bin & Unfolded value & Total uncertainty (up/down) & Statistical uncertainty & Type A uncertainty & Type B uncertainty (up/down) & Type C uncertainty (up/down) \\\ \n"
  textable+="\hline \n\hline \n"

  XH_bins = array("d",[0,15,45,85,125,165,200])
  h_XH = TH1F("hXH","hXH",len(XH_bins)-1,XH_bins)

  for bin in range(1,7):
    err_up = 0
    err_down = 0
    err_up_th = 0  
    err_down_th = 0

    XH = file_XH.Get("hTrue").GetBinContent(bin)/(err_pth[bin-1]*2*lumi)

############# HRes ---  emu flavor correction - ew corrections - resummation correction ##############
    hres_scaleup[bin-1] = (hres_central[bin-1]-hres_scaleup[bin-1])*2*1.05*1.06 + XH
    hres_scaledown[bin-1] = (hres_scaledown[bin-1]-hres_central[bin-1])*2*1.05*1.06 + XH
    hres_central[bin-1] = hres_central[bin-1]*2*1.05*1.06 + XH
    hres_stat[bin-1] = hres_stat[bin-1]*2*1.05*1.06
 
    central_value = in_file.Get("central").GetBinContent(bin)
    syst_no_matrix = in_file.Get("central").GetBinError(bin)
    
    stat_error = in_file.Get("statOnly").GetBinError(bin)
  
    #truth = file_truth.Get("hTrue").GetBinContent(bin)
    powhegV2_central = file_powhegV2_central.Get("hDummy").GetBinContent(bin)
    powhegV2_scaleup = powhegV2_central - file_powhegV2_scaleup.Get("hDummy").GetBinContent(bin)
    powhegV2_scaledown = file_powhegV2_scaledown.Get("hDummy").GetBinContent(bin)- powhegV2_central
  
    for s in syst:
      if "up" in s or "down" in s:
        up = in_file.Get(s).GetBinContent(bin)
        down = in_file.Get(s).GetBinContent(bin)
        if ( (up > central_value) and (down < central_value) ) :
          err_up_th += (up-central_value)**2
          err_down_th += (down - central_value)**2
        elif ( (up < central_value) and (down > central_value) ) :
          err_up_th += (down-central_value)**2
          err_down_th += (up - central_value)**2
        elif ( (up > central_value) and (down > central_value) ) :
          err_up_th += max((up-central_value)**2, (down - central_value)**2)
          err_down_th += 0
        elif ( (up < central_value) and (down < central_value) ) :
          err_up_th += 0
          err_down_th += max((up-central_value)**2, (down - central_value)**2)
        elif ( (up == central_value) and (down > central_value) ) :
          err_up_th += (down-central_value)**2
          err_down_th += 0
        elif ( (up == central_value) and (down < central_value)  ) :
          err_up_th += 0
          err_down_th += (down - central_value)**2
        elif ( (up > central_value) and (down == central_value) ) :
          err_up_th += (up-central_value)**2
          err_down_th += 0
        elif (  (up < central_value) and (down == central_value) ) :
          err_up_th += 0
          err_down_th += (up-central_value)**2
        else :
          print " ggH SYSTEMATIC ERROR...:)"
          break

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
        print "Nuisance = ", s, " Up error = ", sqrt(err_up), " Syst no matrix = ", syst_no_matrix, " Stat = ", stat_error


    central_value_tot.append((central_value)/(err_pth[bin-1]*2*lumi))
  
#    syst_up_tot.append( sqrt( err_up )/(err_pth[bin-1]*2*lumi) )
#    syst_down_tot.append( sqrt( err_down )/(err_pth[bin-1]*2*lumi) )


    #### model dependence band summed in quadrature
    #up_tot.append( sqrt( err_up + err_up_th  + (syst_no_matrix)**2 )/(err_pth[bin-1]*2*lumi) )
    #down_tot.append( sqrt( err_down + err_down_th + (syst_no_matrix)**2 )/(err_pth[bin-1]*2*lumi) )
  
    #### model dependence band not summed
    up_tot.append( sqrt( err_up + (syst_no_matrix)**2 )/(err_pth[bin-1]*2*lumi) )
    down_tot.append( sqrt( err_down + (syst_no_matrix)**2 )/(err_pth[bin-1]*2*lumi) ) 

    up_theo.append( sqrt(err_up_th)/(err_pth[bin-1]*2*lumi) )
    down_theo.append( sqrt(err_down_th)/(err_pth[bin-1]*2*lumi) ) 

    stat_error_tot.append(stat_error/(err_pth[bin-1]*2*lumi))
    syst_no_matrix_tot.append( sqrt(syst_no_matrix**2 - stat_error**2)/(err_pth[bin-1]*2*lumi)  )

    XH_tot.append(XH)
    h_XH.SetBinContent(bin,XH)    

    #truth_tot.append(truth/(err_pth[bin-1]*2*lumi))
    powhegV2_central_tot.append(powhegV2_central/(err_pth[bin-1]*2) + XH)
    powhegV2_scaleup_tot.append(powhegV2_scaleup/(err_pth[bin-1]*2) + XH)
    powhegV2_scaledown_tot.append(powhegV2_scaledown/(err_pth[bin-1]*2) + XH)

    print "###### BIN ",bin
    print "central tot = ", (central_value)/(err_pth[bin-1]*2*lumi)
    print "Err up = ", up_tot[bin-1], " Err down = ", down_tot[bin-1]
    print "Stat = ", stat_error_tot[bin-1]
    print "Type A = ", syst_no_matrix_tot[bin-1]
    print "Type B up = ", sqrt(err_up)/(err_pth[bin-1]*2*lumi), "Type B down = ", sqrt(err_down)/(err_pth[bin-1]*2*lumi)
    print "Type C up = ", sqrt(err_up_th)/(err_pth[bin-1]*2*lumi), "Type C down = ", sqrt(err_down_th)/(err_pth[bin-1]*2*lumi)
    textable+=str(bin)+" & %1.3f & +%1.3f/-%1.3f & $\pm$%1.3f & $\pm$%1.3f & +%1.3f/-%1.3f  & +%1.4f/-%1.4f \\\ \n" %(central_value_tot[bin-1], (up_tot[bin-1]), (down_tot[bin-1]), (stat_error_tot[bin-1]), (syst_no_matrix_tot[bin-1]), (sqrt(err_up)/(err_pth[bin-1]*2*lumi)), (sqrt(err_down)/(err_pth[bin-1]*2*lumi)), (sqrt(err_up_th)/(err_pth[bin-1]*2*lumi)), (sqrt(err_down_th)/(err_pth[bin-1]*2*lumi)) )
  textable+="\hline \n"
  textable+="\end{tabular}\n"

  print textable


  for bin in range(6):
    print "bin ",bin, " tot up = ", up_tot[bin], " tot down = ", down_tot[bin], " stat = ", stat_error_tot[bin]
    print up_tot[bin]**2 - stat_error_tot[bin]**2, " ", down_tot[bin]**2 - stat_error_tot[bin]**2
    syst_up_tot.append( sqrt(up_tot[bin]**2 - stat_error_tot[bin]**2 ))
    syst_down_tot.append( sqrt(down_tot[bin]**2 - stat_error_tot[bin]**2 ))

  x_pth = array("d",[7.5*0.5,15*0.5,20*0.5,20*0.5,20*0.5,17.5*0.5])
  x_pth_stat = array("d",[7.5*0.25,15*0.2,20*0.2,20*0.2,20*0.2,17.5*0.2])
  x_pth_syst = array("d",[7.5*0.15,15*0.1,20*0.1,20*0.1,20*0.1,17.5*0.1])
  pthbins_XH = array("d",[0, 7.5,30,65,105,145,182.5, 200])
  XH_tot.insert(0,0)
  XH_tot.insert(-1,0)
#  x_pth = array("d",[5,5,5,5,5,5])
#  x_pth_stat = array("d",[4,4,4,4,4,4])
#  x_pth_syst = array("d",[2,2,2,2,2,2])

  gsyst = TGraphAsymmErrors(6, pthbins, central_value_tot, x_pth_syst, x_pth_syst, syst_down_tot, syst_up_tot)
  #gtot = TGraphAsymmErrors(6, pthbins, central_value_tot, zero, zero, down_tot, up_tot)
  gtot = TGraphAsymmErrors(6, pthbins, central_value_tot, err_pth, err_pth, down_tot, up_tot)
  gXH = TGraphErrors(6, pthbins, XH_tot, err_pth, zero)
  #gtruth = TGraphErrors(6, pthbins, truth_tot, err_pth, zero)
  gpowhegV2 = TGraphErrors(6, powheg_bins, powhegV2_central_tot, powheg_err, zero)
  gpowhegV2_scale = TGraphAsymmErrors(6, powheg_bins, powhegV2_central_tot, powheg_err, powheg_err, powhegV2_scaleup_tot, powhegV2_scaledown_tot)
  gstat = TGraphErrors(6, pthbins, central_value_tot, x_pth_stat, stat_error_tot)
  gtheo = TGraphAsymmErrors(6, pthbins, central_value_tot, x_pth, x_pth, up_theo, down_theo)
  ghres = TGraphErrors(6, hres_bins, hres_central, hres_err, zero)
  ghres_scale = TGraphAsymmErrors(6, hres_bins, hres_central, hres_err, hres_err, hres_scaleup, hres_scaledown)
  

#  gtot.SetTitle("k_{reg} = 1")
  gtot.SetLineColor(kBlack)
  gtot.SetLineWidth(2) 
#  gtot.SetFillColor(2) 
#  gtot.SetFillStyle(3002) 
  gtot.GetYaxis().SetTitle("d#sigma_{fid}/dp_{T}^{H} [fb/GeV]")
  gtot.GetYaxis().SetLabelSize(0.04) 
  gtot.GetYaxis().SetTitleSize(0.04)
  gtot.GetYaxis().SetTitleOffset(1.5)
  gtot.GetXaxis().SetRangeUser(0,200)
  gtot.GetXaxis().SetTitle("p_{T}^{H} [GeV]") 
  gtot.GetXaxis().SetLabelSize(0.04)
  gtot.GetXaxis().SetTitleSize(0.04)
  gtot.GetXaxis().SetTitleOffset(1.2)
  gtot.Draw("AP") 

# gstat.SetLineColor(kBlack) 
  gstat.SetFillColor(kAzure-8)
  gstat.SetLineColor(kWhite) 
#  gstat.SetFillStyle(3002) 
  gstat.SetLineWidth(1) 
  #gstat.Draw("P2Z") 

  gStyle.SetHatchesSpacing(0.5)
  gStyle.SetHatchesLineWidth(2)
  #  gsyst.SetFillStyle(3004)
  # gsyst.SetFillStyle(3354)
  gsyst.SetFillColor(kGray)
  gsyst.SetLineWidth(1)
  gsyst.SetLineColor(kWhite)
  #gsyst.Draw("P2Z")

  gtheo.SetFillColor(kRed-7)
  gtheo.SetLineWidth(1)
  gtheo.SetLineColor(kWhite)
  #gtheo.Draw("P2Z")

  gpowhegV2_scale.SetFillStyle(3354)
  gpowhegV2_scale.SetLineWidth(3)
  gpowhegV2_scale.SetLineColor(kGreen+1)
  gpowhegV2_scale.SetFillColor(kGreen)
  gpowhegV2_scale.Draw("2Z")

  ghres_scale.SetFillStyle(3345)
  ghres_scale.SetLineWidth(3)
  ghres_scale.SetLineColor(kMagenta+1)
  ghres_scale.SetFillColor(kMagenta)
  ghres_scale.Draw("2Z")

  gpowhegV2.SetMarkerSize(0)
  gpowhegV2.SetLineColor(kGreen+1)
  gpowhegV2.SetLineWidth(3)
  gpowhegV2.Draw("Z")

  ghres.SetMarkerSize(0)
  ghres.SetLineColor(kMagenta+1)
  ghres.SetLineWidth(3)
  ghres.Draw("Z")

#  gXH.SetMarkerSize(0)
#  gXH.SetLineColor(kBlue)
#  gXH.SetFillColor(kBlue)
#  gXH.SetLineWidth(3)
#  gXH.Draw("FZ")
  h_XH.SetMarkerSize(0)
  h_XH.SetLineWidth(2)
  h_XH.SetLineColor(kTeal-7)
  h_XH.SetFillColor(kTeal-8)
  h_XH.Draw("HISTsame")

  gPad.RedrawAxis()

  gtheo.Draw("P2Z")
  gstat.Draw("P2Z")
  gsyst.Draw("P2Z")
  gtot.Draw("PZ")

  leg = TLegend(0.4,0.48,0.92,0.9)
  leg.SetFillStyle(0)
  leg.SetBorderSize(0)
  leg.SetFillColor(kWhite)
  leg.SetTextSize(0.031)
# leg.SetBorderSize(0)
  #leg.SetTextFont(72) 
  #leg.SetTextSize(0.04) 
  leg.AddEntry(gtot,"Data","lep") 
  leg.AddEntry(gstat,"Statistical uncertainty","F") 
  leg.AddEntry(gsyst,"Systematic uncertainty","F")
  leg.AddEntry(gtheo,"Model dependence","F")
  leg.AddEntry(gpowhegV2_scale,"ggH (PowhegV2+JHUGen) + XH","LF")
  leg.AddEntry(ghres_scale, "ggH (HRes) + XH","LF")
  leg.AddEntry(h_XH, "XH = VBF + VH","F")
  leg.Draw() 

  CMS_lumi.CMS_lumi(canvas, 2, iPos)

  a=raw_input()
