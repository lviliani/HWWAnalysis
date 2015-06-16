#!/usr/env/bin python

from ROOT import *
from array import *
import numpy

TH1.SetDefaultSumw2()
gStyle.SetOptStat(0)

selection = "(( (njet==0 && (mth>60.000000 && mth<280.000000 && mth<200.000000  && pt1>20 && pt2>10 && (ch1*ch2)<0 && trigger==1. && pfmet>20. && mth>12 && (zveto>-1||!sameflav) && mpmet>20. && bveto_mu==1 && nextra==0 && bveto_ip==1 && ptll>30.000000)) || (njet>0 && (mth>60.000000 && mth<280.000000 && mth<200.000000  && pt1>20 && pt2>10 && (ch1*ch2)<0 && trigger==1. && pfmet>20. && mth>12 && (zveto>-1||!sameflav) && mpmet>20. && nextra==0 && ( jetbjpb1<1.4 || jetpt1<30) && ( jetbjpb2<1.4 || jetpt2<30) && ( jetbjpb3<1.4 || jetpt3<30) && ( jetbjpb4<1.4 || jetpt4<30)  && ptll>30.000000 && mth>60.000000 && mth<280.000000 && mth<200.000000 ))) && !sameflav)"

pth = "sqrt((pt1*cos(phi1) + pt2*cos(phi2) + pfmet*cos(pfmetphi))**2 + (pt1*sin(phi1) + pt2*sin(phi2) + pfmet*sin(pfmetphi))**2)" 

edges=[0., 15., 45., 87., 125., 162., 200.]

xbin = numpy.array(edges)

mllbins = array("d",[12,30,45,60,75,100,125,150,175,200])
mthbins = array("d",[60,70,80,90,100,110,120,140,160,180,200,220,240,280])

fileWW = TFile("/data/lenzip/differential/tree_noskim/nominals/latino_000_WWJets2LMad.root")
fileWW_nlo = TFile("/afs/cern.ch/work/c/calderon/public/RooUnfold/nnllResummation/latino000_nll_ewk.root")
fileMCNLO = TFile("/data/lenzip/differential/tree_noskim/nominals/latino_002_WWto2L2NuMCatNLO.root")
filePowheg = TFile("/data/lenzip/differential/tree_noskim/nominals/latino_006_WWJets2LPowheg.root")

treeWW = fileWW.Get("latino")
treeWW_nlo = fileWW_nlo.Get("latino")
treeMCNLO = fileMCNLO.Get("latino")
treePowheg = filePowheg.Get("latino")


outFile = TFile("mth.root","recreate")

c1 = TCanvas("c1")
c2 = TCanvas("c2")
c3 = TCanvas("c3")
c4 = TCanvas("c4")
c5 = TCanvas("c5")
c6 = TCanvas("c6")

canvas = [c1,c2,c3,c4,c5,c6]

hWWBin1=TH1F("hWWBin1","hWWBin1",len(mthbins)-1,mthbins)
hWWBin2=TH1F("hWWBin2","hWWBin2",len(mthbins)-1,mthbins)
hWWBin3=TH1F("hWWBin3","hWWBin3",len(mthbins)-1,mthbins)
hWWBin4=TH1F("hWWBin4","hWWBin4",len(mthbins)-1,mthbins)
hWWBin5=TH1F("hWWBin5","hWWBin5",len(mthbins)-1,mthbins)
hWWBin6=TH1F("hWWBin6","hWWBin6",len(mthbins)-1,mthbins)

histosWW=[hWWBin1,hWWBin2,hWWBin3,hWWBin4,hWWBin5,hWWBin6]

hWWnloBin1=TH1F("hWWnloBin1","hWWnloBin1",len(mthbins)-1,mthbins)
hWWnloBin2=TH1F("hWWnloBin2","hWWnloBin2",len(mthbins)-1,mthbins)
hWWnloBin3=TH1F("hWWnloBin3","hWWnloBin3",len(mthbins)-1,mthbins)
hWWnloBin4=TH1F("hWWnloBin4","hWWnloBin4",len(mthbins)-1,mthbins)
hWWnloBin5=TH1F("hWWnloBin5","hWWnloBin5",len(mthbins)-1,mthbins)
hWWnloBin6=TH1F("hWWnloBin6","hWWnloBin6",len(mthbins)-1,mthbins)

histosWWnlo=[hWWnloBin1,hWWnloBin2,hWWnloBin3,hWWnloBin4,hWWnloBin5,hWWnloBin6]

hWWBinMCNLOMCNLO1=TH1F("hWWBinMCNLO1","hWWBinMCNLO1",len(mthbins)-1,mthbins)
hWWBinMCNLOMCNLO2=TH1F("hWWBinMCNLO2","hWWBinMCNLO2",len(mthbins)-1,mthbins)
hWWBinMCNLOMCNLO3=TH1F("hWWBinMCNLO3","hWWBinMCNLO3",len(mthbins)-1,mthbins)
hWWBinMCNLOMCNLO4=TH1F("hWWBinMCNLO4","hWWBinMCNLO4",len(mthbins)-1,mthbins)
hWWBinMCNLOMCNLO5=TH1F("hWWBinMCNLO5","hWWBinMCNLO5",len(mthbins)-1,mthbins)
hWWBinMCNLOMCNLO6=TH1F("hWWBinMCNLO6","hWWBinMCNLO6",len(mthbins)-1,mthbins)

