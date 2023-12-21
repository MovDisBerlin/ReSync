"""
utilisation function
"""

import os
import json
from tkinter.filedialog import askdirectory
import scipy
import numpy as np
import operator



def _define_folders():

    """
    This function is used if the user hasn't already define 
    the saving path in the config.json file (back up function).
    """

    #import settings
    json_path = os.path.join(os.getcwd(), 'config')
    json_filename = 'config.json'
    with open(os.path.join(json_path, json_filename), 'r') as f:
        loaded_dict =  json.load(f)

    saving_folder = askdirectory(title= 'Select Saving Folder') 
    saving_path = os.path.join(saving_folder, loaded_dict['subject_ID'])
    if not os.path.isdir(saving_path):
        os.makedirs(saving_path)

    return saving_path


parameters = {}

def _update_and_save_params(key, value, sub_ID, saving_path):
    parameters[key] = value
    parameter_filename = ('parameters_' + str(sub_ID) + '.json')
    json_file_path = os.path.join(saving_path, parameter_filename)
    with open(json_file_path, 'w') as json_file:
        json.dump(parameters, json_file, indent=4)



def _is_channel_in_list(
		channel_array, 
		desired_channel_name
):
    if desired_channel_name.lower() in (channel.lower() for channel in channel_array):
        return True
    else:
        return False

### FUNCTIONS FOR CONVERSION time/index ###

# Conversion between index and timestamps

def _convert_index_to_time(
    art_idx: list,
    sf: int
):
    """ 
    Function to calculate timestamps 
    of indexes from a list
    
    Inputs:
        - art_idx : list of indexes
        - sf : sampling frequency of the signal 
        from which the indexes come from

    Returns:
        - art_time : list of timestamps
    """

    art_time = []
    for n in np.arange(0, len(art_idx), 1):
        art_time_x = art_idx[n]/sf
        art_time.append(art_time_x)
        
    return art_time



def _convert_time_to_index(
    art_time: list, 
    sf: int
):
    
    """ 
    Function to calculate indexes from a list of timestamps.
    
    Inputs:
        - art_time : list of timestamps
        - sf : sampling frequency of the signal 
        from which the timestamps come from
    
    Returns:
        - art_idx : list of indexes    
    """

    art_idx = []
    for n in np.arange(0, len(art_time), 1):
        art_idx_x = art_time[n]*sf
        art_idx.append(art_idx_x)
    
    return art_idx




def _extract_elements(data_list, indices_to_extract):
    # Create an itemgetter object with the indices specified in indices_to_extract
    getter = operator.itemgetter(*indices_to_extract)

    # Use the itemgetter to extract the elements from the data_list
    extracted_elements = getter(data_list)

    return extracted_elements



def _get_input_y_n(message: str) -> str:

    """Get `y` or `n` user input."""

    while True:

        user_input = input(f"{message} (y/n)? ")

        if user_input.lower() in ["y", "n"]:

            break

        print(

            f"Input must be `y` or `n`. Got: {user_input}."

            " Please provide a valid input."

        )

    return user_input


def _get_user_input(message: str) -> str:

    """Get user input."""

    while True:

        user_input = input(f"{message}? ")

        assert user_input[-5:] == '.json', (
        f'filename no .json INCORRECT extension: {user_input}'
    )

    return user_input


def _filtering(
        BIP_channel
):
    """
    This function applies a highpass filter at 1Hz to detrend the data.
    """

    b, a = scipy.signal.butter(1, 0.05, 'highpass')
    filteredHighPass = scipy.signal.filtfilt(b, a, BIP_channel)

    return filteredHighPass


def _calculate_difference(data, sampling_rate):
    # Calculate the number of samples corresponding to the first 2 seconds
    num_samples_2_seconds = int(sampling_rate * 2)

    # Extract the first 2 seconds of data
    data_2_seconds = data[:num_samples_2_seconds]

    # Find the minimum and maximum values
    min_value = min(data_2_seconds)
    max_value = max(data_2_seconds)

    # Calculate the difference
    difference = abs(max_value - min_value)

    return difference