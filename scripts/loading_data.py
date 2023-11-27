import numpy as np
import os
import sys
import json
#import scripts.config as cfg

# Function to open TMSi data

def _load_TMSi_artefact_channel(
    TMSi_data
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
	json_path = os.path.join(os.getcwd(), 'config')
	json_filename = 'config.json'  # dont forget json extension
	with open(os.path.join(json_path, json_filename), 'r') as f:
		loaded_dict =  json.load(f)

	# Conversion of .Poly5 to MNE raw array
	toMNE = True
	TMSi_rec = TMSi_data.read_data_MNE()
	external_rec_ch_names = TMSi_rec.ch_names
	n_chan = len(TMSi_rec.ch_names)
	time_duration_TMSi_s = (TMSi_rec.n_times/TMSi_rec.info['sfreq']).astype(float)
	sf_external = int(TMSi_rec.info['sfreq'])

	if loaded_dict['AUTOMATIC']:
		# recorded with TMSi SAGA, electrode BIP 01
		if sf_external in {4000, 4096, 512} and _is_channel_in_list(external_rec_ch_names, 'BIP 01'):
			loaded_dict['CH_NAME_BIP'] = 'BIP 01' 
			ch_index = TMSi_rec.ch_names.index('BIP 01')
		# recorded with TMSi Porti, electrode Bip25 
		elif sf_external == 2048 and _is_channel_in_list(external_rec_ch_names, 'Bip25'):
			loaded_dict['CH_NAME_BIP'] = 'Bip25' 
			ch_index = TMSi_rec.ch_names.index('Bip25')
		else:
			raise ValueError (
				f'Data recorder or electrode unknown, please set automatic as False' 
				f'and change CH_NAME_BIP directly in json file. Choose a channel in' 
				f'the following list:  {external_rec_ch_names}'
			)
	else:
		ch_index = TMSi_rec.ch_names.index(loaded_dict['CH_NAME_BIP'])

	BIP_channel = TMSi_rec.get_data()[ch_index]
	loaded_dict['BIP_CH_INDEX'] = ch_index
	external_file = TMSi_rec.get_data()

	# save dict as JSON, 'w' stands for write
	with open(os.path.join(json_path, json_filename), 'w') as f:
			json.dump(loaded_dict, f, indent=4)
	
	print(     
		f'The data object has:\n\t{TMSi_rec.n_times} time samples,'      
		f'\n\tand a sample frequency of {TMSi_rec.info["sfreq"]} Hz'      
		f'\n\twith a recording duration of {time_duration_TMSi_s} seconds.'      
		f'\n\t{n_chan} channels were labeled as \n{TMSi_rec.ch_names}.'
	)
	
	print(
		f'The channel used to align datas is the channel named {TMSi_rec.ch_names[ch_index]} ' 
		f'and has index {ch_index}'
	)

	return BIP_channel, external_file, external_rec_ch_names, sf_external



def _load_LFP_rec(sub_ID, session, condition, task, run):
	project_path = os.getcwd()
	pyPerceive_path = os.chdir("C:\\Users\\Juliette\\Research\\Projects\\PyPerceive\\code")
	sys.path.append(pyPerceive_path)
	from PerceiveImport.classes import (
		main_class, modality_class, metadata_class,
		session_class, condition_class, task_class,
		contact_class, run_class
	)
	import PerceiveImport.methods.load_rawfile as load_rawfile
	import PerceiveImport.methods.find_folders as find_folders
	import PerceiveImport.methods.metadata_helpers as metaHelpers

	#reset the proper working directory for the analysis
	os.chdir(project_path)
	os.getcwd()

	sub = main_class.PerceiveData(
	sub = sub_ID, 
	incl_modalities=['streaming'],
	incl_session = [f'{session}'],
	incl_condition =[f'{condition}'],
	incl_task = [f'{task}'],
	# incl_contact = ["RingL", "SegmInterR", "SegmIntraR"],
	import_json=False,
	warn_for_metaNaNs=False,
	allow_NaNs_in_metadata=False
	)

	LFP_rec = sub.streaming.fu24m.m0s0.rest.run1.data

	return LFP_rec



# extract variables from LFP recording:
def _set_lfp_data(LFP_rec):

	#import settings
	json_path = os.path.join(os.getcwd(), 'config')
	json_filename = 'config.json'
	with open(os.path.join(json_path, json_filename), 'r') as f:
		loaded_dict =  json.load(f)

	LFP_array = LFP_rec.get_data()
	ch_index = loaded_dict['LFP_CH_INDEX']
	lfp_sig = LFP_rec.get_data()[ch_index]
	LFP_rec_ch_names = LFP_rec.ch_names
	sf_LFP = int(LFP_rec.info["sfreq"])

	n_chan = len(LFP_rec.ch_names)
	time_duration_LFP = (LFP_rec.n_times/LFP_rec.info['sfreq']).astype(float)
	print(     
		f'The data object has:\n\t{LFP_rec.n_times} time samples,'      
		f'\n\tand a sample frequency of {LFP_rec.info["sfreq"]} Hz'      
		f'\n\twith a recording duration of {time_duration_LFP} seconds.'      
		f'\n\t{n_chan} channels were labeled as \n{LFP_rec.ch_names}.'
	)
	print(
		f'The channel containing artefacts has index {ch_index} and is named {LFP_rec.ch_names[ch_index]}'
	)

	return LFP_array, lfp_sig, LFP_rec_ch_names, sf_LFP


def _is_channel_in_list(
		channel_array, 
		desired_channel_name
):
    if desired_channel_name.lower() in (channel.lower() for channel in channel_array):
        return True
    else:
        return False