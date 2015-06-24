#!/usr/bin/env python

import sys
from ROOT import *
import numpy

gROOT.ProcessLine(".L ~/tdrStyle.C")
setTDRStyle()
gStyle.SetPalette(1)
gStyle.SetPaintTextFormat("4.2f");

file=TFile(sys.argv[1])

tree=file.Get("latino")

ptgen="min(PtHiggs,167)"
ptreco="min(sqrt((pt1*cos(phi1) + pt2*cos(phi2) + pfmet*cos(pfmetphi))**2 + (pt1*sin(phi1) + pt2*sin(phi2) + pfmet*sin(pfmetphi))**2), 167)"
recovsgen=ptreco+":"+ptgen

selection="(( (njet==0 && (mth>60.000000 && mth<280.000000 && mll<200.000000  && pt1>20 && pt2>10 && (ch1*ch2)<0 && trigger==1. && pfmet>20. && mll>12 && (zveto>-1||!sameflav) && mpmet>20. && bveto_mu==1 && nextra==0 && bveto_ip==1 && ptll>30.000000)) || (njet>0 && (mth>60.000000 && mth<280.000000 && mll<200.000000  && pt1>20 && pt2>10 && (ch1*ch2)<0 && trigger==1. && pfmet>20. && mll>12 && (zveto>-1||!sameflav) && mpmet>20. && nextra==0 && ( jetbjpb1<1.4 || jetpt1<30) && ( jetbjpb2<1.4 || jetpt2<30) && ( jetbjpb3<1.4 || jetpt3<30) && ( jetbjpb4<1.4 || jetpt4<30)  && ptll>30.000000 && mth>60.000000 && mth<280.000000 && mll<200.000000 ))) && !sameflav)*baseW*puW*effW*triggW*19.47"

labelReco = "p_{T}^{H,RECO}"
labelGen  = "p_{T}^{H,GEN}"
label     = "p_{T}^{H}"

bins = [0., 15., 45., 85., 125., 165., 200]
binning=numpy.asarray(bins)

plot2D = TH2F("recoVSgen", "recoVSgen", len(bins)-1, binning, len(bins)-1, binning)
plot2D.GetXaxis().SetTitle(labelGen)
plot2D.GetXaxis().SetNdivisions(505)
plot2D.GetYaxis().SetTitle(labelReco)
plot2D.GetYaxis().SetNdivisions(505)

plotreco = TH1F("reco", "reco", len(bins)-1, binning)
plotreco.GetXaxis().SetTitle(labelReco)
plotreco.SetLineColor(kRed)
plotreco.SetMarkerColor(kRed)
plotreco.SetLineWidth(2)

plotgen  = TH1F("gen", "gen", len(bins)-1, binning)
plotgen.GetXaxis().SetTitle(labelGen)
plotgen.SetLineColor(kBlue)
plotgen.SetMarkerColor(kBlue)
plotgen.SetLineWidth(2)

latino.Draw(recovsgen+">>recoVSgen", selection)
latino.Draw(ptgen+">>gen", selection)
latino.Draw(ptreco+">>reco", selection)


plot2DnormReco = plot2D.Clone()
plot2DnormReco.SetNameTitle("recoVSgenNormReco", "recoVSgenNormReco")

plot2DnormGen = plot2D.Clone()
plot2DnormGen.SetNameTitle("recoVSgenNormGen", "recoVSgenNormGen")

for i in range(1, len(bins)):
  for j in range(1, len(bins)):
    plot2DnormReco.SetBinContent( i, j, plot2D.GetBinContent(i,j)/max(plotreco.GetBinContent(j), 1.) )
    plot2DnormGen.SetBinContent( i, j, plot2D.GetBinContent(i,j)/max(plotgen.GetBinContent(i),1.) )

out=TFile("binning.root", "RECREATE")
out.cd()

plot2D.Write()
plotreco.Write()
plotgen.Write()
plot2DnormReco.Write()
plot2DnormGen.Write()


c1=TCanvas("recoVSgenNormReco")
c1.SetRightMargin(0.13)
c1.cd()
plot2DnormReco.Draw("COLZ")
plot2DnormReco.Draw("TEXTsame")


c2=TCanvas("recoVSgenNormGen")
c2.SetRightMargin(0.13)
c2.cd()
plot2DnormGen.Draw("COLZ")
plot2DnormGen.Draw("TEXTsame")

c3=TCanvas("spectra")
c3.SetRightMargin(0.13)
c3.cd()
plotgen.Draw()
plotreco.Draw("sames")
leg=TLegend(0.8, 0.8, 1., 1.)
leg.AddEntry(plotgen, labelGen, "l")
leg.AddEntry(plotreco, labelReco, "l")
leg.SetFillStyle(4000)
leg.SetFillColor(0)
leg.SetBorderSize(0)
leg.Draw("same")

c1.Write()
c2.Write()
c3.Write()

out.Close()



a=raw_input("press any key to exit")
