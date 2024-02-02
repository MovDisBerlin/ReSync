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
    This function is used only in the notebook, if the user hasn't already define 
    the saving path in the config.json file (back up function).
    """

    #import settings
    json_path = os.path.join(os.getcwd(), 'config')
    json_filename = 'config.json'
    with open(os.path.join(json_path, json_filename), 'r') as f:
        loaded_dict =  json.load(f)

    saving_folder = askdirectory(title = 'Select Saving Folder') 
    saving_path = os.path.join(saving_folder, loaded_dict['subject_ID'])
    if not os.path.isdir(saving_path):
        os.makedirs(saving_path)

    return saving_path


parameters = {}

def _update_and_save_params(
        key, 
        value, 
        session_ID, 
        saving_path
        ):
    parameters[key] = value
    parameter_filename = ('parameters_' + str(session_ID) + '.json')
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




def _extract_elements(
        data_list, 
        indices_to_extract
        ):
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


def _get_user_input(message: str) -> int:

    """Get user input."""

    while True:
        try:
            user_input = int(input(f"{message}? "))
            break
        except ValueError:
            print("Input must be an integer. Please provide a valid input.")

    return user_input


