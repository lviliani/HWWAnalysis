#!/usr/env/bin python


from ROOT import *

gROOT.ProcessLine(".L ~/tdrStyle.C")
setTDRStyle()
gStyle.SetPalette(1)

selection = "(( (njet==0 && (mth>60.000000 && mth<280.000000 && mll<200.000000  && pt1>20 && pt2>10 && (ch1*ch2)<0 && trigger==1. && pfmet>20. && mll>12 && (zveto>-1||!sameflav) && mpmet>20. && bveto_mu==1 && nextra==0 && bveto_ip==1 && ptll>30.000000)) || (njet>0 && (mth>60.000000 && mth<280.000000 && mll<200.000000  && pt1>20 && pt2>10 && (ch1*ch2)<0 && trigger==1. && pfmet>20. && mll>12 && (zveto>-1||!sameflav) && mpmet>20. && nextra==0 && ( jetbjpb1<1.4 || jetpt1<30) && ( jetbjpb2<1.4 || jetpt2<30) && ( jetbjpb3<1.4 || jetpt3<30) && ( jetbjpb4<1.4 || jetpt4<30)  && ptll>30.000000 && mth>60.000000 && mth<280.000000 && mll<200.000000 ))) && !sameflav)";

pth = "min(sqrt((pt1*cos(phi1) + pt2*cos(phi2) + pfmet*cos(pfmetphi))**2 + (pt1*sin(phi1) + pt2*sin(phi2) + pfmet*sin(pfmetphi))**2),200)"; 

#file = TFile("/data/lenzip/differential/tree_noskim/nominals/latino_1125_ggToH125toWWTo2LAndTau2Nu.root");
file = TFile("/data/lenzip/differential/tree_noskim/nominals/latino_2125_vbfToH125toWWTo2LAndTau2Nu.root");
tree = file.Get("latino");
#edges=[0., 15., 45., 87., 125., 162., 200.]

corrmll = TH2F("corrmll", "corrmll", 40, 10, 110, 40, 0, 200)
corrmll.GetXaxis().SetTitle("m_{ll}")
corrmll.GetYaxis().SetTitle("p_{T,reco}^{H}")
corrmth = TH2F("corrmth", "corrmth", 44, 60, 180, 40, 0, 200)
corrmth.GetXaxis().SetTitle("m_{T}^{H}")
corrmth.GetYaxis().SetTitle("p_{T,reco}^{H}")



tree.Draw(pth+":mll>>corrmll", selection)
tree.Draw(pth+":mth>>corrmth", selection)

c1=TCanvas()
c1.cd()
corrmll.Draw("COLZ")
corrmllfactor = corrmll.GetCorrelationFactor()
text1 = TText(35, 140, "Correlation factor: "+str("{0:.5f}".format(corrmllfactor)))
text1.SetTextSize(0.04);
text1.Draw("sames")

c2=TCanvas()
c2.cd()
corrmth.Draw("COLZ")
corrmthfactor = corrmth.GetCorrelationFactor()
text2 = TText(90, 140, "Correlation factor: "+str("{0:.5f}".format(corrmthfactor)))
text2.SetTextSize(0.04)
text2.Draw("sames")



a=raw_input()

