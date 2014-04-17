#include "TH2F.h"
#include "TString.h"
#include "TFile.h"
#include <vector>

const int nMuJetET = 10;
const int nElJetET = 3;


class FakeProbabilities {
 public:
  //! constructor at least wants leptons and MET
  FakeProbabilities();
  virtual ~FakeProbabilities() {}

  double rate(double pt,double eta,TH2F* h2, int stat);
  void setHisto2D(TH2F* H2, TString fname, TString type);
  void setHisto2D(TH2F* fakeH2Mu,TH2F* fakeH2MuUp,TH2F* fakeH2MuDn,TH2F* promptH2Mu,TH2F* fakeH2El,TH2F* fakeH2ElUp,TH2F* fakeH2ElDn,TH2F* promptH2El);
  void setFRElectrons(TH2F* fakeH2El,  TFile *FR_file);
  void setPRElectrons(TH2F* promptH2El,  TFile *PR_file);
  void setFRMuons(TH2F* fakeH2Mu, TFile *FR_file);
  void setPRMuons(TH2F* promptH2Mu, TFile *PR_file);

  void SetKinematic(float pt1, float eta1, float id1, float type1, float pt2, float eta2, float id2, float type2, float pt3, float eta3, float id3, float type3, float pt4, float eta4, float id4, float type4);
  void SetNjet(float njet);
  //! probability fuctions
  double FakeW3l(int syst);  //---- syst = -1 down, 0 nominal, 1 up
  double FakeW3l(int syst, float pt1, float eta1, float id1, float type1, float pt2, float eta2, float id2, float type2, float pt3, float eta3, float id3, float type3);
  double GetPPFWeight(int muonJetPt, int elecJetPt);
  double GetPFFWeight(int muonJetPt, int elecJetPt);
  double GetFFFWeight(int muonJetPt, int elecJetPt);
  double GetPPPWeight(int muonJetPt, int elecJetPt);

  double FakeW4l(int syst);
  double FakeW4l(int syst, float pt1, float eta1, float id1, float type1, float pt2, float eta2, float id2, float type2, float pt3, float eta3, float id3, float type3, float pt4, float eta4, float id4, float type4);
  double GetPPPPWeight(int muonJetPt, int elecJetPt);

  double GetFakeElectron(float pt, float eta, int jetit);
  double GetFakeMuon(float pt, float eta, int jetit);
  double GetPromptElectron(float pt, float eta);
  double GetPromptMuon(float pt, float eta);


 private:

  int njet_;

  float pt1_;
  float eta1_;
  float id1_;
  float type1_;  //---- 1 = pass (a.k.a. tight),   0 = fail

  float pt2_;
  float eta2_;
  float id2_;
  float type2_;

  float pt3_;
  float eta3_;
  float id3_;
  float type3_;

  float pt4_;
  float eta4_;
  float id4_;
  float type4_;

  TH2F* fakeMuH2[nMuJetET];
  TH2F* fakeElH2[nElJetET];
  TH2F* promptMuH2;
  TH2F* promptElH2;

};


//---- init ----

