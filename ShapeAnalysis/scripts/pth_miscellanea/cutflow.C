
void cutflow(){

  gStyle->SetOptStat("emrio") ;

  TString var = "mll";

  TString LumiW = "*19.468" ;

  TString CutsName[7] ; 
  TString CutsCut [7] ; 

  TString no_cut = "(trigger==1 && !sameflav && ch1*ch2<0)";
  TString leptons_cut = "*(nextra==0 && pt1>20 && pt2>10)";
  TString mll_cut = "*(mll>12)";
  TString ptll_cut = "*(ptll>30)";  
  TString met_cut = "*(mpmet>20. && pfmet>20.)";
  TString mth_cut = "*(mth>60)";
  TString btag_cut = "*((njet==0)*(bveto_mu==1 && bveto_ip==1) || (njet>0)*(( jetbjpb1<1.4 || jetpt1<30) && ( jetbjpb2<1.4 || jetpt2<30) && ( jetbjpb3<1.4 || jetpt3<30) && ( jetbjpb4<1.4 || jetpt4<30)))"; 

  CutsName [0] = "no cut";
  CutsCut  [0] = no_cut;
  CutsName [1] = "leptons cut" ;  
  CutsCut  [1] = no_cut+leptons_cut;
  CutsName [2] = "mll cut" ;
  CutsCut  [2] = no_cut+leptons_cut+mll_cut ;
  CutsName [3] = "ptll cut" ;
  CutsCut  [3] = no_cut+leptons_cut+mll_cut+ptll_cut ;
  CutsName [4] = "met cut" ;
  CutsCut  [4] = no_cut+leptons_cut+mll_cut+met_cut ;
  CutsName [5] = "mth cut"  ;
  CutsCut  [5] = no_cut+leptons_cut+mll_cut+met_cut+mth_cut ;
  CutsName [6] = "btag cut";
  CutsCut  [6] = no_cut+leptons_cut+mll_cut+met_cut+mth_cut+btag_cut ;


  TString Dir = "/data/lviliani/tree_latino_nosel";

  TH1F* wjet2stack = new TH1F("wjet","wjet",7,0,7);
  TH1F* ww2stack = new TH1F("ww","ww",7,0,7);
  TH1F* vg2stack = new TH1F("vg","vg",7,0,7);
  TH1F* top2stack = new TH1F("top","top",7,0,7);
  TH1F* dytt2stack = new TH1F("dytt","dytt",7,0,7);
  TH1F* vv2stack = new TH1F("vv","vv",7,0,7);
  TH1F* sig2stack = new TH1F("sig","sig",7,0,7);
  TH1F* data = new TH1F("data","data",7,0,7);

for(int iCut=0; iCut<7; ++iCut){

  double bkg_tot = 0;
  double sig = 0;

  // DATA
  
  TChain * Data = new TChain("Data");
  Data->Add(Dir+"/Data_TightTight/4L/latino_RunA_892pbinv.root/latino") ;
  Data->Add(Dir+"/Data_TightTight/4L/latino_RunB_4404pbinv.root/latino") ;
  Data->Add(Dir+"/Data_TightTight/4L/latino_RunC_7032pbinv.root/latino") ;
  Data->Add(Dir+"/Data_TightTight/4L/latino_RunD_7274pbinv.root/latino") ;

  cout << "DATA:" << endl;
  TH1F* hdata = new TH1F("hdata","Data",100,0,1000);
  hdata->Sumw2();
  Data->Draw(var+">> hdata",CutsCut[iCut]+"*(run!=201191)");
  cout << CutsName[iCut] << " = " << hdata->Integral() << endl ;
  if (iCut<6)    data->SetBinContent(iCut+1,hdata->Integral());
  else  data->SetBinContent(iCut+1,0);

  delete hdata;
  delete Data;
  // WJET

  TChain * WJet = new TChain("WJet");
  WJet->Add(Dir+"/wjets/latino_LooseLoose_19.5fb.root/latino") ;

  cout << "WJet:" << endl;
  TH1F* hwjet = new TH1F("hwjet","W+jets",100, 0,1000);
  WJet->Draw(var+">> hwjet",CutsCut[iCut]+"*fakeW*(run!=201191)");
  //WJet->Draw(var+">> hwjet",CutsCut[iCut]+"*puW*baseW*effW*triggW"+LumiW);
  cout << CutsName[iCut] << " = " << hwjet->Integral() << endl ;
  wjet2stack->SetBinContent(iCut+1,hwjet->Integral());  
  bkg_tot+=hwjet->Integral();

  delete hwjet;
  delete WJet;  

  TChain * WW =  new TChain("WW");
  WW->Add(Dir+"/MC_TightTight_DABCABC/latino_000_WWJets2LMad.root/latino") ;
  WW->Add(Dir+"/MC_TightTight_DABCABC/latino_001_GluGluToWWTo4L.root/latino");  
  cout << "WW:" << endl;
  TH1F* hww = new TH1F("hww","ww",100, 0,1000);
  WW->Draw(var+">> hww",CutsCut[iCut]+"*puW*baseW*effW*triggW"+LumiW);
  cout << CutsName[iCut] << " = " << hww->Integral() << endl ;
  ww2stack->SetBinContent(iCut+1,hww->Integral());
  bkg_tot+=hww->Integral();

  delete hww;
  delete WW;
  
  // VG

  TChain * VG =  new TChain("VG");
  VG->Add(Dir+"/MC_TightTight_DABCABC/latino_082_WGstarToElNuMad.root/latino");
  VG->Add(Dir+"/MC_TightTight_DABCABC/latino_083_WGstarToMuNuMad.root/latino");
  VG->Add(Dir+"/MC_TightTight_DABCABC/latino_084_WGstarToTauNuMad.root/latino");
  VG->Add(Dir+"/MC_TightTight_DABCABC/latino_085_WgammaToLNuG.root/latino");
  VG->Add(Dir+"/MC_TightTight_DABCABC/latino_086_ZgammaToLLuG.root/latino");

  cout << "VG:" << endl;
  TH1F* hvg = new TH1F("hvg","VG",100, 0,1000);
  VG->Draw(var+">> hvg",CutsCut[iCut]+"*puW*baseW*effW*triggW"+LumiW);
  cout << CutsName[iCut] << " = " << hvg->Integral() << endl ;
  vg2stack->SetBinContent(iCut+1,hvg->Integral());  
  bkg_tot+=hvg->Integral();

  delete hvg;
  delete VG;

  // TTbar
 
  TChain * Top =  new TChain("Top");
  Top->Add(Dir+"/MC_TightTight_DABCABC/latino_019_TTTo2L2Nu2B.root/latino");
  Top->Add(Dir+"/MC_TightTight_DABCABC/latino_011_TtWFullDR.root/latino");
  Top->Add(Dir+"/MC_TightTight_DABCABC/latino_012_TbartWFullDR.root/latino");

  cout << "TOP:" << endl;
  TH1F* htop = new TH1F("htop","top",100, 0,1000);
  Top->Draw(var+">> htop",CutsCut[iCut]+"*puW*0.002328604*effW*triggW"+LumiW);
  cout << CutsName[iCut] << " = " << htop->Integral() << endl ;
  top2stack->SetBinContent(iCut+1,htop->Integral());
  bkg_tot+=htop->Integral(); 

  delete htop;
  delete Top;

  // DYtt

  TChain * DYtt =  new TChain("DYtt");
  DYtt->Add(Dir+"/MC_TightTight_DABCABC/latino_DYtt_19.5fb.root/latino");
  cout << "DYtt:" << endl;
  TH1F* hdytt = new TH1F("hdytt","DYTT",100, 0,1000);
  DYtt->Draw(var+">> hdytt",CutsCut[iCut]+"*puW*baseW*effW*triggW"+LumiW);
  cout << CutsName[iCut] << " = " << hdytt->Integral() << endl ;
  dytt2stack->SetBinContent(iCut+1,hdytt->Integral());
  bkg_tot+=hdytt->Integral();

  delete hdytt;
  delete DYtt;

  // VV = WZ ZZ  WGsToElNuM WGsToMuNu WGsToTauNu WG WZ2L2Q ZZ2L2Q ZGToLLuG

  TChain * VV =  new TChain("VV");
  VV->Add(Dir+"/MC_TightTight_DABCABC/latino_074_WZJetsMad.root/latino");
  VV->Add(Dir+"/MC_TightTight_DABCABC/latino_078_WZTo2L2QMad.root/latino");
  VV->Add(Dir+"/MC_TightTight_DABCABC/latino_075_ZZJetsMad.root/latino");
  VV->Add(Dir+"/MC_TightTight_DABCABC/latino_079_ZZTo2L2QMad.root/latino");
  VV->Add(Dir+"/MC_TightTight_DABCABC/latino_088_WWGJets.root/latino");
  VV->Add(Dir+"/MC_TightTight_DABCABC/latino_089_WZZJets.root/latino");
  VV->Add(Dir+"/MC_TightTight_DABCABC/latino_090_ZZZJets.root/latino");
  VV->Add(Dir+"/MC_TightTight_DABCABC/latino_091_WWZJets.root/latino");
  VV->Add(Dir+"/MC_TightTight_DABCABC/latino_092_WWWJets.root/latino");
  VV->Add(Dir+"/MC_TightTight_DABCABC/latino_093_TTWJets.root/latino");
  VV->Add(Dir+"/MC_TightTight_DABCABC/latino_094_TTZJets.root/latino");
  VV->Add(Dir+"/MC_TightTight_DABCABC/latino_095_TTWWJets.root/latino");
  VV->Add(Dir+"/MC_TightTight_DABCABC/latino_096_TTGJets.root/latino");
  cout << "VV:" << endl;
  TH1F* hvv = new TH1F("hvv","WZ/ZZ/W#gamma/Z#gamma",100, 0,1000);
  VV->Draw(var+">> hvv",CutsCut[iCut]+"*puW*baseW*effW*triggW*(1+0.5*(dataset>=82&&dataset<=84))"+LumiW);
  cout << CutsName[iCut] << " = " << hvv->Integral() << endl ;
  vv2stack->SetBinContent(iCut+1,hvv->Integral());
  bkg_tot+=hvv->Integral();

  delete hvv;
  delete VV;

  // Signal  

  TChain * H125 =  new TChain("H125");
  H125->Add(Dir+"/MC_TightTight_DABCABC/latino_1125_ggToH125toWWTo2LAndTau2Nu.root/latino");
  H125->Add(Dir+"/MC_TightTight_DABCABC/latino_2125_vbfToH125toWWTo2LAndTau2Nu.root/latino");
  H125->Add(Dir+"/MC_TightTight_DABCABC/latino_3125_wzttH125ToWW.root/latino");
  cout << "H125:" << endl;
  TH1F* hh = new TH1F("hh","hh",100, 0,1000);
  H125->Draw(var+">> hh",CutsCut[iCut]+"*puW*baseW*effW*triggW"+LumiW);
  cout << CutsName[iCut] << " = " << hh->Integral() << endl ;
  sig2stack->SetBinContent(iCut+1,(hh->Integral())*100) ;
  sig=hh->Integral();

  delete hh;
  delete H125;

  std::cout << "####### BIN " << iCut << " S/B = " << sig/bkg_tot << std::endl;
}

//sig2stack->SetFillColor(kRed);
sig2stack->SetLineColor(kRed);
sig2stack->SetLineWidth(3);

vv2stack->SetFillColor(858);
dytt2stack->SetFillColor(418);
top2stack->SetFillColor(400);
vg2stack->SetFillColor(617);
ww2stack->SetFillColor(851);
wjet2stack->SetFillColor(921);


TLegend * leg = new TLegend(0.2, 0.6, 0.8, 0.9);
leg->SetFillColor(0);
leg->SetNColumns(3);
leg->AddEntry(vv2stack, "WZ,ZZ,VVV", "f");
leg->AddEntry(wjet2stack, "W+jets", "f");
leg->AddEntry(vg2stack, "V#gamma^{*},V#gamma", "f");
leg->AddEntry(top2stack, "Top", "f");
leg->AddEntry(dytt2stack, "DY#tau#tau", "f");
leg->AddEntry(ww2stack, "WW", "f");        
leg->AddEntry(sig2stack, "ggH+VBF+VH * 100", "f");

THStack* stack =  new THStack();
stack->Add(vg2stack);
stack->Add(vv2stack);
stack->Add(wjet2stack);
stack->Add(ww2stack);
stack->Add(dytt2stack);
stack->Add(top2stack);
//stack->Add(sig2stack);

//stack->SetMinimum(200);

//gPad->SetLogy(1);

stack->Draw();
data->SetMarkerStyle(20);
data->Draw("E1 same");
sig2stack->Draw("same");
//stack->GetYaxis()->SetRangeUser(0.001, 2*stack->GetMaximum());
leg->Draw();
//gPad->Update();

//gPad->SetLogy(1);

}
