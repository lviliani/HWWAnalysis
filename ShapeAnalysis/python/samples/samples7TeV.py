import hwwtools
import re


backgrounds = {
    'WW'                      : ['nominals/latino_000_WWJets2LMad.root'],
    'ggWW'                    : ['nominals/latino_001_GluGluToWWTo4L.root'],
    'VgS'                     : ['nominals/latino_085_WGstarToLNu2Mu.root',
                                 'nominals/latino_086_WGstarToLNu2E.root',
                                ],
    'VgS-template'            : ['vgTemplate/latino_082_WGstarToElNuMad.root',
                                 'vgTemplate/latino_083_WGstarToMuNuMad.root',
                                 'vgTemplate/latino_084_WGstarToTauNuMad.root',
                                ],
    'Vg'                      : ['nominals/latino_082_WgammaToElNuMad.root',
                                 'nominals/latino_083_WgammaToMuNuMad.root',
                                 'nominals/latino_084_WgammaToTauNuMad.root',
                                ],
    'Vg-template'             : ['vgTemplate/latino_085_WgammaToLNuG.root'],
    'WJet-2j-fix'                    : ['wjets/WJetsEstimated_Full2011_added.root'],
    'WJetFakeRate-nominal-2j-fix'    : ['vgTemplate/latino_RunA_892pbinv_LooseLoose.root',
                                        'vgTemplate/latino_RunB_4404pbinv_LooseLoose.root',
                                        'vgTemplate/latino_RunC_7032pbinv_LooseLoose.root',
                                        'vgTemplate/latino_RunD_7274pbinv_LooseLoose.root',
                                ],
    'WJet'                    : ['wjets/WJetsEstimated_Full2011_added.root'],
    'WJetFakeRate-nominal'    : ['vgTemplate/latino_RunA_892pbinv_LooseLoose.root',
                                 'vgTemplate/latino_RunB_4404pbinv_LooseLoose.root',
                                 'vgTemplate/latino_RunC_7032pbinv_LooseLoose.root',
                                 'vgTemplate/latino_RunD_7274pbinv_LooseLoose.root',
                                ],
    'WJet-template-2j'        : ['wjetsTemplate/latino_RunA_892pbinv_LooseLoose.root',
                                 'wjetsTemplate/latino_RunB_4404pbinv_LooseLoose.root',
                                 'wjetsTemplate/latino_RunC_6807pbinv_LooseLoose.root',
                                ],
    'WJetFakeRate-template-2j': ['wjetsTemplate/latino_RunA_892pbinv_LooseLoose.root',
                                 'wjetsTemplate/latino_RunB_4404pbinv_LooseLoose.root',
                                 'wjetsTemplate/latino_RunC_6807pbinv_LooseLoose.root',
                                ],
    'Top'                     : ['nominals/latino_011_TtWFullDR.root',
                                 'nominals/latino_012_TbartWFullDR.root',
                                 'nominals/latino_013_TtFull.root',
                                 'nominals/latino_014_TbartFull.root',
                                 'nominals/latino_015_TsFull.root',
                                 'nominals/latino_016_TbarsFull.root',
                                 'nominals/latino_019_TTTo2L2Nu2B.root',
                                ],
    'VV'                      : ['nominals/latino_074_WZJetsMad.root',
                                 'nominals/latino_071_ZZFull.root',
                                ],
    'DYTT'                    : ['nominals/latino_DYtt_2011_added.root'], # for ee/mm channels DYTT is included in DD
    'DYLL'                    : ['nominals/latino_036_DY10toLLMad.root',
                                 'nominals/latino_037_DY50toLLMad.root'
                                ],
    'DYee'                    : ['nominals/latino_000_WWJets2LMad.root',   # dummy, just to have the histogram in cut based
                                ],
    'DYmm'                    : ['nominals/latino_000_WWJets2LMad.root',   # dummy, just to have the histogram in cut based
                                ],
    'DYLL-template-0j1j'      : ['dyTemplate/latino_036_DY10toLLMad.root',
                                 'dyTemplate/latino_037_DY50toLLMad.root',
                                ],
    'DYLL-templatesyst-0j1j'  : ['dyTemplate/latino_036_DY10toLLMad.root',
                                 'dyTemplate/latino_037_DY50toLLMad.root',
                                ],
    'WWnlo'                   : ['nominals/latino_002_WWto2L2NuMCatNLO.root'],
    'WWnloUp'                 : ['nominals/latino_003_WWto2L2NuMCatNLOUp.root'],
    'WWnloDown'               : ['nominals/latino_004_WWto2L2NuMCatNLODown.root'],
    'DYLL-template-dd'        : ['dyTemplate-dd/latino_036_DY10toLLMad.root',
                                 'dyTemplate-dd/latino_037_DY50toLLMad.root',
                                ],
    'DYLL-template-vbf'       : ['dyTemplate/latino_036_DY10toLLMad.root',
                                 'dyTemplate/latino_037_DY50toLLMad.root',
                                ],

#    for 2H model and signal injection
    'ggH_SM'   : ['nominals/latino_9125_ggToH125toWWTo2LAndTau2Nu.root',
                ],
    'qqH_SM'   : ['nominals/latino_8125_vbfToH125toWWTo2LAndTau2Nu.root',
                ],
    'wzttH_SM' : ['nominals/latino_7125_wzttH125ToWW.root'],
    'VH_SM'    : ['nominals/latino_7125_wzttH125ToWW.root'],

}

