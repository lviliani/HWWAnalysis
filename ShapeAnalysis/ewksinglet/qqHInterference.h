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