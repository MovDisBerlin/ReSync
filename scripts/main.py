'''
main.py is the main function of ReSync for performing one-by-one session 
analysis. Use main_batch.py for batch analysis. 

Usage:
1. complete all the parameters in the main function according to your needs
	session_ID: string, name of the session to be analyzed

	fname_lfp: string, name of the LFP file to be analyzed (csv or mat file)

	ch_idx_lfp: int, index of the channel containing the stimulation artifacts
				in the LFP file

	fname_external: string, name of the external file to be analyzed (csv or 
					Poly5 file)

	BIP_ch_name: string, name of the channel containing the stimulation 
				artifacts in the external file

	saving_format: string, format of the output file (csv, pickle or mat)

	json_filename: string, name of the JSON file containing the intracranial
					recording. Only needed if CHECK_FOR_PACKET_LOSS is True. If
					not, set to None

	CROP_BOTH: boolean, if True, crop both LFP and external data to the shortest
				if False, crop only the external data to match the intracranial

	CHECK_FOR_TIMESHIFT: boolean, if True, perform timeshift analysis

	CHECK_FOR_PACKET_LOSS: boolean, if True, perform packet loss analysis

	SHOW_FIGURES: boolean, if True, show figures, if False only save them

2. run main.py

Result:
The results will be saved in the results folder, in a sub-folder named after the 
session_ID parameter.

'''

import os
from os.path import join

from loading_data import (_load_mat_file, _load_data_lfp, 
						  _load_TMSi_artifact_channel, _load_sourceJSON, 
						  _load_intracranial_csv_file, _load_external_csv_file)
from plotting import plot_LFP_external, ecg
from timeshift import check_timeshift
from utils import _update_and_save_params
from tmsi_poly5reader import Poly5Reader
from resync_function import run_resync
from packet_loss import check_packet_loss

def main(
	session_ID='test_brainvision_test_saving', 
	fname_lfp='Intracerebral_LFP_dataset1_250Hz.csv', 
	ch_idx_lfp=0,
	fname_external='External_data_dataset1_4096Hz.csv',
	BIP_ch_name = 'BIP 01', 
	saving_format = 'brainvision',
	json_filename = None,
	CROP_BOTH=True,
	CHECK_FOR_TIMESHIFT=False,
	CHECK_FOR_PACKET_LOSS=False,
	SHOW_FIGURES=True
	):

	#  Set saving path
	saving_path = join("results", session_ID)
	if not os.path.isdir(saving_path):
		os.makedirs(saving_path)
	
	#  Set source path
	source_path = "sourcedata"

	#  Loading datasets
		##  LFP (here Percept datas preprocessed with Perceive toolbox)
	if fname_lfp.endswith('.mat'):
		dataset_lfp= _load_mat_file(session_ID, fname_lfp, saving_path)
		(LFP_array, lfp_sig, 
   		LFP_rec_ch_names, sf_LFP) = _load_data_lfp(session_ID, dataset_lfp, 
												ch_idx_lfp, saving_path
												)
	if fname_lfp.endswith('.csv'):
		(LFP_array, lfp_sig, 
   		LFP_rec_ch_names, sf_LFP) = _load_intracranial_csv_file(session_ID, 
															 fname_lfp,
															 ch_idx_lfp,
															 saving_path
															 )


		##  External data recorder
	if fname_external.endswith('.Poly5'):
		TMSi_data = Poly5Reader(join(source_path, fname_external)) 
		(BIP_channel, external_file, external_rec_ch_names, sf_external, 
   		ch_index_external)= _load_TMSi_artifact_channel(session_ID, TMSi_data, 
													 fname_external, 
													 BIP_ch_name, saving_path
													 )
	if fname_external.endswith('.csv'):
		(BIP_channel, external_file, external_rec_ch_names, 
   		sf_external, ch_index_external) = _load_external_csv_file(session_ID, 
															   fname_external, 
															   BIP_ch_name, 
															   saving_path
															   )

	#  Sync recording sessions
	LFP_df_offset, external_df_offset = run_resync(session_ID, LFP_array, 
												lfp_sig, LFP_rec_ch_names, 
												sf_LFP, external_file, 
												BIP_channel, 
												external_rec_ch_names, 
												sf_external, saving_path, 
												saving_format, CROP_BOTH, 
												SHOW_FIGURES = True
												)
	plot_LFP_external(session_ID, LFP_df_offset, external_df_offset, sf_LFP, 
				   sf_external, ch_idx_lfp, ch_index_external, saving_path, 
				   SHOW_FIGURES)

	#  OPTIONAL : check timeshift:
	if CHECK_FOR_TIMESHIFT:
		print('Starting timeshift analysis...')
		check_timeshift(session_ID, LFP_df_offset, sf_LFP, external_df_offset, 
				  sf_external, saving_path, SHOW_FIGURES
				  )

	# OPTIONAL : check for packet loss:
	if CHECK_FOR_PACKET_LOSS:
		_update_and_save_params('JSON_FILE', json_filename, session_ID, 
						  saving_path
						  )
		json_object = _load_sourceJSON(json_filename)
		check_packet_loss(json_object)

	# OPTIONAL : plot cardiac artifact:
	#ecg(session_ID, LFP_df_offset, sf_LFP, external_df_offset, 
		#sf_external, saving_path, xmin= 0.25, xmax= 0.36, SHOW_FIGURES=True
		#)


if __name__ == '__main__':
    main()
