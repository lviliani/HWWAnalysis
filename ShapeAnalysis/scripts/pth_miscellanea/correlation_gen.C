void correlation_gen() {

  gStyle->SetOptStat("mri") ;
  TH1::SetDefaultSumw2();
  //gROOT->ProcessLine(".L ~/tdrStyle.C");
  //setTDRStyle();
  gStyle->SetPalette(1);

  TString LumiW = "*19.47" ;

  TString of_gen = "( (abs(leptonGenpid1)==11 && abs(leptonGenpid2)==13) || (abs(leptonGenpid1)==13 && abs(leptonGenpid2)==11) )";

  TString mll_gen = "sqrt(2*leptonGenpt1*leptonGenpt2*(cosh(leptonGeneta1 - leptonGeneta2 ) - cos(leptonGenphi1 - leptonGenphi2)))";
  TString ptll_gen = "sqrt((((leptonGenpt1*cos(leptonGenphi1))+(leptonGenpt2*cos(leptonGenphi2)))*((leptonGenpt1*cos(leptonGenphi1))+(leptonGenpt2*cos(leptonGenphi2))))+(((leptonGenpt1*sin(leptonGenphi1))+(leptonGenpt2*sin(leptonGenphi2)))*((leptonGenpt1*sin(leptonGenphi1))+(leptonGenpt2*sin(leptonGenphi2)))))";
  TString ptnn_gen = "sqrt((((neutrinoGenpt1*cos(neutrinoGenphi1))+(neutrinoGenpt2*cos(neutrinoGenphi2)))*((neutrinoGenpt1*cos(neutrinoGenphi1))+(neutrinoGenpt2*cos(neutrinoGenphi2))))+(((neutrinoGenpt1*sin(neutrinoGenphi1))+(neutrinoGenpt2*sin(neutrinoGenphi2)))*((neutrinoGenpt1*sin(neutrinoGenphi1))+(neutrinoGenpt2*sin(neutrinoGenphi2)))))";
  TString mth_gen = "sqrt( ("+ptll_gen+" + "+ptnn_gen+" )**2 - ( ( leptonGenpt1*cos(leptonGenphi1) + leptonGenpt2*cos(leptonGenphi2) + neutrinoGenpt1*cos(neutrinoGenphi1) + neutrinoGenpt2*cos(neutrinoGenphi2) )**2 + ( leptonGenpt1*sin(leptonGenphi1) + leptonGenpt2*sin(leptonGenphi2) + neutrinoGenpt1*sin(neutrinoGenphi1) + neutrinoGenpt2*sin(neutrinoGenphi2)  )**2 ) )";

  TString acceptance = "( leptonGenpt1>18. && leptonGenpt2>8. && abs(leptonGeneta1)<2.5 && abs(leptonGeneta2)<2.5 && "+ptnn_gen+">15 && "+ptll_gen+">25 && "+mll_gen+">12 && "+mth_gen+">50 && "+of_gen+")";
  TString acceptance_whzh = "("+acceptance + "*( ((mctruth==24 || mctruth==26) && (mcHWWdecay==3) && (leptonGenpt3<0) && (neutrinoGenpt3<0))  ))";

  TString Dir = "/data/lenzip/differential/tree_noskim_gen/nominals/";

  TChain * H125 =  new TChain("latino");
  H125->Add(Dir+"latino_1125_ggToH125toWWTo2LAndTau2Nu.root");
  H125->Add(Dir+"latino_2125_vbfToH125toWWTo2LAndTau2Nu.root");

  TChain * H125_wzh =  new TChain("latino");
  H125_wzh->Add(Dir+"latino_3125_wzttH125ToWW.root");


  H125->Draw(ptll_gen+":"+mll_gen+">> hptllmll(50,12,100,50,25,170)","("+acceptance+")*baseW"+LumiW);
//  H125_wzh->Draw(ptll_gen+":"+mll_gen+">>+ hptllmll(50,12,100,50,0,170)","("+acceptance_whzh+")*baseW"+LumiW);

  H125->Draw(ptll_gen+":"+mth_gen+">> hptllmth(50,50,125,50,25,170)","("+acceptance+")*baseW"+LumiW);
//  H125_wzh->Draw(ptll_gen+":"+mth_gen+">>+ hptllmth(50,50,200,50,0,170)","("+acceptance_whzh+")*baseW"+LumiW);

  TString PtHiggs = "TMath::Min(PtHiggs,167.)";
  
  H125->Draw(PtHiggs+":"+mll_gen+">> hpthmll(50,12,100,50,0,170)","("+acceptance+")*baseW"+LumiW);
//  H125_wzh->Draw(PtHiggs+":"+mll_gen+">>+ hpthmll(50,12,100,50,0,170)","("+acceptance_whzh+")*baseW"+LumiW);

  H125->Draw(PtHiggs+":"+mth_gen+">> hpthmth(50,50,125,50,0,170)","("+acceptance+")*baseW"+LumiW);
//  H125_wzh->Draw(PtHiggs+":"+mth_gen+">>+ hpthmth(50,50,200,50,0,170)","("+acceptance_whzh+")*baseW"+LumiW);

  TCanvas* c1 = new TCanvas();
  c1->cd();
  hpthmll->GetXaxis()->SetTitle("m_{ll,GEN}  (GeV)");
  hpthmll->GetYaxis()->SetTitle("p_{T,GEN}^{H} (GeV)");
  double corrpthmll = hpthmll->GetCorrelationFactor();
  TString corr1;
  corr1.Form("Correlation factor = %f",corrpthmll);
  hpthmll->SetTitle(corr1);
  hpthmll->Draw("COLZ");


  TCanvas* c2 = new TCanvas();
  c2->cd();
  hpthmth->GetXaxis()->SetTitle("m_{T,GEN}^{H}  (GeV)");
  hpthmth->GetYaxis()->SetTitle("p_{T,GEN}^{H} (GeV)");
  double corrpthmth = hpthmth->GetCorrelationFactor();
  TString corr2;
  corr2.Form("Correlation factor = %f",corrpthmth);
  hpthmth->SetTitle(corr2);
  hpthmth->Draw("COLZ");


  TCanvas* c3 = new TCanvas();
  c3->cd();
  hptllmll->GetXaxis()->SetTitle("m_{ll,GEN}  (GeV)");
  hptllmll->GetYaxis()->SetTitle("p_{T,GEN}^{ll} (GeV)");
  double corrptllmll = hptllmll->GetCorrelationFactor();
  TString corr3;
  corr3.Form("Correlation factor = %f",corrptllmll);
  hptllmll->SetTitle(corr3);
  hptllmll->Draw("COLZ");


  TCanvas* c4 = new TCanvas();
  c4->cd();
  hptllmth->GetXaxis()->SetTitle("m_{T,GEN}^{H}  (GeV)");
  hptllmth->GetYaxis()->SetTitle("p_{T,GEN}^{ll} (GeV)");
  double corrptllmth = hptllmth->GetCorrelationFactor();
  TString corr4;
  corr4.Form("Correlation factor = %f",corrptllmth);
  hptllmth->SetTitle(corr4);
  hptllmth->Draw("COLZ");


}
