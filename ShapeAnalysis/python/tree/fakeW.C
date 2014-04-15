#include <vector>

class FakeProbabilities {
 public:
  //! constructor at least wants leptons and MET
  FakeProbabilities(float pt1, float eta1, float id1, float pt2, float eta2, float id2, float pt3, float eta3, float id3, float pt4, float eta4, float id4);
  virtual ~FakeProbabilities() {}

  //! probability fuctions
  double FakeW4l();
  double FakeW4l(float pt1, float eta1, float id1, float pt2, float eta2, float id2, float pt3, float eta3, float id3, float pt4, float eta4, float id4);

 private:

  float pt1_;
  float eta1_;
  float id1_;

  float pt2_;
  float eta2_;
  float id2_;

  float pt3_;
  float eta3_;
  float id3_;

  float pt4_;
  float eta4_;
  float id4_;

};

//---- init ----

FakeProbabilities::FakeProbabilities(float pt1, float eta1, float id1, float pt2, float eta2, float id2, float pt3, float eta3, float id3, float pt4, float eta4, float id4) {
 pt1_  = pt1;
 eta1_ = eta1;
 id1_  = id1;

 pt2_  = pt2;
 eta2_ = eta2;
 id2_  = id2;

 pt3_  = pt3;
 eta3_ = eta3;
 id3_  = id3;

 pt4_  = pt4;
 eta4_ = eta4;
 id4_  = id4;

}


//---- 4 leptons case ----

double FakeProbabilities::FakeW4l(){
 
 return 1.;
}


double FakeProbabilities::FakeW4l(float pt1, float eta1, float id1, float pt2, float eta2, float id2, float pt3, float eta3, float id3, float pt4, float eta4, float id4){
 pt1_  = pt1;
 eta1_ = eta1;
 id1_  = id1;

 pt2_  = pt2;
 eta2_ = eta2;
 id2_  = id2;

 pt3_  = pt3;
 eta3_ = eta3;
 id3_  = id3;

 pt4_  = pt4;
 eta4_ = eta4;
 id4_  = id4;

 return FakeW4l();
}

