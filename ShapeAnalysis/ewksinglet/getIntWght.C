

// X. Janssen: Function to weight Higgs line shape to the new CPS
// You have to load the correct TSpline3 before using it !!!

#include <TROOT.h>
#include <TH1F.h>
#include <TSpline.h>
#include <TFile.h>
#include <string>
#include <sstream>
#include <iostream>
#include <iomanip>

#include "qqHInterference.h

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
       if      (mass > 210 and mass < 1000.) wInt_ggH->Eval(mass) ;
       else if (mass <= 210 ) wInt_ggH->Eval(210) ;
       else if (mass >= 1000) wInt_ggH->Eval(1000);
       if ( cpsq < 1. ) wInt = 1.+(wInt-1.)/cpsq;
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

   TFile* f = new TFile(wFile.c_str() , "READ");
   gROOT->cd();
   if ( iType == 0 ) { //---- ggH 
     if ( iSyst == 0 ) hInt_ggH = (TH1F*) f->Get("h_MWW_rel_NNLO_cen")->Clone("hInt_ggH");
     //hInt_ggH.Smooth(10);
     wInt_ggH = new TSpline3(hInt_ggH) ;
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
     if (kind == 0) nameS = Form ("data/InterferenceVBF/results_em_S.txt");
     if (kind == 1) nameS = Form ("data/InterferenceVBF/results_mm_S.txt");
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
     if (kind == 0) nameSI = Form ("data/InterferenceVBF/results_em_SI.txt");
     if (kind == 1) nameSI = Form ("data/InterferenceVBF/results_mm_SI.txt");
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
   f->Close();
}
