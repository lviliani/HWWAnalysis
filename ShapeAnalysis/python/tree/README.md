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




Useful corrections
====

xyshift for met

    mkdir /tmp/amassiro/ww-xyshift/
    ./gardener.py  xyShift  /tmp/amassiro/latino000_nll_ewk.root     /tmp/amassiro/ww-xyshift/latino000_nll_ewk.root
    ./gardener.py  xyShift  /tmp/amassiro/latino002_nll_ewk.root     /tmp/amassiro/ww-xyshift/latino002_nll_ewk.root
    ./gardener.py  xyShift  /tmp/amassiro/latino006_nll_ewk.root     /tmp/amassiro/ww-xyshift/latino006_nll_ewk.root



Useful variables
====

add useful variables, if not already available:

    id1, id2, id3, id4 --> lepton flavour (and charge)
    type1, type2, type3, type4 --> if the lepton passed of failed lepton id/iso (used in fake rate application)


    echo y | ./gardener.py  adder \
               -v 'id1/F=11.*(bdt1<100)*(-ch1)+13.*(bdt1>=100)*(-ch1)'  \
               -v 'id2/F=11.*(bdt2<100)*(-ch2)+13.*(bdt2>=100)*(-ch2)'  \
               -v 'id3/F=11.*(bdt3<100)*(-ch3)+13.*(bdt3>=100)*(-ch3)'  \
               -v 'id4/F=11.*(bdt4<100)*(-ch4)+13.*(bdt4>=100)*(-ch4)'  \
               -r input output


    echo y | ./gardener.py  adder \
               -v 'id1/F=11.*(bdt1<100)*(-ch1)+13.*(bdt1>=100)*(-ch1)'  \
               -v 'id2/F=11.*(bdt2<100)*(-ch2)+13.*(bdt2>=100)*(-ch2)'  \
               -v 'id3/F=11.*(bdt3<100)*(-ch3)+13.*(bdt3>=100)*(-ch3)'  \
               -v 'id4/F=11.*(bdt4<100)*(-ch4)+13.*(bdt4>=100)*(-ch4)'  \
               /tmp/amassiro/latino_RunA_892pbinv_LooseLoose_NEW.root /tmp/amassiro/latino_RunA_892pbinv_LooseLoose_NEW_idx.root 


    echo y | ./gardener.py  adder \
               -v 'type1/F=pass2012ICHEP1'  \
               -v 'type2/F=pass2012ICHEP2'  \
               -v 'type3/F=pass2012ICHEP3'  \
               -v 'type4/F=pass2012ICHEP4'  \
               /tmp/amassiro/latino_RunA_892pbinv_LooseLoose_NEW_idx.root /tmp/amassiro/latino_RunA_892pbinv_LooseLoose_NEW_idx_pass.root 




Fake W+jets
====

fakeW

    ./gardener.py  fakeW  /tmp/amassiro/latino_RunA_892pbinv_LooseLoose.root   /tmp/amassiro/latino_RunA_892pbinv_LooseLoose_NEW.root
    ./gardener.py  fakeW  /tmp/amassiro/latino_RunA_892pbinv_LooseLoose_NEW_idx_pass.root   /tmp/amassiro/latino_RunA_892pbinv_LooseLoose_NEW_idx_pass_NEW.root




ZHWWlvlv
====

new variables


    ./gardener.py  zhwwlvlvVar  /data/amassiro/LatinosTrees/nominals_TEMP/latinostep3_latinosYieldSkim_MC_ZHWW_100k_new.root    /tmp/amassiro/latinostep3_latinosYieldSkim_MC_ZHWW_100k_new.root



Electroweak corrections for WW
====

    /afs/cern.ch/work/d/dmeister/public/LatinoTrees/NoSkim_puW_effW_triggW/latino000.root
    gardener.py  qq2vvEWKcorrections  /tmp/amassiro/latino000.root    /tmp/amassiro/latino000_ewk.root

    gardener.py  qq2vvEWKcorrections  /data/amassiro/LatinosTrees/ww/latino000_nll.root    /data/amassiro/LatinosTrees/ww/latino000_nll_ewk.root
    gardener.py  qq2vvEWKcorrections  /data/amassiro/LatinosTrees/ww/latino002_nll.root    /data/amassiro/LatinosTrees/ww/latino002_nll_ewk.root
    gardener.py  qq2vvEWKcorrections  /data/amassiro/LatinosTrees/ww/latino006_nll.root    /data/amassiro/LatinosTrees/ww/latino006_nll_ewk.root


