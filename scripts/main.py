from loading_data import _load_LFP_rec, _set_lfp_data, _load_TMSi_artefact_channel
from tmsi_poly5reader import Poly5Reader
#from scripts.phase_analysis import phase_spiking
#from scripts.utils import _get_brain_areas, _load_data


def main(sub_ID="024", session="fu24m", condition="m0s0", task="rest", run= "run1"):
    LFP_rec = _load_LFP_rec(sub_ID, session, condition, task, run)
    (LFP_array, lfp_sig, LFP_rec_ch_names, sf_LFP) = _set_lfp_data(LFP_rec)

    TMSi_data = Poly5Reader()  # open TMSi data from poly5
    # extract necessary objects for further analysis
    (BIP_channel,
    external_file,
    external_rec_ch_names,
    sf_external) = _load_TMSi_artefact_channel(TMSi_data) 



if __name__ == '__main__':
    main()
