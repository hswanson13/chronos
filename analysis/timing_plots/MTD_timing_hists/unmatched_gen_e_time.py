import warnings
warnings.filterwarnings("ignore")

import numpy as np
import coffea

from coffea.nanoevents import NanoEventsFactory, BaseSchema

import matplotlib.pyplot as plt
import mplhep as hep #matplotlib wrapper for easy plotting in HEP
plt.style.use(hep.style.CMS)

import awkward as ak #just lets you do lists but faster i guess

from coffea.nanoevents.methods import vector
ak.behavior.update(vector.behavior)

import boost_histogram as bh

from Tools.helpers import get_four_vec_fromPtEtaPhiM, delta_phi, cross, delta_r, delta_r2, choose, match, finalizePlotDir
events0mm = NanoEventsFactory.from_root(
    '/home/users/hswanson13/CMSSW_11_3_1_patch1/src/Phase2Timing/Phase2TimingAnalyzer/python/ntuple_phase2timing0mm.root',
    schemaclass = BaseSchema,
    treepath='demo/tree',
    entry_stop = 1000).events() 

events100mm = NanoEventsFactory.from_root(
    '/home/users/hswanson13/CMSSW_11_3_1_patch1/src/Phase2Timing/Phase2TimingAnalyzer/python/ntuple_phase2timing100mm.root',
    schemaclass = BaseSchema,
    treepath='demo/tree',
    entry_stop = 1000).events()


events = NanoEventsFactory.from_root(
    '/home/users/hswanson13/CMSSW_11_3_1_patch1/src/Phase2Timing/Phase2TimingAnalyzer/python/ntuple_phase2timing1000mm.root',
    schemaclass = BaseSchema,
    treepath='demo/tree',
    entry_stop = 1000).events()


#get gen electron times for 0mm, 100mm, 1000mm
ge_pt = events['e_pt']
ge_eta = events['e_eta']
ge_phi = events['e_phi']
ge_M = np.zeros_like(ge_pt)

ge_pt100 = events100mm['e_pt']
ge_eta100 = events100mm['e_eta']
ge_phi100 = events100mm['e_phi']
ge_M100 = np.zeros_like(ge_pt100)

ge_pt0 = events0mm['e_pt']
ge_eta0 = events0mm['e_eta']
ge_phi0 = events0mm['e_phi']
ge_M0 = np.zeros_like(ge_pt0)

#get reco photon times for 0mm, 100mm, 1000mm
reco_photon_pt = events['reco_photon_pt']
reco_photon_eta = events['reco_photon_eta']
reco_photon_phi = events['reco_photon_phi']
reco_photon_M = np.zeros_like(reco_photon_pt)

reco_photon_pt100 = events100mm['reco_photon_pt']
reco_photon_eta100 = events100mm['reco_photon_eta']
reco_photon_phi100 = events100mm['reco_photon_phi']
reco_photon_M100 = np.zeros_like(reco_photon_pt100)

reco_photon_pt0 = events0mm['reco_photon_pt']
reco_photon_eta0 = events0mm['reco_photon_eta']
reco_photon_phi0 = events0mm['reco_photon_phi']
reco_photon_M0 = np.zeros_like(reco_photon_pt0)

#make gen e four vectors
ge_vec4 = ak.zip({"pt": ge_pt,"eta": ge_eta,"phi": ge_phi,"mass": ge_M,},with_name="PtEtaPhiMLorentzVector",)
ge100_vec4 = ak.zip( {"pt": ge_pt100,"eta": ge_eta100,"phi": ge_phi100,"mass": ge_M100,},with_name="PtEtaPhiMLorentzVector",)
ge0_vec4 = ak.zip( {"pt": ge_pt0,"eta": ge_eta0,"phi": ge_phi0,"mass": ge_M0,},with_name="PtEtaPhiMLorentzVector",)

#make gen e four vectors
reco_photon_vec4 = ak.zip({"pt": reco_photon_pt,"eta": reco_photon_eta,"phi": reco_photon_phi,"mass": reco_photon_M,},with_name="PtEtaPhiMLorentzVector",)
reco_photon_vec4100 = ak.zip({"pt": reco_photon_pt100,"eta": reco_photon_eta100,"phi": reco_photon_phi100,"mass": reco_photon_M100,},with_name="PtEtaPhiMLorentzVector",)
reco_photon_vec40 = ak.zip({"pt":reco_photon_pt0, "eta":reco_photon_eta0, "phi": reco_photon_phi0, "mass":reco_photon_M0,},with_name="PtEtaPhiMLorentzVector",)

