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

2. run main.py

Results:
The results will be saved in the results folder, in a sub-folder named after the 
session_ID parameter.
8 figures are automatically generated and saved:
- Fig 1: External bipolar channel raw plot (of the channel containing artifacts)
- Fig 2: External bipolar channel with artifact detected
- Fig 3: External bipolar channel - first artifact detected (zoom of Fig2)
- Fig 4: Intracranial channel raw plot (of the channel containing artifacts)
- Fig 5 : Intracranial channel with artifact detected - kernel ID (indicates which 
kernel was used to detect the artifact properly)
- Fig 6: Intracranial channel - first artifact detected - kernel ID (zoom of Fig5)
- (Fig 7:Intracranial channel - first artifact corrected by user)
Fig 7 is only generated when no automatic detection of the artifact was possible,
and the user therefore had to manually select it (rare cases)
- Fig 8: Intracranial and external recordings aligned

IF the timeshift analysis is also performed, there will be one supplementary figure:
- Fig A : Timeshift - Intracranial and external recordings aligned - last artifact

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
from utils import _update_and_save_params, _get_input_y_n, _get_user_input
from tmsi_poly5reader import Poly5Reader
from resync_function import (
    detect_artifacts_in_external_recording, 
	detect_artifacts_in_intracranial_recording,
    synchronize_recordings, 
    save_synchronized_recordings
)
from packet_loss import check_packet_loss