WW+2j
====

new variables


    gardener.py  ww2jVar  /tmp/amassiro/latino_006_WWJets2LPowheg.root       /tmp/amassiro/latino_006_WWJets2LPowheg_new.root

    gardener.py  ww2jVar  -F -r  /data/amassiro/LatinosTrees/2j/nominals_all/      /data/amassiro/LatinosTrees/2jewk/nominals_all/
    gardener.py  ww2jVar  -F -r  /data/amassiro/LatinosTrees/2j/wjets/             /data/amassiro/LatinosTrees/2jewk/wjets/
    gardener.py  ww2jVar  -F -r  /data/amassiro/LatinosTrees/2j/data/              /data/amassiro/LatinosTrees/2jewk/data/

    ls --color=none /data/amassiro/LatinosTrees/tree_skim_all_2j/ | awk '{print "gardener.py  ww2jVar -r  -F  /data/amassiro/LatinosTrees/tree_skim_all_2j/"$1"  /data/amassiro/LatinosTrees/tree_skim_all_2j_mva/"$1   }'



Filter
====

How to filter folders with a TFormula string

    gardener.py  filter -f "njet>=2 && pfmet>20"   -r    /data/amassiro/LatinosTrees/nominals_all/      /data/amassiro/LatinosTrees/2j/nominals_all/
    gardener.py  filter -f "njet>=2 && pfmet>20"   -r    /data/amassiro/LatinosTrees/wjets/             /data/amassiro/LatinosTrees/2j/wjets/
    gardener.py  filter -f "njet>=2 && pfmet>20"   -r    /data/amassiro/LatinosTrees/data/              /data/amassiro/LatinosTrees/2j/data/

    ls --color=none /home/amassiro/Latinos/Shape/tree_skim_all/ | awk '{print "gardener.py  filter -f \"njet>=2 && pfmet>20\"   -r  -F  /home/amassiro/Latinos/Shape/tree_skim_all/"$1"  /data/amassiro/LatinosTrees/tree_skim_all_2j/"$1   }'






NLL corrections for WW
====

    /afs/cern.ch/work/d/dmeister/public/LatinoTrees/NoSkim_puW_effW_triggW/latino000.root
    gardener.py  wwNLLcorrections  -d ../../data/ratio_output_nnlo.root  -m powheg  /tmp/amassiro/latino000.root    /tmp/amassiro/latino000_nll.root

    /afs/cern.ch/work/d/dmeister/public/LatinoTrees/NoSkim_genJet_puW_effW_triggW/
    gardener.py  wwNLLcorrections  -d ../../data/ratio_output_nnlo.root  -m powheg    /data/amassiro/LatinosTrees/ww/latino006.root    /data/amassiro/LatinosTrees/ww/latino006_nll.root
    gardener.py  wwNLLcorrections  -d ../../data/ratio_output_nnlo.root  -m madgraph  /data/amassiro/LatinosTrees/ww/latino000.root    /data/amassiro/LatinosTrees/ww/latino000_nll.root
    gardener.py  wwNLLcorrections  -d ../../data/ratio_output_nnlo.root  -m mcatnlo   /data/amassiro/LatinosTrees/ww/latino002.root    /data/amassiro/LatinosTrees/ww/latino002_nll.root





WW+2j
====

mva addition

    gardener.py  wwewkMVAVar  /data/amassiro/LatinosTrees/2jewk/nominals_all/latino_006_WWJets2LPowheg.root       /tmp/amassiro/latino_006_WWJets2LPowheg_new.root
    gardener.py  wwewkMVAVar  /data/amassiro/LatinosTrees/2jewk/nominals_all/latino_052_WW2JetsPhantom.root       /tmp/amassiro/latino_052_WW2JetsPhantom_new.root

    ls --color=none /data/amassiro/LatinosTrees/tree_skim_all_2j_mva/ | awk '{print "gardener.py  wwewkMVAVar -r  -F  /data/amassiro/LatinosTrees/tree_skim_all_2j_mva/"$1"  /data/amassiro/LatinosTrees/tree_skim_all_2j_mva_new/"$1   }'




ww invariant mass for Higgs width
====

mva addition

    gardener.py  higgsWWVar  /tmp/amassiro/latinogg2vv_Hw1_SigOnPeak_8TeV.root     /tmp/amassiro/latinogg2vv_Hw1_SigOnPeak_8TeV_mww.root

    gardener.py  higgsWWVar -r /tmp/amassiro/gg2vv/     /tmp/amassiro/gg2vv_mww/









