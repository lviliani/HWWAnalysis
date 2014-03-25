#!/bin/env python

# import modules for regular expressions, math, and printing
import re
from math import *
from pprint import pprint


triggers = {}

class TriggerEff:

    def __init__(self,path):
        
        # open file (TODO: replace with config option)
        vals = open(path, "r")

        # read every line
        for line in vals:
            m = re.match(r"(Single|Double)(Mu|El)(Lead|Trail)?\s([0-9\.]+)\s([0-9\.]+)\s([0-9\.]+)\s([0-9\.]+)\s([0-9\.]+)", line)
            if not m: continue
            if (m.group(1) == 'Single'):
                if (m.group(2) == 'El'):
                    trigname = 'SingleEl'
                else:
                    trigname = 'SingleMu'
            else:
                if (m.group(2) == 'El'):
                    trigname = 'Ele17_Ele8_Ele'
                else:
                    trigname = 'Mu17_Mu8_Mu'
                if (m.group(3) == 'Lead'):
                    trigname += '17Leg'
                else:
                    trigname += '8Leg'
            pt = (float(m.group(6)),float(m.group(7)))
            eta = (float(m.group(4)),float(m.group(5)))
            eff = float(m.group(8))
            if not trigname in triggers:
                triggers[trigname] = []
            triggers[trigname].append({'ptrange': pt, 'etarange': eta, 'efficiency': eff})

#        print triggers
#        exit(0)

    def getMMeff(self):
        # works only with 2012 data for the moment
        triggers = self.getTriggersForRun(190456)
        return DiMuEventEfficiency(triggers,mode='onlyDouble')

    def getEEeff(self):
        # works only with 2012 data for the moment
        triggers = self.getTriggersForRun(190456)
        return DiElEventEfficiency(triggers,mode='onlyDouble')

    def getEMeff(self):
        # works only with 2012 data for the moment
        triggers = self.getTriggersForRun(190456)
        return ElMuEventEfficiency(triggers,mode='onlyDouble')

    def getTriggersForRun(self, run, verbose=0):
        ret = {}
        for (trigname,pars) in triggers.items():
            ret[trigname] = LegEfficiency(trigname,pars)
        if verbose: print "Triggers for run %d: %s" % (run, ", ".join(ret.keys()))
        return ret


    def getTriggerEfficiency(self, eff, tree, signalSelection = lambda x : True, weight = lambda x : 1.0):
        debug_low = 0
        num = 0.0; den = 0.0
        if signalSelection(tree):
            w = weight(tree)
            if tree.channel == 2: # make sure for e+mu the 1 is mu
                e = eff(tree.pt2, tree.eta2, tree.pt1, tree.eta1, verbose=0)
            else:
                e = eff(tree.pt1, tree.eta1, tree.pt2, tree.eta2, verbose=0)
            if e < 0.5 and debug_low > 0:
                debug_low -= 1
                if tree.channel == 2: # make sure for e+mu the 1 is mu
                    e = eff(tree.pt2, tree.eta2, tree.pt1, tree.eta1, verbose=2)
                else:
                    e = eff(tree.pt1, tree.eta1, tree.pt2, tree.eta2, verbose=2)
            return e


## Giovannis classes:

class LegEfficiency:
    def __init__(self,name,params):
        self._name    = name
        self._params  = params
    def __call__(self,pt,eta,verbose=0):
        for bin in self._params:
            (ptlow,pthigh) = bin['ptrange']
            (etalow,etahigh) = bin['etarange']
            if pt >= ptlow and pt < pthigh and abs(eta) >= etalow and abs(eta) < etahigh:
                # no linear interpolation
                return bin['efficiency']
                # comment out above line to run with linear interpolation in pt
                ptcen = (ptlow + pthigh) / 2
                eff = bin['efficiency']
                for nbin in self._params:
                    (nptlow,npthigh) = nbin['ptrange']
                    (netalow,netahigh) = nbin['etarange']
                    if (pt > ptcen and nptlow == pthigh or pt <= ptcen and npthigh == ptlow) and netalow == etalow and netahigh == etahigh:
                        nptcen = (nptlow + npthigh) / 2
                        neff = nbin['efficiency']
                        return eff + (pt - ptcen) * (neff - eff) / (nptcen - ptcen)
                return eff
        print pt, eta
        return 0.0

class ZeroEfficiency:
    def __init__(self, name=None):
        self._name = name
    def __call__(self,pt,eta,verbose=0):
        if verbose > 0 and self._name != None:
            print "Called ZeroEfficiency %s for (pt,eta) = (%.1f,%.2f)" % (self._name,pt,eta)
        return 0.0;

class PerfectEfficiency:
    def __init__(self,threshold=0,plateau=1.0):
        self._threshold = 0
        self._plateau   = 1.0
    def __call__(self,pt,eta,verbose=0): 
        return self._plateau if pt > self._threshold else 0.0;

