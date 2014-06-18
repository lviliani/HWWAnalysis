

// X. Janssen: Function to weight Higgs line shape to the new CPS
// You have to load the correct TSpline3 before using it !!!

#include <TROOT.h>
#include <TCanvas.h>
#include <TH1F.h>
#include <TF1.h>
#include <TGraph2D.h>
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







//---- division of CBLowHigh+ExponentialFall with CBLowHigh ----
double doubleGausCrystalBallLowHighPlusExp (double* x, double* par) {
  //[0] = N
  //[1] = mean
  //[2] = sigma
  //[3] = alpha
  //[4] = n
  //[5] = alpha2
  //[6] = n2

  //[7] = R = ratio between exponential and CB
  //[8] = tau = tau falling of exponential

 double xx = x[0];

// double mean = par[1] ; // mean
// double sigmaP = par[2] ; // sigma of the positive side of the gaussian
// double sigmaN = par[3] ; // sigma of the negative side of the gaussian
// double alpha = par[4] ; // junction point on the positive side of the gaussian
// double n = par[5] ; // power of the power law on the positive side of the gaussian
// double alpha2 = par[6] ; // junction point on the negative side of the gaussian
// double n2 = par[7] ; // power of the power law on the negative side of the gaussian

 double mean = par[1] ; // mean
 double sigmaP = par[2] ; // sigma of the positive side of the gaussian | they are the same!!!
 double sigmaN = par[2] ; // sigma of the negative side of the gaussian |
 double alpha = par[3] ; // junction point on the positive side of the gaussian
 double n = par[4] ; // power of the power law on the positive side of the gaussian
 double alpha2 = par[5] ; // junction point on the negative side of the gaussian
 double n2 = par[6] ; // power of the power law on the negative side of the gaussian

 double R = par[7] ;
 double tau = par[8] ;

 
 if ((xx-mean)/sigmaP > fabs(alpha)) {
  double A = pow(n/fabs(alpha), n) * exp(-0.5 * alpha*alpha);
  double B = n/fabs(alpha) - fabs(alpha);

  return par[0] * ( (1-R)*(A * pow(B + (xx-mean)/sigmaP, -1.*n)) + R * exp(-xx/tau));
 }

 else if ((xx-mean)/sigmaN < -1.*fabs(alpha2)) {
  double A = pow(n2/fabs(alpha2), n2) * exp(-0.5 * alpha2*alpha2);
  double B = n2/fabs(alpha2) - fabs(alpha2);

  return par[0] * ( (1-R)*(A * pow(B - (xx-mean)/sigmaN, -1.*n2)) + R * exp(-xx/tau));
 }

 else if ((xx-mean) > 0) {
  return par[0] * ( (1-R)*exp(-1. * (xx-mean)*(xx-mean) / (2*sigmaP*sigmaP) ) + R * exp(-xx/tau));
 }

 else {
  return par[0] * ( (1-R)*exp(-1. * (xx-mean)*(xx-mean) / (2*sigmaN*sigmaN) ) + R * exp(-xx/tau));
 }

}




/**
 exponential for I@126
**/
double exponential(double* x, double* par) {
  //[0] = N normalization factor
  //[1] = lambda slope
 double xx = x[0];
 double N = par[0];
 double lambda = par[1];

  //std::cout << "N: " << N << " lambda: " << lambda << std::endl;
 return N * exp(-1.*lambda*xx);
}



//---- division of CBLowHighPlusExp with CBLowHigh ----
// Double_t CrystalBallLowHighPlusExpDividedByCrystalBallLowHigh(Double_t *x,Double_t *par) {
//  double den = crystalBallLowHigh (x, par + 9) ; // signal only
//  if (den == 0) return -1. ;
//  double num = doubleGausCrystalBallLowHighPlusExp (x, par) ; // signal and interference
//  return num / den ;
// }


//---- division of CBLowHighPlusExp with CBLowHigh ----
Double_t CrystalBallLowHighPlusExpDividedByCrystalBallLowHigh(Double_t *x,Double_t *par) {
 double den = crystalBallLowHigh (x, par + 9) ; // signal only
 if (den == 0) return -1. ;
 double num = doubleGausCrystalBallLowHighPlusExp (x, par) ; // signal + I@800 +I@126
 double I126 = - exponential (x,par+16); //interference from H126
 //I126 is fitted as positive (BnoH-SBI125), so need to change the sign

 float alpha = par[18];
 float beta = par[19];
 float zeta = par[20];
// num = beta*S + sqrt(beta)*I@800 + sqrt(zeta)*I@126
// den = S

 double S_par[7] = {par[9],par[10],beta*par[11],par[12],par[13],par[14],par[15]};
 double S = crystalBallLowHigh (x, S_par) ; //SM signal with width rescaled for c',BRnew
 float I = (num - beta*S - sqrt(1-beta)*I126)/sqrt(beta);

 float w = 0;
 if (S>0) w = (alpha*S + sqrt(alpha)*I + sqrt(zeta)*I126) / den;

 if (w<0) return 0;
 else return w;

}


TH1F*     hInt_ggH = 0 ;
TSpline3* wInt_ggH = 0 ;

TGraph2D* variables_S[7];
TGraph2D* variables_SI[9];
TGraph2D* variables_I126[2];
TF1* crystal_Icorr_qqH;

// iType = 0 : ggH
//         1 : qqH

