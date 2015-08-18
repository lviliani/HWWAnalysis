#!/bin/bash

base=${1}

eval `scram runtime -sh`
cd -

arg=${2}

cp $base/buildMatrix.py ./toRun.py
cp $base/libRooUnfold* .
python toRun.py $arg > log_$arg &> err_$arg

cp responseMatrix.root $base/responseMatricesPreApp/responseMatrix_${arg}.root
cp log_$arg $base
cp err_$arg $base