FakeProbabilities::FakeProbabilities() {
 //- FakeRate
 const int ptBinsSizeMuFake(5);
 float ptBinsMuFake[ptBinsSizeMuFake+1];
 ptBinsMuFake[0] = 10;
 ptBinsMuFake[1] = 15;
 ptBinsMuFake[2] = 20;
 ptBinsMuFake[3] = 25;
 ptBinsMuFake[4] = 30;
 ptBinsMuFake[5] = 35;

 const int etaBinsSizeMuFake(4);
 float etaBinsMuFake[etaBinsSizeMuFake+1];
 etaBinsMuFake[0] = 0;
 etaBinsMuFake[1] = 1.0;
 etaBinsMuFake[2] = 1.479;
 etaBinsMuFake[3] = 2.0;
 etaBinsMuFake[4] = 2.5;

 const int ptBinsSizeElFake(5);
 float ptBinsElFake[ptBinsSizeElFake+1];
 ptBinsElFake[0] = 10;
 ptBinsElFake[1] = 15;
 ptBinsElFake[2] = 20;
 ptBinsElFake[3] = 25;
 ptBinsElFake[4] = 30;
 ptBinsElFake[5] = 35;

 const int etaBinsSizeElFake(4);
 float etaBinsElFake[etaBinsSizeElFake+1];
 etaBinsElFake[0] = 0;
 etaBinsElFake[1] = 1.0;
 etaBinsElFake[2] = 1.479;
 etaBinsElFake[3] = 2.0;
 etaBinsElFake[4] = 2.5;

 //- PromptRate
 const int ptBinsSizeMuPrompt(5);
 float ptBinsMuPrompt[ptBinsSizeMuPrompt+1];
 ptBinsMuPrompt[0] = 10;
 ptBinsMuPrompt[1] = 15;
 ptBinsMuPrompt[2] = 20;
 ptBinsMuPrompt[3] = 25;
 ptBinsMuPrompt[4] = 50;
 ptBinsMuPrompt[5] = 100;

 const int etaBinsSizeMuPrompt(2);
 float etaBinsMuPrompt[etaBinsSizeMuPrompt+1];
 etaBinsMuPrompt[0] = 0;
 etaBinsMuPrompt[1] = 1.5;
 etaBinsMuPrompt[2] = 2.4;

 const int ptBinsSizeElPrompt(5);
 float ptBinsElPrompt[ptBinsSizeElPrompt+1];
 ptBinsElPrompt[0] = 10;
 ptBinsElPrompt[1] = 15;
 ptBinsElPrompt[2] = 20;
 ptBinsElPrompt[3] = 25;
 ptBinsElPrompt[4] = 50;
 ptBinsElPrompt[5] = 100;

 const int etaBinsSizeElPrompt(3);
 float etaBinsElPrompt[etaBinsSizeElPrompt+1];
 etaBinsElPrompt[0] = 0;
 etaBinsElPrompt[1] = 1.4442;
 etaBinsElPrompt[2] = 1.566;
 etaBinsElPrompt[3] = 2.5;

 // histograms for FR (with different jet ET thresholds) and PR 
//  int muJetETdn = 2, muJetETnom = 3, muJetETup = 6; // 15/20/35 for 0jet (+05 for 1-jet, +10 for 2-jet for nominal)
//  int elJetETdn = 0, elJetETnom = 1, elJetETup = 2; // 15/35/50
 TString muJetET[nMuJetET] = { "05", "10", "15", "20", "25", "30", "35", "40", "45", "50" };
 TString elJetET[nElJetET] = { "15", "35", "50" };

 TString dirhisto = "results/";
 for (int i=0; i<nMuJetET; ++i) {
  fakeMuH2[i] = new TH2F("fakeMuH2_jet"+muJetET[i],"fakeMuH2_jet"+muJetET[i],             ptBinsSizeMuFake,ptBinsMuFake,            etaBinsSizeMuFake,etaBinsMuFake);
  TString fnamemu = dirhisto+"MuFR_Moriond13_jet"+muJetET[i]+"_EWKcorr.root";
  setHisto2D(fakeMuH2[i], fnamemu, "FRMu");
 }
 for (int i=0; i<nElJetET; ++i) {
  fakeElH2[i] = new TH2F("fakeElH2_jet"+elJetET[i],"fakeElH2_jet"+elJetET[i],             ptBinsSizeElFake,ptBinsElFake,            etaBinsSizeElFake,etaBinsElFake);
  TString fnameel = dirhisto+"fakerates_trigger_Moriond13_ewksub_jet"+elJetET[i]+".root";
  setHisto2D(fakeElH2[i], fnameel, "FREl");
 }

 promptMuH2 = new TH2F("promptMuH2","promptMuH2",              ptBinsSizeMuPrompt,ptBinsMuPrompt,              etaBinsSizeMuPrompt,etaBinsMuPrompt);
 setHisto2D(promptMuH2, dirhisto+"prompt_rateMuons_Moriond13.root",     "PRMu");
 promptElH2 = new TH2F("promptElH2","promptElH2",              ptBinsSizeElPrompt,ptBinsElPrompt,              etaBinsSizeElPrompt,etaBinsElPrompt);
 setHisto2D(promptElH2, dirhisto+"prompt_rateElectrons_Moriond13.root", "PREl");

}




