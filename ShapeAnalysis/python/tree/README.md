Examples
=======

How to use the gardener for standard MC samples

Where:

    scripts
    source ../test/env.sh


Trigger weight

    triggW
    echo y | ./gardener.py efftfiller -r input/ output -f ../data/fit_results.txt


Efficiency weight

    effW
    echo y | ./gardener.py effwfiller \
            -r input/ output/ \
            --mufile=../data/muons_scale_factors.root \
            --elfile=../data/electrons_scale_factors.root \
            --muname=muonsDATAMCratio_all \
            --elname=electronsDATAMCratio_All_selec


PileUp weight

    puW
    echo y | ./gardener.py  puadder -r input output --mc=../data/PileupMC_60bin_S10.root    \
               --data=../data/PUdata2012Final.root   \
               --HistName=pileup   \
               --branch=puW  \
               --kind=trpu