data = {
    'Data2011A' : ['data/latino_150_SingleElectron2011AMay10.root',
                   'data/latino_151_SingleMuon2011AMay10.root',
                   'data/latino_152_DoubleMuon2011AMay10.root',
                   'data/latino_153_DoubleElectron2011AMay10.root',
                   'data/latino_154_MuEG2011AMay10.root',

                   'data/latino_100_SingleElectron2011Av4.root',
                   'data/latino_101_SingleMuon2011Av4.root',
                   'data/latino_102_DoubleElectron2011Av4.root',
                   'data/latino_103_DoubleMuon2011Av4.root',
                   'data/latino_104_MuEG2011Av4.root',

                   'data/latino_160_SingleElectron2011AAug05.root',
                   'data/latino_161_SingleMuon2011AAug05.root',
                   'data/latino_162_DoubleElectron2011AAug05.root',
                   'data/latino_163_DoubleMuon2011AAug05.root',
                   'data/latino_164_MuEG2011AAug05.root',

                   'data/latino_120_SingleElectron2011Av6.root',
                   'data/latino_121_SingleMuon2011Av6.root',
                   'data/latino_122_DoubleElectron2011Av6.root',
                   'data/latino_123_DoubleMuon2011Av6.root',
                   'data/latino_124_MuEG2011Av6.root',
                  ],

    'Data2011B'  :['data/latino_140_SingleElectron2011Bv1a.root',
                   'data/latino_141_SingleMuon2011Bv1a.root',
                   'data/latino_142_DoubleElectron2011Bv1a.root',
                   'data/latino_143_DoubleMuon2011Bv1a.root',
                   'data/latino_144_MuEG2011Bv1a.root',
                  ],

}

#data['Data2012'] = data['Data2012A']+data['Data2012B']+data['Data2012C']+data['Data2012D']
data['Data2011'] = data['Data2011A']+data['Data2011B']

#--------------
# signal samples labels and generation