double FakeProbabilities::rate(double pt,double eta,TH2F* h2, int stat){

 double etaMax = h2->GetYaxis()->GetBinUpEdge(h2->GetYaxis()->GetNbins());
 double ptMax  = h2->GetXaxis()->GetBinUpEdge(h2->GetXaxis()->GetNbins());
 double ptMin  = h2->GetXaxis()->GetBinLowEdge(1);
 double eps = 0.001;

 float ptbound  = std::min(pt,ptMax-eps);
 if (ptbound<ptMin+eps) ptbound = ptMin+eps;
 float etabound = std::min(fabs(eta),etaMax-eps);
 int bin = h2->FindFixBin(ptbound,etabound);
 double result = h2->GetBinContent(bin);
 double error  = h2->GetBinError(bin);
 return (result+float(stat)*error);

}

// with systematics - maiko

void FakeProbabilities::setHisto2D(TH2F* fakeH2Mu,TH2F* fakeH2MuUp,TH2F* fakeH2MuDn,TH2F* promptH2Mu,TH2F* fakeH2El,TH2F* fakeH2ElUp,TH2F* fakeH2ElDn,TH2F* promptH2El){

 //--- [2012 analysis] ---//
 // ----------- Initialize FR and PR -------------------

 TFile *muFR_jet05 = TFile::Open("results/MuFR_Moriond13_jet05_EWKcorr.root");
 TFile *muFR_jet15 = TFile::Open("results/MuFR_Moriond13_jet15_EWKcorr.root"); 
 TFile *muFR_jet30 = TFile::Open("results/MuFR_Moriond13_jet30_EWKcorr.root");
 TFile *muPR = TFile::Open("results/prompt_rateMuons_Moriond13.root");

 TFile *elFR_jet15 = TFile::Open("results/fakerates_trigger_Moriond13_ewksub_jet15.root");
 TFile *elFR_jet35 = TFile::Open("results/fakerates_trigger_Moriond13_ewksub.root");
 TFile *elFR_jet50 = TFile::Open("results/fakerates_trigger_Moriond13_ewksub_jet50.root");
 TFile *elPR = TFile::Open("results/prompt_rateElectrons_Moriond13.root"); 

 setFRMuons(fakeH2Mu,   muFR_jet15);
 setFRMuons(fakeH2MuUp, muFR_jet30);
 setFRMuons(fakeH2MuDn, muFR_jet05);
 setPRMuons(promptH2Mu, muPR);
 setFRElectrons(fakeH2El,   elFR_jet35);
 setFRElectrons(fakeH2ElUp, elFR_jet50);
 setFRElectrons(fakeH2ElDn, elFR_jet15);
 setPRElectrons(promptH2El, elPR);

}

// for a given file name - maiko
// type = "FRMu", "FREl", "PRMu", "PREl"

void FakeProbabilities::setHisto2D(TH2F* H2, TString fname, TString type) {

 TFile *file = TFile::Open(fname);

 type.ToLower();
 if      (type=="frmu") setFRMuons(     H2, file);
 else if (type=="frel") setFRElectrons( H2, file);
 else if (type=="prmu") setPRMuons(     H2, file);
 else if (type=="prel") setPRElectrons( H2, file);

}


//-------------------------//
//--- [2012 analysis] ---// 
//-------------------------//

