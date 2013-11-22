

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

TH1F*     hInt_ggH = 0 ;
TSpline3* wInt_ggH = 0 ;

// iType = 0 : ggH
//         1 : qqH

float getIntWght(int iType, float mass , float cpsq)
{
   float wInt=1.;
   if ( iType == 0 ) {  
     if ( wInt_ggH ) {
       if      (mass > 210 and mass < 1000.) wInt_ggH->Eval(mass) ;
       else if (mass <= 210 ) wInt_ggH->Eval(210) ;
       else if (mass >= 1000) wInt_ggH->Eval(1000);
       if ( cpsq < 1. ) wInt = 1.+(wInt-1.)/cpsq;
     } else {
       std::cout << "Missing Interference !!!!" << std::endl;
     }
   }
   return wInt;
}


// iSyst =  0 : Cent
//         +1 :
//         -1 : 
void initIntWght(std::string wFile , int iType , int iSyst ) {

   TFile* f = new TFile(wFile.c_str() , "READ");
   gROOT->cd();
   if ( iType == 0 ) { 
     if ( iSyst == 0 ) hInt_ggH = (TH1F*) f->Get("h_MWW_rel_NNLO_cen")->Clone("hInt_ggH");
     //hInt_ggH.Smooth(10);
     wInt_ggH = new TSpline3(hInt_ggH) ;
   } 
   f->Close();
}
