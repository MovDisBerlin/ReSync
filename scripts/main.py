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

from loading_data import (
	load_mat_file, 
	load_data_lfp, 
	load_TMSi_artifact_channel, 
	load_sourceJSON, 
	load_intracranial_csv_file, 
	load_external_csv_file
	)
from plotting import plot_LFP_external, ecg
from timeshift import check_timeshift
from utils import _update_and_save_params, _get_input_y_n
from tmsi_poly5reader import Poly5Reader
from resync_function import detect_artifacts_in_recordings, synchronize_recordings, save_synchronized_recordings
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

	#  1. LOADING DATASETS

		##  Intracranial LFP (here Percept datas)
	# the resync function needs 4 information about the intracranial recording:
	# 1. the intracranial recording itself, containing all the recorded channels (LFP_array)
	# 2. the intracranial recording, but only the channel containing the stimulation artifacts (lfp_sig)
	# 3. the names of all the channels recorded intracerebrally (LFP_rec_ch_names)
	# 4. the sampling frequency of the intracranial recording (sf_LFP)
	if fname_lfp.endswith('.mat'):
		dataset_lfp= load_mat_file(session_ID, fname_lfp, saving_path, 
							 source_path)
		(LFP_array, lfp_sig, 
   		LFP_rec_ch_names, sf_LFP) = load_data_lfp(session_ID, dataset_lfp, 
												ch_idx_lfp, saving_path
												)
	if fname_lfp.endswith('.csv'):
		(LFP_array, lfp_sig, 
   		LFP_rec_ch_names, sf_LFP) = load_intracranial_csv_file(session_ID, 
															 fname_lfp,
															 ch_idx_lfp,
															 saving_path,
															 source_path
															 )


		##  External data recorder
	# the resync function needs 5 information about the external recording:
	# 1. the external recording itself, containing all the recorded channels (external_file)
	# 2. the channel containing the stimulation artifacts (BIP_channel)
	# 3. the names of all the channels recorded externally (external_rec_ch_names)
	# 4. the sampling frequency of the external recording (sf_external)
	# 5. the index of the bipolar channel in the external recording (ch_index_external)
	if fname_external.endswith('.Poly5'):
		TMSi_data = Poly5Reader(join(source_path, fname_external)) 
		(external_file, BIP_channel, external_rec_ch_names, sf_external, 
   		ch_index_external) = load_TMSi_artifact_channel(session_ID, TMSi_data, 
													 fname_external, 
													 BIP_ch_name, saving_path
													 )
	if fname_external.endswith('.csv'):
		(external_file, BIP_channel, external_rec_ch_names, 
   		sf_external, ch_index_external) = load_external_csv_file(session_ID, 
															   fname_external, 
															   BIP_ch_name, 
															   saving_path,
															   source_path
															   )

	#  2. FIND ARTIFACTS IN BOTH RECORDINGS:
	kernels = ['2', '1', 'manual']
	for kernel in kernels:
		print('Running resync with kernel = {}...'.format(kernel))
		art_start_LFP, art_start_BIP = detect_artifacts_in_recordings(session_ID, 
																lfp_sig, sf_LFP, 
																BIP_channel, 
																sf_external, 
																saving_path, 
																kernel, 
																SHOW_FIGURES = True)
		artifact_correct = _get_input_y_n("Are artifacts properly selected ? ")
		if artifact_correct == 'y':
			_update_and_save_params('ART_TIME_LFP', art_start_LFP, 
                                session_ID, saving_path)
			_update_and_save_params('KERNEL', kernel, session_ID, saving_path)
			_update_and_save_params('ART_TIME_BIP', art_start_BIP, 
                                session_ID, saving_path)
			break

	# 3. SYNCHRONIZE RECORDINGS TOGETHER:
	LFP_df_offset, external_df_offset = synchronize_recordings(LFP_array,
															external_file,
															art_start_LFP,
															art_start_BIP,
															LFP_rec_ch_names, 
															external_rec_ch_names, 
															sf_LFP,
															sf_external,
															CROP_BOTH)

	# 4. SAVE SYNCHRONIZED RECORDINGS:
	_update_and_save_params('SAVING_FORMAT', saving_format, session_ID, saving_path) 
	save_synchronized_recordings(
		session_ID,
    	LFP_df_offset, 
    	external_df_offset,
    	LFP_rec_ch_names,
    	external_rec_ch_names,
    	sf_LFP,
    	sf_external,
    	saving_format,
    	saving_path,
    	CROP_BOTH
		)


	# 5. PLOT SYNCHRONIZED RECORDINGS:
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
		json_object = load_sourceJSON(json_filename, source_path)
		check_packet_loss(json_object)

	# OPTIONAL : plot cardiac artifact:
	#ecg(session_ID, LFP_df_offset, sf_LFP, external_df_offset, 
		#sf_external, saving_path, xmin= 0.25, xmax= 0.36, SHOW_FIGURES=True
		#)


if __name__ == '__main__':
    main()
