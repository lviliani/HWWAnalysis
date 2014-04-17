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

    for dytt embedded sample, we need to apply efficiency weights and not scale factors, since no special id is applied (to be checked)
            --elname=effDATA_All_selec   for dytt embeded sample

PileUp weight

    puW
    echo y | ./gardener.py  puadder -r input output --mc=../data/PileupMC_60bin_S10.root    \
               --data=../data/PUdata2012Final.root   \
               --HistName=pileup   \
               --branch=puW  \
               --kind=trpu





Useful variables
====

add useful variables, if not already available:

    id1, id2, id3, id4 --> lepton flavour (and charge)
    type1, type2, type3, type4 --> if the lepton passed of failed lepton id/iso (used in fake rate application)


    echo y | ./gardener.py  adder \
               -v 'id1/F=11*(bdt1<100)*(-ch1)+13*(bdt1>=100)*(-ch1)'  \
               -v 'id2/F=11*(bdt2<100)*(-ch2)+13*(bdt2>=100)*(-ch2)'  \
               -v 'id3/F=11*(bdt3<100)*(-ch3)+13*(bdt3>=100)*(-ch3)'  \
               -v 'id4/F=11*(bdt4<100)*(-ch4)+13*(bdt4>=100)*(-ch4)'  \
               -r input output


    echo y | ./gardener.py  adder \
               -v 'id1/F=11*(bdt1<100)*(-ch1)+13*(bdt1>=100)*(-ch1)'  \
               -v 'id2/F=11*(bdt2<100)*(-ch2)+13*(bdt2>=100)*(-ch2)'  \
               -v 'id3/F=11*(bdt3<100)*(-ch3)+13*(bdt3>=100)*(-ch3)'  \
               -v 'id4/F=11*(bdt4<100)*(-ch4)+13*(bdt4>=100)*(-ch4)'  \
               /tmp/amassiro/latino_RunA_892pbinv_LooseLoose_NEW.root /tmp/amassiro/latino_RunA_892pbinv_LooseLoose_NEW_idx.root 


    echo y | ./gardener.py  adder \
               -v 'type1/F=pass2012ICHEP1'  \
               -v 'type2/F=pass2012ICHEP2'  \
               -v 'type3/F=pass2012ICHEP3'  \
               -v 'type4/F=pass2012ICHEP4'  \
               /tmp/amassiro/latino_RunA_892pbinv_LooseLoose_NEW.root /tmp/amassiro/latino_RunA_892pbinv_LooseLoose_NEW_pass.root 




Fake W+jets
====

fakeW

    ./gardener.py  fakeW  /tmp/amassiro/latino_RunA_892pbinv_LooseLoose.root   /tmp/amassiro/latino_RunA_892pbinv_LooseLoose_NEW.root





ZHWWlvlv
====

new variables


    ./gardener.py  zhwwlvlvVar  /data/amassiro/LatinosTrees/nominals_TEMP/latinostep3_latinosYieldSkim_MC_ZHWW_100k_new.root    /tmp/amassiro/latinostep3_latinosYieldSkim_MC_ZHWW_100k_new.root



