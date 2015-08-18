#!/usr/bin/env python

from ROOT import *
from ROOT import RooUnfoldResponse
from ROOT import RooUnfold
from ROOT import RooUnfoldBayes
# from ROOT import RooUnfoldSvd
# from ROOT import RooUnfoldTUnfold
from array import *
from math import *

lumi = 19.47

base="/afs/cern.ch/work/l/lviliani/DatacardFramework/CMSSW_7_1_5/src/Unfolding/"

sample_ggH="latino_1125_ggToH125toWWTo2LAndTau2Nu.root"
sample_VBF="latino_2125_vbfToH125toWWTo2LAndTau2Nu.root"
sample_WZH="latino_3125_wzttH125ToWW.root"

pthbins = array("d",[0,15,45,85,125,165,200])

chain = TChain("latino")
chain.Add(base+"samples/nominals/"+sample_ggH)
chain.Add(base+"samples/nominals/"+sample_VBF)
chain.Add(base+"samples/nominals/"+sample_WZH)

hTrue = TH1F("hTrue ","pTH GEN ",len(pthbins)-1,pthbins)

# Start loop
iEvt=0
for e in chain :
  iEvt+=1
#   if iEvt==1000 : break
  if iEvt%10000==0 : 
    print "Event ",iEvt

  current_file = chain.GetFile().GetName()

  pl1 = TLorentzVector()
  pl2 = TLorentzVector()
  pn1 = TLorentzVector()
  pn2 = TLorentzVector()

  if abs(e.leptonGenpid1)==13:
    pl1.SetPtEtaPhiM(e.leptonGenpt1,e.leptonGeneta1,e.leptonGenphi1,0.1056)
  elif abs(e.leptonGenpid1)==11:
    pl1.SetPtEtaPhiM(e.leptonGenpt1,e.leptonGeneta1,e.leptonGenphi1,0.000511)
  else:
    pl1.SetPtEtaPhiM(e.leptonGenpt1,e.leptonGeneta1,e.leptonGenphi1,1.777)

  if abs(e.leptonGenpid2)==13:
    pl2.SetPtEtaPhiM(e.leptonGenpt2,e.leptonGeneta2,e.leptonGenphi2,0.1056)
  elif abs(e.leptonGenpid1)==11:
    pl2.SetPtEtaPhiM(e.leptonGenpt2,e.leptonGeneta2,e.leptonGenphi2,0.000511)
  else:
    pl2.SetPtEtaPhiM(e.leptonGenpt2,e.leptonGeneta2,e.leptonGenphi2,1.777)


  pn1.SetPtEtaPhiM(e.neutrinoGenpt1,e.neutrinoGeneta1,e.neutrinoGenphi1,0)
  pn2.SetPtEtaPhiM(e.neutrinoGenpt2,e.neutrinoGeneta2,e.neutrinoGenphi2,0)

  pTll_gen = (pl1+pl2).Perp()

  pTnn_gen = (pn1+pn2).Perp()

  mll_gen = (pl1+pl2).M()

  if ( ( pTll_gen + pTnn_gen  )**2 < ( ( e.leptonGenpt1*cos(e.leptonGenphi1) + e.leptonGenpt2*cos(e.leptonGenphi2) + e.neutrinoGenpt1*cos(e.neutrinoGenphi1) + e.neutrinoGenpt2*cos(e.neutrinoGenphi2) )**2 + ( e.leptonGenpt1*sin(e.leptonGenphi1) + e.leptonGenpt2*sin(e.leptonGenphi2) + e.neutrinoGenpt1*sin(e.neutrinoGenphi1) + e.neutrinoGenpt2*sin(e.neutrinoGenphi2)  )**2 ) ):
    continue
  else:
    mth_gen = sqrt( ( pTll_gen + pTnn_gen  )**2 - ( ( e.leptonGenpt1*cos(e.leptonGenphi1) + e.leptonGenpt2*cos(e.leptonGenphi2) + e.neutrinoGenpt1*cos(e.neutrinoGenphi1) + e.neutrinoGenpt2*cos(e.neutrinoGenphi2) )**2 + ( e.leptonGenpt1*sin(e.leptonGenphi1) + e.leptonGenpt2*sin(e.leptonGenphi2) + e.neutrinoGenpt1*sin(e.neutrinoGenphi1) + e.neutrinoGenpt2*sin(e.neutrinoGenphi2)  )**2 ) )

  pTH_gen = (pl1+pl2+pn1+pn2).Perp()

  of_gen = ( (abs(e.leptonGenpid1)==11 and abs(e.leptonGenpid2)==13) or (abs(e.leptonGenpid1)==13 and abs(e.leptonGenpid2)==11) )

  if e.dataset==3125:
    wzemu_gen = ( (e.mctruth==24 or e.mctruth==26)*(e.dataset==3125)*(e.mcHWWdecay==3)*(e.leptonGenpt3<0)*(e.neutrinoGenpt3<0) )
  else :
    wzemu_gen=1

  acceptance = e.leptonGenpt1>20. and e.leptonGenpt2>10. and abs(e.leptonGeneta1)<2.5 and abs(e.leptonGeneta2)<2.5 and pTll_gen>30. and mll_gen>12. and mth_gen>50. and of_gen and wzemu_gen


  ### Acceptance selection
  if ( acceptance ):
    hTrue.Fill(min(pTH_gen,167.),e.baseW*lumi)


file_out = TFile("TheTruthPreApp.root","recreate")
file_out.cd()
hTrue.Write()
file_out.Close()

