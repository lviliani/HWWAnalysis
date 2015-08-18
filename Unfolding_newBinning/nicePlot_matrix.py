#!/usr/bin/env python

from ROOT import *
from array import *
from math import *
import CMS_lumi, tdrstyle

#gInterpreter.ExecuteMacro("/afs/cern.ch/work/l/lviliani/DatacardFramework/CMSSW_6_1_1/src/HWWAnalysis/ShapeAnalysis/macros/LatinoStyle2.C")

### Normalization: 0 for "by row", 1 for "by column"
normalization = 1

def set_palette(name="palette", ncontours=100):
    """Set a color palette from a given RGB list
    stops, red, green and blue should all be lists of the same length
    see set_decent_colors for an example"""

    if name == "gray" or name == "grayscale":
        stops = [0.00, 0.34, 0.61, 0.84, 1.00]
        red   = [1.00, 0.84, 0.61, 0.34, 0.00]
        green = [1.00, 0.84, 0.61, 0.34, 0.00]
        blue  = [1.00, 0.84, 0.61, 0.34, 0.00]
    # elif name == "whatever":
        # (define more palettes)
    else:
        # default palette, looks cool
        stops = [0.00, 0.34, 0.61, 0.84, 1.00]
        #red   = [0.00, 0.00, 0.87, 1.00, 0.51]
        #green = [0.00, 0.81, 1.00, 0.20, 0.00]
        red = [0,0,0,0,0]
        green = [0,0,0,0,0]
        #blue  = [0.51, 1.00, 0.12, 0.00, 0.00]
        blue = [0.5, 0.4, 0.3, 0.2, 0.1]

    s = array('d', stops)
    r = array('d', red)
    g = array('d', green)
    b = array('d', blue)

    npoints = len(s)
    TColor.CreateGradientColorTable(npoints, s, r, g, b, ncontours)
    gStyle.SetNumberContours(ncontours)

#set the tdr style
tdrstyle.setTDRStyle()

#set_palette()

#change the CMS_lumi variables (see CMS_lumi.py)
CMS_lumi.lumi_8TeV = "19.47 fb^{-1}"
CMS_lumi.writeExtraText = 1
CMS_lumi.extraText = "Preliminary"

iPos = 9

H_ref = 1200
W_ref = 1200 
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

lumi = 19.468
in_file = TFile("responseMatricesPreApp/responseMatrix_central.root")

matrix = in_file.Get("matrix_central")

###Normalize by row

matrix_norm = matrix.Clone()
matrix_norm.Reset()

for i in range(matrix_norm.GetNbinsX()):
  for j in range(matrix_norm.GetNbinsY()):
    matrix_norm.SetBinContent(i+1,j+1,0.0000000000000000000000000000000000000000000000001)

### Normalize by column
if normalization==1:
  for i in range(1,matrix.GetNbinsX()+1):
    integral = matrix.Integral(i,i,1,6)
    for j in range(1,matrix.GetNbinsY()+1):
      matrix_norm.SetBinContent(i,j,(matrix.GetBinContent(i,j)/integral)+0.0000000000000000000000000000000000001)
### normalize by row
elif normalization==0:
  for i in range(1,matrix.GetNbinsY()+1):
    integral = matrix.Integral(1,6,i,i)
    for j in range(1,matrix.GetNbinsX()+1):
      matrix_norm.SetBinContent(j,i,(matrix.GetBinContent(j,i)/integral)+0.0000000000000000000000000000000000001)
else:
  print "Unrecognized option for normalization"


matrix_norm.GetXaxis().SetTitle("p_{T,reco}^{H} (GeV)")
matrix_norm.GetXaxis().SetLabelFont(42)
matrix_norm.GetXaxis().SetTitleOffset(1.09)
matrix_norm.GetXaxis().SetTitleFont(42)
matrix_norm.GetYaxis().SetTitle("p_{T,gen}^{H} (GeV)")
matrix_norm.GetYaxis().SetLabelFont(42)
matrix_norm.GetYaxis().SetTitleOffset(1.1)
matrix_norm.GetYaxis().SetTitleFont(42)
matrix_norm.GetZaxis().SetLabelFont(42)
matrix_norm.GetZaxis().SetTitleOffset(1.1)
matrix_norm.GetZaxis().SetTitleFont(42)
#matrix_norm.SetMinimum(-0.01)
#matrix_norm.GetZaxis().SetRangeUser(-0.0000001, 1)
matrix_norm.SetMarkerSize(1.)

gStyle.SetPalette(1)
gStyle.SetPaintTextFormat("4.2f")

matrix_norm.Draw("colz text")

CMS_lumi.CMS_lumi(canvas, 2, iPos)

a=raw_input()