histosMCNLO=[hWWBinMCNLO1,hWWBinMCNLO2,hWWBinMCNLO3,hWWBinMCNLO4,hWWBinMCNLO5,hWWBinMCNLO6]

hWWBinPowhegPowheg1=TH1F("hWWBinPowheg1","hWWBinPowheg1",len(mthbins)-1,mthbins)
hWWBinPowhegPowheg2=TH1F("hWWBinPowheg2","hWWBinPowheg2",len(mthbins)-1,mthbins)
hWWBinPowhegPowheg3=TH1F("hWWBinPowheg3","hWWBinPowheg3",len(mthbins)-1,mthbins)
hWWBinPowhegPowheg4=TH1F("hWWBinPowheg4","hWWBinPowheg4",len(mthbins)-1,mthbins)
hWWBinPowhegPowheg5=TH1F("hWWBinPowheg5","hWWBinPowheg5",len(mthbins)-1,mthbins)
hWWBinPowhegPowheg6=TH1F("hWWBinPowheg6","hWWBinPowheg6",len(mthbins)-1,mthbins)

histosPowheg=[hWWBinPowheg1,hWWBinPowheg2,hWWBinPowheg3,hWWBinPowheg4,hWWBinPowheg5,hWWBinPowheg6]



legBin1 = TLegend(0.6,0.7,0.9,0.9)
legBin2 = TLegend(0.6,0.7,0.9,0.9)
legBin3 = TLegend(0.6,0.7,0.9,0.9)
legBin4 = TLegend(0.6,0.7,0.9,0.9)
legBin5 = TLegend(0.6,0.7,0.9,0.9)
legBin6 = TLegend(0.6,0.7,0.9,0.9)

legends = [legBin1,legBin2,legBin3,legBin4,legBin5,legBin6]

for bin in range(1,len(edges)):

  print bin
  histosWW[bin-1].SetLineColor(kBlue)
  histosWWnlo[bin-1].SetLineColor(kRed)
  histosMCNLO[bin-1].SetLineColor(kGreen)
  histosPowheg[bin-1].SetLineColor(kMagenta)

  histosWW[bin-1].SetLineWidth(2)
  histosWWnlo[bin-1].SetLineWidth(2)
  histosMCNLO[bin-1].SetLineWidth(2)
  histosPowheg[bin-1].SetLineWidth(2)

  histosWW[bin-1].GetXaxis().SetTitle("m_{T}^{H} (GeV)")
  
  treeWW.Draw("mth>>hWWBin"+str(bin),selection+"*("+pth+"<"+str(edges[bin])+" && "+pth+">"+str(edges[bin-1])+")")
  treeWW_nlo.Draw("mth>>hWWnloBin"+str(bin),selection+"*nllW*("+pth+"<"+str(edges[bin])+" && "+pth+">"+str(edges[bin-1])+")")
  treeMCNLO.Draw("mth>>hWWBinMCNLO"+str(bin),selection+"*("+pth+"<"+str(edges[bin])+" && "+pth+">"+str(edges[bin-1])+")")
  treePowheg.Draw("mth>>hWWBinPowheg"+str(bin),selection+"*("+pth+"<"+str(edges[bin])+" && "+pth+">"+str(edges[bin-1])+")")

    
  print selection+"*("+pth+"<"+str(edges[bin])+")"

#  histosWW[bin-1].Sumw2()
#  histosWWnlo[bin-1].Sumw2()

  histosWW[bin-1].Scale(1./histosWW[bin-1].Integral())
  histosWWnlo[bin-1].Scale(1./histosWWnlo[bin-1].Integral())
  histosMCNLO[bin-1].Scale(1./histosMCNLO[bin-1].Integral())
  histosPowheg[bin-1].Scale(1./histosPowheg[bin-1].Integral())


  legends[bin-1].AddEntry(histosWW[bin-1],"Madgraph","l")
  legends[bin-1].AddEntry(histosWWnlo[bin-1],"Madgraph NNLL","l")
  legends[bin-1].AddEntry(histosMCNLO[bin-1],"MC@NLO","l")
  legends[bin-1].AddEntry(histosPowheg[bin-1],"Powheg","l")


  canvas[bin-1].cd() 
  histosWW[bin-1].Draw()
  histosWWnlo[bin-1].Draw("sames")
  histosMCNLO[bin-1].Draw("sames")
  histosPowheg[bin-1].Draw("sames")
  legends[bin-1].Draw()
  canvas[bin-1].Write()
  canvas[bin-1].Print("mthBin"+str(bin)+".eps")

#a=raw_input()
outFile.Write()
