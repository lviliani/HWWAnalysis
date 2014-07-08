Examples
====

Scale and smear trees
====

    scaleAndSmearTree.py



## Example:

    source test/env.sh

    ./scaleAndSmearTree.py -i H140_ll.root -o blu/bla/bli.root -t latino -a leptonEfficiency -d down
    scaleAndSmearTree.py -a jetEnergyResolution   -i   /home/amassiro/Latinos/Shape/tree_skim_all/nominals/latino_8004_SMH125ToWW2Tau2Nu.root   -o test.root
    scaleAndSmearTree.py -a jetEnergyResolution   -i   /home/amassiro/Latinos/Shape/tree_skim_all/nominals/latino_8004_SMH125ToWW2Tau2Nu.root   -o test.root   --variation="up"
    scaleAndSmearTree.py -a jetEnergyResolution   -i   /home/amassiro/Latinos/Shape/tree_skim_all/nominals/latino_8004_SMH125ToWW2Tau2Nu.root   -o test.root   --variation="down"


## auto:

    ls --color=none nominals/ | grep .root | awk '{print "scaleAndSmearTree.py -i nominals/"$1" -o jetEnergyScale_up/"$1"    -a jetEnergyScale -v up"}'  | /bin/sh
    ls --color=none nominals/ | grep .root | awk '{print "scaleAndSmearTree.py -i nominals/"$1" -o jetEnergyScale_down/"$1"  -a jetEnergyScale -v down"}'| /bin/sh

    ls --color=none nominals/ | grep .root | awk '{print "scaleAndSmearTree.py -i nominals/"$1" -o electronScale_up/"$1"    -a electronScale -v up"}'| /bin/sh
    ls --color=none nominals/ | grep .root | awk '{print "scaleAndSmearTree.py -i nominals/"$1" -o electronScale_down/"$1"  -a electronScale -v down"}'| /bin/sh

    ls --color=none nominals/ | grep .root | awk '{print "scaleAndSmearTree.py -i nominals/"$1" -o muonScale_up/"$1"    -a muonScale -v up"}'| /bin/sh
    ls --color=none nominals/ | grep .root | awk '{print "scaleAndSmearTree.py -i nominals/"$1" -o muonScale_down/"$1"  -a muonScale -v down"}'| /bin/sh

    ls --color=none nominals/ | grep .root | awk '{print "scaleAndSmearTree.py -i nominals/"$1" -o metResolution/"$1"         -a metResolution"}'| /bin/sh
    ls --color=none nominals/ | grep .root | awk '{print "scaleAndSmearTree.py -i nominals/"$1" -o electronResolution/"$1"    -a electronResolution"}'| /bin/sh