def main(
	session_ID = 'test_thresh', 
	fname_lfp = 'sub-20230905PStn_ses-2023121802263096_run-BrainSense20231218024800.mat', 
	ch_idx_lfp = 0,
	fname_external = 'sub084_3mfu_m1s0_BrStr_restTap - 20231218T154811.DATA.Poly5',
	BIP_ch_name = 'Bip25', 
	saving_format = 'brainvision',
	json_filename = None,
	CROP_BOTH = True,
	CHECK_FOR_TIMESHIFT = False,
	CHECK_FOR_PACKET_LOSS = False
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
		dataset_lfp = load_mat_file(
			session_ID = session_ID, 
			filename = fname_lfp, 
			saving_path = saving_path, 
			source_path = source_path
			)
		(LFP_array, lfp_sig, 
   		LFP_rec_ch_names, sf_LFP) = load_data_lfp(
			   session_ID = session_ID, 
			   dataset_lfp = dataset_lfp, 
			   ch_idx_lfp = ch_idx_lfp, 
			   saving_path = saving_path
			   )
	if fname_lfp.endswith('.csv'):
		(LFP_array, lfp_sig, 
   		LFP_rec_ch_names, sf_LFP) = load_intracranial_csv_file(
			   session_ID = session_ID, 
			   filename = fname_lfp,
			   ch_idx_lfp = ch_idx_lfp,
			   saving_path = saving_path,
			   source_path = source_path
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
   		ch_index_external) = load_TMSi_artifact_channel(
			   session_ID = session_ID, 
			   TMSi_data = TMSi_data, 
			   fname_external = fname_external,
			   BIP_ch_name = BIP_ch_name, 
			   saving_path = saving_path
			   )
	if fname_external.endswith('.csv'):
		(external_file, BIP_channel, external_rec_ch_names, 
   		sf_external, ch_index_external) = load_external_csv_file(
			   session_ID = session_ID, 
			   filename = fname_external, 
			   BIP_ch_name = BIP_ch_name, 
			   saving_path = saving_path,
			   source_path = source_path
			   )

	#  2. FIND ARTIFACTS IN BOTH RECORDINGS:
		# 2.1. Find artifacts in external recording:
	art_start_BIP = detect_artifacts_in_external_recording(
		session_ID = session_ID,
		BIP_channel = BIP_channel,
		sf_external = sf_external,
		saving_path = saving_path,
		start_index = 0
	)
	artifact_correct = _get_input_y_n(
		"Is the external artifact properly selected ? "
		)
	if artifact_correct == 'y':
		_update_and_save_params(
			key = 'ART_TIME_BIP', 
			value = art_start_BIP,
			session_ID = session_ID, 
			saving_path = saving_path
			)
	else: 
		start_later = _get_user_input(
			"How many seconds in the beginning should be ignored?"
			)
		start_later_index = start_later*sf_external
		art_start_BIP = detect_artifacts_in_external_recording(
			session_ID = session_ID,
			BIP_channel = BIP_channel,
			sf_external = sf_external,
			saving_path = saving_path,
			start_index = start_later_index
		)
		_update_and_save_params(
			key = 'ART_TIME_BIP', 
			value = art_start_BIP,
			session_ID = session_ID, 
			saving_path = saving_path
			)

		# 2.2. Find artifacts in intracranial recording:
	kernels = ['thresh', '2', '1', 'manual']
	# kernel 1 only searches for the steep decrease
    # kernel 2 is more custom and takes into account the steep decrease and slow recover
	# manual kernel is for none of the tw previous kernels work. Then the artifact
	# has to be manually selected by the user, in a pop up window that will automatically open.
	for kernel in kernels:
		print('Running resync with kernel = {}...'.format(kernel))
		art_start_LFP = detect_artifacts_in_intracranial_recording(
			session_ID = session_ID, 
			lfp_sig = lfp_sig,
			sf_LFP = sf_LFP,
			saving_path = saving_path, 
			kernel = kernel
			)
		artifact_correct = _get_input_y_n(
			"Is the intracranial artifact properly selected ? "
			)
		if artifact_correct == 'y':
			_update_and_save_params(
				key = 'ART_TIME_LFP', 
				value = art_start_LFP, 
				session_ID = session_ID, 
				saving_path = saving_path
				)
			_update_and_save_params(
				key = 'KERNEL', 
				value = kernel, 
				session_ID = session_ID, 
				saving_path = saving_path
				)
			break

	# 3. SYNCHRONIZE RECORDINGS TOGETHER:
	(LFP_df_offset, external_df_offset) = synchronize_recordings(
		LFP_array = LFP_array,
		external_file = external_file,
		art_start_LFP = art_start_LFP,
		art_start_BIP = art_start_BIP,
		LFP_rec_ch_names = LFP_rec_ch_names, 
		external_rec_ch_names = external_rec_ch_names, 
		sf_LFP = sf_LFP,
		sf_external = sf_external,
		CROP_BOTH = CROP_BOTH
		)

	# 4. SAVE SYNCHRONIZED RECORDINGS:
	_update_and_save_params(
		key = 'SAVING_FORMAT', 
		value = saving_format, 
		session_ID = session_ID, 
		saving_path = saving_path
		) 
	save_synchronized_recordings(
		session_ID = session_ID,
    	LFP_df_offset = LFP_df_offset, 
    	external_df_offset = external_df_offset,
    	LFP_rec_ch_names = LFP_rec_ch_names,
    	external_rec_ch_names = external_rec_ch_names,
    	sf_LFP = sf_LFP,
    	sf_external = sf_external,
    	saving_format = saving_format,
    	saving_path = saving_path,
    	CROP_BOTH = CROP_BOTH
		)


	# 5. PLOT SYNCHRONIZED RECORDINGS:
	plot_LFP_external(
		session_ID = session_ID, 
		LFP_df_offset = LFP_df_offset, 
		external_df_offset = external_df_offset, 
		sf_LFP = sf_LFP, 
		sf_external = sf_external, 
		ch_idx_lfp = ch_idx_lfp, 
		ch_index_external = ch_index_external, 
		saving_path = saving_path)

	#  OPTIONAL : check timeshift:
	if CHECK_FOR_TIMESHIFT:
		print('Starting timeshift analysis...')
		check_timeshift(
			session_ID = session_ID, 
			LFP_df_offset = LFP_df_offset, 
			sf_LFP = sf_LFP, 
			external_df_offset = external_df_offset, 
			sf_external = sf_external, 
			saving_path = saving_path
			)

	# OPTIONAL : check for packet loss:
	if CHECK_FOR_PACKET_LOSS:
		_update_and_save_params(
			key = 'JSON_FILE', 
			value = json_filename, 
			session_ID = session_ID, 
			saving_path = saving_path
			)
		json_object = load_sourceJSON(
			json_filename = json_filename, 
			source_path = source_path
			)
		check_packet_loss(json_object = json_object)

	# OPTIONAL : plot cardiac artifact:
	ecg(
		session_ID = session_ID, 
		LFP_df_offset = LFP_df_offset, 
		sf_LFP = sf_LFP, 
		external_df_offset = external_df_offset, 
		sf_external = sf_external, 
		saving_path = saving_path, 
		xmin = 0.25, 
		xmax = 0.36
		)


if __name__ == '__main__':
    main()
