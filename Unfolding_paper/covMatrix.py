#!/usr/bin/env python

from ROOT import *
from ROOT import RooUnfoldResponse
from ROOT import RooUnfold
from ROOT import RooUnfoldSvd
from array import *
from math import *
import nicePlot_unfolded
import CMS_lumi, tdrstyle


lumi = 19.47
kreg = 3

#set the tdr style
tdrstyle.setTDRStyle()

#set_palette()

#change the CMS_lumi variables (see CMS_lumi.py)
CMS_lumi.lumi_8TeV = "19.4 fb^{-1}"
CMS_lumi.writeExtraText = 1
CMS_lumi.extraText = "Preliminary"

iPos = 9

H_ref = 700
W_ref = 700
W = W_ref
H  = H_ref

# references for T, B, L, R
T = 0.08*H_ref
B = 0.12*H_ref
L = 0.14*W_ref
R = 0.14*W_ref

canvas = TCanvas("c2","c2",50,50,W,H)
#canvas = TCanvas("c2","c2")
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

Number = 3
Red = array("d",[0., 1., 1.00])
Green = array("d",[0.0, 1., 0.])
Blue = array("d",[1.00, 1., 0.])
Length = array("d",[0.00, 0.5, 1.00])
nb = 99
TColor.CreateGradientColorTable(Number,Length,Red,Green,Blue,nb)

### File with signal extracted from the fit for each nuisance up/down variation
#syst_file = TFile("plotsFromFit.root")
syst_file = TFile("plotsFromFit_ggWWscale.root")

### File with the response martices for the systematics which need them
#matrix_file = TFile("responseMatricesPreAppWithFakesAndWZttH.root")

### First of all get the central distribution and unfold with central, up and down matrices, corresponding to the ggH/VBF ratio variation
h = syst_file.Get("HcentralNotChangingRM")


matrix_file = TFile("responseMatricesPreApp/responseMatrix_central.root")
response = matrix_file.Get("central")
unfold = RooUnfoldSvd(response, h, kreg)

cov_matrix = syst_file.Get("Hcentral_covariance")
cov_matrix.Print()

unfolded_cov_matrix = unfold.Ereco()

unfold.SetMeasuredCov(cov_matrix)
hReco = unfold.Hreco(2)
unfolded_cov_matrix.Print()
#gStyle.SetPalette(1)
cov_matrix = TH2D("cov_matrix","Covariance matrix, kreg = "+str(kreg),6,0,6,6,0,6)

for row in range(6):
  for column in range(6):
    print row+1, column+1, unfolded_cov_matrix[row][column]/sqrt(unfolded_cov_matrix[row][row])/sqrt(unfolded_cov_matrix[column][column])
    cov_matrix.SetBinContent(row+1,column+1, unfolded_cov_matrix[row][column]/sqrt(unfolded_cov_matrix[row][row])/sqrt(unfolded_cov_matrix[column][column]))

cov_matrix.SetStats(0)
cov_matrix.SetTitle("")
cov_matrix.SetMarkerSize(1.5)
cov_matrix.SetContour(nb)
cov_matrix.GetZaxis().SetRangeUser(-1,1)
cov_matrix.GetXaxis().SetTitle("Bin number")
cov_matrix.GetYaxis().SetTitle("Bin number")
cov_matrix.GetXaxis().SetTitleOffset(1)
cov_matrix.GetYaxis().SetTitleOffset(1)
gStyle.SetPaintTextFormat("4.1f")
cov_matrix.Draw("colz text")
CMS_lumi.CMS_lumi(canvas, 2, iPos)

a=raw_input()
