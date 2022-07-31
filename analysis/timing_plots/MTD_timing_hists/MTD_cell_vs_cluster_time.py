exec(open("/home/users/hswanson13/CMSSW_12_2_0/src/chronos/analysis/timing_plots/config_plots.py").read())

events= NanoEventsFactory.from_root(
    '/home/users/hswanson13/CMSSW_11_3_1_patch1/src/Phase2Timing/Phase2TimingAnalyzer/python/ntuple_phase2timing100mm.root',
    schemaclass = BaseSchema,
    treepath='demo/tree',
    entry_stop = 1000).events()


MTDCellTime = ak.flatten(events['reco_photon_MTDtime'])

#Cluster Time
MTDCluTime = ak.flatten(events['reco_photon_MTDClutime'])


bin_start = -5
bin_end = 15
n_bins = 25
bin_width = (bin_end - bin_start)/n_bins

names = [r'$c\tau$=100mm',r'$c\tau$=100mm']
colors = ['b','r']

arrs = [MTDCellTime, MTDCluTime]
xlabel = 'Time (ns)'
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

fig.savefig('/home/users/hswanson13/public_html/MTD_timing_hists/MTD_Cell_vs_Clu_time.png')