import hwwtools
import re


signals = ['ggH',
           'ggHBin0','ggHBin1','ggHBin2','ggHBin3','ggHBin4','ggHBin5', 
           'ggHFidBin0','ggHFidBin1','ggHFidBin2','ggHFidBin3','ggHFidBin4','ggHFidBin5', 
           'ggHFidRecBin0','ggHFidRecBin1','ggHFidRecBin2','ggHFidRecBin3','ggHFidRecBin4','ggHFidRecBin5', 
           'qqH',
           'qqHBin0','qqHBin1','qqHBin2','qqHBin3','qqHBin4','qqHBin5', 
           'qqHFidBin0','qqHFidBin1','qqHFidBin2','qqHFidBin3','qqHFidBin4','qqHFidBin5', 
           'qqHFidRecBin0','qqHFidRecBin1','qqHFidRecBin2','qqHFidRecBin3','qqHFidRecBin4','qqHFidRecBin5', 
           'wzttH','ggH_ALT','qqH_ALT',
           'WH',
           'WHBin0','WHBin1','WHBin2','WHBin3','WHBin4','WHBin5',
           'WHFidBin0','WHFidBin1','WHFidBin2','WHFidBin3','WHFidBin4','WHFidBin5',
           'WHFidRecBin0','WHFidRecBin1','WHFidRecBin2','WHFidRecBin3','WHFidRecBin4','WHFidRecBin5',
           'ZH',
           'ZHBin0','ZHBin1','ZHBin2','ZHBin3','ZHBin4','ZHBin5',
           'ZHFidBin0','ZHFidBin1','ZHFidBin2','ZHFidBin3','ZHFidBin4','ZHFidBin5',
           'ZHFidRecBin0','ZHFidRecBin1','ZHFidRecBin2','ZHFidRecBin3','ZHFidRecBin4','ZHFidRecBin5',
           'ttH','VH']


#--------------
# mcsets,
# list of samples and compact dictionary
#
# filter the list of samples
# and create association     label          -> label                  -> vector of root files
#                       used by mkShapes      just for association       blabla.root
#

