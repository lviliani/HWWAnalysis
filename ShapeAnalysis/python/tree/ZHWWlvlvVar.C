//////////////////////////////////////////////
//
// Written and designed by M. franke 04-15-14
// Northeastern University
//
//////////////////////////////////////////////

# include <TMath.h>
# include <algorithm>

// add dphi Z-W-lepton1,2!

class ZHWW4lvari {
 public:
  //! constructor
  ZHWW4lvari(float pt1,float pt2,float pt3,float pt4,float eta1,float eta2,float eta3,float eta4,float phi1,float phi2,float phi3,float phi4,float ch1,float ch2,float ch3,float ch4,float fl1,float fl2,float fl3,float fl4);
  virtual ~ZHWW4lvari() {}

  //! functions
  int CalcValues();
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
ZHWW4lvari::ZHWW4lvari(float pt1,float pt2,float pt3,float pt4,float eta1,float eta2,float eta3,float eta4,float phi1,float phi2,float phi3,float phi4,float ch1,float ch2,float ch3,float ch4,float fl1,float fl2,float fl3,float fl4) {
 pTs[0] = pt1; pTs[1] = pt2; pTs[2] = pt3; pTs[3] = pt4;
 etas[0] = eta1; etas[1] = eta2; etas[2] = eta3; etas[3] = eta4;
 phis[0] = phi1; phis[1] = phi2; phis[2] = phi3; phis[3] = phi4;
 charges[0] = ch1; charges[1] = ch2; charges[2] = ch3; charges[3] = ch4; // +/- 1
 flavors[0] = fl1; flavors[1] = fl2; flavors[2] = fl3; flavors[3] = fl4; // flavor: 13 = Muon, 11 = Electron

 CalcValues();
}

//! functions
int ZHWW4lvari::CalcValues(){
 int finalI6 = 0;
 float mlls[6]; // invariant mass for all combinations
 float dmlls[6]; // difference in invariant mass from Z-mass
 float mindmll = 600;
 int index[4] = {0,0,0,0}; // 0 + 1 -> Z, 2 + 3 -> W
 int Z = 0;
 if(charges[0] + charges[1] + charges[2] + charges[3] == 0){
  int I6 = 0;
  for(int i = 0; i<3;i++){
   for(int j = i+1; j<4;j++){
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
      Z = 1;
     }
    }
    I6++;
   }
  }
 }
 if(Z){
  float mllZ = mlls[finalI6];
  float mllW = mlls[5-finalI6];
  float dphillZ = std::min(1.*fabs(phis[index[0]]-phis[index[1]]),1.*(2*TMath::Pi()-fabs(phis[index[0]]-phis[index[1]])));
  float dphillW = std::min(1.*fabs(phis[index[2]]-phis[index[3]]),1.*(2*TMath::Pi()-fabs(phis[index[2]]-phis[index[3]])));
  float mllll = 0;
  for (int i = 0;i<6;i++){
   mllll = mllll + TMath::Power(mlls[i],2);
  }
  mllll = TMath::Sqrt(mllll);

  // fill array with values
  values[0] = mllZ; // mass of leptons from Z
  values[1] = dphillZ; // dphi between leptons from Z
  values[2] = flavors[index[0]]; // flavor of leptons from Z: 11 == ee, 13 == mm
  values[3] = TMath::Sqrt(TMath::Power(pTs[index[0]]*TMath::Cos(phis[index[0]]) + pTs[index[1]]*TMath::Cos(phis[index[1]]),2) + TMath::Power(pTs[index[0]]*TMath::Sin(phis[index[0]]) + pTs[index[1]]*TMath::Sin(phis[index[1]]),2));// pT of leptons from Z

  values[4] = mllW; // mass of leptons from WW
  values[5] = dphillW; // dphi between leptons from WW
  values[6] = 0.5*(flavors[index[2]] + flavors[index[3]]); // flavor of leptons from WW: 11 == ee, 12==em, 13==mm
  values[7] = TMath::Sqrt(TMath::Power(pTs[index[2]]*TMath::Cos(phis[index[2]]) + pTs[index[3]]*TMath::Cos(phis[index[3]]),2) + TMath::Power(pTs[index[2]]*TMath::Sin(phis[index[2]]) + pTs[index[3]]*TMath::Sin(phis[index[3]]),2));// pT of leptons from WW

        // add dphi Z-W-lepton1,2
  values[8] = -99999;// dphi Z-W-lepton1
  values[9] = -99999;// dphi Z-W-lepton2
        
  values[10] = mllll; // invariant mass of 4-lepton system
  return 0;
 }
 else{ // NO Z fOUND!! return standard values
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

float ZHWW4lvari::GetMllZ(){
 return values[0];
}
float ZHWW4lvari::GetDphiZ(){
 return values[1];
}
float ZHWW4lvari::GetFlZ(){
 return values[2];
}
float ZHWW4lvari::GetPTZ(){
 return values[3];
}
float ZHWW4lvari::GetMllWW(){
 return values[4];
}
float ZHWW4lvari::GetDphiWW(){
 return values[5];
}
float ZHWW4lvari::GetFlWW(){
 return values[6];
}
float ZHWW4lvari::GetPTWW(){
 return values[7];
}
float ZHWW4lvari::GetDphiZ1(){
 return values[8];
}
float ZHWW4lvari::GetDphiZ2(){
 return values[9];
}
float ZHWW4lvari::GetM4l(){
 return values[10];
}

int ZHWW4lvari::getIndex(int a, int b){
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

 