#get gen electron timing info
e_time = events['e_ebdelay']
e_time100 = events100mm['e_ebdelay']
e_time0 = events0mm['e_ebdelay']

#get reco photon timing info for Cell times and Cluster times
MTDCellTime = events['reco_photon_MTDtime']
MTDCluTime = events['reco_photon_MTDClutime']
MTDCellTime100 = events100mm['reco_photon_MTDtime']
MTDCluTime100 = events100mm['reco_photon_MTDClutime']
MTDCellTime0 = events0mm['reco_photon_MTDtime']
MTDCluTime0 = events0mm['reco_photon_MTDClutime']


def tdiff_calc(e_time, ge_vec4, TCell, TClu, reco_photon_vec4):

    #main matching of photon and gen e
    pe_cart = ak.cartesian([reco_photon_vec4, ge_vec4]) #not nested, axis=1

    #timing matching
    te_cartCell = ak.cartesian([TCell, ge_vec4]) #how to take in account the -50 numbers???
    te_cartClu = ak.cartesian([TClu, ge_vec4])    #how to take in account the -50 numbers, dont??
    ge_time_cart = ak.cartesian([reco_photon_vec4, e_time])

    #Create a mask, True if less than 0.4 and True if more
    dRmask = delta_r(pe_cart['0'], pe_cart['1']) < 0.4

    #applying the mask, same dims as the combo but False just removes the ones w <0.4 dR
    mch_timeCell = (te_cartCell[dRmask])['0'] #cluster time of a matched photon, bec of loop over photons in C++
    mch_timeClu = (te_cartClu[dRmask])['0']   #cell time of a matched photon
    mch_timeE = (ge_time_cart[dRmask])['1']*10**9

    #time diff of Cluster time of photon and gen electron time
    tdiff_e_Clu = (mch_timeClu - mch_timeE)#/mch_timeE
    tdiff_e_Cell = (mch_timeCell - mch_timeE)#/mch_timeE
    return [tdiff_e_Clu, tdiff_e_Cell, mch_timeClu, mch_timeE]


tdiff1000 = tdiff_calc(e_time, ge_vec4, MTDCellTime, MTDCluTime, reco_photon_vec4)
tdiff100 = tdiff_calc(e_time100, ge100_vec4, MTDCellTime100, MTDCluTime100, reco_photon_vec4100)
tdiff0 = tdiff_calc(e_time0, ge0_vec4, MTDCellTime0, MTDCluTime0, reco_photon_vec40)

bin_start = 0
bin_end = 3 
n_bins = 10
bin_width = (bin_end - bin_start)/n_bins

e_1000 = np.clip(ak.flatten(e_time)*10**9, bin_start,bin_end-.02)
e_100 = np.clip(ak.flatten(e_time100)*10**9, bin_start,bin_end-.02)
e_0 = np.clip(ak.flatten(e_time0)*10**9, bin_start,bin_end-.02)
e_arrs = [e_1000,e_100,e_0]


names = [r'$c\tau$=1000mm',r'$c\tau$=100mm',r'$c\tau$=0mm']
colors = ['b','r','g']

arrs = e_arrs
xlabel = 'Unmatched Gen Electron Time'
binning = np.linspace(bin_start,bin_end,n_bins)
histograms = []
for arr in arrs:
    hist = bh.Histogram(bh.axis.Variable(binning), storage=bh.storage.Weight(),)
    hist.fill(arr, weight=np.ones_like(arr),)
    area = sum(hist.counts()) #bin_width*hist.counts(), guess not! haha works
    histograms.append(hist)

fig, ax = plt.subplots(figsize=(8, 8))
hep.histplot([hist.counts() for hist in histograms],
        binning,
        histtype="step",
        stack=False,
        label=[fr'$h\to XX\to 4e$: {name}' for name in names],
        color=colors,
        ax=ax,)

hep.cms.label("Preliminary",data=False,lumi='X',com=14,loc=0,ax=ax,fontsize=15,)

ax.set_ylabel(r'Counts')
ax.set_xlabel(xlabel, fontsize=18)
plt.legend(loc=0)
finalizePlotDir('/home/users/hswanson13/public_html/MTD_timing_hists/')

fig.savefig('/home/users/hswanson13/public_html/MTD_timing_hists/unmatched_gen_e_time.png')
