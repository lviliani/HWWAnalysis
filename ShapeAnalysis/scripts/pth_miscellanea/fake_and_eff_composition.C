
void fake_and_eff_composition(){

  bool doLoose = true;
  bool doVH = true;
  bool doTau = false;

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

  TString acceptance;
  TString acceptance_whzh;
  TString name_fake;
  TString name_pass;
  TString name_tot;
  TString AccCuts[6];
  AccCuts[0] = doLoose ? "(leptonGenpt1>20. && leptonGenpt2>10. && abs(leptonGeneta1)<2.5 && abs(leptonGeneta2)<2.5 )" : "(leptonGenpt1>20. && leptonGenpt2>10. && abs(leptonGeneta1)<2.5 && abs(leptonGeneta2)<2.5 )";
  AccCuts[1] = AccCuts[0]+" && ("+mll_gen+">12 )";
  AccCuts[2] = doLoose ? AccCuts[1]+" && ("+ptll_gen+">30 )" : AccCuts[1]+" && ("+ptll_gen+">30 )";
  AccCuts[3] = doLoose ? AccCuts[2]+" && ("+ptnn_gen+">0 )" : AccCuts[2]+" && ("+ptnn_gen+">20 )";
  AccCuts[4] = doLoose ? AccCuts[3]+" && ("+mth_gen+">50 )" : AccCuts[3]+" && ("+mth_gen+">60 )";
  AccCuts[5] = doTau ? AccCuts[4]+" && ("+of_gen_tau+" )" : AccCuts[4]+" && ("+of_gen+" )";

  TString Dir = "/data/lenzip/differential/tree_noskim_gen/nominals/";

  TH1D* hfake0 = new TH1D("hfake0","hfake0",nbins,vedges);
  TH1D* hfake1 = new TH1D("hfake1","hfake1",nbins,vedges);
  TH1D* hfake2 = new TH1D("hfake2","hfake2",nbins,vedges);
  TH1D* hfake3 = new TH1D("hfake3","hfake3",nbins,vedges);
  TH1D* hfake4 = new TH1D("hfake4","hfake4",nbins,vedges);
  TH1D* hfake5 = new TH1D("hfake5","hfake5",nbins,vedges);
  TH1D* hpass0 = new TH1D("hpass0","hpass0",nbins,vedges);
  TH1D* hpass1 = new TH1D("hpass1","hpass1",nbins,vedges);
  TH1D* hpass2 = new TH1D("hpass2","hpass2",nbins,vedges);
  TH1D* hpass3 = new TH1D("hpass3","hpass3",nbins,vedges);
  TH1D* hpass4 = new TH1D("hpass4","hpass4",nbins,vedges);
  TH1D* hpass5 = new TH1D("hpass5","hpass5",nbins,vedges);
  TH1D* htot0 = new TH1D("htot0","htot0",nbins,vedges);
  TH1D* htot1 = new TH1D("htot1","htot1",nbins,vedges);
  TH1D* htot2 = new TH1D("htot2","htot2",nbins,vedges);
  TH1D* htot3 = new TH1D("htot3","htot3",nbins,vedges);
  TH1D* htot4 = new TH1D("htot4","htot4",nbins,vedges);
  TH1D* htot5 = new TH1D("htot5","htot5",nbins,vedges);

  TH1D* hsel = new TH1D("hsel","hsel",nbins,vedges);

  // Signal  

  TChain * H125 =  new TChain("latino");
  H125->Add(Dir+"latino_1125_ggToH125toWWTo2LAndTau2Nu.root");
  H125->Add(Dir+"latino_2125_vbfToH125toWWTo2LAndTau2Nu.root");
  

  TChain * H125_wzh =  new TChain("H125_wzh");
  H125_wzh->Add(Dir+"latino_3125_wzttH125ToWW.root/latino");

  H125->Draw(var+">> hsel",selection+"*puW*baseW*effW*triggW"+LumiW);
  if (doVH)  H125_wzh->Draw(var+">>+ hsel",selection+"*puW*baseW*effW*triggW"+LumiW);

  delete H125;
  delete H125_wzh;

  for (int iCut=0; iCut<6; iCut++){

	  TChain * H125 =  new TChain("latino");
	  H125->Add(Dir+"latino_1125_ggToH125toWWTo2LAndTau2Nu.root");
	  H125->Add(Dir+"latino_2125_vbfToH125toWWTo2LAndTau2Nu.root");

	  TChain * H125_wzh =  new TChain("H125_wzh");
	  if (doVH)  H125_wzh->Add(Dir+"latino_3125_wzttH125ToWW.root/latino");

	  cout << "iCut = " << iCut << endl;
	  acceptance = "("+AccCuts[iCut]+")";
	  if (doVH) acceptance_whzh = "("+acceptance+"*( ((mctruth==24 || mctruth==26) && (mcHWWdecay==3) && (leptonGenpt3<0) && (neutrinoGenpt3<0))  ))";

          cout << acceptance << endl;

          name_fake.Form("hfake%d",iCut);
       	  H125->Draw(var+">>"+name_fake, selection+"*(!"+acceptance+")*puW*baseW*effW*triggW"+LumiW);
	  if (doVH)  H125_wzh->Draw(var+">>+"+name_fake, selection+"*(!"+acceptance_whzh+")*puW*baseW*effW*triggW"+LumiW);

          name_pass.Form("hpass%d",iCut);
          H125->Draw(var+">>"+name_pass, selection+"*"+acceptance+"*puW*baseW*effW*triggW"+LumiW);
          if (doVH)  H125_wzh->Draw(var+">>+"+name_pass, selection+"*"+acceptance_whzh+"*puW*baseW*effW*triggW"+LumiW);

          name_tot.Form("htot%d",iCut);
          H125->Draw(var+">>"+name_tot, acceptance+"*baseW"+LumiW);
          if (doVH)  H125_wzh->Draw(var+">>+"+name_tot, "("+acceptance_whzh+")*baseW"+LumiW);

	  delete H125;
	  delete H125_wzh;

	  if(iCut==5){
	  	  double err_pass = 0.;
		  double int_pass = hpass5->IntegralAndError(1,nbins,err_pass);
		  double err_tot = 0.;
		  double int_tot = htot5->IntegralAndError(1,nbins,err_tot);
		  double err_fake = 0.;
		  double int_fake = hfake5->IntegralAndError(1,nbins,err_fake);

		  cout << "############# Efficiency = " << int_pass/int_tot << " +/- " << (int_pass/int_tot)*(err_tot/int_tot + err_pass/int_pass)  << endl;
		  cout << "############# Fake rate  = " << int_fake/int_pass << " +/- " << (int_fake/int_pass)*(err_fake/int_fake + err_pass/int_pass)  << endl;
	  }

  }


  TFile * fout = new TFile("fakes.root", "recreate");
  fout->cd();
  hfake5->SetNameTitle("hfake","Fake histogram");
  hfake5->Write();
  fout->Close();

  TGraphAsymmErrors* g0 = new TGraphAsymmErrors(hfake0,hsel);
  TGraphAsymmErrors* g1 = new TGraphAsymmErrors(hfake1,hsel);
  TGraphAsymmErrors* g2 = new TGraphAsymmErrors(hfake2,hsel);
  TGraphAsymmErrors* g3 = new TGraphAsymmErrors(hfake3,hsel);
  TGraphAsymmErrors* g4 = new TGraphAsymmErrors(hfake4,hsel);
  TGraphAsymmErrors* g5 = new TGraphAsymmErrors(hfake5,hsel);

  TLegend* leg = new TLegend(0.15, 0.65, 0.45, 0.85);
  leg->AddEntry(g0, "Lepton cuts", "lp");
  leg->AddEntry(g1, "mll cut", "lp");
  leg->AddEntry(g2, "pTll cut", "lp");
  //leg->AddEntry(g3, "pTnn cut", "lp");
  leg->AddEntry(g4, "mTH cut", "lp");
  leg->AddEntry(g5, "of cut", "lp");
  leg->SetFillColor(kWhite);
  leg->SetBorderSize(0);

  TGraphAsymmErrors* gr0 = new TGraphAsymmErrors(hpass0,htot0);
  TGraphAsymmErrors* gr1 = new TGraphAsymmErrors(hpass1,htot1);
  TGraphAsymmErrors* gr2 = new TGraphAsymmErrors(hpass2,htot2);
  TGraphAsymmErrors* gr3 = new TGraphAsymmErrors(hpass3,htot3);
  TGraphAsymmErrors* gr4 = new TGraphAsymmErrors(hpass4,htot4);
  TGraphAsymmErrors* gr5 = new TGraphAsymmErrors(hpass5,htot5);

  TLegend* leg2 = new TLegend(0.15, 0.65, 0.45, 0.85);
  leg2->AddEntry(gr0, "Lepton cuts", "lp");
  leg2->AddEntry(gr1, "mll cut", "lp");
  leg2->AddEntry(gr2, "pTll cut", "lp");
  //leg2->AddEntry(gr3, "pTnn cut", "lp");
  leg2->AddEntry(gr4, "mTH cut", "lp");
  leg2->AddEntry(gr5, "of cut", "lp");
  leg2->SetFillColor(kWhite);
  leg2->SetBorderSize(0);


  TCanvas * c1 = new TCanvas();
  c1->cd();
  c1->SetTicky();

  g0->SetNameTitle("Fake_rate","Fakes Composition");
  g0->GetXaxis()->SetTitle("p_{T,gen}^{H} (GeV)");
  g0->GetXaxis()->SetRangeUser(0,200);
  g0->GetYaxis()->SetTitle("Fraction of fake events");
  g0->SetLineColor(kRed);
  g0->SetLineWidth(3);
//  g0->SetMarkerStyle(20);
  g0->GetYaxis()->SetRangeUser(0.,1);
  g0->Draw("AP");
//  g0->Write();
  cout << "here" << endl;

  g1->SetLineColor(kBlue);
  g1->SetLineWidth(3);
//  g1->SetMarkerStyle(21);
  g1->Draw("Psame");
//  g1->Write();
  cout << "here" << endl;


  g2->SetLineColor(kGreen);
  g2->SetLineWidth(3);
//  g2->SetMarkerStyle(22);
  g2->Draw("Psame");
//  g2->Write();
  cout << "here" << endl;

  g3->SetLineColor(kMagenta);
  g3->SetLineWidth(3);
//  g3->SetMarkerStyle(23);
//  g3->Draw("Psame");
//  g3->Write();
  cout << "here" << endl;

  g4->SetLineColor(kAzure+1);
  g4->SetLineWidth(3);
//  g4->SetMarkerStyle(33);
  g4->Draw("Psame");
//  g4->Write();
  cout << "here" << endl;

  g5->SetLineColor(kOrange);
  g5->SetLineWidth(3);
//  g5->SetMarkerStyle(34);
  g5->Draw("Psame");
//  g5->Write();
  cout << "here" << endl;

  leg->Draw();

  TCanvas* c2 = new TCanvas();
  c2->cd();
  c2->SetTicky();

  gr0->SetNameTitle("eff_sel","Efficiency Composition");
  gr0->GetXaxis()->SetTitle("p_{T,gen}^{H} (GeV)");
  gr0->GetXaxis()->SetRangeUser(0,200);
  gr0->GetYaxis()->SetTitle("Efficiency");
  gr0->SetLineColor(kRed);
  gr0->SetLineWidth(3);
//  g0->SetMarkerStyle(20);
  gr0->GetYaxis()->SetRangeUser(0.,1);
  gr0->Draw("AP");
//  g0->Write();

  gr1->SetLineColor(kBlue);
  gr1->SetLineWidth(3);
//  g1->SetMarkerStyle(21);
  gr1->Draw("Psame");
//  g1->Write();


  gr2->SetLineColor(kGreen);
  gr2->SetLineWidth(3);
//  g2->SetMarkerStyle(22);
  gr2->Draw("Psame");
//  g2->Write();

  gr3->SetLineColor(kMagenta);
  gr3->SetLineWidth(3);
//  g3->SetMarkerStyle(23);
//  gr3->Draw("Psame");
//  g3->Write();

  gr4->SetLineColor(kAzure+1);
  gr4->SetLineWidth(3);
//  g4->SetMarkerStyle(33);
  gr4->Draw("Psame");
//  g4->Write();

  gr5->SetLineColor(kOrange);
  gr5->SetLineWidth(3);
//  g5->SetMarkerStyle(34);
  gr5->Draw("Psame");
//  g5->Write();

  leg2->Draw();



//  fout->Write();  

}
