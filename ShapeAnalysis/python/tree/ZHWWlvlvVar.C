//////////////////////////////////////////////
//
// Written and designed by M. Franke 04-04-14
// Northeastern University
//
//////////////////////////////////////////////

#include <TMath.h>

// add dphi Z-W-lepton1,2!

class ZHWW4lvari{
 public:
  //! constructor
  ZHWW4lvari(float pt1,float pt2,float pt3,float pt4,float eta1,float eta2,float eta3,float eta4,float phi1,float phi2,float phi3,float phi4,int ch1,int ch2,int ch3,int ch4,int fl1,int fl2,int fl3,int fl4);
  virtual ~ZHWW4lvari() {}
  
  //! functions
  int CalcValues(float& values);
  float GetMllZ();
  float GetDphiZ();
  float GetFlZ();
  float GetPTZ();
  float GetMllWW();
  float GetDphiWW();
  float GetFlWW();
  float GetPTWW();
  float GetDphiZ1();
  float GetDphiZ2();
  float GetM4l();
  
 private:
  //! variables
  float pTs[4];
  float etas[4];
  float phis[4];
  int charges[4];
  int flavors[4];
  float values[11];
  
  //! functions
  int getIndex(int a, int b);
};

//! constructor, filling arrays, Calculating values
ZHWW4lvari(float pt1,float pt2,float pt3,float pt4,float eta1,float eta2,float eta3,float eta4,float phi1,float phi2,float phi3,float phi4,int ch1,int ch2,int ch3,int ch4,int fl1,int fl2,int fl3,int fl4){
 pTs = {pt1, pt2, pt3, pt4};
 etas = {eta1, eta2, eta3, eta4};
 phis = {phi1, phi2, phi3, phi4};
 charges = {ch1, ch2, ch3, ch4}; // +/- 1
 flavors = {fl1, fl2, fl3, fl4}; // flavor: 13 = Myon, 11 = Electron
 CalcValues(&values);
}

//! functions
int CalcValues(float& values){
 int finalI6 = 0;
 if(charges[0] + charges[1] + charges[2] + charges[3] == 0){
  float mlls[6]; // invariant mass for all combinations
  float dmlls[6]; // difference in invariant mass from Z-mass
  float mindmll = 600;
  int index[4] = {0,0,0,0}; // 0 + 1 -> Z, 2 + 3 -> W
  int I6 = 0;
  for(Int i = 0; i<3;i++){
   for(Int j = i+1; j<4;j++){
    mlls[I6] = TMath::Sqrt(2*pTs[i]*pTs[j]*(TMath::CosH(etas[i]-etas[j]) - TMath::Cos(phis[i]-phis[j]))); // invariant mass of i and j 
    dmlls[I6] = TMath::Abs(91.1876-mlls[I6]); // difference to Z mass
    int i3 = getIndex(i,j);
    if (i3>= 0 && (mindmll > dmlls[I6]) && (charges[i] != charges[j]) && (charges[i3] != charges[6 - i3-i-j])){
     if(flavors[i] == flavors [j]){
      mindmll = dmlls[I6];
      index[0] = i; // Z_lepton_1
      index[1] = j; // Z_lepton_2
      index[2] = i3; // W_lepton_1
      index[3] = 6 - i-j-i3; // W_lepton_2
      finalI6 = I6;
     }
    }
    I6++;
   }
  }
 }
 if(finalI6){    
  float mllZ = mlls[finalI6];
  float mllW = mlls[5-finalI6];
  float dphillZ = TMath::Min(TMath::Abs(phis[index[0]]-phis[index[1]]),(2*TMath::Pi()-TMath::Abs(phis[index[0]]-phis[index[1]])));
  float dphillW = TMath::Min(TMath::Abs(phis[index[2]]-phis[index[3]]),(2*TMath::Pi()-TMath::Abs(phis[index[2]]-phis[index[3]])));
  float mllll = 0;
  for (Int_t i = 0;i<6;i++){
   mllll = mllll + TMath::Power(mlls[i],2);
  }
  mllll = TMath::Sqrt(mllll);
        
  pt = sqrt((pt1*cos(phi1) + pt2*cos(phi2))^2 + (pt1*sin(phi) + pt2*sin(phi2))^2)
        
        // fill array with values
    values[0] = mllZ; // mass of leptons from Z
  values[1] = dphillZ; // dphi between leptons from Z
  values[2] = flavors[index[0]]; // flavor of leptons from Z: 11 == ee, 13 == mm
  values[3] = TMath::Sqrt(TMath::Power(pTs[index[0]]*TMath::Cos(phis[index[0]] + TMath::Power(pTs[index[1]]*TMath::Cos(phis[index[1]]),2) + TMath::Power(pTs[index[0]]*TMath::Sin(phis[index[0]] + TMath::Power(pTs[index[1]]*TMath::Sin(phis[index[1]]),2));// pT of leptons from Z
        
  values[4] = mllW; // mass of leptons from WW
  values[5] = dphillW; // dphi between leptons from WW
  values[6] = 0.5*(flavors[index[2]] + flavors[index[3]]); // flavor of leptons from WW: 11 == ee, 12==em, 13==mm
  values[7] = TMath::Sqrt(TMath::Power(pTs[index[2]]*TMath::Cos(phis[index[2]] + TMath::Power(pTs[index[3]]*TMath::Cos(phis[index[3]]),2) + TMath::Power(pTs[index[2]]*TMath::Sin(phis[index[2]] + TMath::Power(pTs[index[3]]*TMath::Sin(phis[index[3]]),2));// pT of leptons from WW
        
        // add dphi Z-W-lepton1,2
  values[8] = -99999;// dphi Z-W-lepton1
  values[9] = -99999;// dphi Z-W-lepton2
        
  values[10] = mllll; // invariant mass of 4-lepton system
  return 0;
 }
 else{ // NO Z FOUND!! return standard values
  values[0] = -9999; // mass of leptons from Z
  values[1] = -9999; // dphi between leptons from Z
  values[2] = -9999; // flavor of leptons from Z: 0 == ee, 1==em, 2==mm
  values[3] = -9999;// pT of leptons from Z
        
  values[4] = -9999; // mass of leptons from WW
  values[5] = -9999; // dphi between leptons from WW
  values[6] = -9999; // flavor of leptons from WW: 0 == ee, 1==em, 2==mm
  values[7] = -9999;// pT of leptons from WW
        
  values[8] = -9999;// dphi Z-W-lepton1
  values[9] = -9999;// dphi Z-W-lepton2
        
  values[10] = -9999; // invariant mass of 4-lepton system
  return 1;
 }  
}

float GetMllZ(){
 return values[0];
}
float GetDphiZ(){
 return values[1];
}
float GetFlZ(){
 return values[2];
}
float GetPTZ(){
 return values[3];
}
float GetMllWW(){
 return values[4];
}
float GetDphiWW(){
 return values[5];
}
float GetFlWW(){
 return values[6];
}
float GetPTWW(){
 return values[7];
}
float GetDphiZ1(){
 return values[8];
}
float GetDphiZ2(){
 return values[9];
}
float GetM4l(){
 return values[10];
}

int getIndex(int a, int b){
    // takes index 1 + 2 of a 4 variable system
    // returns index 3 so that 1 != 2 != 3
    // index 4 = 6 - a - b - getIndex(a,b) 
 switch( 6 - a - b ){ 
  case 5: return 2;
  case 4: return 1; 
  case 3: if(a == 0){return 1;} else{return 0;}
  case 2: return 0;
  case 1: return 0; 
 }
 return -1;
}
