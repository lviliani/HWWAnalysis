This repository contains all the needed stuff to build the response matrices, unfold the measured spectrum and plot the final results for the pT Higgs analysis in H->WW.

buildMatrix.py
==============
Three different kinds of systematic uncertainties are taken into account. Type A uncertainties, i.e. those that affect the signal strengths but not the response matrix, are accounted using the covariance matrix extracted from the fitting procedure. Type B uncertainties, i.e. the ones affecting both the signal strengths and the response matrix, are included building different response matrices for each systematic up and down variations.
These systematics are:
- electronResolution
- metResolution
- metScale (up/down)
- leptonEfficiency (up/down)
- btagsf (up/down)
- jetEnergyScale (up/down)
- electronScale (up/down)
- muonScale (up/down)

Type C uncertainties are the ones affecting only the response matrix and are accounted for varying the ggH/VBF ratio (so called up/down variation).
To speed up the matrices creation, two scripts to submit the jobs on LSF can be used ("launchOnLSF.py" and "submitOnLSF.py").

Unfold.py
===================
Compute the nominal (central) response matrix that is used to unfold all the histograms but the ones which need a different response matrix. These ones are unfolded with the correct matrix taken from the "responseMatrices" directory.
This script automatically call the finalPlot.py script.

finalPlot.py
============
Compute the systematic and statistical error and plot the final result.

finalPlot_preUnfold.py
======================
Same as "finalPlot.py" but plots the results obtained from the fit, i.e. before unfolding.

MCtruth.py
==========
Calculate the MC truth pTH spectrum, used as a closure test on unfolded spectrum.

MCmeasured.py
=============
Calculate the MC measured pTH spectrum, used as a closure test on pre-unfolded spectrum.