void FakeProbabilities::setPRMuons(TH2F* promptH2Mu, TFile *PR_file){

 PR_file->cd();

 TH2F *histoPR = (TH2F*)((TH2F*)PR_file->Get("effDATA_prompt_rate"))->Clone(); //effDATA_Prompt_Rate->Clone();

 for (int i = 1; i < 6; i++) {
  for (int j = 1; j < 3; j++) {
   float value = histoPR->GetBinContent(j,i);
   float error = histoPR->GetBinError(j,i);

   promptH2Mu->SetBinContent(i,j,value);
   promptH2Mu->SetBinError(i,j,error);
  }
 }

 PR_file->Close();
}



void FakeProbabilities::setFRMuons(TH2F* fakeH2Mu, TFile *FR_file){

 FR_file->cd();  

 TH2F *histoFR = (TH2F*)((TH2F*)FR_file->Get("FR_pT_eta_EWKcorr"))->Clone();

 for (int i = 1; i < 6; i++) {
  for (int j = 1; j < 5; j++) {
   float value = histoFR->GetBinContent(i,j);
   float error = histoFR->GetBinError(i,j);

   fakeH2Mu->SetBinContent(i,j,value);
   fakeH2Mu->SetBinError(i,j,error);
  }
 }

 FR_file->Close();
}

void FakeProbabilities::setPRElectrons(TH2F* promptH2El,  TFile *PR_file){

 PR_file->cd();

 TH2F *histoPR = (TH2F*)((TH2F*)PR_file->Get("effDATA_All_selec"))->Clone(); //effDATA_Prompt_Rate->Clone();

 for (int i = 1; i < 6; i++) {
  float valueB = histoPR->GetBinContent(1,i);
  float errorB = histoPR->GetBinError(1,i);
  float valueCr = histoPR->GetBinContent(2,i);
  float errorCr = histoPR->GetBinError(2,i);
  float valueE = histoPR->GetBinContent(3,i);
  float errorE = histoPR->GetBinError(3,i);

  promptH2El->SetBinContent(i,1,valueB);
  promptH2El->SetBinError(i,1,errorB);
  promptH2El->SetBinContent(i,2,valueCr);
  promptH2El->SetBinError(i,2,errorCr);
  promptH2El->SetBinContent(i,3,valueE);
  promptH2El->SetBinError(i,3,errorE);
 }
 PR_file->Close();
}

void FakeProbabilities::setFRElectrons(TH2F* fakeH2El,  TFile *FR_file){

 FR_file->cd();

 TH1F *histoFR_B1 = (TH1F*)((TH1F*)FR_file->Get("TrgElenewWPHWWPtBarrel1"))->Clone();
 TH1F *histoFR_B2 = (TH1F*)((TH1F*)FR_file->Get("TrgElenewWPHWWPtBarrel2"))->Clone();
 TH1F *histoFR_E1 = (TH1F*)((TH1F*)FR_file->Get("TrgElenewWPHWWPtEndcap1"))->Clone();
 TH1F *histoFR_E2 = (TH1F*)((TH1F*)FR_file->Get("TrgElenewWPHWWPtEndcap2"))->Clone();

 for (int i = 4; i < 9; i++) {
  float valueB1 = histoFR_B1->GetBinContent(i);
  float errorB1 = histoFR_B1->GetBinError(i);
  float valueB2 = histoFR_B2->GetBinContent(i);
  float errorB2 = histoFR_B2->GetBinError(i);
  float valueE1 = histoFR_E1->GetBinContent(i);
  float errorE1 = histoFR_E1->GetBinError(i);
  float valueE2 = histoFR_E2->GetBinContent(i);
  float errorE2 = histoFR_E2->GetBinError(i);

  fakeH2El->SetBinContent(i-3,1,valueB1);
  fakeH2El->SetBinError(i-3,1,errorB1);
  fakeH2El->SetBinContent(i-3,2,valueB2);
  fakeH2El->SetBinError(i-3,2,errorB2);
  fakeH2El->SetBinContent(i-3,3,valueE1);
  fakeH2El->SetBinError(i-3,3,errorE1);
  fakeH2El->SetBinContent(i-3,4,valueE2);
  fakeH2El->SetBinError(i-3,4,errorE2);

 }

 FR_file->Close();


}



