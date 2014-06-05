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






//---- division of CBLowHighPlusExp with CBLowHigh ----
Double_t CrystalBallLowHighPlusExpDividedByCrystalBallLowHigh(Double_t *x,Double_t *par) {
 double den = crystalBallLowHigh (x, par + 9) ; // signal only
 if (den == 0) return -1. ;
 double num = doubleGausCrystalBallLowHighPlusExp (x, par) ; // signal and interference
 return num / den ;
}



