#!/usr/bin/env python

from ROOT import *
from array import *
from math import *

lumi = 19.47

eff_acc =  0.361935
eff = 0.03960

in_file = TFile("plotsFromFit.root")

h = in_file.Get("HcentralNotChangingRM")
hstat = in_file.Get("HcentralStat")

cov_matrix = in_file.Get("Hcentral_covariance")
cov_matrix.Print()

nev=0
err=0
### Compute the integral of the differential distribution
for bin in range(1,7):
  nev+=h.GetBinContent(bin)
  print "Bin ", bin, " Total error = ", h.GetBinError(bin)

### Compute the total (stat+syst) variance on the integral, which is given by summing up all the elements of the covariance matrix
for row in range(6):
  for col in range(6):
    err+=cov_matrix[row][col]

### Compute the statistical uncertainty on the integral
stat_err=0
for bin in range(1,7):
  stat_err+=hstat.GetBinError(bin)**2
  print "Bin ", bin, " Stat error = ", hstat.GetBinError(bin)
stat_err=sqrt(stat_err)

print "Tot inclusive error = ", sqrt(err), " Stat  inclusive error = ", stat_err

### Compute the systematic error by subtracting in quadrature total and statistical uncertainties
syst_err = sqrt(err - stat_err**2)

print "N events = ", nev, " +/- ", stat_err
print "x-sec = ", (nev)/lumi, " +/- ", stat_err/lumi, " (stat) +/- ", syst_err/lumi ," (syst) fb"
print "Acceptance efficiency = ", eff_acc
print "Acceptance x-sec = ", nev/lumi/eff_acc, " +/- ", ( stat_err/nev )*nev/lumi/eff_acc," (stat) +/- ", ( syst_err/nev )*nev/lumi/eff_acc, " (syst)  fb"
print "Total efficiency = ", eff
print "Total x-sec = ", nev/lumi/eff, " +/- ",  ( stat_err/nev )*nev/lumi/eff, " (stat) +/- ", ( syst_err/nev )*nev/lumi/eff, " (syst) fb"

#a=raw_input()
