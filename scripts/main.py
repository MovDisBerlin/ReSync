from loading_data import _load_mat_file, _load_data_lfp, _load_TMSi_artefact_channel, _load_sourceJSON
from plotting import plot_LFP_external
from timeshift import check_timeshift
from utils import _update_and_save_params
from tmsi_poly5reader import Poly5Reader
import os
from os.path import join
#import json
#from utils import _update_and_save_params
from main_resync import run_resync
from packet_loss import check_packet_loss

#from scripts.phase_analysis import phase_spiking
#from scripts.utils import _get_brain_areas, _load_data

def main(
	sub_ID='Sub036 18MFU M0S0', 
	fname_lfp='sub-20210415PStn_ses-2023040408103277_run-BrainSense20230404081800.mat', 
	ch_idx_lfp=0, 
	fname_external='sub019_24mfu_M0S0_BrStr_Rest-20230404T101235.DATA.Poly5', 
	kernel = '2',
	saving_format = 'mat',
	json_filename = 'Report_Json_Session_Report_20230404T131412_ANOM.json',
	CROP_BOTH=False,
	AUTOMATIC=False,
	CHECK_FOR_TIMESHIFT=False,
	CHECK_FOR_PACKET_LOSS=False,
	SHOW_FIGURES=True
	):

	#  Set saving path
	saving_path = join("results", sub_ID)
	if not os.path.isdir(saving_path):
		os.makedirs(saving_path)
	
	#  Loading datasets
	##  LFP (here Percept datas preprocessed in Matlab with Perceive toolbox)
	dataset_lfp= _load_mat_file(sub_ID, fname_lfp, saving_path)
	LFP_array, lfp_sig, LFP_rec_ch_names, sf_LFP = _load_data_lfp(sub_ID, dataset_lfp, 
															   ch_idx_lfp, saving_path)
	##  External data recorder
	source_path = "sourcedata"
	TMSi_data = Poly5Reader(join(source_path, fname_external)) 
	(BIP_channel, external_file, external_rec_ch_names, 
  sf_external, ch_index_external)= _load_TMSi_artefact_channel(sub_ID, TMSi_data, 
															  fname_external, AUTOMATIC, saving_path)

	#  Process/align recordings
	LFP_df_offset, external_df_offset = run_resync(sub_ID, kernel, LFP_array, lfp_sig, 
												LFP_rec_ch_names, sf_LFP, external_file, BIP_channel, 
												external_rec_ch_names, sf_external, saving_path, 
												saving_format, CROP_BOTH, SHOW_FIGURES = True)

	#  Plot the two recordings aligned
	plot_LFP_external(sub_ID, LFP_df_offset, external_df_offset, sf_LFP, sf_external, 
				   ch_idx_lfp, ch_index_external, saving_path, SHOW_FIGURES)

	#  OPTIONAL : check timeshift:
	if CHECK_FOR_TIMESHIFT:
		check_timeshift(sub_ID, LFP_df_offset, sf_LFP, external_df_offset, sf_external, saving_path, SHOW_FIGURES)

	# OPTIONAL : check for packet loss:
	if CHECK_FOR_PACKET_LOSS:
		_update_and_save_params('JSON_FILE', json_filename, sub_ID, saving_path)
		json_object = _load_sourceJSON(json_filename)
		check_packet_loss(json_object)


if __name__ == '__main__':
    main()
