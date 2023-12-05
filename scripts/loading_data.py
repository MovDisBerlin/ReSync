from utils import _update_and_save_params, _is_channel_in_list
import numpy as np
import os
import sys
import json
from scipy.io import loadmat
from mne.io import read_raw_fieldtrip
from os.path import join
#import scripts.config as cfg

#### LFP DATASET ####

def _load_mat_file(sub_ID, filename: str, saving_path):
    """"
    Reads (perceived) .mat-file in FieldTrip
    structure using mne-function
    
    Input:
        - sub: str code of sub
        - filename: str of only .mat-filename
    
    Returns:
        - data: mne-object of .mat file
    """

    # Error if filename doesn´t end with .mat
    assert filename[-4:] == '.mat', (
        f'filename no .mat INCORRECT extension: {filename}'
    )

    # find the path to the raw_perceive folder of a subject
    source_path = "sourcedata"

    _update_and_save_params('SUBJECT_ID', sub_ID, sub_ID, saving_path)
    _update_and_save_params('FNAME_LFP', filename, sub_ID, saving_path)


    data = read_raw_fieldtrip(
        join(source_path, filename),
        info={}, # add info here
        data_name='data',  # name of heading dict/ variable of original MATLAB object
		)
    
    return data


# extract variables from LFP recording:
def _load_data_lfp(sub_ID, dataset_lfp, ch_idx_lfp, saving_path):

	LFP_array = dataset_lfp.get_data()
	ch_index = ch_idx_lfp
	lfp_sig = dataset_lfp.get_data()[ch_index]
	LFP_rec_ch_names = dataset_lfp.ch_names
	sf_LFP = int(dataset_lfp.info["sfreq"])

	n_chan = len(dataset_lfp.ch_names)
	time_duration_LFP = (dataset_lfp.n_times/dataset_lfp.info['sfreq']).astype(float)

	_update_and_save_params('CH_IDX_LFP', ch_index, sub_ID, saving_path)
	_update_and_save_params('LFP_REC_CH_NAMES', LFP_rec_ch_names, sub_ID, saving_path)
	_update_and_save_params('LFP_REC_DURATION', time_duration_LFP, sub_ID, saving_path)
	_update_and_save_params('sf_LFP', sf_LFP, sub_ID, saving_path)	


	return LFP_array, lfp_sig, LFP_rec_ch_names, sf_LFP


#### External data recorder dataset ####

def _load_TMSi_artefact_channel(
	sub_ID,
    TMSi_data,
	fname_external,
	AUTOMATIC: bool,
	saving_path
):
    
	"""
	Function that takes a poly5 object and returns in an array the channel 
	which will be used for sync ("BIP 01" in our settings),	and in another 
	array the timescale in milliseconds of the TMSi recording. It also prints 
	information about the recording (duration, channels, sampling frequency,...)
	
	Input:
		- TMSi_data : TMSiFileFormats.file_readers.poly5reader.Poly5Reader

	Returns:
		- TMSi_channel (np.ndarray with shape (y,)): the channel of the external 
            recording to be used for alignment (the one containing deep brain 
            stimulation artefacts = the channel recorded with the bipolar 
            electrode, y datapoints)
        - TMSi_file (np.ndarray with shape: (x, y)): the external recording 
            containing all recorded channels (x channels, y datapoints)
		- external_rec_ch_names (list of x names): the names of all the channels 
            recorded externally
		- sf_external (int): sampling frequency of external recording
	"""

	#import settings
	#json_path = os.path.join(os.getcwd(), 'config')
	#json_filename = 'config.json'  # dont forget json extension
	#with open(os.path.join(json_path, json_filename), 'r') as f:
		#loaded_dict =  json.load(f)

	# Conversion of .Poly5 to MNE raw array
	toMNE = True
	TMSi_rec = TMSi_data.read_data_MNE()
	external_rec_ch_names = TMSi_rec.ch_names
	n_chan = len(TMSi_rec.ch_names)
	time_duration_TMSi_s = (TMSi_rec.n_times/TMSi_rec.info['sfreq']).astype(float)
	sf_external = int(TMSi_rec.info['sfreq'])

	_update_and_save_params('FNAME_EXTERNAL', fname_external, sub_ID, saving_path)
	_update_and_save_params('EXTERNAL_REC_CH_NAMES', external_rec_ch_names, sub_ID, saving_path)	
	_update_and_save_params('EXTERNAL_REC_DURATION', time_duration_TMSi_s, sub_ID, saving_path)
	_update_and_save_params('sf_EXTERNAL', sf_external, sub_ID, saving_path)	

	if AUTOMATIC :
		# recorded with TMSi SAGA, electrode BIP 01
		if sf_external in {4000, 4096, 512} and _is_channel_in_list(external_rec_ch_names, 'BIP 01'):
			ch_index = TMSi_rec.ch_names.index('BIP 01')
			_update_and_save_params('CH_NAME_EXTERNAL', 'BIP 01', sub_ID, saving_path)				
			_update_and_save_params('CH_IDX_EXTERNAL', ch_index, sub_ID, saving_path)	
		# recorded with TMSi Porti, electrode Bip25 
		elif sf_external == 2048 and _is_channel_in_list(external_rec_ch_names, 'Bip25'):
			ch_index = TMSi_rec.ch_names.index('Bip25')
			_update_and_save_params('CH_NAME_EXTERNAL', 'Bip25', sub_ID, saving_path)				
			_update_and_save_params('CH_IDX_EXTERNAL', ch_index, sub_ID, saving_path)
		else:
			raise ValueError (
				f'Data recorder or electrode unknown, please set AUTOMATIC as False' 
				f'Choose a channel in the following list:  {external_rec_ch_names}'
			)
	else:
		ch_name = input("Enter name of external channel containing sync artefacts: ")
		ch_index = TMSi_rec.ch_names.index(ch_name)
		_update_and_save_params('CH_NAME_EXTERNAL', ch_name, sub_ID, saving_path)		
		_update_and_save_params('CH_IDX_EXTERNAL', ch_index, sub_ID, saving_path)

	BIP_channel = TMSi_rec.get_data()[ch_index]
	external_file = TMSi_rec.get_data()

	# save dict as JSON, 'w' stands for write
	#with open(os.path.join(json_path, json_filename), 'w') as f:
			#json.dump(loaded_dict, f, indent=4)
	
	#print(     
		#f'The data object has:\n\t{TMSi_rec.n_times} time samples,'      
		#f'\n\tand a sample frequency of {TMSi_rec.info["sfreq"]} Hz'      
		#f'\n\twith a recording duration of {time_duration_TMSi_s} seconds.'      
		#f'\n\t{n_chan} channels were labeled as \n{TMSi_rec.ch_names}.'
	#)
	
	#print(
		#f'The channel used to align datas is the channel named {TMSi_rec.ch_names[ch_index]} ' 
		#f'and has index {ch_index}'
	#)

	return BIP_channel, external_file, external_rec_ch_names, sf_external



