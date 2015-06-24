
void eff_sel(){

  gStyle->SetOptStat("emrio") ;
  TH1::SetDefaultSumw2();

  TString var = "TMath::Min(PtHiggs,167.)";
  //TString var = "TMath::Min(sqrt( (leptonGenpt1*cos(leptonGenphi1)+leptonGenpt2*cos(leptonGenphi2)+neutrinoGenpt1*cos(neutrinoGenphi1)+neutrinoGenpt2*cos(neutrinoGenphi2) )**2 + (leptonGenpt1*sin(leptonGenphi1)+leptonGenpt2*sin(leptonGenphi2)+neutrinoGenpt1*sin(neutrinoGenphi1)+neutrinoGenpt2*sin(neutrinoGenphi2) )**2),167.)";
  //TString var = "1";
  double vedges[] = {0,15,45,87,125,162,200};
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
  TString mll_gen = "sqrt(2*leptonGenpt1*leptonGenpt2*(cosh(leptonGeneta1 - leptonGeneta2 ) - cos(leptonGenphi1 - leptonGenphi2)))";
  TString ptll_gen = "sqrt((((leptonGenpt1*cos(leptonGenphi1))+(leptonGenpt2*cos(leptonGenphi2)))*((leptonGenpt1*cos(leptonGenphi1))+(leptonGenpt2*cos(leptonGenphi2))))+(((leptonGenpt1*sin(leptonGenphi1))+(leptonGenpt2*sin(leptonGenphi2)))*((leptonGenpt1*sin(leptonGenphi1))+(leptonGenpt2*sin(leptonGenphi2)))))";
  TString ptnn_gen = "sqrt((((neutrinoGenpt1*cos(neutrinoGenphi1))+(neutrinoGenpt2*cos(neutrinoGenphi2)))*((neutrinoGenpt1*cos(neutrinoGenphi1))+(neutrinoGenpt2*cos(neutrinoGenphi2))))+(((neutrinoGenpt1*sin(neutrinoGenphi1))+(neutrinoGenpt2*sin(neutrinoGenphi2)))*((neutrinoGenpt1*sin(neutrinoGenphi1))+(neutrinoGenpt2*sin(neutrinoGenphi2)))))";
  TString mth_gen = "sqrt( ("+ptll_gen+" + "+ptnn_gen+" )**2 - ( ( leptonGenpt1*cos(leptonGenphi1) + leptonGenpt2*cos(leptonGenphi2) + neutrinoGenpt1*cos(neutrinoGenphi1) + neutrinoGenpt2*cos(neutrinoGenphi2) )**2 + ( leptonGenpt1*sin(leptonGenphi1) + leptonGenpt2*sin(leptonGenphi2) + neutrinoGenpt1*sin(neutrinoGenphi1) + neutrinoGenpt2*sin(neutrinoGenphi2)  )**2 ) )";

  TString acceptance = "( leptonGenpt1>18. && leptonGenpt2>8. && abs(leptonGeneta1)<2.5 && abs(leptonGeneta2)<2.5 && "+ptnn_gen+">15 && "+ptll_gen+">25 && "+mll_gen+">12 && "+mth_gen+">50 && "+of_gen+")";
  //TString acceptance = "1";
  TString acceptance_whzh = "("+acceptance + "*( ((mctruth==24 || mctruth==26) && (mcHWWdecay==3) && (leptonGenpt3<0) && (neutrinoGenpt3<0))  ))";

  cout << acceptance << endl;

  TString Dir = "/data/lenzip/differential/tree_noskim_gen/nominals/";

  // Signal  

  TChain * H125 =  new TChain("latino");
//  H125->Add(Dir+"latino_1125_ggToH125toWWTo2LAndTau2Nu.root");
  H125->Add(Dir+"latino_2125_vbfToH125toWWTo2LAndTau2Nu.root");
  

  TChain * H125_wzh =  new TChain("H125_wzh");
  H125_wzh->Add(Dir+"latino_3125_wzttH125ToWW.root/latino");


//  H125->Add(Dir+"latino_3125_wzttH125ToWW.root/latino");

  TH1D* htot = new TH1D("htot","htot",nbins,vedges);
  TH1D* hpass = new TH1D("hpass","hpass",nbins,vedges);
  TH1D* hfake = new TH1D("hfake","hfake",nbins,vedges);

//  H125->Draw(var+">> hpass",selection+"*puW*baseW*effW*triggW"+LumiW);
  H125->Draw(var+">> hpass",selection+"*"+acceptance+"*puW*baseW*effW*triggW"+LumiW);
  H125->Draw(var+">> htot",acceptance+"*baseW"+LumiW);  
  H125->Draw(var+">> hfake", selection+"*(!"+acceptance+")*puW*baseW*effW*triggW"+LumiW);

//  H125_wzh->Draw(var+">>+ hpass",selection+"*"+acceptance_whzh+"*puW*baseW*effW*triggW"+LumiW);
//  H125_wzh->Draw(var+">>+ htot","("+acceptance_whzh+")*baseW"+LumiW);
//  H125_wzh->Draw(var+">>+ hfake", selection+"*(!"+acceptance_whzh+")*puW*baseW*effW*triggW"+LumiW);

  delete H125;

  cout << "Selected events = " << hpass->Integral() << " Tot events = " << htot->Integral() << endl;
  cout << "Fake events = " << hfake->Integral() << endl;

  double err_pass = 0.;
  double int_pass = hpass->IntegralAndError(1,nbins,err_pass);
  double err_tot = 0.;
  double int_tot = htot->IntegralAndError(1,nbins,err_tot);
  double err_fake = 0.;
  double int_fake = hfake->IntegralAndError(1,nbins,err_fake);


  cout << "Efficiency = " << int_pass/int_tot << " +/- " << (int_pass/int_tot)*(err_tot/int_tot + err_pass/int_pass)  << endl;
  cout << "Fake rate  = " << int_fake/int_pass << " +/- " << (int_fake/int_pass)*(err_fake/int_fake + err_pass/int_pass)  << endl;

  TFile * fout = new TFile("efficiencies.root", "recreate");
  fout->cd();
  TCanvas * c = new TCanvas();
  c->cd();
  TGraphAsymmErrors* g = new TGraphAsymmErrors(hpass,htot);
  g->SetNameTitle("Selection_efficiency","Selection efficiency");
  g->GetXaxis()->SetTitle("p_{T,gen}^{H} (GeV)");
  g->GetXaxis()->SetRangeUser(0,200);
  g->GetYaxis()->SetTitle("Efficiency");
  g->SetLineColor(kRed);
  g->SetLineWidth(3);
  g->Draw("AP");


  TCanvas * c1 = new TCanvas();
  c1->cd();
  TGraphAsymmErrors* g1 = new TGraphAsymmErrors(hfake,hpass);
  g1->SetNameTitle("Fake_rate","Fake rate");
  g1->GetXaxis()->SetTitle("p_{T,gen}^{H} (GeV)");
  g1->GetXaxis()->SetRangeUser(0,200);
  g1->GetYaxis()->SetTitle("Fake rate");
  g1->SetLineColor(kRed);
  g1->SetLineWidth(3);
  g1->Draw("AP");
  g->Write();
  g1->Write();


  fout->Write();  

}
