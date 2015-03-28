#!/usr/env/bin python


from ROOT import *
import numpy

selection = "(( (njet==0 && (mth>60.000000 && mth<280.000000 && mll<200.000000  && pt1>20 && pt2>10 && (ch1*ch2)<0 && trigger==1. && pfmet>20. && mll>12 && (zveto>-1||!sameflav) && mpmet>20. && bveto_mu==1 && nextra==0 && bveto_ip==1 && ptll>30.000000)) || (njet>0 && (mth>60.000000 && mth<280.000000 && mll<200.000000  && pt1>20 && pt2>10 && (ch1*ch2)<0 && trigger==1. && pfmet>20. && mll>12 && (zveto>-1||!sameflav) && mpmet>20. && nextra==0 && ( jetbjpb1<1.4 || jetpt1<30) && ( jetbjpb2<1.4 || jetpt2<30) && ( jetbjpb3<1.4 || jetpt3<30) && ( jetbjpb4<1.4 || jetpt4<30)  && ptll>30.000000 && mth>60.000000 && mth<280.000000 && mll<200.000000 ))) && !sameflav)";

pth = "min(sqrt((pt1*cos(phi1) + pt2*cos(phi2) + pfmet*cos(pfmetphi))**2 + (pt1*sin(phi1) + pt2*sin(phi2) + pfmet*sin(pfmetphi))**2),200)"; 

edges=[0., 15., 45., 87., 125., 162., 200.]

xbin = numpy.array(edges)

njetNuisance = {'n0': 0.940, 'n1': 1.110, 'n2': 1.293}

file = TFile("/data/lenzip/differential/tree_noskim/nominals/latino_1125_ggToH125toWWTo2LAndTau2Nu.root");

tree = file.Get("latino");

h = TH1F("h", "h", 6, xbin);

tree.Draw(pth+">>h", selection);

h.SetLineColor(4);

h.Draw();

infile=''
infile+='bin\tggH_UEPS\n'

for bin in range(1,len(edges)):
  thisbin = selection+" && ("+pth+">"+str(edges[bin-1])+") && ("+pth+"<"+str(edges[bin])+")"
  h_jet=TH1F("hjet"+str(bin), "hjet"+str(bin), 3, 0, 3)
  tree.Draw("min(njet,2)>>hjet"+str(bin), thisbin)
  h_jet.Scale(1./h_jet.Integral())
  frac0 = h_jet.GetBinContent(1)
  frac1 = h_jet.GetBinContent(2)
  frac2 = 1-frac0-frac1
  
  ggHUEPS = njetNuisance['n0']*frac0 + njetNuisance['n1']*frac1 + njetNuisance['n2']*frac2

  print "############## BIN ", bin
  print "frac0 = ",frac0, "\tfrac1 = ",frac1, "\tfrac2 = ",frac2
  print "ggH UEPS = ", ggHUEPS
  infile+=str(bin-1)+"\t%.3f\n" % ggHUEPS

print "INFILE"
print infile
a=raw_input()


