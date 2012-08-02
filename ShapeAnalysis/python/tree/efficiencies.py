import optparse
import numpy
from tree.gardening import TreeCloner
from HWWAnalysis.ShapeAnalysis.triggerEffCombiner import TriggerEff

#    ____________            _____ ____       
#   / __/ _/ _/ /  ___ ___  / __(_) / /__ ____
#  / _// _/ _/ /__/ -_) _ \/ _// / / / -_) __/
# /___/_//_//____/\__/ .__/_/ /_/_/_/\__/_/   
#                   /_/                       
class EffLepFiller(TreeCloner):

    def __init__(self):
        pass

    def __del__(self):
        for f in ['elfile','mufile']:
            if hasattr(self,f):
                getattr(self,f).Close()

#     @staticmethod
    def _getBoundaries(self,h2):
        xlo = h2.GetXaxis().GetXmin()
        xhi = h2.GetXaxis().GetXmax()

        ylo = h2.GetYaxis().GetXmin()
        yhi = h2.GetYaxis().GetXmax()

        return (xlo,xhi,ylo,yhi,h2)

#     @staticmethod
    def _getWeight(self,eta,pt,bounds):

        eta_lo, eta_hi, pt_lo, pt_hi, hW = bounds
        
        eta = abs(eta) if abs(eta) < eta_hi else eta_hi-0.01
        pt = pt if pt < pt_hi else pt_hi-0.01
        pt = pt if pt > pt_lo else pt_lo+0.01

        effW = hW.GetBinContent(hW.FindBin(eta,pt))
        return effW

    def help(self):
        return '''Add a new lepton efficiency weight. The source root files for electrons and muons have to be specified'''

    def addOptions(self,parser):
        description = self.help()
        group = optparse.OptionGroup(parser,self.label, description)

        group.add_option('-e', '--elfile', dest='elfile', help='Name of the input root file with electron efficiencies',)
        group.add_option('-m', '--mufile', dest='mufile', help='Name of the input root file with muon efficiencies',)
        group.add_option('-E', '--elname', dest='elname', help='Electon\'s histogram name', default='newhwwWP_ratio')
        group.add_option('-M', '--muname', dest='muname', help='Muon\'s histogram name', default='muonDATAMCratio')
        group.add_option('-b', '--branch',   dest='branch', help='Name of the lepton efficiency weight branch', default='effW')

        parser.add_option_group(group)
        return group



    def checkOptions(self,opts):
        if not ( (hasattr(opts,'elfile') and hasattr(opts,'mufile') ) and (opts.elfile and opts.mufile)):
            raise RuntimeError('Missing options: mufile, elfile')

        self.elfile = self._openRootFile(opt.elfile)
        elhist = self._getRootObj(self.elfile,opts.elname)
        self.mufile = self._openRootFile(opt.mufile)
        muhist = self._getRootObj(self.mufile, opts.muname)

        self.branch = opts.branch

        self.elBounds = self._getBoundaries(elhist)
        self.muBounds = self._getBoundaries(muhist)

    def process(self,**kwargs):
        tree  = kwargs['tree']
        input = kwargs['input']
        output = kwargs['output']

        self.connect(tree,input)
        self.clone(output,[self.branch]) 

        weight = numpy.ones(1, dtype=numpy.float32)
        w1 = numpy.ones(1, dtype=numpy.float32)
        w2 = numpy.ones(1, dtype=numpy.float32)
        self.otree.Branch(self.branch,weight,self.branch+'/F')
        self.otree.Branch('w1',w1,'w1/F')
        self.otree.Branch('w2',w2,'w2/F')
        

        nentries = self.itree.GetEntries()
        print 'Total number of entries: ',nentries 
                
        # avoid dots to go faster
        itree     = self.itree
        otree     = self.otree
        elBounds  = self.elBounds
        muBounds  = self.muBounds
        getWeight = self._getWeight
        
        print '- Starting eventloop'
        step = 5000
        for i in xrange(nentries):
            itree.GetEntry(i)

            ## print event count
            if i > 0 and i%step == 0.:
                print i,'events processed.'

            channel = itree.channel
            eta1    = itree.eta1
            pt1     = itree.pt1
            eta2    = itree.eta2
            pt2     = itree.pt2

            if channel == 0:
                b1 = muBounds
                b2 = muBounds
            elif channel == 1:
                b1 = elBounds
                b2 = elBounds
            elif channel == 2:
                b1 = elBounds
                b2 = muBounds
            elif channel == 3:
                b1 = muBounds
                b2 = elBounds
            else:
                raise ValueError('channel=={0} What is that?!?!'.format(channel))

            w1[0] = getWeight(eta1,pt1,b1)
            w2[0] = getWeight(eta2,pt2,b2)

            w1[0] = w1[0] if w1[0] >= 0.5 else 1.
            w2[0] = w2[0] if w2[0] >= 0.5 else 1.

            weight[0] = w1[0]*w2[0]
            
            otree.Fill()
        self.disconnect()
        print '- Eventloop completed'



