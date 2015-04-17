#include "TCanvas.h"
#include "cmath"
#include "TGraph.h"
#include <iostream>
#include "TString.h"
#include "TStyle.h"
#include "TH1F.h"
#include "TLegend.h"
#include "TChain.h"
#include "TFile.h"
#include "TMatrix.h"
double err_Syst_tot() 
{
Double_t xbins[12]={7.5,30,66,106,143.5,181};
Double_t err_x[6]={7.5,15,21,19,18.5,19};
//TFile *f3 = new TFile("/afs/cern.ch/user/l/lredapi/work/hlarghezza/differenziale/RooUnfold/Syst_ggH.root");
TFile *f3 = new TFile("syst_ggH.root");
TString syst[20]={"CMS_8TeV_hww_FakeRate","CMS_8TeV_norm_DYTT","CMS_8TeV_norm_Vg","QCDscale_VV","QCDscale_VVV","QCDscale_VgS","QCDscale_WW","QCDscale_WW1in","QCDscale_ggWW","lumi_8TeV","pdf_gg","pdf_qqbar","CMS_8TeV_btagsf","CMS_8TeV_eff_l","CMS_8TeV_met","CMS_8TeV_p_res_e","CMS_8TeV_p_scale_e","CMS_8TeV_p_scale_j","CMS_8TeV_p_scale_m","CMS_8TeV_p_scale_met"};
//TFile *f4 = new TFile("/afs/cern.ch/user/l/lredapi/work/hlarghezza/differenziale/RooUnfold/Syst_otherH.root");
TFile *f4 = new TFile("syst_vbf.root");

Double_t string_err_up_syst_gg[7];
Double_t string_err_down_syst_gg[7];
Double_t string_err_stat_gg[7];
Double_t val_cent_gg[7];
Double_t val_true_gg[7];
Double_t string_err_up_syst_vbf[7];
Double_t string_err_down_syst_vbf[7];
Double_t string_err_stat_vbf[7];
Double_t val_cent_vbf[7];
Double_t val_true_vbf[7];
Double_t string_err_up_syst[7];
Double_t string_err_down_syst[7];
Double_t string_err_stat[7];
Double_t val_cent[7];
Double_t val_true[7];
	for(int i=1; i<=6; i++){
	
	double err_up_syst_gg=0;
	double err_down_syst_gg=0;
	double err_up_syst_vbf=0;
	double err_down_syst_vbf=0;
		for(int j=0; j<20; j++){
//		TString nome_up_gg="ggH"+syst[j]+"Up"; 
                TString nome_up_gg=syst[j]+"Up";            		
        	TH1 *h1_gg = (TH1*)f3->Get("central");
		TH1 *h2_gg = (TH1*)f3->Get(nome_up_gg);
//		TH1 *h6_gg = (TH1*)f3->Get("hTrue");
//                cout<<h1_gg<<h2_gg<<h6_gg<<endl ;
		double val_cent_bis_gg = h1_gg->GetBinContent(i);
		double val_up_gg = h2_gg->GetBinContent(i);
		double err_up_gg = (val_up_gg-val_cent_bis_gg);
		cout<<"err_up_gg= "<<err_up_gg<<endl;
		err_up_syst_gg= err_up_syst_gg+(err_up_gg*err_up_gg);

//		TString nome_down_gg="ggH"+syst[j]+"Down"; 
                TString nome_down_gg=syst[j]+"Down";             		
		TH1 *h3_gg = (TH1*)f3->Get(nome_down_gg);
		double val_down_gg = h3_gg->GetBinContent(i);
		double err_down_gg = (val_down_gg-val_cent_bis_gg);
		cout<<"err_down_gg= "<<err_down_gg<<endl;
		err_down_syst_gg= err_down_syst_gg+(err_down_gg*err_down_gg);


//		TString nome_up_vbf="otherH"+syst[j]+"Up"; 
                TString nome_up_vbf=syst[j]+"Up";              		
        	TH1 *h1_vbf = (TH1*)f4->Get("central");
		TH1 *h2_vbf  = (TH1*)f4->Get(nome_up_vbf );
//		TH1 *h6_vbf  = (TH1*)f4->Get("hTrue");
		double val_cent_bis_vbf  = h1_vbf ->GetBinContent(i);
		double val_up_vbf  = h2_vbf ->GetBinContent(i);
		double err_up_vbf  = (val_up_vbf -val_cent_bis_vbf );
		cout<<"err_up_vbf= "<<err_up_vbf<<endl;
		err_up_syst_vbf = err_up_syst_vbf +(err_up_vbf *err_up_vbf );

//		TString nome_down_vbf ="otherH"+syst[j]+"Down"; 
                TString nome_down_vbf =syst[j]+"Down";               		
		TH1 *h3_vbf  = (TH1*)f4->Get(nome_down_vbf );
		double val_down_vbf  = h3_vbf ->GetBinContent(i);
		double err_down_vbf  = (val_down_vbf -val_cent_bis_vbf );
		cout<<"err_down_vbf= "<<err_down_vbf<<endl;
		err_down_syst_vbf = err_down_syst_vbf +(err_down_vbf *err_down_vbf );
					}
	val_cent[i-1]= ((h1_gg->GetBinContent(i))+(h1_vbf->GetBinContent(i)))/(err_x[i-1]*2*19.468);
	cout<<"val_cent="<< val_cent[i-1]<<endl;
//	val_true[i-1]= ((h6_gg->GetBinContent(i))+(h6_vbf->GetBinContent(i)))/(err_x[i-1]*2*19.468));
	//cout<<"val_true="<< val_true[i-1]<<endl;
        string_err_up_syst[i-1]=((sqrt(err_up_syst_gg))+(sqrt(err_up_syst_vbf)))/(err_x[i-1]*2*19.468);
	cout<<"err_up_syst="<< string_err_up_syst[i-1]<<endl;
	string_err_down_syst[i-1]=((sqrt(err_down_syst_gg))+(sqrt(err_down_syst_vbf)))/(err_x[i-1]*2*19.468);
	cout<<"err_down_syst="<< string_err_down_syst[i-1]<<endl;
	string_err_stat[i-1] = ((h1_gg->GetBinError(i))+(h1_vbf->GetBinError(i)))/(err_x[i-1]*2*19.468);
	cout<<"err_stat="<< string_err_stat[i-1]<<endl;
					
				 }
//h1->Draw();

TGraphAsymmErrors *g1 = new TGraphAsymmErrors(6,xbins,val_cent,err_x,err_x,string_err_down_syst,string_err_up_syst);
TGraphAsymmErrors *g2 = new TGraphAsymmErrors(6,xbins,val_cent,err_x,err_x,string_err_stat,string_err_stat);
TGraphErrors *g3 = new TGraphErrors(6,xbins,val_true,err_x,0);
g2->SetLineColor(2);
g2->SetLineWidth(3);
g2->SetFillColor(2);
g2->SetFillStyle(3001);
g2->SetTitle("Differential_cross_section");
g2->GetYaxis()->SetTitle("frac{d#sigma}{dp_{t}^{H}} [#frac{fb}{GeV}]");
g2->GetXaxis()->SetTitle("p_{t}^{H} [GeV]");
g2->Draw("AP2");
g1->SetLineColor(4);
g1->SetFillColor(4);
g1->SetFillStyle(3001);
g1->SetLineWidth(3);
g1->Draw("P2");
g2->Draw("P");
g1->Draw("P");
g3->SetLineColor(3);
g3->SetLineWidth(3);
g3->Draw("P");

TLegend *legend=new TLegend(0.7,0.65,0.4,0.3);
	legend->SetTextFont(72);
	legend->SetTextSize(0.04);
	legend->AddEntry(g2,"Stat error","F");
	legend->AddEntry(g1,"Syst error","F");
legend->AddEntry(g3,"True","L");
	legend->Draw();


}