///---- actual "get fake/prompt" ----

double FakeProbabilities::GetFakeElectron(float pt, float eta, int jetit) {
 float result = 1.;
 result = fakeElH2[jetit]->GetBinContent(fakeElH2[jetit]->FindBin(std::min(1.*pt,35.),eta));
 return result;
}

double FakeProbabilities::GetFakeMuon(float pt, float eta, int jetit) {
 float result = 1.;
 result = fakeMuH2[jetit]->GetBinContent(fakeMuH2[jetit]->FindBin(std::min(1.*pt,35.),eta));
 return result;
}

double FakeProbabilities::GetPromptElectron(float pt, float eta) {
 float result = 1.;
 result = promptElH2->GetBinContent(promptElH2->FindBin(std::min(1.*pt,35.),eta));
 return result;
}

double FakeProbabilities::GetPromptMuon(float pt, float eta) {
 float result = 1.;
 result = promptMuH2->GetBinContent(promptMuH2->FindBin(std::min(1.*pt,35.),eta));
 return result;
}


//---- init kinematic ----

void FakeProbabilities::SetKinematic(float pt1, float eta1, float id1, float type1, float pt2, float eta2, float id2, float type2, float pt3, float eta3, float id3, float type3, float pt4, float eta4, float id4, float type4) {
 pt1_   = pt1;
 eta1_  = eta1;
 id1_   = id1;
 type1_ = type1;

 pt2_   = pt2;
 eta2_  = eta2;
 id2_   = id2;
 type2_ = type2;

 pt3_   = pt3;
 eta3_  = eta3;
 id3_   = id3;
 type3_ = type3;

 pt4_   = pt4;
 eta4_  = eta4;
 id4_   = id4;
 type4_ = type4;

}


void FakeProbabilities::SetNjet(float njet) {
 njet_ = int(njet);
}



//---- 3 leptons case ----

double FakeProbabilities::FakeW3l(int syst){
 float weight = 1.;

 int muonJetPt = -1;
 int elecJetPt = -1;

 if (njet_ == 0  &&  syst == -1) { muonJetPt = 2;   elecJetPt = 0;  }
 if (njet_ == 0  &&  syst ==  0) { muonJetPt = 3;   elecJetPt = 1;  }
 if (njet_ == 0  &&  syst ==  1) { muonJetPt = 6;   elecJetPt = 2;  }

 if (njet_ == 1  &&  syst == -1) { muonJetPt = 3;   elecJetPt = 0;  }
 if (njet_ == 1  &&  syst ==  0) { muonJetPt = 4;   elecJetPt = 1;  }
 if (njet_ == 1  &&  syst ==  1) { muonJetPt = 7;   elecJetPt = 2;  }

 if (njet_ >= 2  &&  syst == -1) { muonJetPt = 4;   elecJetPt = 0;  }
 if (njet_ >= 2  &&  syst ==  0) { muonJetPt = 5;   elecJetPt = 1;  }
 if (njet_ >= 2  &&  syst ==  1) { muonJetPt = 8;   elecJetPt = 2;  }

 //---- muons:  15/20/35 for 0jet (+05 for 1-jet, +10 for 2-jet for nominal)
 //---- electrons:    15/35/50
 //                                  0     1     2     3     4     5     6     7     8     9
 //  TString muJetET[nMuJetET] = { "05", "10", "15", "20", "25", "30", "35", "40", "45", "50" };
 //  TString elJetET[nElJetET] = { "15", "35", "50" };

 weight = GetPPPWeight( muonJetPt,    elecJetPt);
 return weight;

}


double FakeProbabilities::FakeW3l(int syst, float pt1, float eta1, float id1, float type1, float pt2, float eta2, float id2, float type2, float pt3, float eta3, float id3, float type3){
 pt1_   = pt1;
 eta1_  = eta1;
 id1_   = id1;
 type1_ = type1;

 pt2_   = pt2;
 eta2_  = eta2;
 id2_   = id2;
 type2_ = type2;

 pt3_   = pt3;
 eta3_  = eta3;
 id3_   = id3;
 type3_ = type3;

 return FakeW3l(syst);
}


