

// X. Janssen: Function to weight Higgs line shape to the new CPS
// You have to load the correct TSpline3 before using it !!!

#include <TROOT.h>
#include <TCanvas.h>
#include <TH1F.h>
#include <TF1.h>
#include <TSpline.h>
#include <TFile.h>
#include <string>
#include <sstream>
#include <fstream>
#include <iostream>
#include <iomanip>

//#include "qqHInterference.h"


//-------------------
//---- functions ----
//-------------------

double crystalBallLowHigh (double* x, double* par) {
  //[0] = N
  //[1] = mean
  //[2] = sigma
  //[3] = alpha on the right-hand side
  //[4] = n
  //[5] = alpha2 on the left-hand side
  //[6] = n2

 double xx = x[0];
 double mean = par[1];
 double sigma = fabs (par[2]);
 double alpha = par[3];
 double n = par[4];
 double alpha2 = par[5];
 double n2 = par[6];

 if( (xx-mean)/sigma > fabs(alpha) ) {
  double A = pow(n/fabs(alpha), n) * exp(-0.5 * alpha*alpha);
  double B = n/fabs(alpha) - fabs(alpha);

  return par[0] * A * pow(B + (xx-mean)/sigma, -1.*n);
 }

 else if( (xx-mean)/sigma < -1.*fabs(alpha2) ) {
  double A = pow(n2/fabs(alpha2), n2) * exp(-0.5 * alpha2*alpha2);
  double B = n2/fabs(alpha2) - fabs(alpha2);

  return par[0] * A * pow(B - (xx-mean)/sigma, -1.*n2);
 }

 else {
  return par[0] * exp(-1. * (xx-mean)*(xx-mean) / (2*sigma*sigma) );
 }

}


//---- division of CBLowHigh with CBLowHigh ----

Double_t CrystalBallLowHighDivideCrystalBallLowHigh(Double_t *x,Double_t *par) {
 Double_t num = 0;
 num = crystalBallLowHigh(x,par);

 Double_t den = 1;
 den = crystalBallLowHigh(x,&par[7]);

 if (den != 0) return num/den;
 else return 1.;

}

TH1F*     hInt_ggH = 0 ;
TSpline3* wInt_ggH = 0 ;

TGraph* em_variables_S[7];
TGraph* em_variables_SI[7];
TGraph* mm_variables_S[7];
TGraph* mm_variables_SI[7];
TF1* em_crystal_Icorr_qqH;
TF1* mm_crystal_Icorr_qqH;

// iType = 0 : ggH
//         1 : qqH

//---- for qqH only
// kind = 0 : em
//        1 : mm/ee

float getIntWght(int iType, float mass , float cpsq, float kind = 0)
{
   float wInt=1.;
   if ( iType == 0 ) { //---- ggH
     if ( wInt_ggH ) {
       wInt = wInt_ggH->Eval(mass) ;
       if ( cpsq < 1. ) wInt = wInt/cpsq;
       wInt += 1;
       if (wInt < 0) wInt = 0;
     } else {
       std::cout << "Missing Interference !!!!" << std::endl;
     }
   }
   else if ( iType == 1 ) { //---- qqH
    wInt = 1.;
    if (kind == 0) wInt = em_crystal_Icorr_qqH->Eval(mass);
    if (kind == 1) wInt = mm_crystal_Icorr_qqH->Eval(mass);

    if ( cpsq < 1. ) wInt = 1.+(wInt-1.)/cpsq; //---- needed also here?
   }
   return wInt;
}


