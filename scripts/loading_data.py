import json
import pandas as pd
from mne.io import read_raw_fieldtrip
from os.path import join

from utils import _update_and_save_params

#### LFP DATASET ####

def load_sourceJSON(json_filename: str, source_path):

    """
    Reads source JSON file  

    Input:
        - fname: str of JSON filename

    Returns: 
        - json_object: loaded JSON file

    """

    with open(join(source_path, json_filename), 'r') as f:
        json_object = json.loads(f.read())

    return json_object


def load_mat_file(
		session_ID: str, 
		filename: str, 
		saving_path: str,
		source_path):
    """"
    Reads .mat-file in FieldTrip structure using mne-function
    
    Input:
        - sub_ID: str 
        - filename: str of only .mat-filename
		- saving_path: str of path to save the parameters
    
    Returns:
        - data: mne-object of .mat file
    """

    # Error if filename doesn´t end with .mat
    assert filename[-4:] == '.mat', (
        f'filename no .mat INCORRECT extension: {filename}'
    )

    _update_and_save_params(
		key = 'SUBJECT_ID', 
		value = session_ID, 
		session_ID = session_ID, 
		saving_path = saving_path
		)
    _update_and_save_params(
		key = 'FNAME_LFP', 
		value = filename, 
		session_ID = session_ID, 
		saving_path = saving_path
		)


    data = read_raw_fieldtrip(
        join(source_path, filename),
        info={},
        data_name='data',  
		)
    
    return data


def load_intracranial_csv_file(
		session_ID: str, 
		filename: str, 
		ch_idx_lfp: int, 
		saving_path: str,
		source_path
		):

	_update_and_save_params(
		key = 'SUBJECT_ID', 
		value = session_ID, 
		session_ID = session_ID, 
		saving_path = saving_path
		)
	_update_and_save_params(
		key = 'FNAME_LFP', 
		value = filename, 
		session_ID = session_ID, 
		saving_path = saving_path
		)
	sf_LFP = int(filename[filename.find('Hz')-3:filename.find('Hz')])
	# load a csv file :
	dataset_lfp = pd.read_csv(join(source_path, filename))
	# convert to array :
	LFP_array = dataset_lfp.to_numpy()
	# transpose array:
	LFP_array = LFP_array.transpose()
	# store the first column of dataset_lfp in an array called lfp_sig:
	lfp_sig = LFP_array[ch_idx_lfp,:]
	LFP_rec_ch_names = list(dataset_lfp.columns)

	time_duration_LFP = (len(lfp_sig)/sf_LFP)

	_update_and_save_params(
		key = 'CH_IDX_LFP', 
		value = ch_idx_lfp, 
		session_ID = session_ID, 
		saving_path = saving_path
		)
	_update_and_save_params(
		key = 'LFP_REC_CH_NAMES', 
		value = LFP_rec_ch_names, 
		session_ID = session_ID,
		saving_path = saving_path
		)
	_update_and_save_params(
		key = 'LFP_REC_DURATION', 
		value = time_duration_LFP, 
		session_ID = session_ID,
		saving_path = saving_path
		)
	_update_and_save_params(
		key = 'sf_LFP', 
		value = sf_LFP, 
		session_ID = session_ID, 
		saving_path = saving_path
		)	

	return LFP_array, lfp_sig, LFP_rec_ch_names, sf_LFP



def load_external_csv_file(
		session_ID: str, 
		filename: str, 
		BIP_ch_name: str, 
		saving_path: str,
		source_path
		):
	
	_update_and_save_params(
		key = 'SUBJECT_ID', 
		value = session_ID, 
		session_ID = session_ID, 
		saving_path = saving_path
		)
	_update_and_save_params(
		key = 'FNAME_EXTERNAL', 
		value = filename, 
		session_ID = session_ID, 
		saving_path = saving_path
		)
	sf_external = int(filename[filename.find('Hz')-4:filename.find('Hz')])
	# load a csv file :
	dataset_external = pd.read_csv(join(source_path, filename))

	external_file = dataset_external.to_numpy()
	external_file = external_file.transpose()
	external_rec_ch_names = list(dataset_external.columns)

	ch_index_external = external_rec_ch_names.index(BIP_ch_name)
	BIP_channel = external_file[ch_index_external,:]

	time_duration_external_s = (len(BIP_channel)/sf_external)

	_update_and_save_params(
		key = 'FNAME_EXTERNAL', 
		value = filename, 
		session_ID = session_ID, 
		saving_path = saving_path
		)
	_update_and_save_params(
		key = 'EXTERNAL_REC_CH_NAMES', 
		value = external_rec_ch_names, 
		session_ID = session_ID, 
		saving_path = saving_path
		)	
	_update_and_save_params(
		key = 'EXTERNAL_REC_DURATION', 
		value = time_duration_external_s, 
		session_ID = session_ID, 
		saving_path = saving_path
		)
	_update_and_save_params(
		key = 'sf_EXTERNAL', 
		value = sf_external, 
		session_ID = session_ID, 
		saving_path = saving_path
		)	
	_update_and_save_params(
		key = 'CH_IDX_EXTERNAL', 
		value = ch_index_external, 
		session_ID = session_ID, 
		saving_path = saving_path
		)

	return (external_file, BIP_channel, external_rec_ch_names, sf_external, 
		 ch_index_external)



      
