
void signal_composition(){

  gStyle->SetOptStat("emrio") ;
  TH1::SetDefaultSumw2();

  TString var = "TMath::Min(PtHiggs,167.)";
  //TString var = "TMath::Min(sqrt( (leptonGenpt1*cos(leptonGenphi1)+leptonGenpt2*cos(leptonGenphi2)+neutrinoGenpt1*cos(neutrinoGenphi1)+neutrinoGenpt2*cos(neutrinoGenphi2) )**2 + (leptonGenpt1*sin(leptonGenphi1)+leptonGenpt2*sin(leptonGenphi2)+neutrinoGenpt1*sin(neutrinoGenphi1)+neutrinoGenpt2*sin(neutrinoGenphi2) )**2),167.)";
  //TString var = "1";
  double vedges[] = {0,15,45,85,125,165,200};
  double nbins = 6;

  TString LumiW = "*19.47" ;

  TString leptons_cut = "(!sameflav && trigger==1 && nextra==0 && pt1>20 && pt2>10  && ch1*ch2<0)";
  TString mll_cut = "*(mll>12 && mll<200)";
  TString ptll_cut = "*(ptll>30)";
  TString met_cut = "*(mpmet>20. && pfmet>20.)";
  TString mth_cut = "*(mth>60 && mth<280)";
  TString btag_cut = "*((njet==0)*(bveto_mu==1 && bveto_ip==1) || (njet>0)*(( jetbjpb1<1.4 || jetpt1<30) && ( jetbjpb2<1.4 || jetpt2<30) && ( jetbjpb3<1.4 || jetpt3<30) && ( jetbjpb4<1.4 || jetpt4<30)))";

  TString selection = "("+leptons_cut+mll_cut+met_cut+mth_cut+btag_cut+ptll_cut+")";

  TString of_gen = "( (abs(leptonGenpid1)==11 && abs(leptonGenpid2)==13) || (abs(leptonGenpid1)==13 && abs(leptonGenpid2)==11) )";
  TString of_gen_tau = "( (abs(leptonGenpid1)==11 && abs(leptonGenpid2)==13) || (abs(leptonGenpid1)==13 && abs(leptonGenpid2)==11) || (abs(leptonGenpid1)==11 && abs(leptonGenpid2)==15) || (abs(leptonGenpid1)==15 && abs(leptonGenpid2)==11) || (abs(leptonGenpid1)==15 && abs(leptonGenpid2)==13) || (abs(leptonGenpid1)==13 && abs(leptonGenpid2)==15) || (abs(leptonGenpid1)==15 && abs(leptonGenpid2)==15) || (abs(leptonGenpid1)==15 && abs(leptonGenpid2)==15) )";

  TString mll_gen = "sqrt(2*leptonGenpt1*leptonGenpt2*(cosh(leptonGeneta1 - leptonGeneta2 ) - cos(leptonGenphi1 - leptonGenphi2)))";
  TString ptll_gen = "sqrt((((leptonGenpt1*cos(leptonGenphi1))+(leptonGenpt2*cos(leptonGenphi2)))*((leptonGenpt1*cos(leptonGenphi1))+(leptonGenpt2*cos(leptonGenphi2))))+(((leptonGenpt1*sin(leptonGenphi1))+(leptonGenpt2*sin(leptonGenphi2)))*((leptonGenpt1*sin(leptonGenphi1))+(leptonGenpt2*sin(leptonGenphi2)))))";
  TString ptnn_gen = "sqrt((((neutrinoGenpt1*cos(neutrinoGenphi1))+(neutrinoGenpt2*cos(neutrinoGenphi2)))*((neutrinoGenpt1*cos(neutrinoGenphi1))+(neutrinoGenpt2*cos(neutrinoGenphi2))))+(((neutrinoGenpt1*sin(neutrinoGenphi1))+(neutrinoGenpt2*sin(neutrinoGenphi2)))*((neutrinoGenpt1*sin(neutrinoGenphi1))+(neutrinoGenpt2*sin(neutrinoGenphi2)))))";
  TString mth_gen = "sqrt( ("+ptll_gen+" + "+ptnn_gen+" )**2 - ( ( leptonGenpt1*cos(leptonGenphi1) + leptonGenpt2*cos(leptonGenphi2) + neutrinoGenpt1*cos(neutrinoGenphi1) + neutrinoGenpt2*cos(neutrinoGenphi2) )**2 + ( leptonGenpt1*sin(leptonGenphi1) + leptonGenpt2*sin(leptonGenphi2) + neutrinoGenpt1*sin(neutrinoGenphi1) + neutrinoGenpt2*sin(neutrinoGenphi2)  )**2 ) )";

  TString acceptance = "( leptonGenpt1>18. && leptonGenpt2>8. && abs(leptonGeneta1)<2.5 && abs(leptonGeneta2)<2.5 && "+ptnn_gen+">15 && "+ptll_gen+">25 && "+mll_gen+">12 && "+mth_gen+">50 && "+of_gen+")";
  //TString acceptance = "( leptonGenpt1>20. && leptonGenpt2>10. && abs(leptonGeneta1)<2.5 && abs(leptonGeneta2)<2.5 && "+ptnn_gen+">20 && "+ptll_gen+">30 && "+mll_gen+">12 && "+mth_gen+">60 && "+of_gen+")";

  //TString acceptance = "1";
  TString acceptance_whzh = "("+acceptance + "*( ((mctruth==24 || mctruth==26) && (mcHWWdecay==3) && (leptonGenpt3<0) && (neutrinoGenpt3<0))  ))";

  cout << acceptance << endl;

  TString Dir = "/data/lenzip/differential/tree_noskim_gen/nominals/";

  // Signal  

  TChain * ggH =  new TChain("ggH");
  ggH->Add(Dir+"latino_1125_ggToH125toWWTo2LAndTau2Nu.root/latino");

  TChain * VBF =  new TChain("VBF");
  VBF->Add(Dir+"latino_2125_vbfToH125toWWTo2LAndTau2Nu.root/latino");
  
  TChain * WZH =  new TChain("WZH");
  WZH->Add(Dir+"latino_3125_wzttH125ToWW.root/latino");


  TH1D* hggH = new TH1D("hggH","hggH",nbins,vedges);
  TH1D* hVBF = new TH1D("hVBF","hVBF",nbins,vedges);
  TH1D* hWZH = new TH1D("hWZH","hWZH",nbins,vedges);

//  ggH->Draw(var+">> hggH",acceptance+"*baseW"+LumiW);  
//  VBF->Draw(var+">> hVBF",acceptance+"*baseW"+LumiW);
//  WZH->Draw(var+">> hWZH","("+acceptance_whzh+")*baseW"+LumiW);

  ggH->Draw(var+">> hggH",selection+"*baseW"+LumiW);  
  VBF->Draw(var+">> hVBF",selection+"*baseW"+LumiW);
  WZH->Draw(var+">> hWZH",selection+"*baseW"+LumiW);

  double tot = hggH->Integral()+hVBF->Integral()+hWZH->Integral();
  hggH->Scale(1./tot);
  hVBF->Scale(1./tot);
  hWZH->Scale(1./tot);


  TH1D* hggH2 = (TH1D*)hggH->Clone();
  TH1D* hVBF2 = (TH1D*)hVBF->Clone();
  TH1D* hWZH2 = (TH1D*)hWZH->Clone();

  hggH2->SetLineColor(kBlue);
  hVBF2->SetLineColor(kRed);
  hWZH2->SetLineColor(kGreen);
  hggH2->SetLineWidth(2);
  hVBF2->SetLineWidth(2);
  hWZH2->SetLineWidth(2);
  
  for(int bin=1; bin<7; bin++){
    double bin_int = hggH->GetBinContent(bin)+hVBF->GetBinContent(bin)+hWZH->GetBinContent(bin);
    hggH2->SetBinContent(bin, (hggH->GetBinContent(bin))/bin_int);
    hVBF2->SetBinContent(bin, (hVBF->GetBinContent(bin))/bin_int);
    hWZH2->SetBinContent(bin, (hWZH->GetBinContent(bin))/bin_int);
  }

  TCanvas* c2 = new TCanvas();
  c2->cd();

  TLegend * leg2 = new TLegend(0.2, 0.6, 0.8, 0.9);
  leg2->SetFillColor(0);
  leg2->AddEntry(hggH2, "ggH", "f");
  leg2->AddEntry(hVBF2, "VBF", "f");
  leg2->AddEntry(hWZH2, "VH", "f");

  hggH2->SetFillColor(kBlue);
  hVBF2->SetFillColor(kRed);
  hWZH2->SetFillColor(kGreen);
  hggH2->SetFillStyle(3004);
  hVBF2->SetFillStyle(3004);
  hWZH2->SetFillStyle(3004);

  THStack* stack = new THStack();
  stack->Add(hggH2,"histo");
  stack->Add(hVBF2,"histo");
  stack->Add(hWZH2,"histo");

  stack->Draw();
  leg2->Draw();

}
