
// X. Janssen: Function to weight Higgs line shape to the new CPS
// You have to load the correct TSpline3 before using it !!!

#include <TROOT.h>
#include <TSpline.h>
#include <TFile.h>
#include <string>
#include <sstream>
#include <iostream>
#include <iomanip>

TSpline3* wCPS_ggH    = 0 ;
TSpline3* wCPS_qqH    = 0 ;
TSpline3* wCPS_ggH_SM = 0 ;
TSpline3* wCPS_qqH_SM = 0 ;
TSpline3* pCPS = 0 ;

// iType = 0 : ggH
//         1 : qqH
//         2 : ggH_SM (i.e. 125 GeV)
//         3 : qqH_SM (i.e. 125 GeV)

float getCPSWght(int iType, float mass ) 
{
   float wCPS = 1.;
   if      ( iType == 0 ) pCPS = wCPS_ggH    ;
   else if ( iType == 1 ) pCPS = wCPS_qqH    ;
   else if ( iType == 2 ) pCPS = wCPS_ggH_SM ;
   else if ( iType == 3 ) pCPS = wCPS_qqH_SM ;
 
   if (pCPS) 
   {
       wCPS = pCPS->Eval(mass); 
   } else {
       std::cout << "wCPS not found: " << iType << std::endl;
   }
   //std::cout << mass << " " << wCPS << std::endl ;
   return wCPS;
}

void initCPSWght(std::string wFile , std::string Energy , int mH , int mH_SM )
{
   //std::cout << wFile  << std::endl;
   //std::cout << Energy << std::endl;
   //std::cout << mH     << std::endl;
   //std::cout << mH_SM  << std::endl;

   TFile* f = new TFile(wFile.c_str() , "READ"); 
   gROOT->cd();
   std::string wName ;
   std::stringstream smH   ;
   std::stringstream smH_SM;
   smH    << mH ;
   smH_SM << mH_SM ;

   if (mH > 0) {
     wName = "wght_mH"+smH.str()+"_cpsNew_"+Energy+"_ggH";  
     wCPS_ggH = (TSpline3*) f->Get(wName.c_str())->Clone("wCPS_ggH");
     wName = "wght_mH"+smH.str()+"_cpsNew_"+Energy+"_qqH"; 
     wCPS_qqH = (TSpline3*) f->Get(wName.c_str())->Clone("wCPS_qqH");
   } 
   
   if (mH_SM >= 250) {
     wName = "wght_mH"+smH_SM.str()+"_cpsNew_"+Energy+"_ggH";  
     wCPS_ggH_SM = (TSpline3*) f->Get(wName.c_str())->Clone("wCPS_ggH_SM");
     wName = "wght_mH"+smH_SM.str()+"_cpsNew_"+Energy+"_qqH";  
     wCPS_qqH_SM = (TSpline3*) f->Get(wName.c_str())->Clone("wCPS_qqH_SM");
   } 

  f->Close();
  return; 
}
