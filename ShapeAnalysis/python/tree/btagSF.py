from tree.gardening import TreeCloner

import optparse
import numpy
from math import *
from ROOT import TVector3

class btagSF(TreeCloner):
    # ----
    def __init__(self):
        pass

    # ----
    def __del__(self):
        pass

    # ----
    def help(self):
        return '''add btagging SF'''

    # ----
    def addOptions(self,parser):
        description = self.help()
        group = optparse.OptionGroup(parser,self.label, description)
 
        group.add_option('-m', '--eff-mc'    , dest='eff_mc'    , help='efficiency on the MC',)
        group.add_option('-e', '--eff-mc-error'    , dest='eff_mc_error'    , help='efficiency error on the MC',)
        group.add_option('-d', '--eff-data', dest='eff_data', help='efficiency for data')
        group.add_option('-f', '--eff-data-error', dest='eff_data_error', help='efficiency error for data')
        group.add_option('-g', '--mis-mc'    , dest='mis_mc'    , help='mistag rate on the MC',)
        group.add_option('-i', '--mis-mc-error'    , dest='mis_mc_error'    , help='mistag rate error on the MC',)
        group.add_option('-l', '--mis-data', dest='mis_data', help='mistag rate for data')
        group.add_option('-n', '--mis-data-error', dest='mis_data_error', help='mistag rate error for data')

        parser.add_option_group(group)

        return group

    # ----
    def checkOptions(self,opts):
        if not (hasattr(opts,'eff_mc') and 
                hasattr(opts,'eff_data') and
                hasattr(opts,'eff_mc_error') and 
                hasattr(opts,'eff_data_error') and
		hasattr(opts,'mis_mc') and
                hasattr(opts,'mis_data') and
                hasattr(opts,'mis_mc_error') and
                hasattr(opts,'mis_data_error') ):

            raise RuntimeError('Missing parameter')

        self.eff_mc   = opts.eff_mc
        self.eff_mc_error   = opts.eff_mc_error
        self.eff_data   = opts.eff_data
        self.eff_data_error   = opts.eff_data_error
        self.mis_mc   = opts.mis_mc
        self.mis_mc_error   = opts.mis_mc_error
        self.mis_data   = opts.mis_data
        self.mis_data_error   = opts.mis_data_error

    def _setupLambdas(self):
      self._ptsjet = []
      self._phisjet = []
      self._etasjet = []
      self._ptsb = []
      self._phisb = []
      self._etasb = []
      for index in range(1,5):
        self._ptsjet.append(eval('lambda itree: itree.jetpt'+str(index)))
        self._phisjet.append(eval('lambda itree: itree.jetphi'+str(index)))
        self._etasjet.append(eval('lambda itree: itree.jeteta'+str(index)))
      for index in range(1,3):
        self._ptsb.append(eval('lambda itree: itree.jetGenPartonBpt'+str(index)))
        self._phisb.append(eval('lambda itree: itree.jetGenPartonBphi'+str(index)))
        self._etasb.append(eval('lambda itree: itree.jetGenPartonBeta'+str(index)))   


    def extract3Vect(self, itree, basename, index, container):
      if basename == "jet":
        jetpt  = self._ptsjet[index-1](itree)#eval("itree."+basename+"pt"+str(index))
        jetphi = self._phisjet[index-1](itree)#eval("itree."+basename+"phi"+str(index))
        jeteta = self._etasjet[index-1](itree)#eval("itree."+basename+"eta"+str(index))
      else:
        jetpt  = self._ptsb[index-1](itree)#eval("itree."+basename+"pt"+str(index))
        jetphi = self._phisb[index-1](itree)#eval("itree."+basename+"phi"+str(index))
        jeteta = self._etasb[index-1](itree)#eval("itree."+basename+"eta"+str(index))
      vec = TVector3(0.,0.,0.)
      if jetpt>0:
        vec.SetPtEtaPhi(jetpt, jeteta, jetphi)
        container.append(vec)  
       
    # ----
    def process(self,**kwargs):
        print '''
   .----------.     -----------------------------------------------------------------------------------    .----------.   
  /  .-.  .-.  \     _________                             ___________              __                    /  .-.  .-.  \  
 /   | |  | |   \   /   _____/ ____ _____ _______   ____   \_   _____/____    _____/  |_  ___________    /   | |  | |   \ 
 \   ._'  ._'  _/   \_____  \_/ ___\__   \_  __  \_/ __ \   |    __) \__  \ _/ ___\   __\/  _ \_  _ _\   \   ._'  ._'  _/ 
 /\     .--.  / |   /        \  \___ / __ \|  | \/\  ___/   |     \   / __  \  \___|  | (  <_> )  | \/   /\     .--.  / | 
/\ |   /  /  / /    _______  /\___  >____  /__|    \___  >  \___  /  (____  /\___  >__|  \____/|__|     /\ |   /  /  / /  
 / |  '--'  /\ \           \/     \/     \/            \/       \/        \/     \/                      / |  '--'  /\ \  
  /'-------'  \ \   ----------------------------------------------------------------------------------    /'-------'  \ \ 
'''
        tree  = kwargs['tree']
        input = kwargs['input']
        output = kwargs['output']

        self.connect(tree,input)
        newbranches = ["weightBtagSig","weightBtagSigUp","weightBtagSigDown","weightBtagCtrl","weightBtagCtrlUp","weightBtagCtrlDown","isb1","isb2","isb3","isb4"]
        self.clone(output,newbranches)
        weightBtagSig = numpy.ones(1, dtype=numpy.float32)
        weightBtagSigUp = numpy.ones(1, dtype=numpy.float32)
        weightBtagSigDown = numpy.ones(1, dtype=numpy.float32)
        weightBtagCtrl = numpy.ones(1, dtype=numpy.float32)
        weightBtagCtrlUp = numpy.ones(1, dtype=numpy.float32)
        weightBtagCtrlDown = numpy.ones(1, dtype=numpy.float32)
        isb1 = numpy.ones(1, dtype=numpy.float32)
        isb2 = numpy.ones(1, dtype=numpy.float32)
        isb3 = numpy.ones(1, dtype=numpy.float32)
        isb4 = numpy.ones(1, dtype=numpy.float32)

        itree     = self.itree
        otree     = self.otree

        eff_mc = float(self.eff_mc)
        eff_data = float(self.eff_data)
        eff_mc_error = float(self.eff_mc_error)
        eff_data_error = float(self.eff_data_error)  
        mis_mc = float(self.mis_mc)
        mis_data = float(self.mis_data)
        mis_mc_error = float(self.mis_mc_error)
        mis_data_error = float(self.mis_data_error)

        perjetBtag = eff_data/eff_mc 
        perjetBtagError = sqrt((eff_mc_error/eff_mc)**2 + (eff_data_error/eff_data)**2)
        perjetAntiBtag = (1-eff_data)/(1-eff_mc)
        perjetAntiBtagError = sqrt((eff_mc_error/(1-eff_mc))**2 + (eff_data_error/(1-eff_data))**2)

        perjetMistag = mis_data/mis_mc
        perjetMistagError = sqrt((mis_mc_error/mis_mc)**2 + (mis_data_error/mis_data)**2)
        perjetAntiMistag = (1-mis_data)/(1-mis_mc)
        perjetAntiMistagError = sqrt((mis_mc_error/(1-mis_mc))**2 + (mis_data_error/(1-mis_data))**2)


        self.otree.Branch("weightBtagSig",weightBtagSig,'weightBtagSig/F')
        self.otree.Branch("weightBtagSigUp",weightBtagSigUp,'weightBtagSigUp/F')
        self.otree.Branch("weightBtagSigDown",weightBtagSigDown,'weightBtagSigDown/F')
        self.otree.Branch("weightBtagCtrl",weightBtagCtrl,'weightBtagCtrl/F')
        self.otree.Branch("weightBtagCtrlUp",weightBtagCtrlUp,'weightBtagCtrlUp/F')
        self.otree.Branch("weightBtagCtrlDown",weightBtagCtrlDown,'weightBtagCtrlDown/F')      

        

        self.otree.Branch("isb1",isb1,'isb1/F')
        self.otree.Branch("isb2",isb2,'isb2/F')
        self.otree.Branch("isb3",isb3,'isb3/F')
        self.otree.Branch("isb4",isb4,'isb4/F')


        nentries = self.itree.GetEntries()
        print 'Total number of entries: ',nentries

        print '- Starting eventloop'
        self._setupLambdas()
        step = 5000
        for i in xrange(nentries):
            itree.GetEntry(i)

            ## print event count
            if i > 0 and i%step == 0.:
                print i,'events processed.'

            if itree.dataset != 11 and itree.dataset != 12 and itree.dataset != 19 and itree.dataset != 1125 and itree.dataset != 2125 and itree.dataset != 3125 :
              weightBtagSig[0]=1.
              weightBtagSigUp[0]=1.
              weightBtagSigDown[0]=1.
              weightBtagSigDown[0]=1.
              weightBtagCtrlUp[0]=1.
              weightBtagCtrlDown[0]=1.
              isb1[0]=-9999
              isb2[0]=-9999
              isb3[0]=-9999
              isb4[0]=-9999
              otree.Fill()
              continue

            jets=[]
            #goes from 1 to 4    
            for i in range(1,5):
              self.extract3Vect(itree, "jet", i, jets)

           
            if itree.dataset == 1125 or itree.dataset == 2125 or itree.dataset == 3125 :
              j=0
	      for jet in jets :
		if jet.Perp()>30 : j+=1
              
              njet = min(2, j)
              weightBtagSig[0] = perjetAntiMistag**njet
              errorBtagSig =  njet*perjetAntiMistagError
              weightBtagSigUp[0]   = weightBtagSig[0]*(1 + errorBtagSig)
              weightBtagSigDown[0] = weightBtagSig[0]*(1 - errorBtagSig)

              weightBtagCtrl[0] = 1
              weightBtagCtrlUp[0] = 1
              weightBtagCtrlDown[0] = 1

              isb1[0]=-9999
              isb2[0]=-9999
              isb3[0]=-9999
              isb4[0]=-9999

              otree.Fill()
              continue

                       
            trueb = []
            #goes from 1 to 2
            for i in range(1,3):
              self.extract3Vect(itree, "jetGenPartonB", i, trueb)
              
            jets30 = []
            n_matching_jets = 0 
            n_not_matching_jets = 0 
	    i = 0
            isb1[0]=-9999
            isb2[0]=-9999
            isb3[0]=-9999
            isb4[0]=-9999

            for jet in jets:
              if jet.Perp()>30.:
		i+=1
		jets30.append(jet)
		matching=False
                	
                for b in trueb:
                  if jet.DeltaR(b) < 0.5:
                    #print jet.Print()
                    #print"matching with",
                    #print b.Print()
                    #print "with DeltaR=",jet.DeltaR(b)
		    matching=True
                    break	
                if matching:
                  if   (i==1): isb1[0]=1
                  elif (i==2): isb2[0]=1
		  elif (i==3): isb3[0]=1
                  elif (i==4): isb4[0]=1
		  if n_matching_jets < 2:
                    n_matching_jets += 1
                  else:
                    print "WARNING! more than two matching jets. We'll assume two matching jets anyways"
                else:
                  if   (i==1): isb1[0]=0
                  elif (i==2): isb2[0]=0
                  elif (i==3): isb3[0]=0
                  elif (i==4): isb4[0]=0                    

            nb = min(2, int(isb1[0]==1) + int(isb2[0]==1) + int(isb3[0]==1) + int(isb4[0]==1))
            nl = min(2, int(isb1[0]==0) + int(isb2[0]==0) + int(isb3[0]==0) + int(isb4[0]==0))
            #print "nb:", nb, " nl:", nl
            weightBtagSig[0] = (perjetAntiBtag**nb)*(perjetAntiMistag**nl)
            errorBtagSig = sqrt(nb*(perjetAntiBtagError)**2 + nl*(perjetAntiMistagError)**2)
            weightBtagSigUp[0]   = weightBtagSig[0]*(1 + errorBtagSig) 
            weightBtagSigDown[0] = weightBtagSig[0]*(1 - errorBtagSig) 

            weightBtagCtrl[0] = (perjetBtag**(int(isb1[0]==1)))*(perjetMistag**(int(isb1[0]==0)))
            errorBtagCtrl = float(isb1[0]==1)*perjetBtagError + float(isb1[0]==0)*perjetMistagError
            #anticorrelated with signal region
            weightBtagCtrlUp[0] = weightBtagCtrl[0]*(1 - errorBtagCtrl)
            weightBtagCtrlDown[0] = weightBtagCtrl[0]*(1 + errorBtagCtrl)
         
            #n_not_matching_jets = min(2,len(jets30) - n_matching_jets)
            #weight for btagged jets is epsilon_data/epsilon_MC
            #weight for anti b-tagged jets is (1-epsilon_data)/(1-epsilon_MC)
            #weightBtag[0] = (eff_data/eff_mc)**n_matching_jets
            #weightBtagUp[0] = ((eff_data+eff_data_error)/(eff_mc+eff_mc_error))**n_matching_jets
            #weightBtagDown[0] = ((eff_data-eff_data_error)/(eff_mc-eff_mc_error))**n_matching_jets

            #weightAntiBtag[0] = ((1-eff_data)/(1-eff_mc))**n_matching_jets            
            #weightAntiBtagUp[0] = ((1-eff_data-eff_data_error)/(1-eff_mc-eff_mc_error))**n_matching_jets            
            #weightAntiBtagDown[0] = ((1-eff_data+eff_data_error)/(1-eff_mc+eff_mc_error))**n_matching_jets            

            #weightMistag[0] = (mis_data/mis_mc)**n_not_matching_jets
            #weightMistagUp[0] = ((mis_data+mis_data_error)/(mis_mc+mis_mc_error))**n_not_matching_jets
            #weightMistagDown[0] = ((mis_data-mis_data_error)/(mis_mc-mis_mc_error))**n_not_matching_jets

            #weightAntiMistag[0] = ((1-mis_data)/(1-mis_mc))**n_not_matching_jets
            #weightAntiMistagUp[0] = ((1-mis_data-mis_data_error)/(1-mis_mc-mis_mc_error))**n_not_matching_jets
            #weightAntiMistagDown[0] = ((1-mis_data+mis_data_error)/(1-mis_mc+mis_mc_error))**n_not_matching_jets


            otree.Fill()

        self.disconnect()
        print '- Eventloop completed'


