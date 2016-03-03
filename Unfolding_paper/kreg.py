#!/usr/bin/env python

from ROOT import *
from ROOT import RooUnfoldResponse
from ROOT import RooUnfold
from ROOT import RooUnfoldSvd

inFile = TFile("plotsFromFit.root")
matrixFile = TFile("responseMatricesPreApp/responseMatrix_central.root")

response = matrixFile.Get("central")
hMeas = inFile.Get("HcentralStat")

unfold = RooUnfoldSvd(response, hMeas, 3)
hReco = unfold.Hreco()
svd = unfold.Impl()

d = svd.GetD()

d.Draw()

a=raw_input()

