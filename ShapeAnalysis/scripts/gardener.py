#!/bin/env python



from tree.gardening         import gardener_cli
from tree.gardening         import ModuleManager,Pruner,Grafter,AliasGrafter,RootWeighter
from tree.pileup            import PUpper
from tree.ww                import WWPruner, WWFlagsGrafter
from tree.efficiencies      import EffLepFiller,EffTrgFiller
from tree.susyVar           import SusyVarFiller
from tree.mTVar             import MTVarFiller
from tree.ChessVariable     import ChessVarGrafter
from tree.unBoostedVar      import UnBoostedVarFiller
from tree.WobblyBinVariable import WobblyBinVarGrafter
from tree.likelihoodQGVar   import likelihoodQGVarFiller
from tree.susyVar2B2LMET    import SusyVar2B2LMETFiller
from tree.dymvaVar          import DymvaVarFiller
from tree.xyShift           import XYShiftVarFiller
from tree.higgsLineShape    import HiggsLineshapeWeightAdder
from tree.jetHiggsVar       import JetHiggsVarFiller
# from tree.vbfMVAVar         import VbfMVAVarFiller
from tree.wwewkMVAVar       import WWewkMVAVarFiller
from tree.manyJetsHiggsVar  import ManyJetsHiggsVarFiller
from tree.wwGenInfo         import WWGenFiller
from tree.higgsCPS          import HiggsCPSWeightAdder
from tree.fakeW             import FakeWVarFiller
from tree.ZHWWlvlvVar       import ZhwwlvlvVarFiller
from tree.WW2jVar           import WW2jVarFiller
from tree.leptonTypeVar     import LeptonTypeVarFiller

from tree.qq2vvEWKcorrectionsWeight       import qq2vvEWKcorrectionsWeightFiller
from tree.wwNLLcorrectionWeight           import wwNLLcorrectionWeightFiller
from tree.higgsWWVar        import higgsWWVarFiller




if __name__ == '__main__':


    modules = ModuleManager()
    modules['filter']           = Pruner()
    modules['adder']            = Grafter()
    modules['alias']            = AliasGrafter()
    modules['rootweighter']     = RootWeighter()
    modules['wwfilter']         = WWPruner()
    modules['wwflagger']        = WWFlagsGrafter()
    modules['puadder']          = PUpper()
    modules['effwfiller']       = EffLepFiller()
    modules['efftfiller']       = EffTrgFiller()
    modules['susyVar']          = SusyVarFiller()
    modules['mTVar']            = MTVarFiller()
    modules['chessVar']         = ChessVarGrafter()
    modules['unBoostedVar']     = UnBoostedVarFiller()
    modules['WobblyBinVar']     = WobblyBinVarGrafter()
    modules['likelihoodQGVar']  = likelihoodQGVarFiller()
    modules['susyVar2B2LMET']   = SusyVar2B2LMETFiller()
    modules['dymvaVar']         = DymvaVarFiller()
    modules['xyShift']          = XYShiftVarFiller()
    modules['higgsLS']          = HiggsLineshapeWeightAdder()
    modules['jetHiggsVar']      = JetHiggsVarFiller()
#     modules['vbfMVAVar']        = VbfMVAVarFiller()
    modules['wwewkMVAVar']      = WWewkMVAVarFiller()
    modules['manyJetsHiggsVar'] = ManyJetsHiggsVarFiller()
    modules['wwGenInfo']        = WWGenFiller()
    modules['higgsCPS']         = HiggsCPSWeightAdder()

# Fake backgroud
    modules['fakeW']            =  FakeWVarFiller()
# zhwwlvlv
    modules['zhwwlvlvVar']      =  ZhwwlvlvVarFiller()
# add if a lepton pass/fail id+iso
    modules['leptonTypeVar']    =  LeptonTypeVarFiller()
# add electroweak corrections for ww
    modules['qq2vvEWKcorrections']      =  qq2vvEWKcorrectionsWeightFiller()
# ww2j
    modules['ww2jVar']          =  WW2jVarFiller()
# add nll re-weight for ww
    modules['wwNLLcorrections']      =  wwNLLcorrectionWeightFiller()
# ww invariant mass -> for Higgs width
    modules['higgsWWVar']          =  higgsWWVarFiller()

    gardener_cli( modules )




