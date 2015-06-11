#!/usr/env/bin python


from ROOT import *
import numpy

selection = "(( (njet==0 && (mth>60.000000 && mth<280.000000 && mll<200.000000  && pt1>20 && pt2>10 && (ch1*ch2)<0 && trigger==1. && pfmet>20. && mll>12 && (zveto>-1||!sameflav) && mpmet>20. && bveto_mu==1 && nextra==0 && bveto_ip==1 && ptll>30.000000)) || (njet>0 && (mth>60.000000 && mth<280.000000 && mll<200.000000  && pt1>20 && pt2>10 && (ch1*ch2)<0 && trigger==1. && pfmet>20. && mll>12 && (zveto>-1||!sameflav) && mpmet>20. && nextra==0 && ( jetbjpb1<1.4 || jetpt1<30) && ( jetbjpb2<1.4 || jetpt2<30) && ( jetbjpb3<1.4 || jetpt3<30) && ( jetbjpb4<1.4 || jetpt4<30)  && ptll>30.000000 && mth>60.000000 && mth<280.000000 && mll<200.000000 ))) && !sameflav)";

selection_noveto = "(( (njet==0 && (mth>60.000000 && mth<280.000000 && mll<200.000000  && pt1>20 && pt2>10 && (ch1*ch2)<0 && trigger==1. && pfmet>20. && mll>12 && (zveto>-1||!sameflav) && mpmet>20. && nextra==0 && ptll>30.000000)) || (njet>0 && (mth>60.000000 && mth<280.000000 && mll<200.000000  && pt1>20 && pt2>10 && (ch1*ch2)<0 && trigger==1. && pfmet>20. && mll>12 && (zveto>-1||!sameflav) && mpmet>20. && nextra==0 && ptll>30.000000 && mth>60.000000 && mth<280.000000 && mll<200.000000 ))) && !sameflav)";

pth = "min(sqrt((pt1*cos(phi1) + pt2*cos(phi2) + pfmet*cos(pfmetphi))**2 + (pt1*sin(phi1) + pt2*sin(phi2) + pfmet*sin(pfmetphi))**2),200)"; 

edges=[0., 15., 45., 87., 125., 162., 200.]

xbin = numpy.array(edges)


#mH   f_0   f_1   f_2   k_1   k_2
#125  0.64  0.25  0.11  1.24  1.09


binningNuisance = {'k_0': exp(0.15), 'k_1': 1.24, 'k_2':1.09}

file = TFile("/data/lenzip/differential/tree_noskim/nominals/latino_1125_ggToH125toWWTo2LAndTau2Nu.root");

tree = file.Get("latino");

h_nob = TH1F("h_nob", "h_nob", 6, xbin);
h_b = TH1F("h_b", "h_b", 6, xbin);


tree.Draw(pth+">>h_nob", selection_noveto);
tree.Draw(pth+">>h_b", selection);

h_nob.SetLineColor(3);
h_b.SetLineColor(4);

h_nob.Draw();
h_b.Draw("sames");


out = TFile('vetoeff.root', "RECREATE")

eff = TGraphAsymmErrors(h_b, h_nob);
eff.SetNameTitle("eff_vs_pth", "eff_vs_pth")
c2 = TCanvas()
c2.cd();
eff.Draw("AP")

out.cd()
eff.Write()

c3=TCanvas()
c3.cd()
#eff_per_bin = numpy.array(eff.GetY())
#print eff_per_bin
infile=''
infile += "bin\tQCDscale_ggH\tQCDscale_ggH1in\tQCDscale_ggH2in\n"
for bin in range(1,len(edges)):
  thisbin_sel = selection+" && ("+pth+">"+str(edges[bin-1])+") && ("+pth+"<"+str(edges[bin])+")"
  thisbin_sel_nob = selection_noveto+" && ("+pth+">"+str(edges[bin-1])+") && ("+pth+"<"+str(edges[bin])+")" 
  h_jet=TH1F("hjet"+str(bin), "hjet"+str(bin), 3, 0, 3)
  h_jet_nob=TH1F("hjet_nob"+str(bin), "hjet_nob"+str(bin), 3, 0, 3)
  tree.Draw("min(njet,2)>>hjet"+str(bin), thisbin_sel)
  tree.Draw("min(njet,2)>>hjet_nob"+str(bin), thisbin_sel_nob)
  eff_thisbin = TGraphAsymmErrors(h_jet, h_jet_nob, "cpe0");
  eff_thisbin.SetNameTitle("effBin"+str(bin), "effBin"+str(bin))
  h_jet.Scale(1./h_jet.Integral())
  frac0 = h_jet.GetBinContent(1)
  frac1 = h_jet.GetBinContent(2)
  frac2 = 1-frac0-frac1
  x=Double(0)
  effic0 = Double(0)
  effic1 = Double(0)
  effic2 = Double(0)
  eff_thisbin.GetPoint(0, x, effic0) 
  eff_thisbin.GetPoint(1, x, effic1) 
  eff_thisbin.GetPoint(2, x, effic2)
  ggH0 = binningNuisance['k_0']**(1./frac0) if frac0 > 0.02 else 1.
  ggH1in0 = binningNuisance['k_1']**(-(frac2+frac1)/frac0) if frac0 > 0.02 else 1.
  ggH1in1 = binningNuisance['k_1']**((frac2+frac1)/frac1) if frac1 != 0 else 1.
  ggH2in1 = binningNuisance['k_2']**(-frac2/frac1)  if frac1 != 0 else 1.
  ggH2in2 = binningNuisance['k_2'] - 1
  #print "bin", bin, " selection ", thisbin_sel, "fractions", frac0, frac1, frac2, " efficiencies", effic0, effic1, effic2 
  print "bin", bin, "fractions", frac0, frac1, frac2, " efficiencies", effic0, effic1, effic2, "  ggH0,ggH1in0,ggH1in1,ggH2in1,ggH2in2",ggH0,ggH1in0,ggH1in1,ggH2in1,ggH2in2   
  QCDscale_ggH    = (ggH0*frac0*effic0+ggH1in0*frac1*effic1)/(ggH0*frac0*effic0+ggH1in0*frac1*effic0) if frac0 > 0.02 else 1.
  QCDscale_ggH1in = (ggH1in1*frac1*effic1 + ggH2in1*frac2*effic2)/(ggH1in1*frac1*effic1 + ggH2in1*frac2*effic1) if frac1 > 0.02 else 1.
  QCDscale_ggH2in = 1 
  infile += "Bin"+str(bin-1)+"\t%.3f\t%.3f\t%.3f\n" % (QCDscale_ggH, QCDscale_ggH1in, QCDscale_ggH2in)
  #print "QCDscale_ggH, QCDscale_ggH1in, QCDscale_ggH2in", QCDscale_ggH, QCDscale_ggH1in, QCDscale_ggH2in
  out.cd()
  eff_thisbin.Write()

print infile

out.Close()

a=raw_input()

