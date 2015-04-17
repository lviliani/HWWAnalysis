plotsFromFit.root
=================
Contains the up and down variation histograms for all the nuisances in the model, corresponding to the signal extracted from the fit.

buildMatrix.py
==============
Build different response matrices for each systematic up and down variations.
Only the systematics that change the shape of the pTH distribution are taken into account.
These systematics are:
- electronResolution
- metResolution
- metScale (up/down)
- leptonEfficiency (up/down)
- btagsf (up/down)
Lepton scales affect in the same way both leptons transverse momenta and MET and then do not affect pTH.
Jet energy scales do not affect pTH.

Unfold_nuisances.py
===================
Compute the nominal (central) response matrix that is used to unfold all the histograms but the ones which need a different response matrix. These ones are unfolded with the correct matrix taken from "ggHresponseMatrices.root" or "vbfresponseMatrices.root".

finalPlot.py
============
Compute the systematic and statistical error and plot the final result.
