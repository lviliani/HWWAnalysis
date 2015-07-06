#!/bin/bash

base=/afs/cern.ch/user/l/lenzip/work/ww/differential/CMSSW_6_1_1/src/HWWAnalysis/Unfolding/

cd $base
eval `scram runtime -sh`
cd -

arg=${1}

cp $base/buildMatrix.py ./toRun.py
cp $base/lib/libRooUnfold* .
python toRun.py $arg > log_$arg &> err_$arg

cp responseMatrix.root $base/responseMatrix_${arg}.root
cp log_$arg $base
cp err_$arg $base