// iSyst =  0 : Cent
//         +1 :
//         -1 : 
void initIntWght(std::string wFile , int iType , int iSyst, float Hmass = 350) {

   if ( iType == 0 ) { //---- ggH 
     TFile* f = new TFile(wFile.c_str() , "READ");
     gROOT->cd();
     if (hInt_ggH) hInt_ggH->Delete();
     hInt_ggH = new TH1F("h_MWW_rel_NNLO_cen","h_MWW_rel_NNLO_cen",2000,0.,4000.);
     TH1F* hCen = (TH1F*) f->Get("h_MWW_rel_NNLO_cen");
     TH1F* hUp  = (TH1F*) f->Get("h_MWW_rel_NNLO_mul");
     TH1F* hDo  = (TH1F*) f->Get("h_MWW_rel_NNLO_add");
     // low/high Mass -> no value
     float firstM    = 9999.;
     float lastM     = -1.  ;
     float firstVal  = -1;
     float lastVal   = -1;
     bool  foundFirst=false;
     bool  foundLast =false;
     for ( int iBin = 1 ; iBin <= hCen->GetNbinsX() ; ++iBin ) {
       float m  = hCen->GetBinCenter(iBin);
       float v  = hCen->GetBinContent(iBin);
       if (v != 0 && ! foundFirst && m < Hmass ) {
         firstVal   = v ;
         firstM     = m ;
         foundFirst = true;
       }
       if ( m > Hmass && v==0) foundLast = true;
       if (!foundLast) {
         lastVal   = v ;
         lastM     = m ;
       }
     }
     // Create Histograms 
     for ( int iBin = 1 ; iBin <= hInt_ggH->GetNbinsX() ; ++iBin ) {
       float m = hInt_ggH->GetBinCenter(iBin);
       if ( m >= hCen->GetXaxis()->GetXmin() && m <= hCen->GetXaxis()->GetXmax() ) {
         int jBin = hCen->FindBin(m);
         if (iSyst ==  0) hInt_ggH->SetBinContent(iBin,hCen->GetBinContent(jBin));
         if (iSyst ==  1) hInt_ggH->SetBinContent(iBin,hUp->GetBinContent(jBin));
         if (iSyst == -1) hInt_ggH->SetBinContent(iBin,hDo->GetBinContent(jBin));
       } 
       if ( m < firstM || m < hCen->GetXaxis()->GetXmin() ) {
         if (iSyst ==  0) hInt_ggH->SetBinContent(iBin,firstVal);
         if (iSyst ==  1) hInt_ggH->SetBinContent(iBin,firstVal*2);
         if (iSyst == -1) hInt_ggH->SetBinContent(iBin,0.        );
       }
       if ( m > lastM  || m > hCen->GetXaxis()->GetXmax() ) {
         if (iSyst ==  0) hInt_ggH->SetBinContent(iBin,lastVal);
         if (iSyst ==  1) hInt_ggH->SetBinContent(iBin,0.     );
         if (iSyst == -1) hInt_ggH->SetBinContent(iBin,lastVal*2);
       }

     } 
     //hInt_ggH->Draw();
     //hUp->Draw("same");
     wInt_ggH = new TSpline3(hInt_ggH) ;
     wInt_ggH->SetLineColor(kRed); 
     wInt_ggH->Draw("same");
     //gPad->WaitPrimitive();
     f->Close();
   }
   else if ( iType ==1 ) { //---- qqH

    for (int kind = 0; kind < 2; kind ++) { 
    //---- 0 = em,   1 = mm/ee

     std::string buffer;
     float num;
     int counter;

     float S_mass[100];
     float S_N[100];
     float S_Mean[100];
     float S_sigma[100];
     float S_alphaR[100];
     float S_nR[100];
     float S_alphaL[100];
     float S_nL[100];

     float SI_mass[100];
     float SI_N[100];
     float SI_Mean[100];
     float SI_sigma[100];
     float SI_alphaR[100];
     float SI_nR[100];
     float SI_alphaL[100];
     float SI_nL[100];

     TString nameS;
     if (kind == 0) nameS = wFile+"/data/InterferenceVBF/results_em_S.txt";
     if (kind == 1) nameS = wFile+"/data/InterferenceVBF/results_mm_S.txt";
     std::ifstream file_S (nameS.Data());
     counter = 0;
     while(!file_S.eof()) {
      getline(file_S,buffer);
      std::cout << "buffer = " << buffer << std::endl;
      if (buffer != "" && buffer.at(0) != '#'){ ///---> save from empty line at the end! And comments!
       std::stringstream line( buffer );
       line >> S_mass[counter];
       line >> S_N[counter];
       line >> S_Mean[counter];
       line >> S_sigma[counter];
       line >> S_alphaR[counter];
       line >> S_nR[counter];
       line >> S_alphaL[counter];
       line >> S_nL[counter];
       counter++;
       std::cout << std::endl;
      }
     }

     TString nameSI;
     if (kind == 0) nameSI = wFile+"/data/InterferenceVBF/results_em_SI.txt";
     if (kind == 1) nameSI = wFile+"/data/InterferenceVBF/results_mm_SI.txt";
     std::ifstream file_SI (nameSI.Data());
     counter = 0;
     while(!file_SI.eof()) {
      getline(file_SI,buffer);
      std::cout << "buffer = " << buffer << std::endl;
      if (buffer != "" && buffer.at(0) != '#'){ ///---> save from empty line at the end! And comments!
       std::stringstream line( buffer );
       line >> SI_mass[counter];
       line >> SI_N[counter];
       line >> SI_Mean[counter];
       line >> SI_sigma[counter];
       line >> SI_alphaR[counter];
       line >> SI_nR[counter];
       line >> SI_alphaL[counter];
       line >> SI_nL[counter];
       counter++;
       std::cout << std::endl;
      }
     }

    //---- build functions to interpolate ----
     float log_S_N[100];
     float log_SI_N[100];

     for (int i=0; i<5; i++) {
      double tempMass = 0;
      if (i==0) tempMass = 350;
      if (i==1) tempMass = 500;
      if (i==2) tempMass = 650;
      if (i==3) tempMass = 800;
      if (i==4) tempMass = 1000;

      int NBIN = 350;
      if (tempMass>400) NBIN = 120;
      if (tempMass>500) NBIN =  70;
      if (tempMass>700) NBIN = 120;
      if (tempMass>900) NBIN =  40;
      int MAX = 800;
      if (tempMass>400) MAX =  1500;
      if (tempMass>500) MAX =  2000;
      if (tempMass>700) MAX =  4000;
      if (tempMass>900) MAX =  4000;
      float scale = 1./ (MAX/NBIN);
      log_S_N[i]  = log(S_N[i]  * scale);
      log_SI_N[i] = log(SI_N[i] * scale);
     }

     if (kind == 0) {
      for (int iVar=0; iVar<7; iVar++) {
       if (iVar == 0) em_variables_S[iVar] = new TGraph (5,S_mass,log_S_N);
       if (iVar == 1) em_variables_S[iVar] = new TGraph (5,S_mass,S_Mean);
       if (iVar == 2) em_variables_S[iVar] = new TGraph (5,S_mass,S_sigma);
       if (iVar == 3) em_variables_S[iVar] = new TGraph (5,S_mass,S_alphaR);
       if (iVar == 4) em_variables_S[iVar] = new TGraph (5,S_mass,S_nR);
       if (iVar == 5) em_variables_S[iVar] = new TGraph (5,S_mass,S_alphaL);
       if (iVar == 6) em_variables_S[iVar] = new TGraph (5,S_mass,S_nL);
      }

      for (int iVar=0; iVar<7; iVar++) {
       if (iVar == 0) em_variables_SI[iVar] = new TGraph (5,SI_mass,log_SI_N);
       if (iVar == 1) em_variables_SI[iVar] = new TGraph (5,SI_mass,SI_Mean);
       if (iVar == 2) em_variables_SI[iVar] = new TGraph (5,SI_mass,SI_sigma);
       if (iVar == 3) em_variables_SI[iVar] = new TGraph (5,SI_mass,SI_alphaR);
       if (iVar == 4) em_variables_SI[iVar] = new TGraph (5,SI_mass,SI_nR);
       if (iVar == 5) em_variables_SI[iVar] = new TGraph (5,SI_mass,SI_alphaL);
       if (iVar == 6) em_variables_SI[iVar] = new TGraph (5,SI_mass,SI_nL);
      }

      em_crystal_Icorr_qqH = new TF1("em_crystal_Icorr_qqH",CrystalBallLowHighDivideCrystalBallLowHigh,0,3000,14);

      for (int iVar = 0; iVar<7; iVar++) {
       if (iVar == 0) {
        em_crystal_Icorr_qqH->SetParameter(iVar,   exp(em_variables_SI[iVar]->Eval(Hmass)));
        em_crystal_Icorr_qqH->SetParameter(iVar+7, exp(em_variables_S[iVar]->Eval(Hmass)));
       }
       else {
        em_crystal_Icorr_qqH->SetParameter(iVar,   em_variables_SI[iVar]->Eval(Hmass));
        em_crystal_Icorr_qqH->SetParameter(iVar+7, em_variables_S[iVar]->Eval(Hmass));
       }
      }
     }
     else if (kind == 1) {
      for (int iVar=0; iVar<7; iVar++) {
       if (iVar == 0) mm_variables_S[iVar] = new TGraph (5,S_mass,log_S_N);
       if (iVar == 1) mm_variables_S[iVar] = new TGraph (5,S_mass,S_Mean);
       if (iVar == 2) mm_variables_S[iVar] = new TGraph (5,S_mass,S_sigma);
       if (iVar == 3) mm_variables_S[iVar] = new TGraph (5,S_mass,S_alphaR);
       if (iVar == 4) mm_variables_S[iVar] = new TGraph (5,S_mass,S_nR);
       if (iVar == 5) mm_variables_S[iVar] = new TGraph (5,S_mass,S_alphaL);
       if (iVar == 6) mm_variables_S[iVar] = new TGraph (5,S_mass,S_nL);
      }

      for (int iVar=0; iVar<7; iVar++) {
       if (iVar == 0) mm_variables_SI[iVar] = new TGraph (5,SI_mass,log_SI_N);
       if (iVar == 1) mm_variables_SI[iVar] = new TGraph (5,SI_mass,SI_Mean);
       if (iVar == 2) mm_variables_SI[iVar] = new TGraph (5,SI_mass,SI_sigma);
       if (iVar == 3) mm_variables_SI[iVar] = new TGraph (5,SI_mass,SI_alphaR);
       if (iVar == 4) mm_variables_SI[iVar] = new TGraph (5,SI_mass,SI_nR);
       if (iVar == 5) mm_variables_SI[iVar] = new TGraph (5,SI_mass,SI_alphaL);
       if (iVar == 6) mm_variables_SI[iVar] = new TGraph (5,SI_mass,SI_nL);
      }

      mm_crystal_Icorr_qqH = new TF1("mm_crystal_Icorr_qqH",CrystalBallLowHighDivideCrystalBallLowHigh,0,3000,14);

      for (int iVar = 0; iVar<7; iVar++) {
       if (iVar == 0) {
        mm_crystal_Icorr_qqH->SetParameter(iVar,   exp(mm_variables_SI[iVar]->Eval(Hmass)));
        mm_crystal_Icorr_qqH->SetParameter(iVar+7, exp(mm_variables_S[iVar]->Eval(Hmass)));
       }
       else {
        mm_crystal_Icorr_qqH->SetParameter(iVar,   mm_variables_SI[iVar]->Eval(Hmass));
        mm_crystal_Icorr_qqH->SetParameter(iVar+7, mm_variables_S[iVar]->Eval(Hmass));
       }
      }
     }
    }

   }
}
