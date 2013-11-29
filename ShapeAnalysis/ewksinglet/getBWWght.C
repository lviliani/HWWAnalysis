
float getBWWght(float m, float Mass , float GamSM , float Gamma)
{
   float Minv2 = m*m; 
   float BWSM = ( Minv2*GamSM/Mass) / ( pow(Minv2-pow(Mass,2),2) + pow(Minv2*GamSM/Mass,2) ) ;
   float BW   = ( Minv2*Gamma/Mass) / ( pow(Minv2-pow(Mass,2),2) + pow(Minv2*Gamma/Mass,2) ) ;
   return BW/BWSM;
}