mcsets = {
    '0j1j-JHU' : [
        #signals
        'ggH','ggH_ALT','jhu_NORM','jhu_NLO',
        # bkgs
        'WW','ggWW','VgS','Vg','WJet','Top','VV','VVV','DYTT','DYLL','WWnlo','WWnloUp','WWnloDown',
        # systematics
        'WJetFakeRate-nominal',
        ('WJetFakeRate-eUp', 'WJetFakeRate-nominal'),
        ('WJetFakeRate-eDn', 'WJetFakeRate-nominal'),
        ('WJetFakeRate-mUp', 'WJetFakeRate-nominal'),
        ('WJetFakeRate-mDn', 'WJetFakeRate-nominal'),
        ('TopTW',   'Top'),
        ('TopCtrl', 'Top'),
        # templates
        'VgS-template', 'Vg-template',
        # 0j1j specific
        ('DYLL-template',    'DYLL-template-0j1j'),              #    A   <-   sorgente
        ('DYLL-templatesyst','DYLL-templatesyst-0j1j')           #    mkmerged vuole "-template"
    ],
    '0j1j-JHUOthers' : [
        #signals
        'ggH','ggH_ALT','jhu_NORM','jhu_NLO','qqH','qqH_ALT','wzttH',
        # bkgs
        'WW','ggWW','VgS','Vg','WJet','Top','VV','VVV','DYTT','DYLL','WWnlo','WWnloUp','WWnloDown',
        # systematics
        'WJetFakeRate-nominal',
        ('WJetFakeRate-eUp', 'WJetFakeRate-nominal'),
        ('WJetFakeRate-eDn', 'WJetFakeRate-nominal'),
        ('WJetFakeRate-mUp', 'WJetFakeRate-nominal'),
        ('WJetFakeRate-mDn', 'WJetFakeRate-nominal'),
        ('TopTW',   'Top'),
        ('TopCtrl', 'Top'),
        # templates
        'VgS-template','Vg-template',
        # 0j1j specific
        ('DYLL-template',    'DYLL-template-0j1j'),              #    A   <-   sorgente
        ('DYLL-templatesyst','DYLL-templatesyst-0j1j')           #    mkmerged vuole "-template"
    ],
    '0j1j' : [
        #signals
        'ggH','qqH','WH','ZH',
        # bkgs
        'WW','ggWW','VgS','Vg','WJet','Top','VV','VVV','DYTT','WWnlo','WWnloUp','WWnloDown',
        ('DYLL','ggH'),
        # systematics
        'WJetFakeRate-nominal',
        ('WJetFakeRate-eUp', 'WJetFakeRate-nominal'),
        ('WJetFakeRate-eDn', 'WJetFakeRate-nominal'),
        ('WJetFakeRate-mUp', 'WJetFakeRate-nominal'),
        ('WJetFakeRate-mDn', 'WJetFakeRate-nominal'),
        ('TopTW',   'Top'),
        ('TopCtrl', 'Top'),
        # templates
        'VgS-template','Vg-template',
        # 0j1j specific
        #('DYLL-template',    'DYLL-template-0j1j'),              #    A   <-   sorgente
        #('DYLL-templatesyst','DYLL-templatesyst-0j1j')           #    mkmerged vuole "-template"
    ],

    '0j1j-differential' : [
        #signals
#        ('sigSMBin0', 'sigSM'),
#        ('sigSMBin1', 'sigSM'),
#        ('sigSMBin2', 'sigSM'),
#        ('sigSMBin3', 'sigSM'),
#        ('sigSMBin4', 'sigSM'),
#        ('sigSMBin5', 'sigSM'),
	 ('ggHBin0','ggH'),
         ('ggHBin1','ggH'),
         ('ggHBin2','ggH'),
         ('ggHBin3','ggH'),
         ('ggHBin4','ggH'),
         ('ggHBin5','ggH'),
         ('qqHBin0','qqH'),
         ('qqHBin1','qqH'),
         ('qqHBin2','qqH'),
         ('qqHBin3','qqH'),
         ('qqHBin4','qqH'),
         ('qqHBin5','qqH'),
         ('WHBin0','WH'),
         ('WHBin1','WH'),
         ('WHBin2','WH'),
         ('WHBin3','WH'),
         ('WHBin4','WH'),
         ('WHBin5','WH'),
         ('ZHBin0','ZH'),
         ('ZHBin1','ZH'),
         ('ZHBin2','ZH'),
         ('ZHBin3','ZH'),
         ('ZHBin4','ZH'),
         ('ZHBin5','ZH'),

        # bkgs
         'WW','ggWW','VgS','Vg','WJet','VV','VVV','DYTT','WWnlo','WWnloUp','WWnloDown',
         ('DYLL','ggH'),
         # systematics
         'WJetFakeRate-nominal',
         ('WJetFakeRate-eUp', 'WJetFakeRate-nominal'),
         ('WJetFakeRate-eDn', 'WJetFakeRate-nominal'),
         ('WJetFakeRate-mUp', 'WJetFakeRate-nominal'),
         ('WJetFakeRate-mDn', 'WJetFakeRate-nominal'),
         ('TopTW',   'Top'),
         ('Top0jet',   'Top'),
         ('Topge1jet',   'Top'),
         #('Topge1jetUp',   'Top'),
         #('Topge1jetDown',   'Top'),
         ('TopCtrl', 'Top'),
         # templates
         'VgS-template','Vg-template',
         # 0j1j specific
         #('DYLL-template',    'DYLL-template-0j1j'),              #    A   <-   sorgente
         #('DYLL-templatesyst','DYLL-templatesyst-0j1j')           #    mkmerged vuole "-template"
         #('CHITOP-Top0jet','Top')
     ],

      '0j1j-differential2' : [
        #signals
#        ('sigSMBin0', 'sigSM'),
#        ('sigSMBin1', 'sigSM'),
#        ('sigSMBin2', 'sigSM'),
#        ('sigSMBin3', 'sigSM'),
#        ('sigSMBin4', 'sigSM'),
#        ('sigSMBin5', 'sigSM'),
         ('ggHBin0','ggH'),
         ('ggHBin1','ggH'),
         ('ggHBin2','ggH'),
         ('ggHBin3','ggH'),
         ('ggHBin4','ggH'),
         ('ggHBin5','ggH'),
         ('qqHBin0','qqH'),
         ('qqHBin1','qqH'),
         ('qqHBin2','qqH'),
         ('qqHBin3','qqH'),
         ('qqHBin4','qqH'),
         ('qqHBin5','qqH'),
         ('WHBin0','WH'),
         ('WHBin1','WH'),
         ('WHBin2','WH'),
         ('WHBin3','WH'),
         ('WHBin4','WH'),
         ('WHBin5','WH'),
         ('ZHBin0','ZH'),
         ('ZHBin1','ZH'),
         ('ZHBin2','ZH'),
         ('ZHBin3','ZH'),
         ('ZHBin4','ZH'),
         ('ZHBin5','ZH'),

        # bkgs
         ('WWBin0', 'WW'), 
         ('WWBin1', 'WW'), 
         ('WWBin2', 'WW'), 
         ('WWBin3', 'WW'), 
         ('WWBin4', 'WW'), 
         ('WWBin5', 'WW'), 
        

         'ggWW','VgS','Vg','WJet','VV','VVV','DYTT','WWnlo','WWnloUp','WWnloDown',
         ('DYLL','ggH'),
         # systematics
         'WJetFakeRate-nominal',
         ('WJetFakeRate-eUp', 'WJetFakeRate-nominal'),
         ('WJetFakeRate-eDn', 'WJetFakeRate-nominal'),
         ('WJetFakeRate-mUp', 'WJetFakeRate-nominal'),
         ('WJetFakeRate-mDn', 'WJetFakeRate-nominal'),
         ('TopTW',   'Top'),
         ('Top0jet',   'Top'),
         ('Topge1jet',   'Top'),
         #('Top0jet_nowe',   'Top'),
         #('Topge1jet_nowe',   'Top'),


         ('TopCtrl', 'Top'),
         # templates
         'VgS-template','Vg-template',
     ],
      '0j1j-differential3' : [
        #signals
#        ('sigSMBin0', 'sigSM'),
#        ('sigSMBin1', 'sigSM'),
#        ('sigSMBin2', 'sigSM'),
#        ('sigSMBin3', 'sigSM'),
#        ('sigSMBin4', 'sigSM'),
#        ('sigSMBin5', 'sigSM'),
         ('ggHBin0','ggH'),
         ('ggHBin1','ggH'),
         ('ggHBin2','ggH'),
         ('ggHBin3','ggH'),
         ('ggHBin4','ggH'),
         ('ggHBin5','ggH'),
         ('qqHBin0','qqH'),
         ('qqHBin1','qqH'),
         ('qqHBin2','qqH'),
         ('qqHBin3','qqH'),
         ('qqHBin4','qqH'),
         ('qqHBin5','qqH'),
         ('WHBin0','WH'),
         ('WHBin1','WH'),
         ('WHBin2','WH'),
         ('WHBin3','WH'),
         ('WHBin4','WH'),
         ('WHBin5','WH'),
         ('ZHBin0','ZH'),
         ('ZHBin1','ZH'),
         ('ZHBin2','ZH'),
         ('ZHBin3','ZH'),
         ('ZHBin4','ZH'),
         ('ZHBin5','ZH'),

        # bkgs
         ('WWBin0', 'WW'),
         ('WWBin1', 'WW'),
         ('WWBin2', 'WW'),
         ('WWBin3', 'WW'),
         ('WWBin4', 'WW'),
         ('WWBin5', 'WW'),
	 ('WWnloBin0', 'WWnlo'),
	 ('WWnloBin1', 'WWnlo'), 
	 ('WWnloBin2', 'WWnlo'),
	 ('WWnloBin3', 'WWnlo'), 
	 ('WWnloBin4', 'WWnlo'),
	 ('WWnloBin5', 'WWnlo'),
         ('WWnloUpBin0', 'WWnloUp'),
         ('WWnloUpBin1', 'WWnloUp'),
         ('WWnloUpBin2', 'WWnloUp'), 
         ('WWnloUpBin3', 'WWnloUp'), 
         ('WWnloUpBin4', 'WWnloUp'), 
         ('WWnloUpBin5', 'WWnloUp'),
         ('WWnloDownBin0', 'WWnloDown'),
         ('WWnloDownBin1', 'WWnloDown'),
         ('WWnloDownBin2', 'WWnloDown'), 
         ('WWnloDownBin3', 'WWnloDown'), 
         ('WWnloDownBin4', 'WWnloDown'), 
         ('WWnloDownBin5', 'WWnloDown'),
	
         'ggWW','VgS','Vg','WJet','VV','VVV','DYTT','WWnlo','WWnloUp','WWnloDown',
         ('DYLL','ggH'),
         # systematics
         'WJetFakeRate-nominal',
         ('WJetFakeRate-eUp', 'WJetFakeRate-nominal'),
         ('WJetFakeRate-eDn', 'WJetFakeRate-nominal'),
         ('WJetFakeRate-mUp', 'WJetFakeRate-nominal'),
         ('WJetFakeRate-mDn', 'WJetFakeRate-nominal'),
         ('TopTWge1jetBin0',   'Top'),
         ('TopTWge1jetBin1',   'Top'),
         ('TopTWge1jetBin2',   'Top'),
         ('TopTWge1jetBin3',   'Top'),
         ('TopTWge1jetBin4',   'Top'),
         ('TopTWge1jetBin5',   'Top'),
         ('TopTW0jet',   'Top'),
         ('Top0jet',   'Top'),
         ('Topge1jetBin0',   'Top'),
         ('Topge1jetBin1',   'Top'),
         ('Topge1jetBin2',   'Top'),
         ('Topge1jetBin3',   'Top'),
         ('Topge1jetBin4',   'Top'),
         ('Topge1jetBin5',   'Top'),

         #('Top0jet_nowe',   'Top'),
         #('Topge1jet_nowe',   'Top'),


         ('TopCtrl', 'Top'),
         # templates
         'VgS-template','Vg-template',
     ],
     '0j1j-differential4' : [
        #signals
#        ('sigSMBin0', 'sigSM'),
#        ('sigSMBin1', 'sigSM'),
#        ('sigSMBin2', 'sigSM'),
#        ('sigSMBin3', 'sigSM'),
#        ('sigSMBin4', 'sigSM'),
#        ('sigSMBin5', 'sigSM'),
         ('ggHFidRecBin0','ggH'),
         ('ggHFidRecBin1','ggH'),
         ('ggHFidRecBin2','ggH'),
         ('ggHFidRecBin3','ggH'),
         ('ggHFidRecBin4','ggH'),
         ('ggHFidRecBin5','ggH'),
         ('qqHFidRecBin0','qqH'),
         ('qqHFidRecBin1','qqH'),
         ('qqHFidRecBin2','qqH'),
         ('qqHFidRecBin3','qqH'),
         ('qqHFidRecBin4','qqH'),
         ('qqHFidRecBin5','qqH'),
         ('WHFidRecBin0','WH'),
         ('WHFidRecBin1','WH'),
         ('WHFidRecBin2','WH'),
         ('WHFidRecBin3','WH'),
         ('WHFidRecBin4','WH'),
         ('WHFidRecBin5','WH'),
         ('ZHFidRecBin0','ZH'),
         ('ZHFidRecBin1','ZH'),
         ('ZHFidRecBin2','ZH'),
         ('ZHFidRecBin3','ZH'),
         ('ZHFidRecBin4','ZH'),
         ('ZHFidRecBin5','ZH'),

        # bkgs
         ("ggHNonFid", "ggH"),
         ("qqHNonFid", "qqH"),
         ("WHNonFid", "WH"),
         ("ZHNonFid", "ZH"),
         
         ('WWBin0', 'WW'),
         ('WWBin1', 'WW'),
         ('WWBin2', 'WW'),
         ('WWBin3', 'WW'),
         ('WWBin4', 'WW'),
         ('WWBin5', 'WW'),


         'ggWW','VgS','Vg','WJet','VV','VVV','DYTT','WWnlo','WWnloUp','WWnloDown',
         ('DYLL','ggH'),
         # systematics
         'WJetFakeRate-nominal',
         ('WJetFakeRate-eUp', 'WJetFakeRate-nominal'),
         ('WJetFakeRate-eDn', 'WJetFakeRate-nominal'),
         ('WJetFakeRate-mUp', 'WJetFakeRate-nominal'),
         ('WJetFakeRate-mDn', 'WJetFakeRate-nominal'),
         ('TopTWge1jetBin0',   'Top'),
         ('TopTWge1jetBin1',   'Top'),
         ('TopTWge1jetBin2',   'Top'),
         ('TopTWge1jetBin3',   'Top'),
         ('TopTWge1jetBin4',   'Top'),
         ('TopTWge1jetBin5',   'Top'),
         ('TopTW0jet',   'Top'),
         ('Top0jet',   'Top'),
         ('Topge1jetBin0',   'Top'),
         ('Topge1jetBin1',   'Top'),
         ('Topge1jetBin2',   'Top'),
         ('Topge1jetBin3',   'Top'),
         ('Topge1jetBin4',   'Top'),
         ('Topge1jetBin5',   'Top'),

         #('Top0jet_nowe',   'Top'),
         #('Topge1jet_nowe',   'Top'),


         ('TopCtrl', 'Top'),
         # templates
         'VgS-template','Vg-template',
     ], 
      '0j1j-differential3EmbeddedUnfolding' : [
        #signals
#        ('sigSMBin0', 'sigSM'),
#        ('sigSMBin1', 'sigSM'),
#        ('sigSMBin2', 'sigSM'),
#        ('sigSMBin3', 'sigSM'),
#        ('sigSMBin4', 'sigSM'),
#        ('sigSMBin5', 'sigSM'),
         ('ggHFidBin0','ggH'),
         ('ggHFidBin1','ggH'),
         ('ggHFidBin2','ggH'),
         ('ggHFidBin3','ggH'),
         ('ggHFidBin4','ggH'),
         ('ggHFidBin5','ggH'),
         ('qqHFidBin0','qqH'),
         ('qqHFidBin1','qqH'),
         ('qqHFidBin2','qqH'),
         ('qqHFidBin3','qqH'),
         ('qqHFidBin4','qqH'),
         ('qqHFidBin5','qqH'),
         ('WHFidBin0','WH'),
         ('WHFidBin1','WH'),
         ('WHFidBin2','WH'),
         ('WHFidBin3','WH'),
         ('WHFidBin4','WH'),
         ('WHFidBin5','WH'),
         ('ZHFidBin0','ZH'),
         ('ZHFidBin1','ZH'),
         ('ZHFidBin2','ZH'),
         ('ZHFidBin3','ZH'),
         ('ZHFidBin4','ZH'),
         ('ZHFidBin5','ZH'),

        # bkgs
         ("ggHNonFid", "ggH"),
         ("qqHNonFid", "qqH"),
         ("WHNonFid", "WH"),
         ("ZHNonFid", "ZH"),
         ('WWBin0', 'WW'),
         ('WWBin1', 'WW'),
         ('WWBin2', 'WW'),
         ('WWBin3', 'WW'),
         ('WWBin4', 'WW'),
         ('WWBin5', 'WW'),


         'ggWW','VgS','Vg','WJet','VV','VVV','DYTT','WWnlo','WWnloUp','WWnloDown',
         ('DYLL','ggH'),
         # systematics
         'WJetFakeRate-nominal',
         ('WJetFakeRate-eUp', 'WJetFakeRate-nominal'),
         ('WJetFakeRate-eDn', 'WJetFakeRate-nominal'),
         ('WJetFakeRate-mUp', 'WJetFakeRate-nominal'),
         ('WJetFakeRate-mDn', 'WJetFakeRate-nominal'),
         ('TopTWge1jetBin0',   'Top'),
         ('TopTWge1jetBin1',   'Top'),
         ('TopTWge1jetBin2',   'Top'),
         ('TopTWge1jetBin3',   'Top'),
         ('TopTWge1jetBin4',   'Top'),
         ('TopTWge1jetBin5',   'Top'),
         ('TopTW0jet',   'Top'),
         ('Top0jet',   'Top'),
         ('Topge1jetBin0',   'Top'),
         ('Topge1jetBin1',   'Top'),
         ('Topge1jetBin2',   'Top'),
         ('Topge1jetBin3',   'Top'),
         ('Topge1jetBin4',   'Top'),
         ('Topge1jetBin5',   'Top'),

         #('Top0jet_nowe',   'Top'),
         #('Topge1jet_nowe',   'Top'),


         ('TopCtrl', 'Top'),
         # templates
         'VgS-template','Vg-template',
     ],   

     '0j1j-differential2Ctrl' : [
        #signals
#        ('sigSMBin0', 'sigSM'),
#        ('sigSMBin1', 'sigSM'),
#        ('sigSMBin2', 'sigSM'),
#        ('sigSMBin3', 'sigSM'),
#        ('sigSMBin4', 'sigSM'),
#        ('sigSMBin5', 'sigSM'),
         ('ggHBin0','ggH'),
         ('ggHBin1','ggH'),
         ('ggHBin2','ggH'),
         ('ggHBin3','ggH'),
         ('ggHBin4','ggH'),
         ('ggHBin5','ggH'),
         ('qqHBin0','qqH'),
         ('qqHBin1','qqH'),
         ('qqHBin2','qqH'),
         ('qqHBin3','qqH'),
         ('qqHBin4','qqH'),
         ('qqHBin5','qqH'),
         ('WHBin0','WH'),
         ('WHBin1','WH'),
         ('WHBin2','WH'),
         ('WHBin3','WH'),
         ('WHBin4','WH'),
         ('WHBin5','WH'),
         ('ZHBin0','ZH'),
         ('ZHBin1','ZH'),
         ('ZHBin2','ZH'),
         ('ZHBin3','ZH'),
         ('ZHBin4','ZH'),
         ('ZHBin5','ZH'),

        # bkgs
         ('WWBin0', 'WW'),
         ('WWBin1', 'WW'),
         ('WWBin2', 'WW'),
         ('WWBin3', 'WW'),
         ('WWBin4', 'WW'),
         ('WWBin5', 'WW'),


         'ggWW','VgS','Vg','WJet','VV','VVV','DYTT','WWnlo','WWnloUp','WWnloDown',
         ('DYLL','ggH'),
         # systematics
         'WJetFakeRate-nominal',
         ('WJetFakeRate-eUp', 'WJetFakeRate-nominal'),
         ('WJetFakeRate-eDn', 'WJetFakeRate-nominal'),
         ('WJetFakeRate-mUp', 'WJetFakeRate-nominal'),
         ('WJetFakeRate-mDn', 'WJetFakeRate-nominal'),
         #('TopTW',   'Top'),
         ('Top0jet',   'Top'),
         ('Topge1jetCtrl',   'Top'),
         #('Top0jet_nowe',   'Top'),
         #('Topge1jet_nowe',   'Top'),


         #('TopCtrl', 'Top'),
         # templates
         #'VgS-template','Vg-template',
     ],
      '0j1j-differential3Ctrl' : [
        #signals
#        ('sigSMBin0', 'sigSM'),
#        ('sigSMBin1', 'sigSM'),
#        ('sigSMBin2', 'sigSM'),
#        ('sigSMBin3', 'sigSM'),
#        ('sigSMBin4', 'sigSM'),
#        ('sigSMBin5', 'sigSM'),
         ('ggHBin0','ggH'),
         ('ggHBin1','ggH'),
         ('ggHBin2','ggH'),
         ('ggHBin3','ggH'),
         ('ggHBin4','ggH'),
         ('ggHBin5','ggH'),
         ('qqHBin0','qqH'),
         ('qqHBin1','qqH'),
         ('qqHBin2','qqH'),
         ('qqHBin3','qqH'),
         ('qqHBin4','qqH'),
         ('qqHBin5','qqH'),
         ('WHBin0','WH'),
         ('WHBin1','WH'),
         ('WHBin2','WH'),
         ('WHBin3','WH'),
         ('WHBin4','WH'),
         ('WHBin5','WH'),
         ('ZHBin0','ZH'),
         ('ZHBin1','ZH'),
         ('ZHBin2','ZH'),
         ('ZHBin3','ZH'),
         ('ZHBin4','ZH'),
         ('ZHBin5','ZH'),

        # bkgs
         ('WWBin0', 'WW'),
         ('WWBin1', 'WW'),
         ('WWBin2', 'WW'),
         ('WWBin3', 'WW'),
         ('WWBin4', 'WW'),
         ('WWBin5', 'WW'),


         'ggWW','VgS','Vg','WJet','VV','VVV','DYTT','WWnlo','WWnloUp','WWnloDown',
         ('DYLL','ggH'),
         # systematics
         'WJetFakeRate-nominal',
         ('WJetFakeRate-eUp', 'WJetFakeRate-nominal'),
         ('WJetFakeRate-eDn', 'WJetFakeRate-nominal'),
         ('WJetFakeRate-mUp', 'WJetFakeRate-nominal'),
         ('WJetFakeRate-mDn', 'WJetFakeRate-nominal'),
         #('TopTW',   'Top'),
         ('Top0jet',   'Top'),
         ('Topge1jetCtrlBin0',   'Top'),
         ('Topge1jetCtrlBin1',   'Top'),
         ('Topge1jetCtrlBin2',   'Top'),
         ('Topge1jetCtrlBin3',   'Top'),
         ('Topge1jetCtrlBin4',   'Top'),
         ('Topge1jetCtrlBin5',   'Top'),
   
         #('Top0jet_nowe',   'Top'),
         #('Topge1jet_nowe',   'Top'),


         #('TopCtrl', 'Top'),
         # templates
         #'VgS-template','Vg-template',
     ],
     '0j1j-inclusiveCtrl' : [
        #signals
        'ggH','qqH','WH','ZH',
        # bkgs
         'WW','ggWW','VgS','Vg','WJet','VV','VVV','DYTT','WWnlo','WWnloUp','WWnloDown',
         ('DYLL','ggH'),
         # systematics
         'WJetFakeRate-nominal',
         ('WJetFakeRate-eUp', 'WJetFakeRate-nominal'),
         ('WJetFakeRate-eDn', 'WJetFakeRate-nominal'),
         ('WJetFakeRate-mUp', 'WJetFakeRate-nominal'),
         ('WJetFakeRate-mDn', 'WJetFakeRate-nominal'),
         #('TopTW',   'Top'),
         ('Top0jet',   'Top'),
         ('Topge1jetCtrl',   'Top'),
         #('Top0jet_nowe',   'Top'),
         #('Topge1jet_nowe',   'Top'),


         #('TopCtrl', 'Top'),
         # templates
         #'VgS-template','Vg-template',
     ], 
     '0j1j-inclusive' : [
        #signals
        'ggH','qqH','WH','ZH',
        # bkgs
         'WW','ggWW','VgS','Vg','WJet','VV','VVV','DYTT','WWnlo','WWnloUp','WWnloDown',
         ('DYLL','ggH'),
         # systematics
         'WJetFakeRate-nominal',
         ('WJetFakeRate-eUp', 'WJetFakeRate-nominal'),
         ('WJetFakeRate-eDn', 'WJetFakeRate-nominal'),
         ('WJetFakeRate-mUp', 'WJetFakeRate-nominal'),
         ('WJetFakeRate-mDn', 'WJetFakeRate-nominal'),
         #('TopTW',   'Top'),
         ('Top0jet',   'Top'),
         ('Topge1jet',   'Top'),
         #('Top0jet_nowe',   'Top'),
         #('Topge1jet_nowe',   'Top'),


         #('TopCtrl', 'Top'),
         # templates
         #'VgS-template','Vg-template',
     ],

     'differential' : [
         #signals
         'ggH','vbfwzttH', 
         # bkgs
         'WW','ggWW','VgS','Vg','WJet','Top','VV','VVV','DYTT','WWnlo','WWnloUp','WWnloDown',
         ('DYLL','ggH'),
         # systematics
         'WJetFakeRate-nominal',
         ('WJetFakeRate-eUp', 'WJetFakeRate-nominal'),
         ('WJetFakeRate-eDn', 'WJetFakeRate-nominal'),
         ('WJetFakeRate-mUp', 'WJetFakeRate-nominal'),
         ('WJetFakeRate-mDn', 'WJetFakeRate-nominal'),
         ('TopTW',   'Top'),
         ('TopCtrl', 'Top'),
         # templates
         'VgS-template','Vg-template',
         # 0j1j specific
         #('DYLL-template',    'DYLL-template-0j1j'),              #    A   <-   sorgente
         #('DYLL-templatesyst','DYLL-templatesyst-0j1j')           #    mkmerged vuole "-template"
     ],

    '0j1j-mH125' : [
        #signals
        'ggH','qqH','WH','ZH',
        # bkgs
        'WW','ggWW','VgS','Vg','WJet','Top','VV','VVV','DYTT','WWnlo','WWnloUp','WWnloDown',
        ('DYLL','ggH'),
        # systematics
        'WJetFakeRate-nominal',
        ('WJetFakeRate-eUp', 'WJetFakeRate-nominal'),
        ('WJetFakeRate-eDn', 'WJetFakeRate-nominal'),
        ('WJetFakeRate-mUp', 'WJetFakeRate-nominal'),
        ('WJetFakeRate-mDn', 'WJetFakeRate-nominal'),
        ('TopTW',   'Top'),
        ('TopCtrl', 'Top'),
        # templates
        'VgS-template','Vg-template',
        # 0j1j specific
        #('DYLL-template',    'DYLL-template-0j1j'),              #    A   <-   sorgente
        #('DYLL-templatesyst','DYLL-templatesyst-0j1j') ,         #    mkmerged vuole "-template"
        # mH125 as background
        'ggH_SM', 'qqH_SM', 'WH_SM','ZH_SM',
    ],
     '0j1j-ss' : [
        #signals
        'ggH','qqH','WH','ZH',
        # bkgs
        'Other','VgS','Vg','WJet',
        #'WW',
        #'ggWW','VgS','Vg','WJet',
        #'Top',
        #'VV','DYTT','DYLL',
        #'WWnlo','WWnloUp','WWnloDown','TopTW','TopCtrl',
        #,'WJetSS',
        # systematics
        #'WJetFakeRate-eUp', 'WJetFakeRate-eDn','WJetFakeRate-mUp', 'WJetFakeRate-mDn'
        # templates
        #'VgS-template','Vg-template','Top-template',
        # 0j1j specific
        #('DYLL-template',    'DYLL-template-0j1j'),              #    A   <-   sorgente
        #('DYLL-templatesyst','DYLL-templatesyst-0j1j')           #    mkmerged vuole "-template"
    ],
    '0j1jWW' : [
        #signals
        'ggH','qqH','WH','ZH',
        # bkgs
        #('WW', 'WWmad'),
        ('WW', 'WWpow'),
        #('WW', 'WWmc'),
        'ggWW','VgS','Vg','WJet','Top','VV','VVV','DYTT','WWnlo','WWnloUp','WWnloDown',
        #
        ('DYLL','ggH'),
        # systematics
        'WJetFakeRate-nominal',
        ('WJetFakeRate-eUp', 'WJetFakeRate-nominal'),
        ('WJetFakeRate-eDn', 'WJetFakeRate-nominal'),
        ('WJetFakeRate-mUp', 'WJetFakeRate-nominal'),
        ('WJetFakeRate-mDn', 'WJetFakeRate-nominal'),
        ('TopTW',   'Top'),
        ('TopCtrl', 'Top'),
        # templates
        'VgS-template','Vg-template',
        # 0j1j specific
        #('DYLL-template',    'DYLL-template-0j1j'),              #    A   <-   sorgente
        #('DYLL-templatesyst','DYLL-templatesyst-0j1j')           #    mkmerged vuole "-template"
    ],
    'cutbased' : [
        #signals
        'ggH','qqH','WH','ZH',
        # bkgs
        'WW', 'VgS','Vg','WJet','Top','VV','VVV','DYTT',
        # templates
        'VgS-template','Vg-template',
        # replce ggWW and DYLL
        ('ggWW',    'WW'),
        ('DYLL',    'WW'),
    ],
    'vbf_sf' : [
        #signals
        'ggH','qqH', #'wzttH',
        # bkgs
        #'WW','ggWW','VgS','Vg','WJet','Top','VV','DYTT','DYLL',
        'WW','ggWW','VgS','Vg',
        ('WJet', 'WJet-2j-fix'),
        'Top','VV',
        'WWewk',
        # dummy
        ('DYee', 'qqH'),
        ('DYmm', 'qqH'),
        # nuisance
        'WWpow',
        # systematics
        ('WJetFakeRate-2j-template','WJetFakeRate-nominal-2j-fix'), # here and in the following I put the "template" distributions (relaxed cuts)
        ('WJetFakeRate-2j-eUp',     'WJetFakeRate-nominal-2j-fix'),
        ('WJetFakeRate-2j-eDn',     'WJetFakeRate-nominal-2j-fix'),
        ('WJetFakeRate-2j-mUp',     'WJetFakeRate-nominal-2j-fix'),
        ('WJetFakeRate-2j-mDn',     'WJetFakeRate-nominal-2j-fix'),
        # templates
        'VgS-template','Vg-template',
        # templates for Top estimation
        ('CHITOP-Top',     'Top'),
    ],
    'vbf_sf-mH125' : [
        #signals
        'ggH','qqH', #'wzttH',
        # bkgs
        #'WW','ggWW','VgS','Vg','WJet','Top','VV','DYTT','DYLL',
        'WW','ggWW','VgS','Vg',
        ('WJet', 'WJet-2j-fix'),
        'Top','VV',
        'WWewk',
        # dummy
        ('DYee', 'qqH'),
        ('DYmm', 'qqH'),
        # nuisance
        'WWpow',
        # systematics
        ('WJetFakeRate-2j-template','WJetFakeRate-nominal-2j-fix'), # here and in the following I put the "template" distributions (relaxed cuts)
        ('WJetFakeRate-2j-eUp',     'WJetFakeRate-nominal-2j-fix'),
        ('WJetFakeRate-2j-eDn',     'WJetFakeRate-nominal-2j-fix'),
        ('WJetFakeRate-2j-mUp',     'WJetFakeRate-nominal-2j-fix'),
        ('WJetFakeRate-2j-mDn',     'WJetFakeRate-nominal-2j-fix'),
        # templates
        'VgS-template','Vg-template',
        # templates for Top estimation
        ('CHITOP-Top',     'Top'),
        # mH125 as background
        'ggH_SM', 'qqH_SM', # 'WH_SM','ZH_SM',
    ],
    'vbf_of' : [
        #signals
        'ggH','qqH', #'wzttH',
        # bkgs
        'WW','ggWW','VgS','Vg',
        ('WJet', 'WJet-2j-fix'),
        'Top','VV','DYTT',
        'WWewk',
        # nuisance
        'WWpow',
        # systematics
        ('WJetFakeRate-2j-template','WJetFakeRate-nominal-2j-fix'), # here and in the following I put the "template" distributions (relaxed cuts)
        ('WJetFakeRate-2j-eUp',     'WJetFakeRate-nominal-2j-fix'),
        ('WJetFakeRate-2j-eDn',     'WJetFakeRate-nominal-2j-fix'),
        ('WJetFakeRate-2j-mUp',     'WJetFakeRate-nominal-2j-fix'),
        ('WJetFakeRate-2j-mDn',     'WJetFakeRate-nominal-2j-fix'),
        # top shape ---> to be checked if needed
        #('TopTW',   'Top'),
        #('TopCtrl', 'Top'),
        # templates
        'VgS-template','Vg-template',
        # 2j specific
        #('WJet-template',    'WJet-template-2j'),              #    A   <-   sorgente
        #('WJet-templatesyst','WJet-templatesyst-2j')           #    mkmerged vuole "-template"
        # templates for Top estimation
        ('CHITOP-Top',     'Top'),
    ],
   'vbf_of-mH125' : [
        #signals
        'ggH','qqH', #'wzttH',
        # bkgs
        'WW','ggWW','VgS','Vg',
        ('WJet', 'WJet-2j-fix'),
        'Top','VV','DYTT',
        'WWewk',
        # nuisance
        'WWpow',
        # systematics
        ('WJetFakeRate-2j-template','WJetFakeRate-nominal-2j-fix'), # here and in the following I put the "template" distributions (relaxed cuts)
        ('WJetFakeRate-2j-eUp',     'WJetFakeRate-nominal-2j-fix'),
        ('WJetFakeRate-2j-eDn',     'WJetFakeRate-nominal-2j-fix'),
        ('WJetFakeRate-2j-mUp',     'WJetFakeRate-nominal-2j-fix'),
        ('WJetFakeRate-2j-mDn',     'WJetFakeRate-nominal-2j-fix'),
        # top shape ---> to be checked if needed
        #('TopTW',   'Top'),
        #('TopCtrl', 'Top'),
        # templates
        'VgS-template','Vg-template',
        # 2j specific
        #('WJet-template',    'WJet-template-2j'),              #    A   <-   sorgente
        #('WJet-templatesyst','WJet-templatesyst-2j')           #    mkmerged vuole "-template"
        # templates for Top estimation
        ('CHITOP-Top',     'Top'),
        # mH125 as background
        'ggH_SM', 'qqH_SM', # 'WH_SM','ZH_SM',
    ],
   'ggH2j_of' : [
        #signals
        'ggH','qqH', #'wzttH',
        #'ggHminlo',
        # bkgs
        'WW','ggWW','VgS','Vg',
        ('WJet', 'WJet-2j-fix'),
        'Top','VV','DYTT',
        'WWewk',
        # nuisance
        'WWpow',
        # systematics
        ('WJetFakeRate-2j-template','WJetFakeRate-nominal-2j-fix'), # here and in the following I put the "template" distributions (relaxed cuts)
        ('WJetFakeRate-2j-eUp',     'WJetFakeRate-nominal-2j-fix'),
        ('WJetFakeRate-2j-eDn',     'WJetFakeRate-nominal-2j-fix'),
        ('WJetFakeRate-2j-mUp',     'WJetFakeRate-nominal-2j-fix'),
        ('WJetFakeRate-2j-mDn',     'WJetFakeRate-nominal-2j-fix'),
        # top shape ---> to be checked if needed
        #('TopTW',   'Top'),
        #('TopCtrl', 'Top'),
        # templates
        'VgS-template','Vg-template',
        # 2j specific
        #('WJet-template',    'WJet-template-2j'),              #    A   <-   sorgente
        #('WJet-templatesyst','WJet-templatesyst-2j')           #    mkmerged vuole "-template"
        # templates for Top estimation
        #('CHITOP-Top',     'Top'),
    ],
    'vh_sf' : [
        #signals
        'ggH','qqH','WH','ZH',
        #'ttH','VH',
        # bkgs
        'WW','ggWW','VgS','Vg','WJet','Top','VV',
        'VVV',
        # nuisance
        'WWpow',
        #'WWnloNorm',
        #'WWnlo','WWnloUp','WWnloDown',
        # templates
        ('WJetFakeRate-2j-template','WJetFakeRate-nominal'), # here and in the following I put the "template" distributions (relaxed cuts)
        ('WJetFakeRate-2j-eUp',     'WJetFakeRate-nominal'),
        ('WJetFakeRate-2j-eDn',     'WJetFakeRate-nominal'),
        ('WJetFakeRate-2j-mUp',     'WJetFakeRate-nominal'),
        ('WJetFakeRate-2j-mDn',     'WJetFakeRate-nominal'),
        # templates
        'VgS-template','Vg-template',
         # dummy
        ('DYee', 'WW'),
        ('DYmm', 'WW'),
    ],
   'vh_of' : [
        #signals
        'ggH','qqH','WH','ZH',
        #'ttH','VH',
        # bkgs
        'WW','ggWW','VgS','Vg','WJet','Top','VV','DYTT',
        'VVV',
        # nuisance
        'WWpow',
        #'WWnloNorm',
        #'WWnlo','WWnloUp','WWnloDown',
        # templates
        ('WJetFakeRate-2j-template','WJetFakeRate-nominal'), # here and in the following I put the "template" distributions (relaxed cuts)
        ('WJetFakeRate-2j-eUp',     'WJetFakeRate-nominal'),
        ('WJetFakeRate-2j-eDn',     'WJetFakeRate-nominal'),
        ('WJetFakeRate-2j-mUp',     'WJetFakeRate-nominal'),
        ('WJetFakeRate-2j-mDn',     'WJetFakeRate-nominal'),
        'VgS-template','Vg-template',
        # 2j specific
        #('WJet-template',    'WJet-template-2j'),              #    A   <-   sorgente
        #('WJet-templatesyst','WJet-templatesyst-2j')           #    mkmerged vuole "-template"
        #('WJetFakeRate-nominal', 'WJetFakeRate-vh-template-nominal'),
        #('WJetFakeRate-eUp',     'WJetFakeRate-vh-template-nominal'),
        #('WJetFakeRate-eDn',     'WJetFakeRate-vh-template-nominal'),
        #('WJetFakeRate-mUp',     'WJetFakeRate-vh-template-nominal'),
        #('WJetFakeRate-mDn',     'WJetFakeRate-vh-template-nominal'),
    ],
    'zh4j_mm' : [
        #signals
        'ggH','qqH','WH','ZH','ttH',
        # bkgs
        'WW','ggWW','VgS','Vg','WJet','Top','VV',
        'VVV',
         # dummy
        ('DYee', 'WW'),
        ('DYmm', 'WW'),
        # templates
        'VgS-template','Vg-template',
    ],
   'zh4j_ee' : [
        #signals
        'ggH','qqH','WH','ZH','ttH',
        # bkgs
        'WW','ggWW','VgS','Vg','WJet','Top','VV',
        'VVV',
         # dummy
        ('DYee', 'WW'),
        ('DYmm', 'WW'),
        # templates
        'VgS-template','Vg-template',
    ],
   'whsc' : [
        #signals
        'ggH','qqH','WH','ZH','ttH','VH',
        #'WH','ZH','ttH','VH',
        #'VH',
        # bkgs
        'WW','ggWW','VgS','Vg','WJet','Top','VV','DYTT',
        'DYee',
        'DYmm',
        'VVV',
        # templates
        ('WJetFakeRate-2j-template','WJetFakeRate-nominal'), # here and in the following I put the "template" distributions (relaxed cuts)
        ('WJetFakeRate-2j-eUp',     'WJetFakeRate-nominal'),
        ('WJetFakeRate-2j-eDn',     'WJetFakeRate-nominal'),
        ('WJetFakeRate-2j-mUp',     'WJetFakeRate-nominal'),
        ('WJetFakeRate-2j-mDn',     'WJetFakeRate-nominal'),
        'VgS-template','Vg-template',
    ],

   'wwewkshape_of' : [
        #signals
        'ggH','qqH', #'wzttH',
        #'ggHminlo',
        # bkgs
        'WW','ggWW','VgS','Vg',
        ('WJet', 'WJet-2j-fix'),
        'VV','DYTT',
        #('TopPt0','Top'),
        ('TopPt1','Top'),  # 30-50
        ('TopPt2','Top'),  # 50-70
        ('TopPt3','Top'),  # 70-110
        ('TopPt4','Top'),  # 110-150
        ('TopPt5','Top'),  # 150-200
        ('TopPt6','Top'),  # 200-
        #('TopPt7','Top'),
        #('TopPt8','Top'),
        'WWewk',
        'VVV',
        # nuisance
        'WWpow',
        'WWewkMG',
        # systematics
        ('WJetFakeRate-2j-template','WJetFakeRate-nominal-2j-fix'), # here and in the following I put the "template" distributions (relaxed cuts)
        ('WJetFakeRate-2j-eUp',     'WJetFakeRate-nominal-2j-fix'),
        ('WJetFakeRate-2j-eDn',     'WJetFakeRate-nominal-2j-fix'),
        ('WJetFakeRate-2j-mUp',     'WJetFakeRate-nominal-2j-fix'),
        ('WJetFakeRate-2j-mDn',     'WJetFakeRate-nominal-2j-fix'),
        # top shape ---> to be checked if needed
        #('TopTW',   'Top'),
        #('TopCtrl', 'Top'),
        # templates
        'VgS-template','Vg-template',
        # 2j specific
        #('WJet-template',    'WJet-template-2j'),              #    A   <-   sorgente
        #('WJet-templatesyst','WJet-templatesyst-2j')           #    mkmerged vuole "-template"
        # templates for Top estimation
        #('CHITOP-Top',     'Top'),
    ],

   'wwewk_of' : [
        #signals
        'ggH','qqH', #'wzttH',
        #'ggHminlo',
        # bkgs
        'WW','ggWW','VgS','Vg',
        ('WJet', 'WJet-2j-fix'),
        'VV','DYTT',
        ('TopPt0','Top'),
        ('TopPt1','Top'),
        #('TopPt2','Top'),
        'WWewk',
        'VVV',
        # nuisance
        'WWpow',
        'WWewkMG',
        # systematics
        ('WJetFakeRate-2j-template','WJetFakeRate-nominal-2j-fix'), # here and in the following I put the "template" distributions (relaxed cuts)
        ('WJetFakeRate-2j-eUp',     'WJetFakeRate-nominal-2j-fix'),
        ('WJetFakeRate-2j-eDn',     'WJetFakeRate-nominal-2j-fix'),
        ('WJetFakeRate-2j-mUp',     'WJetFakeRate-nominal-2j-fix'),
        ('WJetFakeRate-2j-mDn',     'WJetFakeRate-nominal-2j-fix'),
        # top shape ---> to be checked if needed
        #('TopTW',   'Top'),
        #('TopCtrl', 'Top'),
        # templates
        'VgS-template','Vg-template',
        # 2j specific
        #('WJet-template',    'WJet-template-2j'),              #    A   <-   sorgente
        #('WJet-templatesyst','WJet-templatesyst-2j')           #    mkmerged vuole "-template"
        # templates for Top estimation
        #('CHITOP-Top',     'Top'),
    ],
   'wwewk_sf' : [
        #signals
        'ggH','qqH', #'wzttH',
        #'ggHminlo',
        # bkgs
        'WW','ggWW','VgS','Vg',
        ('WJet', 'WJet-2j-fix'),
        'VV',
         # dummy
        ('TopPt0','WWewk'),
        ('TopPt1','WWewk'),
        #('TopPt2','WWewk'),
         # dummy
        ('DYee', 'WWewk'),
        ('DYmm', 'WWewk'),
        'WWewk',
        'VVV',
        # nuisance
        'WWpow',
        'WWewkMG',
        # systematics
        ('WJetFakeRate-2j-template','WJetFakeRate-nominal-2j-fix'), # here and in the following I put the "template" distributions (relaxed cuts)
        ('WJetFakeRate-2j-eUp',     'WJetFakeRate-nominal-2j-fix'),
        ('WJetFakeRate-2j-eDn',     'WJetFakeRate-nominal-2j-fix'),
        ('WJetFakeRate-2j-mUp',     'WJetFakeRate-nominal-2j-fix'),
        ('WJetFakeRate-2j-mDn',     'WJetFakeRate-nominal-2j-fix'),
        # top shape ---> to be checked if needed
        #('TopTW',   'Top'),
        #('TopCtrl', 'Top'),
        # templates
        'VgS-template','Vg-template',
        # 2j specific
        #('WJet-template',    'WJet-template-2j'),              #    A   <-   sorgente
        #('WJet-templatesyst','WJet-templatesyst-2j')           #    mkmerged vuole "-template"
        # templates for Top estimation
        #('CHITOP-Top',     'Top'),
    ],

   'topestimate' : [
        # signals
        'ggH','qqH','wzttH',
        # backgrounds
        'WW','ggWW','VgS','Vg','WJet','Top','VV','DYTT','DYLL',
   ],
   'topplots' : [
        # signals
        'ggH','qqH','wzttH',
        # backgrounds
        'WW','ggWW','VgS','Vg','WJet','ttbar','tW','VV','DYTT','DYLL',
   ],

   'Hwidth_01j' : [
        #signals
        'ggH','qqH',
        'ggH_sbi','qqH_sbi',
        'ggH_b','qqH_b',
        'ggH_s','qqH_s',
        #'ggHminlo',
        # bkgs
        'WW',
        #'ggWW',
        'VgS','Vg','WJet','Top','VV',
        #'VVV',
        ('VVV','VVVnoEWK'),
        'DYTT','WWnlo','WWnloUp','WWnloDown',
        ('DYLL','ggH'),
        # systematics
        'WJetFakeRate-nominal',
        ('WJetFakeRate-eUp', 'WJetFakeRate-nominal'),
        ('WJetFakeRate-eDn', 'WJetFakeRate-nominal'),
        ('WJetFakeRate-mUp', 'WJetFakeRate-nominal'),
        ('WJetFakeRate-mDn', 'WJetFakeRate-nominal'),
        ('TopTW',   'Top'),
        ('TopCtrl', 'Top'),
        # templates
        'VgS-template','Vg-template',
        # 0j1j specific
        #('DYLL-template',    'DYLL-template-0j1j'),              #    A   <-   sorgente
        #('DYLL-templatesyst','DYLL-templatesyst-0j1j')           #    mkmerged vuole "-template"
    ],

   'Hwidth_2j' : [
        #signals
        'ggH','qqH',
        'ggH_sbi','qqH_sbi',
        'ggH_b','qqH_b',
        'ggH_s','qqH_s',
        #'ggHminlo',
        # bkgs
        'WW',
        #'ggWW',
        'VgS','Vg','WJet','Top','VV',
          #'VVV',
        ('VVV','VVVnoEWK'),
        'DYTT','WWnlo','WWnloUp','WWnloDown',
        ('DYLL','ggH'),
        # systematics
        'WJetFakeRate-nominal',
        ('WJetFakeRate-eUp', 'WJetFakeRate-nominal'),
        ('WJetFakeRate-eDn', 'WJetFakeRate-nominal'),
        ('WJetFakeRate-mUp', 'WJetFakeRate-nominal'),
        ('WJetFakeRate-mDn', 'WJetFakeRate-nominal'),
        #
        'Top'
        #('CHITOP-Top',     'Top'), -> to be fixed for data-driven estimation
        # templates
        'VgS-template','Vg-template',
    ],
   'Hwidth7TeV_01j' : [
        #signals
        'ggH','qqH',
        'ggH_sbi','qqH_sbi',
        'ggH_b','qqH_b',
        'ggH_s','qqH_s',
        #'ggHminlo',
        # bkgs
        'WW',
        #'ggWW',
        'VgS','Vg','WJet','Top','VV',
        #'VVV',
        #('VVV','VVVnoEWK'),
        'DYTT','WWnlo','WWnloUp','WWnloDown',
        ('DYLL','ggH'),
        # systematics
        'WJetFakeRate-nominal',
        ('WJetFakeRate-eUp', 'WJetFakeRate-nominal'),
        ('WJetFakeRate-eDn', 'WJetFakeRate-nominal'),
        ('WJetFakeRate-mUp', 'WJetFakeRate-nominal'),
        ('WJetFakeRate-mDn', 'WJetFakeRate-nominal'),
        ('TopTW',   'Top'),
        ('TopCtrl', 'Top'),
        # templates
        'VgS-template','Vg-template',
        # 0j1j specific
        #('DYLL-template',    'DYLL-template-0j1j'),              #    A   <-   sorgente
        #('DYLL-templatesyst','DYLL-templatesyst-0j1j')           #    mkmerged vuole "-template"
    ],

   'Hwidth7TeV_2j' : [
        #signals
        'ggH','qqH',
        'ggH_sbi','qqH_sbi',
        'ggH_b','qqH_b',
        'ggH_s','qqH_s',
        #'ggHminlo',
        # bkgs
        'WW',
        #'ggWW',
        'VgS','Vg','WJet','Top','VV',
          #'VVV',
        #('VVV','VVVnoEWK'),
        'DYTT','WWnlo','WWnloUp','WWnloDown',
        ('DYLL','ggH'),
        # systematics
        'WJetFakeRate-nominal',
        ('WJetFakeRate-eUp', 'WJetFakeRate-nominal'),
        ('WJetFakeRate-eDn', 'WJetFakeRate-nominal'),
        ('WJetFakeRate-mUp', 'WJetFakeRate-nominal'),
        ('WJetFakeRate-mDn', 'WJetFakeRate-nominal'),
        #
        'Top'
        #('CHITOP-Top',     'Top'), -> to be fixed for data-driven estimation
        # templates
        'VgS-template','Vg-template',
    ],
}