def signalSamples(sigtag,mass=125,suffix=''):

    # get closer mass
    # FIXME: temporary fix
    if int(mass) == 125:
      mass = 126

    signals = {}

    # some preliminary definitions
    std_ggH      = ['nominals/latino_9125_ggToH125toWWTo2LAndTau2Nu.root']
    std_qqH      = ['nominals/latino_8125_vbfToH125toWWTo2LAndTau2Nu.root']
    std_wzttH    = ['nominals/latino_7125_wzttH125ToWW.root']
    std_VH       = ['nominals/latino_7125_wzttH125ToWW.root']

    jhu_ggSM     = ['nominals/latino_13001_SMH125ToWW2L2Nu.root',
                    'nominals/latino_13004_SMH125ToWW2Tau2Nu.root',
                    'nominals/latino_13007_SMH125ToWWLTau2Nu.root'
                   ]
    jhu_ggHiggs0M= ['nominals/latino_13002_Higgs0M125ToWW2L2Nu.root',
                    'nominals/latino_13005_Higgs0M125ToWW2Tau2Nu.root', 
                    'nominals/latino_13008_Higgs0M125ToWWLTau2Nu.root' 
                   ]

    jhu_ggGrav2PM= ['nominals/latino_13003_Graviton2PM2L2Nu.root',
                    'nominals/latino_13006_Graviton2PMToWW2Tau2Nu.root',
                    'nominals/latino_13009_Graviton2PMToWWLTau2Nu.root'
                   ]

    jhu_qqGrav2PM= ['nominals/latino_13010_Graviton2PMqqbarToWW2L2Nu.root',
                    'nominals/latino_13011_Graviton2PMqqbarToWW2Tau2Nu.root',
                    'nominals/latino_13012_Graviton2PMqqbarToWWLTau2Nu.root'
                   ]



    # for higgs width
    ggH_sbi      = [
                    #'nominals/latino_260_ggww1smSBI000140.root', --> only off-shell must be considered
                    'nominals/latino_263_ggww1smSBI140300.root',
                    'nominals/latino_266_ggww1smSBI300.root'
                   ]
    ggH_b        = [
                    'nominals/latino_270_ggwwB000300.root',
                    'nominals/latino_271_ggwwB300.root'
                   ]
    ggH_s        = [
                     #'nominals/latino_250_ggww1sm000140.root',-> only off-shell must be considered
                     'nominals/latino_253_ggww1sm140300.root',
                     'nominals/latino_256_ggww1sm300.root',
                   ]

    qqH_sbi      = ['nominals/latino_272_qqww1smTM.root',
                    'nominals/latino_275_qqww1smTE.root',
                    'nominals/latino_278_qqww1smTT.root',
                    'nominals/latino_281_qqww1smEM.root',
                    'nominals/latino_284_qqww1smEE.root',
                    'nominals/latino_287_qqww1smMM.root',
                   ]
    qqH_b        = ['nominals/latino_272_qqww1smTM.root',
                    'nominals/latino_275_qqww1smTE.root',
                    'nominals/latino_278_qqww1smTT.root',
                    'nominals/latino_281_qqww1smEM.root',
                    #'nominals/latino_284_qqww1smEE.root',
                    #'nominals/latino_287_qqww1smMM.root',

                    'nominals/latino_273_qqww9smTM.root',
                    'nominals/latino_276_qqww9smTE.root',
                    'nominals/latino_279_qqww9smTT.root',
                    'nominals/latino_282_qqww9smEM.root',
                    #'nominals/latino_285_qqww9smEE.root',
                    #'nominals/latino_288_qqww9smMM.root',

                    'nominals/latino_274_qqww25smTM.root',
                    'nominals/latino_277_qqww25smTE.root',
                    'nominals/latino_280_qqww25smTT.root',
                    'nominals/latino_283_qqww25smEM.root',
                    #'nominals/latino_286_qqww25smEE.root',
                    #'nominals/latino_289_qqww25smMM.root',
                   ]
    qqH_s        = ['nominals/latino_272_qqww1smTM.root',
                    'nominals/latino_275_qqww1smTE.root',
                    'nominals/latino_278_qqww1smTT.root',
                    'nominals/latino_281_qqww1smEM.root',
                    #'nominals/latino_284_qqww1smEE.root',
                    #'nominals/latino_287_qqww1smMM.root',

                    'nominals/latino_273_qqww9smTM.root',
                    'nominals/latino_276_qqww9smTE.root',
                    'nominals/latino_279_qqww9smTT.root',
                    'nominals/latino_282_qqww9smEM.root',
                    #'nominals/latino_285_qqww9smEE.root',
                    #'nominals/latino_288_qqww9smMM.root',

                    'nominals/latino_274_qqww25smTM.root',
                    'nominals/latino_277_qqww25smTE.root',
                    'nominals/latino_280_qqww25smTT.root',
                    'nominals/latino_283_qqww25smEM.root',
                    #'nominals/latino_286_qqww25smEE.root',
                    #'nominals/latino_289_qqww25smMM.root',
                   ]





    if sigtag == 'SM' or sigtag == 'Hwidth' :
        ggH = ['nominals/latino_1{mass}_ggToH{mass}toWWto2L2Nu.root',
               'nominals/latino_2{mass}_ggToH{mass}toWWtoLNuTauNu.root',
               'nominals/latino_3{mass}_ggToH{mass}toWWto2Tau2Nu.root',
              ]
        ggHnew = ['nominals/latino_9{mass}_ggToH{mass}toWWTo2LAndTau2Nu.root']
        qqH    = ['nominals/latino_4{mass}_vbfToH{mass}toWWto2L2Nu.root',
                  'nominals/latino_5{mass}_vbfToH{mass}toWWtoLNuTauNu.root',
                  'nominals/latino_6{mass}_vbfToH{mass}toWWto2Tau2Nu.root',
                 ]
        qqHnew  = ['nominals/latino_8{mass}_vbfToH{mass}toWWTo2LAndTau2Nu.root']
        wzttH   = ['nominals/latino_7{mass}_wzttH{mass}ToWW.root']
        VH      = ['nominals/latino_7{mass}_wzttH{mass}ToWW.root']
        WH      = ['nominals/latino_7{mass}_wzttH{mass}ToWW.root']
        ZH      = ['nominals/latino_7{mass}_wzttH{mass}ToWW.root']
        ttH     = ['nominals/latino_7{mass}_wzttH{mass}ToWW.root']

        if mass <= 300:
          if (mass != 110) and (mass != 115) :
            signals['wzttH'+suffix] = [f.format(mass = mass) for f in wzttH]
            signals['VH'+suffix]    = [f.format(mass = mass) for f in VH]
            #signals['WH'+suffix]    = [f.format(mass = mass) for f in WH]
            #signals['ZH'+suffix]    = [f.format(mass = mass) for f in ZH]
            #signals['ttH'+suffix]   = [f.format(mass = mass) for f in ttH]
          else :
            signals['wzttH'+suffix]  = ['nominals/latino_3{mass}_wzttH{mass}ToWW.root'.format(mass = mass)]
            signals['VH'+suffix]     = ['nominals/latino_3{mass}_wzttH{mass}ToWW.root'.format(mass = mass)]
            #signals['WH'+suffix]     = ['nominals/latino_3{mass}_wzttH{mass}ToWW.root'.format(mass = mass)]
            #signals['ZH'+suffix]     = ['nominals/latino_3{mass}_wzttH{mass}ToWW.root'.format(mass = mass)]
            #signals['ttH'+suffix]    = ['nominals/latino_3{mass}_wzttH{mass}ToWW.root'.format(mass = mass)]

        if int(mass)==122:
            signals['ggH'+suffix]   = [f.format(mass = mass) for f in ggHnew]
            signals['wzttH'+suffix] = [f.format(mass = mass) for f in wzttH]
        elif int(mass)==118 or (int(mass)>120 and int(mass)<130) or int(mass)==135:
            signals['ggH'+suffix]   = [f.format(mass = mass) for f in ggHnew]
            signals['qqH'+suffix]   = [f.format(mass = mass) for f in qqHnew]
        elif int(mass) > 115:
            signals['ggH'+suffix]   = [f.format(mass = mass) for f in ggH]
            signals['qqH'+suffix]   = [f.format(mass = mass) for f in qqH]
        else:
            signals['ggH'+suffix]  = ['nominals/latino_9{mass}_ggToH{mass}toWWTo2LAndTau2Nu.root'.format(mass = mass)]
            signals['qqH'+suffix]  = ['nominals/latino_8{mass}_vbfToH{mass}toWWTo2LAndTau2Nu.root'.format(mass = mass)]



        if sigtag == 'Hwidth' :
            signals['ggH_sbi'] = ggH_sbi
            signals['ggH_s']   = ggH_s
            signals['ggH_b']   = ggH_b
            signals['qqH_sbi'] = qqH_sbi
            signals['qqH_s']   = qqH_s
            signals['qqH_b']   = qqH_b


