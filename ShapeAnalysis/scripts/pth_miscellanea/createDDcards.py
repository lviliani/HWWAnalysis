from __future__ import division
from ROOT import *
from math import *


file_sig = TFile("mll-mth_8TeV_pthincl_17_3/merged/hww-19.47fb.mH125.of_pthincl_shape.root")
file_ctrl = TFile("mll-mth_8TeV_pthinclCtrl_17_3/merged/hww-19.47fb.mH125.of_pthincl_shape.root")

snames = [hs.GetName() for hs in file_sig.GetListOfKeys()]
cnames = [hc.GetName() for hc in file_ctrl.GetListOfKeys()]

hsig = {}
for n in snames :
  if not "histo" in n : continue
  hsig[n] = file_sig.Get(n).Integral() 

hctrl = {}
for n in cnames :
  if not "histo" in n : continue
  hctrl[n] = file_ctrl.Get(n).Integral()


#print hctrl

fBin0 = open("Topge1jetBin0Card_of_pthincl.txt","w")
fBin1 = open("Topge1jetBin1Card_of_pthincl.txt","w")
fBin2 = open("Topge1jetBin2Card_of_pthincl.txt","w")
fBin3 = open("Topge1jetBin3Card_of_pthincl.txt","w")
fBin4 = open("Topge1jetBin4Card_of_pthincl.txt","w")
fBin5 = open("Topge1jetBin5Card_of_pthincl.txt","w")

fList = [fBin0,fBin1,fBin2,fBin3,fBin4,fBin5]

mass = 125

textable=""
textable+="\\begin{tabular}{c c c c c c}\n"
textable+="\hline\hline\n"
textable+="p_T^H bin & N_{CTRL}^{DATA} & N_{CTRL}^{TOP} &  N_{SIG}^{TOP} & \\alpha & \\Delta\\alpha \\\ \n"
textable+="\\hline\n"


for pthbin in range(0,6) :
  nsig = hsig["histo_Topge1jetBin"+str(pthbin)]
  nctrl = hctrl["histo_Topge1jetCtrlBin"+str(pthbin)]

  nsigup = hsig["histo_Topge1jetBin"+str(pthbin)+"_CMS_8TeV_btagsfUp"]
  nsigdown = hsig["histo_Topge1jetBin"+str(pthbin)+"_CMS_8TeV_btagsfDown"]
  nctrlup = hctrl["histo_Topge1jetCtrlBin"+str(pthbin)+"_CMS_8TeV_btagsfUp"]
  nctrldown = hctrl["histo_Topge1jetCtrlBin"+str(pthbin)+"_CMS_8TeV_btagsfDown"]

#  errsig = max(abs(nsigup - nsig), abs(nsig - nsigdown))
#  errctrl = max(abs(nctrlup - nctrl), abs(nctrl - nctrldown))

  alpha = nsig/nctrl
  alphaup = nsigup/nctrlup
  alphadown = nsigdown/nctrldown

  alpha_err = max(abs(alpha-alphaup),abs(alpha-alphadown))

#  alpha.append(nsig/nctrl)
#  alphaup.append(nsigup/nctrlup)
#  alpha_err.append( sqrt( (errsig/nsig)**2 + (errctrl/nctrl)**2 )*nsig/nctrl )
#  alpha_err.append( ( (errsig/nsig) + (errctrl/nctrl) )*nsig/nctrl )


  firstbin = 9*14*pthbin
  lastbin = 9*14*(pthbin+1)

  ndata = file_ctrl.Get("histo_Data").Integral(firstbin,lastbin)

  ww = hctrl["histo_WWBin"+str(pthbin)]+file_ctrl.Get("histo_ggWW").Integral(firstbin,lastbin)
  wjet = file_ctrl.Get("histo_WJet").Integral(firstbin,lastbin)
  zh = hctrl["histo_ZHBin"+str(pthbin)]
  wh = hctrl["histo_WHBin"+str(pthbin)]
  dytt = file_ctrl.Get("histo_DYTT").Integral(firstbin,lastbin)
  vg = file_ctrl.Get("histo_VgS").Integral(firstbin,lastbin)+file_ctrl.Get("histo_Vg").Integral(firstbin,lastbin)
  vv = file_ctrl.Get("histo_VV").Integral(firstbin,lastbin)+file_ctrl.Get("histo_VVV").Integral(firstbin,lastbin)

  ndata = ndata - (ww+wjet+zh+wh+dytt+vg+vv)

  print "------------------ BIN ",pthbin," -------------------------"
  print "N_sig = ", nsig, "N_ctrl = ", nctrl, "alpha = ",alpha, "alpha_err = ",alpha_err
  print "N_data_Ctrl = ", ndata
  print "WW = ",ww,"\nW+jets = ",wjet,"\nZH = ",zh,"\nWH = ",wh,"\nDYTT = ",dytt,"\nVg = ",vg,"\nVV = ",vv

# LATEX table  
  textable+=str(pthbin+1)+" & "+str(ndata)+" & "+str(nctrl)+" & "+str(nsig)+" & "+str(alpha)+" & "+str(alpha_err)+" \\\ \n"
#  ndata.append(file_ctrl.Get("histo_Data").Integral(firstbin,lastbin))


  fList[pthbin].write("%d\t%d\t%f\t%f" % (mass,int(ndata+0.5),alpha,alpha_err))

textable+="\\hline\n"
textable+="\\end{tabular}"
print textable