//----------------------
//---- GetPPFWeight ----
//----------------------
double FakeProbabilities::GetPPFWeight(int muonJetPt, int elecJetPt) {
 double promptProbability[3];
 double fakeProbability[3];

 double pt[3];
 double eta[3];
 double id[3];
 double type[3];

 pt[0] = pt1_;        pt[1] = pt2_;        pt[2] = pt3_;
 eta[0] = eta1_;      eta[1] = eta2_;      eta[2] = eta3_;
 id[0] = id1_;        id[1] = id2_;        id[2] = id3_;
 type[0] = type1_;    type[1] = type2_;    type[2] = type3_;

 double f;
 double p;

 for (int ilep = 0; ilep<3; ilep++) {
  f = (abs(id[ilep]) == 13)   ?   GetFakeMuon(pt[ilep], eta[ilep], muonJetPt)    :   GetFakeElectron(pt[ilep], eta[ilep], elecJetPt);
  p = (abs(id[ilep]) == 13)   ?   GetPromptMuon(pt[ilep], eta[ilep])             :   GetPromptElectron(pt[ilep], eta[ilep]);

  if (type[ilep] == 1){
   promptProbability[ilep] = p * (1 - f);
   fakeProbability[ilep] = f * (1 - p);
  }
  else {
   promptProbability[ilep] = p * f;
   fakeProbability[ilep] = p * f;
  }
  promptProbability[ilep] /= (p - f);
  fakeProbability[ilep] /= (p - f);
 }

 //---- now combine properly
 double PPF = promptProbability[0] * promptProbability[1] * fakeProbability[2];
 double PFP = promptProbability[0] * fakeProbability[1]   * promptProbability[2];
 double FPP = fakeProbability[0]   * promptProbability[1] * promptProbability[2];

 double result = PPF + PFP + FPP;

 int nTight = type1_+type2_+type3_;
 if ( nTight == 1 || nTight == 3) result *= -1.;

 return result;
}




//----------------------
//---- GetPFFWeight ----
//----------------------
double FakeProbabilities::GetPFFWeight(int muonJetPt, int elecJetPt) {
 double promptProbability[3];
 double fakeProbability[3];

 double pt[3];
 double eta[3];
 double id[3];
 double type[3];

 pt[0] = pt1_;        pt[1] = pt2_;        pt[2] = pt3_;
 eta[0] = eta1_;      eta[1] = eta2_;      eta[2] = eta3_;
 id[0] = id1_;        id[1] = id2_;        id[2] = id3_;
 type[0] = type1_;    type[1] = type2_;    type[2] = type3_;

 double f;
 double p;

 for (int ilep = 0; ilep<3; ilep++) {
  f = (abs(id[ilep]) == 13)   ?   GetFakeMuon(pt[ilep], eta[ilep], muonJetPt)    :   GetFakeElectron(pt[ilep], eta[ilep], elecJetPt);
  p = (abs(id[ilep]) == 13)   ?   GetPromptMuon(pt[ilep], eta[ilep])             :   GetPromptElectron(pt[ilep], eta[ilep]);

  if (type[ilep] == 1){
   promptProbability[ilep] = p * (1 - f);
   fakeProbability[ilep] = f * (1 - p);
  }
  else {
   promptProbability[ilep] = p * f;
   fakeProbability[ilep] = p * f;
  }
  promptProbability[ilep] /= (p - f);
  fakeProbability[ilep] /= (p - f);
 }

 //---- now combine properly
 Double_t PFF = promptProbability[0] * fakeProbability[1] * fakeProbability[2];
 Double_t FPF = fakeProbability[0] * promptProbability[1] * fakeProbability[2];
 Double_t FFP = fakeProbability[0] * fakeProbability[1] * promptProbability[2];

 double result = PFF + FPF + FFP;

 int nTight = type1_+type2_+type3_;
 if ( nTight == 0 || nTight == 2) result *= -1.;

 return result;
}



