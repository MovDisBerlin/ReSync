from utils import _update_and_save_params
import json
from mne.io import read_raw_fieldtrip
from os.path import join

#### LFP DATASET ####

def _load_sourceJSON(json_filename: str):

    """
    Reads source JSON file 

    Input:
        - subject = str, e.g. "024"
        - fname = str of filename, e.g. "Report_Json_Session_Report_20221205T134700.json"

    Returns: 
        - data: json.loads() loaded JSON file

    """

    # find the path to the folder of a subject
    source_path = "sourcedata"

    with open(join(source_path, json_filename), 'r') as f:
        json_object = json.loads(f.read())

    return json_object


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

	if type(ch_idx_lfp) == float: ch_idx_lfp = int(ch_idx_lfp)

	LFP_array = dataset_lfp.get_data()
	lfp_sig = dataset_lfp.get_data()[ch_idx_lfp]
	LFP_rec_ch_names = dataset_lfp.ch_names
	sf_LFP = int(dataset_lfp.info["sfreq"])

	n_chan = len(dataset_lfp.ch_names)
	time_duration_LFP = (dataset_lfp.n_times/dataset_lfp.info['sfreq']).astype(float)

	_update_and_save_params('CH_IDX_LFP', ch_idx_lfp, sub_ID, saving_path)
	_update_and_save_params('LFP_REC_CH_NAMES', LFP_rec_ch_names, sub_ID, saving_path)
	_update_and_save_params('LFP_REC_DURATION', time_duration_LFP, sub_ID, saving_path)
	_update_and_save_params('sf_LFP', sf_LFP, sub_ID, saving_path)	


	return LFP_array, lfp_sig, LFP_rec_ch_names, sf_LFP


#### External data recorder dataset ####

def _load_TMSi_artefact_channel(
	sub_ID,
    TMSi_data,
	fname_external,
	BIP_ch_name,
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
      
	ch_index = TMSi_rec.ch_names.index(BIP_ch_name)
	_update_and_save_params('CH_IDX_EXTERNAL', ch_index, sub_ID, saving_path)
	
	BIP_channel = TMSi_rec.get_data()[ch_index]
	external_file = TMSi_rec.get_data()


	return BIP_channel, external_file, external_rec_ch_names, sf_external, ch_index



