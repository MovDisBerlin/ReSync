from loading_data import _load_mat_file,_load_lfp_rec, _load_data_lfp
from tmsi_poly5reader import Poly5Reader
import json
from utils import _update_and_save_params
#from scripts.phase_analysis import phase_spiking
#from scripts.utils import _get_brain_areas, _load_data

def main(sub_ID='Sub019 24MFU M0S0 rest', fname_lfp="sub-20210415PStn_ses-2023040408103277_run-BrainSense20230404081800.mat", ch_idx_lfp=0, fname_external="sub019_24mfu_M0S0_BrStr_Rest-20230404T101235.DATA.Poly5", ch_idx_external="BIP 02"):
	dataset_lfp= _load_mat_file(sub_ID, fname_lfp)
	LFP_array, lfp_sig, LFP_rec_ch_names, sf_LFP =_load_data_lfp(sub_ID, dataset_lfp, ch_idx_lfp)




if __name__ == '__main__':
    main()