//----------------------
//---- GetFFFWeight ----
//----------------------
double FakeProbabilities::GetFFFWeight(int muonJetPt, int elecJetPt) {
 double promptProbability[3];
 double fakeProbability[3];

 double pt[3];
 double eta[3];
 double id[3];
 double type[3];

 pt[0] = pt1_;        pt[1] = pt2_;        pt[2] = pt3_;
 eta[0] = eta1_;      eta[1] = eta2_;      eta[2] = eta3_;
 id[0] = id1_;        id[1] = id2_;        id[2] = id3_;
 type[0] = type1_;    type[1] = type2_;    type[2] = type3_;

 double f;
 double p;

 for (int ilep = 0; ilep<3; ilep++) {
  f = (abs(id[ilep]) == 13)   ?   GetFakeMuon(pt[ilep], eta[ilep], muonJetPt)    :   GetFakeElectron(pt[ilep], eta[ilep], elecJetPt);
  p = (abs(id[ilep]) == 13)   ?   GetPromptMuon(pt[ilep], eta[ilep])             :   GetPromptElectron(pt[ilep], eta[ilep]);

  if (type[ilep] == 1){
   promptProbability[ilep] = p * (1 - f);
   fakeProbability[ilep] = f * (1 - p);
  }
  else {
   promptProbability[ilep] = p * f;
   fakeProbability[ilep] = p * f;
  }
  promptProbability[ilep] /= (p - f);
  fakeProbability[ilep] /= (p - f);
 }

 //---- now combine properly
 Double_t FFF = fakeProbability[0] * fakeProbability[1] * fakeProbability[2];

 double result = FFF;

 int nTight = type1_+type2_+type3_;
 if ( nTight == 0 || nTight == 2) result *= -1.;

 return result;
}




//----------------------
//---- GetPPPWeight ----
//----------------------
double FakeProbabilities::GetPPPWeight(int muonJetPt, int elecJetPt) {
 double promptProbability[3];
 double fakeProbability[3];

 double pt[3];
 double eta[3];
 double id[3];
 double type[3];

 pt[0] = pt1_;        pt[1] = pt2_;        pt[2] = pt3_;
 eta[0] = eta1_;      eta[1] = eta2_;      eta[2] = eta3_;
 id[0] = id1_;        id[1] = id2_;        id[2] = id3_;
 type[0] = type1_;    type[1] = type2_;    type[2] = type3_;

 double f;
 double p;

 for (int ilep = 0; ilep<3; ilep++) {
  f = (abs(id[ilep]) == 13)   ?   GetFakeMuon(pt[ilep], eta[ilep], muonJetPt)    :   GetFakeElectron(pt[ilep], eta[ilep], elecJetPt);
  p = (abs(id[ilep]) == 13)   ?   GetPromptMuon(pt[ilep], eta[ilep])             :   GetPromptElectron(pt[ilep], eta[ilep]);

  if (type[ilep] == 1){
   promptProbability[ilep] = p * (1 - f);
   fakeProbability[ilep] = f * (1 - p);
  }
  else {
   promptProbability[ilep] = p * f;
   fakeProbability[ilep] = p * f;
  }
  promptProbability[ilep] /= (p - f);
  fakeProbability[ilep] /= (p - f);
 }

 //---- now combine properly
 Double_t PPP = promptProbability[0] * promptProbability[1] * promptProbability[2];

 double result = PPP;

 int nTight = type1_+type2_+type3_;
 if ( nTight == 0 || nTight == 2) result *= -1.;

 return result;
}




//---- 4 leptons case ----

