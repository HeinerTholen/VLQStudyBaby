import itertools
import ROOT
ROOT.gROOT.SetBatch()

import varial.tools
from DataFormats.FWLite import Events, Handle
from MyUtility.PythonUtil.eventlooputility import deltaR_vec_to_vec


fname_Tj_th = '/nfs/dust/cms/user/ottjoc/gc-output/PHYS14v0/' \
              'signals/MC_TpJ_TH_M800_20x25_11_miniaod.root'

gp_coll_type = 'vector<reco::GenParticle>'
gp_collection = 'prunedGenParticles'

fs_tp = varial.analysis.fileservice('tPrime')
fs_fw = varial.analysis.fileservice('forwardParton')
fs_h  = varial.analysis.fileservice('higgs')
fs_t  = varial.analysis.fileservice('top')
fs_tp.makeTH2D(
    'tPrimeKinematic',
    ";T' p_{T};T' #eta",
    100, 0, 1000,
    100, 0., 10.
)
fs_tp.makeTH1D(
    'tPrimeNumberOfDaughters',
    ";NumberOfDaughters;",
    10, .5, 10.5
)
tPrimeDecayChans = {}
tPrimeMomPdgId = {}
fs_fw.makeTH2D(
    'fwJetKinematic',
    ';forward parton p_{T};forward parton #eta',
    100, 0, 1000,
    100, 0., 10.
)
fwJetPdgId = {}
fs_h.makeTH2D(
    'hKinematic',
    ';H p_{T};H #eta',
    100, 0, 1000,
    100, 0., 10.
)
hDecayChans = {}
fs_h.makeTH1D(
    'bbDeltaR',
    ';#DeltaR(p,p) from H->pp;events',
    100, 0., 5.
)
fs_t.makeTH2D(
    'leptonKinematic',
    ';lepton p_{T};lepton #eta',
    100, 0, 1000,
    100, 0., 10.
)
fs_t.makeTH2D(
    'topKinematic',
    ';top quark p_{T};top quark #eta',
    100, 0, 1000,
    100, 0., 10.
)


def dict_histo_fill(d, v):
    if v in d:
        d[v] += 1
    else:
        d[v] = 1


print 'Starting.'
events = Events(fname_Tj_th)
for evt_no, event in enumerate(events):
    print 'Processing event: %s \r' % evt_no,

    gp_handle = Handle(gp_coll_type)
    event.getByLabel(gp_collection, gp_handle)

    # find particles (throws error if not found)
    tPrimeMom = next(itertools.dropwhile(
        lambda p: not any(abs(p.daughter(i).pdgId()) == 6000006
                          for i in xrange(p.numberOfDaughters())),
        gp_handle.product()
    ))
    tPrime = next(itertools.dropwhile(
        lambda p: not abs(p.pdgId()) == 6000006,
        (tPrimeMom.daughter(i) for i in xrange(10))
    ))
    fwJet = next(itertools.dropwhile(
        lambda p: not abs(p.pdgId()) < 7,
        (tPrimeMom.daughter(i) for i in xrange(10))
    ))
    higg = next(itertools.dropwhile(
        lambda p: not abs(p.pdgId()) == 25,
        (tPrime.daughter(i) for i in xrange(10))
    ))
    top = next(itertools.dropwhile(
        lambda p: not abs(p.pdgId()) == 6,
        (tPrime.daughter(i) for i in xrange(10))
    ))

    while higg.daughter(0).pdgId() == 25:                   # forward to last h
        higg = higg.daughter(0)

    lepton = None
    intermediate = top
    while intermediate.daughter(0).pdgId() == 6:            # forward to last t
        intermediate = intermediate.daughter(0)
    try:
        intermediate = next(itertools.dropwhile(            # get W
            lambda p: not abs(p.pdgId()) == 24,
            (intermediate.daughter(i)
             for i in xrange(intermediate.numberOfDaughters()))
        ))
    except StopIteration:
        intermediate = None
    if intermediate:
        while intermediate.daughter(0).pdgId() == 24:       # forward to last W
            intermediate = intermediate.daughter(0)
        for i in xrange(intermediate.numberOfDaughters()):  # find lepton
            if abs(intermediate.daughter(i).pdgId()) in (11, 13):
                lepton = intermediate.daughter(i)
                break

    # fill histograms
    fs_tp.tPrimeKinematic.Fill(tPrime.pt(), abs(tPrime.eta()))
    fs_fw.fwJetKinematic .Fill(fwJet .pt(), abs(fwJet .eta()))
    fs_t.topKinematic   .Fill(top   .pt(), abs(top   .eta()))
    fs_h.hKinematic     .Fill(higg  .pt(), abs(higg  .eta()))

    fs_tp.tPrimeNumberOfDaughters.Fill(tPrime.numberOfDaughters())

    # fill branchings
    dict_histo_fill(fwJetPdgId, abs(fwJet.pdgId()))
    for i in xrange(higg.numberOfDaughters()):
        dict_histo_fill(hDecayChans, abs(higg.daughter(i).pdgId()))
    for i in xrange(tPrime.numberOfDaughters()):
        dict_histo_fill(tPrimeDecayChans, abs(tPrime.daughter(i).pdgId()))
    for i in xrange(tPrime.numberOfMothers()):
        dict_histo_fill(tPrimeMomPdgId, abs(tPrime.mother(i).pdgId()))

    if lepton:
        fs_t.leptonKinematic.Fill(lepton.pt(), lepton.eta())

    fs_h.bbDeltaR.Fill(deltaR_vec_to_vec(higg.daughter(0),
                                         higg.daughter(1)))

fs_fw.makeTH1D_from_dict(
    'fwJetPdgId', ';forward parton pdgId;', fwJetPdgId)
fs_h.makeTH1D_from_dict(
    'hDecayChans', ';H Decay Channel;', hDecayChans)
fs_tp.makeTH1D_from_dict(
    'tPrimeDecayChans', ';tPrime Decay Channel;', tPrimeDecayChans)
fs_tp.makeTH1D_from_dict(
    'tPrimeMomPdgId', ';tPrime Mother PdgId;', tPrimeMomPdgId)


print 'Done. Num events:'