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
 
 
       
    # ----
    def process(self,**kwargs):
        tree  = kwargs['tree']
        input = kwargs['input']
        output = kwargs['output']

        self.connect(tree,input)
        newbranches = ["weightBtag", "weightAntiBtag", "weightBtagUp", "weightBtagDown", "weightAntiBtagUp", "weightAntiBtagDown"]
        self.clone(output,newbranches)
        weightBtag = numpy.ones(1, dtype=numpy.float32)
        weightAntiBtag = numpy.ones(1, dtype=numpy.float32)
        weightBtagUp = numpy.ones(1, dtype=numpy.float32)
        weightAntiBtagUp = numpy.ones(1, dtype=numpy.float32)
        weightBtagDown = numpy.ones(1, dtype=numpy.float32)
        weightAntiBtagDown = numpy.ones(1, dtype=numpy.float32)
        weightMistag = numpy.ones(1, dtype=numpy.float32)
        weightAntiMistag = numpy.ones(1, dtype=numpy.float32)
        weightMistagUp = numpy.ones(1, dtype=numpy.float32)
        weightAntiMistagUp = numpy.ones(1, dtype=numpy.float32)
        weightMistagDown = numpy.ones(1, dtype=numpy.float32)
        weightAntiMistagDown = numpy.ones(1, dtype=numpy.float32)
        

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

        self.otree.Branch("weightBtag",weightBtag,'weightBtag/F')
        self.otree.Branch("weightAntiBtag",weightAntiBtag,'weightAntiBtag/F')
        self.otree.Branch("weightBtagUp",weightBtagUp,'weightBtagUp/F')
        self.otree.Branch("weightBtagDown",weightBtagDown,'weightBtagDown/F')
        self.otree.Branch("weightAntiBtagUp",weightAntiBtagUp,'weightAntiBtagUp/F')
        self.otree.Branch("weightAntiBtagDown",weightAntiBtagDown,'weightAntiBtagDown/F')
        self.otree.Branch("weightMistag",weightMistag,'weightMistag/F')
        self.otree.Branch("weightAntiMistag",weightAntiMistag,'weightAntiMistag/F')
        self.otree.Branch("weightMistagUp",weightMistagUp,'weightMistagUp/F')
        self.otree.Branch("weightMistagDown",weightMistagDown,'weightMistagDown/F')
        self.otree.Branch("weightAntiMistagUp",weightAntiMistagUp,'weightAntiMistagUp/F')
        self.otree.Branch("weightAntiMistagDown",weightAntiMistagDown,'weightAntiMistagDown/F')

        nentries = self.itree.GetEntries()
        print 'Total number of entries: ',nentries

        print '- Starting eventloop'
        step = 5000
        for i in xrange(nentries):
            itree.GetEntry(i)

            ## print event count
            if i > 0 and i%step == 0.:
                print i,'events processed.'

            jets=[]
            def extract3Vect(itree, basename, index, container):
              jetpt  = eval("itree."+basename+"pt"+str(i))
              jetphi = eval("itree."+basename+"phi"+str(i)) 
              jeteta = eval("itree."+basename+"eta"+str(i))
              vec = TVector3(0.,0.,0.)
              if jetpt>0:
                vec.SetPtEtaPhi(jetpt, jeteta, jetphi)
                container.append(vec) 
            #goes from 1 to 4    
            for i in range(1,5):
              extract3Vect(itree, "jet", i, jets)
           
            trueb = []
            #goes from 1 to 2
            for i in range(1,3):
              extract3Vect(itree, "jetGenPartonB", i, trueb)
              
            jets30 = []
            n_matching_jets = 0 
            for jet in jets:
              if jet.Perp()>30.:
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
		  if n_matching_jets < 2:
                    n_matching_jets += 1
                  else:
                    print "WARNING! more than two matching jets. We'll assume two matching jets anyways"

            n_not_matching_jets = min(2,len(jets30) - n_matching_jets)
            #weight for btagged jets is epsilon_data/epsilon_MC
            #weight for anti b-tagged jets is (1-epsilon_data)/(1-epsilon_MC)
            weightBtag[0] = (eff_data/eff_mc)**n_matching_jets
            weightBtagUp[0] = ((eff_data+eff_data_error)/(eff_mc+eff_mc_error))**n_matching_jets
            weightBtagDown[0] = ((eff_data-eff_data_error)/(eff_mc-eff_mc_error))**n_matching_jets

            weightAntiBtag[0] = ((1-eff_data)/(1-eff_mc))**n_matching_jets            
            weightAntiBtagUp[0] = ((1-eff_data-eff_data_error)/(1-eff_mc-eff_mc_error))**n_matching_jets            
            weightAntiBtagDown[0] = ((1-eff_data+eff_data_error)/(1-eff_mc+eff_mc_error))**n_matching_jets            

            weightMistag[0] = (mis_data/mis_mc)**n_not_matching_jets
            weightMistagUp[0] = ((mis_data+mis_data_error)/(mis_mc+mis_mc_error))**n_not_matching_jets
            weightMistagDown[0] = ((mis_data-mis_data_error)/(mis_mc-mis_mc_error))**n_not_matching_jets

            weightAntiMistag[0] = ((1-mis_data)/(1-mis_mc))**n_not_matching_jets
            weightAntiMistagUp[0] = ((1-mis_data-mis_data_error)/(1-mis_mc-mis_mc_error))**n_not_matching_jets
            weightAntiMistagDown[0] = ((1-mis_data+mis_data_error)/(1-mis_mc+mis_mc_error))**n_not_matching_jets


            otree.Fill()

        self.disconnect()
        print '- Eventloop completed'