#    ________________         _____ ____       
#   / __/ _/ _/_  __/______ _/ __(_) / /__ ____
#  / _// _/ _/ / / / __/ _ `/ _// / / / -_) __/
# /___/_//_/  /_/ /_/  \_, /_/ /_/_/_/\__/_/   
#                     /___/                    

class EffTrgFiller(TreeCloner):

    def __init__(self):
        pass

    def help(self):
        return '''Add a new trigger efficiency weight. The source files must be passed as an option'''

    def addOptions(self,parser):
        description = self.help()
        group = optparse.OptionGroup(parser,self.label, description)

        group.add_option('-f', '--fitfile', dest='fitfile', help='path to the file containing the fit results',)
        group.add_option('-b', '--branch',   dest='branch', help='Name of the trigger efficiency weight branch', default='triggW')

        parser.add_option_group(group)
        return group 

    def checkOptions(self,opts):
        if not (hasattr(opts,'fitfile')):
            raise RuntimeError('Missing parameter')

        self.trgEff = TriggerEff(getattr(opts,'fitfile'))
        self.trgEEeff = self.trgEff.getEEeff()
        self.trgMMeff = self.trgEff.getMMeff()
        self.trgEMeff = self.trgEff.getEMeff()
        
        self.branch = opts.branch

    def process(self,**kwargs):
        tree  = kwargs['tree']
        input = kwargs['input']
        output = kwargs['output']

        self.connect(tree,input)
        self.clone(output,[self.branch]) 

        trgweight = numpy.ones(1, dtype=numpy.float32)
        self.otree.Branch(self.branch,trgweight,self.branch+'/F')

        nentries = self.itree.GetEntries()
        print 'Total number of entries: ',nentries 
                
        # avoid dots to go faster
        itree     = self.itree
        otree     = self.otree
        trgEff    = self.trgEff
        trgEEeff  = self.trgEEeff
        trgMMeff  = self.trgMMeff
        trgEMeff  = self.trgEMeff
        
        print '- Starting eventloop'
        step = 5000
        for i in xrange(nentries):
            itree.GetEntry(i)

            ## print event count
            if i > 0 and i%step == 0.:
                print i,'events processed.'

            channel = itree.channel

            if channel == 0:
                e = trgEff.getTriggerEfficiency(trgMMeff, itree)
            elif channel == 1:
                e = trgEff.getTriggerEfficiency(trgEEeff, itree)
            elif channel == 2 or channel == 3:
                e = trgEff.getTriggerEfficiency(trgEMeff, itree)
            else:
                raise ValueError('channel=={0} What is that?!?!'.format(channel))

            if e > 1:
                print 'channel=={%d}, triggW: {%f} > 1 !!!' % (channel,e)
                
            trgweight[0] = e
            
            otree.Fill()
        self.disconnect()
        print '- Eventloop completed'


