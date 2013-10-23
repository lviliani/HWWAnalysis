import optparse
import numpy as np
from tree.gardening import TreeCloner

class WWGenFiller(TreeCloner):

    def __init__(self):
        pass

    def help(self):
        return '''fill tree with additional GEN level information about the WW system'''

    def addOptions(self,parser):
        description = self.help()
        group = optparse.OptionGroup(parser,self.label, description)

        parser.add_option_group(group)
        return group 

    def checkOptions(self,opts):
        pass

    def process(self,**kwargs):
        tree  = kwargs['tree']
        input = kwargs['input']
        output = kwargs['output']

        self.connect(tree,input)
        self.clone(output,['gen_WplusPt','gen_WplusEta','gen_WplusPhi','gen_WminusPt','gen_WminusEta','gen_WminusPhi','gen_WWPt','gen_WWEta','gen_WWPhi','gen_dPhill']) 

        gen_WplusPt = np.ones(1, dtype=np.float32)
        gen_WplusEta = np.ones(1, dtype=np.float32)
        gen_WplusPhi = np.ones(1, dtype=np.float32)
        gen_WminusPt = np.ones(1, dtype=np.float32)
        gen_WminusEta = np.ones(1, dtype=np.float32)
        gen_WminusPhi = np.ones(1, dtype=np.float32)
        gen_WWPt = np.ones(1, dtype=np.float32)
        gen_WWEta = np.ones(1, dtype=np.float32)
        gen_WWPhi = np.ones(1, dtype=np.float32)
        gen_dPhill = np.ones(1, dtype=np.float32)
        self.otree.Branch('gen_WplusPt',gen_WplusPt,'gen_WplusPt/F')
        self.otree.Branch('gen_WplusEta',gen_WplusEta,'gen_WplusEta/F')
        self.otree.Branch('gen_WplusPhi',gen_WplusPhi,'gen_WplusPhi/F')
        self.otree.Branch('gen_WminusPt',gen_WminusPt,'gen_WminusPt/F')
        self.otree.Branch('gen_WminusEta',gen_WminusEta,'gen_WminusEta/F')
        self.otree.Branch('gen_WminusPhi',gen_WminusPhi,'gen_WminusPhi/F')
        self.otree.Branch('gen_WWPt',gen_WWPt,'gen_WWPt/F')
        self.otree.Branch('gen_WWEta',gen_WWEta,'gen_WWEta/F')
        self.otree.Branch('gen_WWPhi',gen_WWPhi,'gen_WWPhi/F')
        self.otree.Branch('gen_dPhill',gen_dPhill,'gen_dPhill/F')

        nentries = self.itree.GetEntries()
        print 'Total number of entries: ',nentries 

        itree = self.itree
        otree = self.otree
                        
        print '- Starting eventloop'
        step = 5000
        for i in xrange(nentries):
            itree.GetEntry(i)

            ## print event count
            if i > 0 and i%step == 0.:
                print i,'events processed.'

            gen_WplusPt[0] = -9999.0
            gen_WplusEta[0] = -9999.0
            gen_WplusPhi[0] = -9999.0
            gen_WminusPt[0] = -9999.0
            gen_WminusEta[0] = -9999.0
            gen_WminusPhi[0] = -9999.0
            gen_WWPt[0] = -9999.0
            gen_WWEta[0] = -9999.0
            gen_WWPhi[0] = -9999.0
            gen_dPhill[0] = -9999.0

            dphill = itree.leptonGenphi1 - itree.leptonGenphi2
            if dphill < 0:
                dphill += 2*np.pi
            if dphill > np.pi:
                dphill = 2*np.pi - dphill
            gen_dPhill[0] = dphill

            pidl1 = itree.leptonGenpid1
            pidl2 = itree.leptonGenpid2
            pidn1 = itree.neutrinoGenpid1
            pidn2 = itree.neutrinoGenpid2
            switchN = False
            if pidl1 * pidl2 > 0 or pidn1 * pidn2 > 0:
                print '  same sign GEN leptons; continue...'
                continue
            if pidl1 * pidn1 > 0:
                switchN = True
                pidn1 = itree.neutrinoGenpid2
                pidn2 = itree.neutrinoGenpid1
            if abs(abs(pidl1) - abs(pidn1)) > 1 or abs(abs(pidl2) - abs(pidn2)) > 1:
                print '  incompatible GEN lepton types; continue...'

            lppt  = itree.leptonGenpt1    if pidl1 < 0                  else itree.leptonGenpt2
            lpphi = itree.leptonGenphi1   if pidl1 < 0                  else itree.leptonGenphi2
            lpeta = itree.leptonGeneta1   if pidl1 < 0                  else itree.leptonGeneta2
            nppt  = itree.neutrinoGenpt1  if bool(pidn1 > 0) != switchN else itree.neutrinoGenpt2
            npphi = itree.neutrinoGenphi1 if bool(pidn1 > 0) != switchN else itree.neutrinoGenphi2
            npeta = itree.neutrinoGeneta1 if bool(pidn1 > 0) != switchN else itree.neutrinoGeneta2

            lmpt  = itree.leptonGenpt1    if pidl1 > 0                  else itree.leptonGenpt2
            lmphi = itree.leptonGenphi1   if pidl1 > 0                  else itree.leptonGenphi2
            lmeta = itree.leptonGeneta1   if pidl1 > 0                  else itree.leptonGeneta2
            nmpt  = itree.neutrinoGenpt1  if bool(pidn1 < 0) != switchN else itree.neutrinoGenpt2
            nmphi = itree.neutrinoGenphi1 if bool(pidn1 < 0) != switchN else itree.neutrinoGenphi2
            nmeta = itree.neutrinoGeneta1 if bool(pidn1 < 0) != switchN else itree.neutrinoGeneta2

            wpx = lppt * np.cos (lpphi) + nppt * np.cos (npphi)
            wpy = lppt * np.sin (lpphi) + nppt * np.sin (npphi)
            wpz = lppt * np.sinh(lpeta) + nppt * np.sinh(npeta)

            wmx = lmpt * np.cos (lmphi) + nmpt * np.cos (nmphi)
            wmy = lmpt * np.sin (lmphi) + nmpt * np.sin (nmphi)
            wmz = lmpt * np.sinh(lmeta) + nmpt * np.sinh(nmeta)

            wwx = wpx + wmx
            wwy = wpy + wmy
            wwz = wpz + wmz

            wppt  = np.sqrt(wpx * wpx + wpy * wpy)
            wpmag = np.sqrt(wpx * wpx + wpy * wpy + wpz * wpz)
            wpeta = 0.5 * np.log( (wpmag + wpz) / (wpmag - wpz) )
            wpphi = np.arctan2(wpy, wpx)

            wmpt  = np.sqrt(wmx * wmx + wmy * wmy)
            wmmag = np.sqrt(wmx * wmx + wmy * wmy + wmz * wmz)
            wmeta = 0.5 * np.log( (wmmag + wmz) / (wmmag - wmz) )
            wmphi = np.arctan2(wmy, wmx)

            wwpt  = np.sqrt(wwx * wwx + wwy * wwy)
            wwmag = np.sqrt(wwx * wwx + wwy * wwy + wwz * wwz)
            wweta = 0.5 * np.log( (wwmag + wwz) / (wwmag - wwz) )
            wwphi = np.arctan2(wwy, wwx)

            gen_WplusPt[0] = wppt
            gen_WplusEta[0] = wpeta
            gen_WplusPhi[0] = wpphi
            gen_WminusPt[0] = wmpt
            gen_WminusEta[0] = wmeta
            gen_WminusPhi[0] = wmphi
            gen_WWPt[0] = wwpt
            gen_WWEta[0] = wweta
            gen_WWPhi[0] = wwphi
            

            otree.Fill()
        self.disconnect()
        print '- Eventloop completed'