#--------------
def samples(mass, energytag, datatag='Data2012', sigtag='SM', mctag='all'):
    '''
    mass: mass for the higgs samples'
    datatag: tag for the dataset to be included
    sigtag: kind of signal (SM or Graviton)
    mctag: tag for the set of mc to be included
    '''


    if energytag == '8TeV':
        import samples.samples8TeV as sampledb
    elif energytag == '7TeV':
        import samples.samples7TeV as sampledb
    else:
        raise ValueError('Energy misdefined: '+energytag)

    signals = sampledb.signalSamples(sigtag,mass)
    print "*** signals = ",signals

    mcsamples = {}
    mcsamples.update(signals)
    if ('vbf' in mctag or 'wwewk' in mctag or 'vh' in mctag) and  datatag == 'Data2012' :
      sampledb.backgrounds['WJet'] = ['wjets/latino_RunA_892pbinv_LooseLoose.root', 
                                      'wjets/latino_RunB_4404pbinv_LooseLoose.root', 
                                      'wjets/latino_RunC_7032pbinv_LooseLoose.root', 
                                      'wjets/latino_RunD_7274pbinv_LooseLoose.root']
      sampledb.backgrounds['WJetFakeRate-nominal'] = ['wjets/latino_RunA_892pbinv_LooseLoose.root',
                                                      'wjets/latino_RunB_4404pbinv_LooseLoose.root',
                                                      'wjets/latino_RunC_7032pbinv_LooseLoose.root',
                                                      'wjets/latino_RunD_7274pbinv_LooseLoose.root']
      print sampledb.backgrounds['WJet']
      print sampledb.backgrounds['WJetFakeRate-nominal'] 

    mcsamples.update(sampledb.backgrounds)


    if 'mH' in mctag:
        print mctag
        # get the background-higgs mass from the tag
        if   '0j1j'   in mctag : mHbkg = int(re.match('0j1j-mH(\d+)', mctag).group(1))
        elif 'vbf_of' in mctag : mHbkg = int(re.match('vbf_of-mH(\d+)', mctag).group(1))
        elif 'vbf_sf' in mctag : mHbkg = int(re.match('vbf_sf-mH(\d+)', mctag).group(1))
        print 'signal as background', mHbkg
        #signalbkg = sampledb.signalSamples(sigtag, mHbkg, str(mHbkg))
        signalbkg = sampledb.signalSamples(sigtag, mHbkg, "_SM")
        print signalbkg
        mcsamples.update(signalbkg)

    if isinstance(mctag,list):
        mclabels = mctag
    else:
        if mctag not in mcsets:
            raise ValueError('MCtag '+mctag+' not supported')
        mclabels = mcsets[mctag]

    selectedMc = hwwtools.filterSamples( mcsamples, mclabels )

    # add data
    selectedData = {}
    if datatag == 'NoData':
        pass
    elif 'Data' in datatag:
        selectedData['Data'] = sampledb.data[datatag]
    elif 'SI' in datatag:
        # add the signal samples of the given mass
        m = re.match('SI(\d+)',datatag)
        print 'SI with mH =', int(m.group(1))
        if not m:
            raise ValueError('Signal injection must have the format SImmm where mmm is the mass')
        simass = int(m.group(1))
        siSamples = sampledb.signalSamples(sigtag, simass,suffix='-SI')
        selectedData.update(siSamples)
    else:
        raise ValueError('Data tag '+datatag+' not supported')

    samples = {}
    samples.update(selectedMc)
    samples.update(selectedData)

    return samples