double FakeProbabilities::FakeW4l(int syst){
 float weight = 1.;

 int muonJetPt = -1;
 int elecJetPt = -1;

 if (njet_ == 0  &&  syst == -1) { muonJetPt = 2;   elecJetPt = 0;  }
 if (njet_ == 0  &&  syst ==  0) { muonJetPt = 3;   elecJetPt = 1;  }
 if (njet_ == 0  &&  syst ==  1) { muonJetPt = 6;   elecJetPt = 2;  }

 if (njet_ == 1  &&  syst == -1) { muonJetPt = 3;   elecJetPt = 0;  }
 if (njet_ == 1  &&  syst ==  0) { muonJetPt = 4;   elecJetPt = 1;  }
 if (njet_ == 1  &&  syst ==  1) { muonJetPt = 7;   elecJetPt = 2;  }

 if (njet_ >= 2  &&  syst == -1) { muonJetPt = 4;   elecJetPt = 0;  }
 if (njet_ >= 2  &&  syst ==  0) { muonJetPt = 5;   elecJetPt = 1;  }
 if (njet_ >= 2  &&  syst ==  1) { muonJetPt = 8;   elecJetPt = 2;  }

 //---- muons:  15/20/35 for 0jet (+05 for 1-jet, +10 for 2-jet for nominal)
 //---- electrons:    15/35/50
 //                                  0     1     2     3     4     5     6     7     8     9
 //  TString muJetET[nMuJetET] = { "05", "10", "15", "20", "25", "30", "35", "40", "45", "50" };
 //  TString elJetET[nElJetET] = { "15", "35", "50" };

 weight = GetPPPPWeight( muonJetPt,    elecJetPt);
 return weight;
}


double FakeProbabilities::FakeW4l(int syst, float pt1, float eta1, float id1, float type1, float pt2, float eta2, float id2, float type2, float pt3, float eta3, float id3, float type3, float pt4, float eta4, float id4, float type4){
 pt1_   = pt1;
 eta1_  = eta1;
 id1_   = id1;
 type1_ = type1;

 pt2_   = pt2;
 eta2_  = eta2;
 id2_   = id2;
 type2_ = type2;

 pt3_   = pt3;
 eta3_  = eta3;
 id3_   = id3;
 type3_ = type3;

 pt4_   = pt4;
 eta4_  = eta4;
 id4_   = id4;
 type4_ = type4;

 return FakeW4l(syst);
}




//----------------------
//---- GetPPPPWeight ----
//----------------------
double FakeProbabilities::GetPPPPWeight(int muonJetPt, int elecJetPt) {
 double promptProbability[4];
 double fakeProbability[4];

 double pt[4];
 double eta[4];
 double id[4];
 double type[4];

 pt[0] = pt1_;        pt[1] = pt2_;        pt[2] = pt3_;        pt[3] = pt4_;
 eta[0] = eta1_;      eta[1] = eta2_;      eta[2] = eta3_;      eta[3] = eta4_;
 id[0] = id1_;        id[1] = id2_;        id[2] = id3_;        id[3] = id4_;
 type[0] = type1_;    type[1] = type2_;    type[2] = type3_;    type[3] = type4_;

 double f;
 double p;

 for (int ilep = 0; ilep<4; ilep++) {
  f = (abs(id[ilep]) == 13)   ?   GetFakeMuon(pt[ilep], eta[ilep], muonJetPt)    :   GetFakeElectron(pt[ilep], eta[ilep], elecJetPt);
  p = (abs(id[ilep]) == 13)   ?   GetPromptMuon(pt[ilep], eta[ilep])             :   GetPromptElectron(pt[ilep], eta[ilep]);

  if (type[ilep] == 1){
   promptProbability[ilep] = p * (1 - f);
   fakeProbability[ilep] = f * (1 - p);
  }
  else {
   promptProbability[ilep] = p * f;
   fakeProbability[ilep] = p * f;
  }
  promptProbability[ilep] /= (p - f);
  fakeProbability[ilep] /= (p - f);
 }

 //---- now combine properly
 Double_t PPPP = promptProbability[0] * promptProbability[1] * promptProbability[2] * promptProbability[3];

 double result = PPPP;

 int nTight = type1_+type2_+type3_+type4_;
 if ( nTight == 1 || nTight == 3) result *= -1.;

 return result;
}