# extract variables from LFP recording:
def load_data_lfp(
		session_ID: str, 
		dataset_lfp, 
		ch_idx_lfp, 
		saving_path: str
		):

	if type(ch_idx_lfp) == float: ch_idx_lfp = int(ch_idx_lfp)

	LFP_array = dataset_lfp.get_data()
	lfp_sig = dataset_lfp.get_data()[ch_idx_lfp]
	LFP_rec_ch_names = dataset_lfp.ch_names
	sf_LFP = int(dataset_lfp.info["sfreq"])
	time_duration_LFP = (dataset_lfp.n_times/dataset_lfp.info['sfreq']).astype(float)

	_update_and_save_params(
		key = 'CH_IDX_LFP', 
		value = ch_idx_lfp, 
		session_ID = session_ID, 
		saving_path = saving_path
		)
	_update_and_save_params(
		key = 'LFP_REC_CH_NAMES', 
		value = LFP_rec_ch_names, 
		session_ID = session_ID, 
		saving_path = saving_path
		)
	_update_and_save_params(
		key = 'LFP_REC_DURATION', 
		value = time_duration_LFP, 
		session_ID = session_ID, 
		saving_path = saving_path
		)
	_update_and_save_params(
		key = 'sf_LFP', 
		value = sf_LFP, 
		session_ID = session_ID, 
		saving_path = saving_path
		)	


	return LFP_array, lfp_sig, LFP_rec_ch_names, sf_LFP


#### External data recorder dataset ####

def load_TMSi_artifact_channel(
	session_ID: str,
    TMSi_data,
	fname_external: str,
	BIP_ch_name: str,
	saving_path: str
):
    
	"""
	Takes a poly5 object containing all the external channels recorded.
	It extracts the channel containing the artifacts, which will be used for 
	synchronization (usually "BIP 01" in our settings). It also returns the
	whole external recording (in an array), the names of all the channels 
	recorded externally, the sampling frequency of the external recording and 
	the index of the bipolar channel in the external recording.

	Input:
		- sub_ID: str, subject ID
		- TMSi_data: TMSiFileFormats.file_readers.poly5reader.Poly5Reader
		- fname_external: str, name of the external recording session
		- BIP_ch_name: str, name of the bipolar channel, containing the artifacts
		- saving_path: str, path to save the parameters

	Returns:
		- BIP_channel (np.ndarray with shape (y,)): the channel of the external 
            recording to be used for alignment (the one containing deep brain 
            stimulation artifacts = the channel recorded with the bipolar 
            electrode, y datapoints)
        - external_file (np.ndarray with shape: (x, y)): the external recording 
            containing all recorded channels (x channels, y datapoints)
		- external_rec_ch_names (list of x names): the names of all the channels 
            recorded externally
		- sf_external (int): sampling frequency of external recording
		- ch_index (int): index of the bipolar channel in the external recording 
			(BIP_channel)
	"""

	# Conversion of .Poly5 to MNE raw array
	toMNE = True
	TMSi_rec = TMSi_data.read_data_MNE()
	external_rec_ch_names = TMSi_rec.ch_names
	n_chan = len(TMSi_rec.ch_names)
	time_duration_TMSi_s = (TMSi_rec.n_times/TMSi_rec.info['sfreq']).astype(float)
	sf_external = int(TMSi_rec.info['sfreq'])

	_update_and_save_params(
		key = 'FNAME_EXTERNAL', 
		value = fname_external, 
		session_ID = session_ID, 
		saving_path = saving_path
		)
	_update_and_save_params(
		key = 'EXTERNAL_REC_CH_NAMES', 
		value = external_rec_ch_names,
		session_ID = session_ID, 
		saving_path = saving_path
		)	
	_update_and_save_params(
		key = 'EXTERNAL_REC_DURATION', 
		value = time_duration_TMSi_s, 
		session_ID = session_ID, 
		saving_path = saving_path
		)
	_update_and_save_params(
		key = 'sf_EXTERNAL', 
		value = sf_external, 
		session_ID = session_ID, 
		saving_path = saving_path
		)	
      
	ch_index = TMSi_rec.ch_names.index(BIP_ch_name)
	_update_and_save_params(
		key = 'CH_IDX_EXTERNAL', 
		value = ch_index, 
		session_ID = session_ID, 
		saving_path = saving_path
		)
	
	BIP_channel = TMSi_rec.get_data()[ch_index]
	external_file = TMSi_rec.get_data()


	return (external_file, BIP_channel, external_rec_ch_names, 
		 sf_external, ch_index)



