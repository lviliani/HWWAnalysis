
void eff_sel(){

  gStyle->SetOptStat("emrio") ;
  TH1::SetDefaultSumw2();
//  TString var = "njet";
//  double vedges[] = {0,1,2,3,4,5};
//  double nbins = 5;

   TString var = "TMath::Min(PtHiggs,167.)";
  double vedges[] = {0,15,45,87,125,162,200};
  double nbins = 6;

  TString LumiW = "*19.468" ;

  TString leptons_cut = "(!sameflav && trigger==1 && nextra==0 && pt1>20 && pt2>10  && ch1*ch2<0)";
  TString mll_cut = "*(mll>12)";
  TString ptll_cut = "*(ptll>30)";  
  TString met_cut = "*(mpmet>20. && pfmet>20.)";
  TString mth_cut = "*(mth>60)";
  TString btag_cut = "*((njet==0)*(bveto_mu==1 && bveto_ip==1) || (njet>0)*(( jetbjpb1<1.4 || jetpt1<30) && ( jetbjpb2<1.4 || jetpt2<30) && ( jetbjpb3<1.4 || jetpt3<30) && ( jetbjpb4<1.4 || jetpt4<30)))"; 

  TString selection = "("+leptons_cut+mll_cut+met_cut+mth_cut+btag_cut+")";

  TString Dir = "/afs/cern.ch/work/l/lviliani/DatacardFramework/CMSSW_7_1_5/src/Unfolding/samples/nominals/";

  // Signal  

  TChain * H125 =  new TChain("H125");
  H125->Add(Dir+"latino_1125_ggToH125toWWTo2LAndTau2Nu.root/latino");
  TH1F* htot = new TH1F("htot","htot",nbins,vedges);
  TH1F* hpass = new TH1F("hpass","hpass",nbins,vedges);

  H125->Draw(var+">> hpass",selection+"*puW*baseW*effW*triggW"+LumiW);
  H125->Draw(var+">> htot","("+acceptance+" && "+selection+")*(1 - puW*effW*triggW)*baseW"+LumiW+" + ("+acceptance+" && !"+selection+")*baseW"+LumiW);

  delete H125;

  cout << "Selected events = " << hpass->Integral() << " Tot events = " << htot->Integral() << endl;

  double err_pass = 0.;
  double int_pass = hpass->IntegralAndError(1,6,err_pass);
  double err_tot = 0.;
  double int_tot = htot->IntegralAndError(1,6,err_tot);

  cout << "Efficiency = " << int_pass/int_tot << " +/- " << (int_pass/int_tot)*(err_tot/int_tot + err_pass/int_pass)  << endl;
  
  TGraphAsymmErrors* g = new TGraphAsymmErrors(hpass,htot);
  g->SetNameTitle("Selection efficiency","Selection efficiency");
  g->GetXaxis()->SetTitle("p_{T,gen}^{H} (GeV)");
  g->GetXaxis()->SetRangeUser(0,200);
  g->GetYaxis()->SetTitle("Efficiency");
  g->SetLineColor(kRed);
  g->SetLineWidth(3);
  g->Draw("AP");

}
