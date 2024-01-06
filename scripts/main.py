from loading_data import (_load_mat_file, _load_data_lfp, _load_TMSi_artefact_channel, 
						  _load_sourceJSON)
from plotting import plot_LFP_external
from timeshift import check_timeshift
from utils import _update_and_save_params
from tmsi_poly5reader import Poly5Reader
import os
from os.path import join
from main_resync import run_resync
from packet_loss import check_packet_loss
from ecg_plot import ecg

def main(
	sub_ID='sub036 18MFU M0S0', 
	fname_lfp='sub-20220127PStn_ses-2023080107101376_run-BrainSense20230801080800.mat', 
	ch_idx_lfp=0,
	fname_external='sub036_18mfu_M0S0_BrStr_RestTap_run2 - 20230801T100354.DATA.Poly5',
	BIP_ch_name = 'Bip25', 
	kernel = '2',
	saving_format = 'csv',
	json_filename = 'Report_Json_Session_Report_20230822T130201.json',
	CROP_BOTH=False,
	CHECK_FOR_TIMESHIFT=True,
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
															  fname_external, BIP_ch_name, saving_path)

	#  Sync recording sessions
	LFP_df_offset, external_df_offset = run_resync(sub_ID, kernel, LFP_array, lfp_sig, 
												LFP_rec_ch_names, sf_LFP, external_file, BIP_channel, 
												external_rec_ch_names, sf_external, saving_path, 
												saving_format, CROP_BOTH, SHOW_FIGURES = True)
	plot_LFP_external(sub_ID, LFP_df_offset, external_df_offset, sf_LFP, sf_external, 
				   ch_idx_lfp, ch_index_external, saving_path, SHOW_FIGURES)

	#  OPTIONAL : check timeshift:
	if CHECK_FOR_TIMESHIFT:
		print('Starting timeshift analysis...')
		check_timeshift(sub_ID, LFP_df_offset, sf_LFP, external_df_offset, sf_external, saving_path, SHOW_FIGURES)

	# OPTIONAL : check for packet loss:
	if CHECK_FOR_PACKET_LOSS:
		_update_and_save_params('JSON_FILE', json_filename, sub_ID, saving_path)
		json_object = _load_sourceJSON(json_filename)
		check_packet_loss(json_object)

	# OPTIONAL : plot cardiac artifact:
	ecg(sub_ID, LFP_df_offset, sf_LFP, external_df_offset, sf_external, saving_path, xmin= 0.25, xmax= 0.36, SHOW_FIGURES=True)


if __name__ == '__main__':
    main()