float getIntWght(int iType, float mass , float cpsq , float BRnew = 0.0, int EWKcase = 1,  float kind = 0)
{
   float wInt=1.;
   if ( iType == 0 ) { //---- ggH
     if ( wInt_ggH ) {
       wInt = wInt_ggH->Eval(mass) ;
       if ( cpsq < 1. ) wInt = (1-BRnew)*wInt/cpsq;
       wInt += 1;
       if (wInt < 0) wInt = 0.01;
     } else {
       std::cout << "Missing Interference !!!!" << std::endl;
     }
   }
   else if ( iType == 1 ) { //---- qqH
    wInt = 1.;
    wInt = crystal_Icorr_qqH->Eval(mass);
//     std::cout << " qqHinterference calculated "  << std::endl;
    // Done in inputs now : if ( cpsq < 1. ) wInt = 1.+(wInt-1.)/cpsq; //---- needed also here?
   }
   return wInt;
}


// iSyst =  0 : Cent
//         +1 :
//         -1 : 
void initIntWght(std::string wFile , int iType , int iSyst, float Hmass = 350, float cprime = 1.0, float BRnew = 0.0, int EWKcase = 1) { // c'=1.0 --> SM   BRnew = 0.0 --> SM

//    mu -> mu * cprime * (1-BRnew)        = alpha * mu
//    Gamma -> Gamma * cprime / (1-BRnew)  = beta * Gamma
//    alpha = cprime * (1-BRnew)
//    beta  = cprime / (1-BRnew)

//    std::cout << " initialization interference "  << std::endl;

   float alpha = cprime * (1-BRnew);
   float beta  = cprime / (1-BRnew);
   double zeta = 1-cprime;

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
//     std::cout << " initialization interference for qqH "  << std::endl;
    TString *readfile;
//     if (EWKcase) { //---- for c'=1 background is H-10 TeV
//      readfile = new TString (wFile+"data/InterferenceVBF/EWK_SINGLET/file_for_interpolation.root"); //file with the values of the all parameters
//      if (iSyst ==  1) {
//       readfile = new TString (wFile+"data/InterferenceVBF/EWK_SINGLET/file_for_interpolation_up.root");
//      }
//      if (iSyst == -1) {
//       readfile = new TString (wFile+"data/InterferenceVBF/EWK_SINGLET/file_for_interpolation_dn.root");
//      }
//     }
//     else { //---- for c'=1 background is H-126 GeV
//      readfile = new TString (wFile+"data/InterferenceVBF/SM/file_for_interpolation.root"); //file with the values of the all parameters
//      if (iSyst ==  1) {
//       readfile = new TString (wFile+"data/InterferenceVBF/SM/file_for_interpolation_up.root");
//      }
//      if (iSyst == -1) {
//       readfile = new TString (wFile+"data/InterferenceVBF/SM/file_for_interpolation_dn.root");
//      }
//     }

    readfile = new TString (wFile+"data/InterferenceVBF/MODEL_3/file_for_interpolation.root"); //file with the values of the all parameters
    if (iSyst ==  1) {
     readfile = new TString (wFile+"data/InterferenceVBF/MODEL_3/file_for_interpolation_up.root");
    }
    if (iSyst == -1) {
     readfile = new TString (wFile+"data/InterferenceVBF/MODEL_3/file_for_interpolation_dn.root");
    }

    TFile* SI = new TFile(readfile->Data());
//     Double_t fill_param[16]; // 9 + 7 = 16
//     std::cout << " file = " << readfile->Data() << std::endl;
    TString parameters_normal [9] = {"Norm","Mean_CB","Sigma_CB","alphaR_CB","nR_CB","alphaL_CB","nL_CB","R","Tau"};
    TString parameters_I126 [2] = {"N_exp","Tau_exp"};
    for (int i=0; i<9; i++) {
     TString *name = new TString (parameters_normal[i]);
     name->Append("_SI.txt");
//      std::cout << " i = " << i << " name = " << name -> Data()  << std::endl;
     variables_SI[i] = (TGraph2D*)SI->Get(name->Data());
    }
    for (int i=0; i<7; i++) {
     TString *name = new TString (parameters_normal[i]);
     name->Append("_S.txt");
//      std::cout << " i = " << i << " name = " << name -> Data()  << std::endl;
     variables_S[i] = (TGraph2D*)SI->Get(name->Data());
    }
    for (int i=0; i<2; i++) {
     TString *name = new TString (parameters_I126[i]);
     name->Append("_I126.txt");
     variables_I126[i] = (TGraph2D*)SI->Get(name->Data());
    }


    crystal_Icorr_qqH = new TF1("crystal_Icorr_qqH",CrystalBallLowHighPlusExpDividedByCrystalBallLowHigh,0,3000,16+2+3);

    for (int iVar = 0; iVar<9; iVar++) {
//      std::cout << " iVar = " << iVar << " parameters_normal[" << iVar << "] = " << parameters_normal[iVar] << std::endl;
     if (parameters_normal[iVar].Contains("Norm")){
      crystal_Icorr_qqH->SetParameter(iVar, exp(variables_SI[iVar]->Interpolate(Hmass, beta)));
     }
     else {
      crystal_Icorr_qqH->SetParameter(iVar, variables_SI[iVar]->Interpolate(Hmass, beta));
     }
    }
    for (int iVar = 0; iVar<7; iVar++) {
     if (parameters_normal[iVar].Contains("Norm")){
      crystal_Icorr_qqH->SetParameter(iVar+9, exp(variables_S[iVar]->Interpolate(Hmass, beta)));
     }
     else {
      crystal_Icorr_qqH->SetParameter(iVar+9, variables_S[iVar]->Interpolate(Hmass, beta));
     }
    }

    for (int iVar = 0; iVar<2; iVar++) {
     crystal_Icorr_qqH->SetParameter(iVar+16, variables_I126[iVar]->Interpolate(Hmass, beta));
    }


    crystal_Icorr_qqH->SetParameter(6+9+2+1, alpha);
    crystal_Icorr_qqH->SetParameter(6+9+2+2, beta);
    crystal_Icorr_qqH->SetParameter(6+9+2+3, zeta);

   }

}