class DiMuEventEfficiency:
    def __init__(self,legs,mode="default"):
        self._mode   = mode
        if mode != "onlyDouble":
            self._single = legs["SingleMu"] if "SingleMu" in legs else ZeroEfficiency("NoSingleMu")
        else:
            self._single = ZeroEfficiency()
        if "Mu17_Mu8_Mu17Leg" in legs:
            self._doubleHighPt = legs["Mu17_Mu8_Mu17Leg"]
            self._doubleLowPt  = legs["Mu17_Mu8_Mu8Leg"]
        else:
            self._doubleHighPt = ZeroEfficiency()
            self._doubleLowPt  = ZeroEfficiency() 
        if "Mu17_TkMu8_Exclusive" in legs and mode != "noTkMu":
            self._tkMuExclusive = legs["Mu17_TkMu8_Exclusive"]
        else:
            self._tkMuExclusive = ZeroEfficiency()
    def __call__(self,pt1,eta1,pt2,eta2,verbose=0):
        effs_leg1 = [x(pt1,eta1,verbose-1) for x in self._single, self._doubleHighPt, self._doubleLowPt, self._tkMuExclusive]
        effs_leg2 = [x(pt2,eta2,verbose-1) for x in self._single, self._doubleHighPt, self._doubleLowPt, self._tkMuExclusive]
        p0 = effs_leg1[0]
        p1 = effs_leg1[1]
        p2 = effs_leg1[2]
        q0 = effs_leg2[0]
        q1 = effs_leg2[1]
        q2 = effs_leg2[2]
        eff = p0 * (1 - q2) + q0 * (1 - p2) + p1 * q2 + p2 * q1 - p1 * q1
        return eff

class DiElEventEfficiency:
    def __init__(self,legs,mode="default"):
        self._mode   = mode
        if mode != "onlyDouble":
            self._singleEl = legs["SingleEl"] if "SingleEl" in legs else ZeroEfficiency("NoSingleEl")
        else:
            self._singleEl = ZeroEfficiency()
        if "Ele17_Ele8_Ele17Leg" in legs:
            self._doubleElHighPt = legs["Ele17_Ele8_Ele17Leg"]
            self._doubleElLowPt  = legs["Ele17_Ele8_Ele8Leg"]
        else:
            self._doubleElHighPt = ZeroEfficiency("NoDoubleEl_HighPt")
            self._doubleElLowPt  = ZeroEfficiency("NoDoubleEl_LowPt") 
    def __call__(self,pt1,eta1,pt2,eta2,verbose=0):
        effs_leg1 = [x(pt1,eta1,verbose-1) for x in self._singleEl, self._doubleElHighPt, self._doubleElLowPt]
        effs_leg2 = [x(pt2,eta2,verbose-1) for x in self._singleEl, self._doubleElHighPt, self._doubleElLowPt]
        p0 = effs_leg1[0]
        p1 = effs_leg1[1]
        p2 = effs_leg1[2]
        q0 = effs_leg2[0]
        q1 = effs_leg2[1]
        q2 = effs_leg2[2]
        eff = p0 * (1 - q2) + q0 * (1 - p2) + p1 * q2 + p2 * q1 - p1 * q1
        return eff

class ElMuEventEfficiency:
    def __init__(self,legs,mode="default"):
        self._mode   = mode
        if mode != "onlyDouble":
            self._singleEl = legs["SingleEl"] if "SingleEl" in legs else ZeroEfficiency("NoSingleEl")
            self._singleMu = legs["SingleMu"] if "SingleMu" in legs else ZeroEfficiency("NoSingleMu")
        else:
            self._singleEl = ZeroEfficiency()
            self._singleMu = ZeroEfficiency()
        if "Mu13leg_Mu8" in legs:
            self._doubleMuHighPt = legs["Mu13leg_Mu8"]
            self._doubleMuLowPt  = legs["Mu13_Mu8leg"]
        elif "Mu17_Mu8_Mu17Leg" in legs:
            self._doubleMuHighPt = legs["Mu17_Mu8_Mu17Leg"]
            self._doubleMuLowPt  = legs["Mu17_Mu8_Mu8Leg"]
        else:
            self._doubleMuHighPt = ZeroEfficiency()
            self._doubleMuLowPt  = ZeroEfficiency() 
        if "Ele17_Ele8_Ele17Leg" in legs:
            self._doubleElHighPt = legs["Ele17_Ele8_Ele17Leg"]
            self._doubleElLowPt  = legs["Ele17_Ele8_Ele8Leg"]
        elif "Ele17_Ele8_Tighter_Ele17Leg_fromEle8" in legs:
            self._doubleElHighPt = legs["Ele17_Ele8_Tighter_Ele17Leg_fromEle8"]
            self._doubleElLowPt  = legs["Ele17_Ele8_Tighter_Ele8Leg_fromEle8"]
        else:
            self._doubleElHighPt = ZeroEfficiency("NoDoubleEl_HighPt")
            self._doubleElLowPt  = ZeroEfficiency("NoDoubleEl_LowPt") 
    def __call__(self,ptmu,etamu,ptel,etael,verbose=0):
        effs_leg1 = [x(ptmu,etamu,verbose-1) for x in self._singleMu, self._doubleMuHighPt, self._doubleMuLowPt]
        effs_leg2 = [x(ptel,etael,verbose-1) for x in self._singleEl, self._doubleElHighPt, self._doubleElLowPt]
        p0 = effs_leg1[0]
        p1 = effs_leg1[1]
        p2 = effs_leg1[2]
        q0 = effs_leg2[0]
        q1 = effs_leg2[1]
        q2 = effs_leg2[2]
        eff = p0 * (1 - q2) + q0 * (1 - p2) + p1 * q2 + p2 * q1 - p1 * q1
        return eff

class LuminosityWeightedAverage:
    def __init__(self,lumiEffPairs):
        norm = sum([lumi for lumi,eff in lumiEffPairs])
        self._pairs = [ (lumi/norm, eff) for (lumi,eff) in lumiEffPairs]
    def __call__(self,pt1,eta1,pt2,eta2,verbose):
        avg = 0
        for (w,eff) in self._pairs:
            avg += w*eff(pt1,eta1,pt2,eta2,verbose)
        return avg


