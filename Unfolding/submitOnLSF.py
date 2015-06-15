#!/bin/bash

base=/afs/cern.ch/work/l/lviliani/DatacardFramework/CMSSW_7_1_5/src/Unfolding_12_6

cd $base
eval `scram runtime -sh`
cd -

arg=${1}

cp $base/buildMatrix.py ./toRun.py
cp $base/libRooUnfold* .
python toRun.py $arg > log_$arg &> err_$arg

cp responseMatrix.root $base/responseMatrix_${arg}.root
cp log_$arg $base
cp err_$arg $base