# and the JHU case:

    elif sigtag == 'Grav2PM' and mass==125:

        signals['ggH']     = std_ggH
        signals['qqH']     = std_qqH
        signals['wzttH']   = std_wzttH
               
        signals['ggH_ALT'] = jhu_ggGrav2PM
        signals['qqH_ALT'] = jhu_qqGrav2PM
        signals['jhu_NORM']= std_ggH

    elif sigtag == 'Higgs0M' and mass==125:

        signals['ggH']     = std_ggH
        signals['qqH']     = std_qqH
        signals['wzttH']   = std_wzttH
               
        signals['ggH_ALT'] = jhu_ggHiggs0M
        signals['jhu_NORM']= std_ggH
            
# some old stuff (kept for reference & commented out)
#    elif sigtag == 'JHUSMONLY' and mass==125:
#
#        signals['jhu']     = jhu_ggSM
#        signals['jhu_NORM']= std_ggH
#
#    elif sigtag == 'JHU0MONLY' and mass==125:
#
#        signals['jhu']     = jhu_ggHiggs0M
#        signals['jhu_NORM']= std_ggH
#
#    elif sigtag == 'JHU2MONLY' and mass==125:
#        signals['jhu']     = jhu_ggGrav2PM
#        signals['jhu_NORM']= std_ggH
#
#    elif sigtag == 'JHUSMvs0M' and mass==125:
#        signals['jhu']     = jhu_ggSM
#        signals['jhu_ALT'] = jhu_ggHiggs0M
#        signals['jhu_NORM']= std_ggH
#
#    elif sigtag == 'JHUSMvs2M' and mass==125:
#
#        signals['jhu']      = jhu_ggSM
#        signals['jhu_ALT']  = jhu_ggGrav2PM
#        signals['jhu_NORM'] = std_ggH
#        signals['jhu_NLO']  = std_ggH
#
#    elif sigtag == 'JHUSMvs2MnoNLO' and mass==125:
#
#        signals['jhu']     = jhu_ggSM
#        signals['jhu_ALT'] = jhu_ggGrav2PM
#        signals['jhu_NORM']= std_ggH
#
#    elif sigtag == 'PWGSMvs2M' and mass==125:
#
#        signals['jhu']      = std_ggH
#        signals['jhu_ALT']  = jhu_ggGrav2PM
#        signals['jhu_NORM'] = std_ggH
#        signals['jhu_NLO']  = std_ggH 
#
#    elif sigtag == 'PWGSMvs2MnoNLO' and mass==125:
#
#        signals['jhu']     = std_ggH
#        signals['jhu_ALT'] = jhu_ggGrav2PM
#        signals['jhu_NORM']= std_ggH
#
#    elif sigtag == 'JHUSMvs2MplOthers' and mass==125:
#
#        signals['jhu']     = jhu_ggSM
#        signals['vbfH']    = std_vbf
#        signals['wzttH']   = std_wzttH
#
#        signals['jhu_ALT'] = jhu_ggGrav2PM
#        signals['vbfH_ALT'] = std_vbf
#        signals['wzttH_ALT']= std_wzttH
#        signals['jhu_NORM']= std_ggH
#
#    elif sigtag == 'PWGSMqqHwzttHvs2MnoNLO' and mass==125:
#
#        signals['jhu']     = std_ggH
#        signals['vbfH']    = std_vbf
#        signals['wzttH']   = std_wzttH
#               
#        signals['jhu_ALT'] = jhu_ggGrav2PM
#        #signals['vbfH_ALT'] = std_vbf
#        #signals['wzttH_ALT']= std_wzttH
#        signals['jhu_NORM']= std_ggH
#
#    elif sigtag == 'PWGSMqqHwzttHvs0MnoNLO' and mass==125:
#
#        signals['jhu']     = std_ggH
#        signals['vbfH']    = std_vbf
#        signals['wzttH']   = std_wzttH
#
#        signals['jhu_ALT'] = jhu_ggHiggs0M
#
#        signals['jhu_NORM']= std_ggH

    else:
        raise ValueError('Signal tag %s not found for mass %d' % (sigtag,mass) )
    return signals

