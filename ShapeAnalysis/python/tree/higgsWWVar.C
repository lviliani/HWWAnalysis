
#include <TMath.h>
#include <algorithm>
#include <TLorentzVector.h>
#include <iostream>

class higgsWW {
 public:
  //! constructor
  higgsWW(float pt1, float pt2, float eta1, float eta2, float phi1, float phi2,     float vpt1, float vpt2, float veta1, float veta2, float vphi1, float vphi2);
  virtual ~higgsWW() {}

  //! functions
  float mWW();
  float ptWW();

 private:
  //! variables
  TLorentzVector L1,L2;
  TLorentzVector V1,V2;

};

//! constructor
higgsWW::higgsWW(float pt1, float pt2, float eta1, float eta2, float phi1, float phi2,     float vpt1, float vpt2, float veta1, float veta2, float vphi1, float vphi2) {

 L1.SetPtEtaPhiM(pt1, eta1, phi1, 0.);
 L2.SetPtEtaPhiM(pt2, eta2, phi2, 0.);

 V1.SetPtEtaPhiM(vpt1, veta1, vphi1, 0.);
 V2.SetPtEtaPhiM(vpt2, veta2, vphi2, 0.);

}

//! functions

float higgsWW::mWW(){

 return (L1+L2+V1+V2).M();

}

float higgsWW::ptWW(){

 return (L1+L2+V1+V2).Pt();

}


