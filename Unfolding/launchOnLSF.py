#!/bin/bash

for arg in "central" "up" "down" "metScale_up" "metScale_down" "jetEnergyScale_up" "jetEnergyScale_down" "electronScale_up" "electronScale_down" "muonScale_up" "muonScale_down" "metResolution" "electronResolution" "leptonEfficiency_up" "leptonEfficiency_down" "btagsf_up" "btagsf_down"
do
echo $arg
bsub -q 1nd "submit.sh $arg"
done
