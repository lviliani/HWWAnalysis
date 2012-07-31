#!/bin/env python

from tree.gardening    import gardener_cli
from tree.gardening    import ModuleManager,Pruner,Grafter,AliasGrafter,RootWeighter
from tree.pileup       import PUpper
from tree.ww           import WWPruner, WWFlagsGrafter
from tree.efficiencies import EffLepFiller,EffTrgFiller
from tree.susyVar      import SusyVarFiller


if __name__ == '__main__':

    modules = ModuleManager()
    modules['filter']       = Pruner()
    modules['adder']        = Grafter()
    modules['alias']        = AliasGrafter()
    modules['rootweighter'] = RootWeighter()
    modules['wwfilter']     = WWPruner()
    modules['wwflagger']    = WWFlagsGrafter()
    modules['puadder']      = PUpper()
    modules['effwfiller']   = EffLepFiller()
    modules['efftfiller']   = EffTrgFiller()
    modules['susyVar']      = SusyVarFiller()

    gardener_cli( modules )