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

    # import settings
    json_path = os.path.join(os.getcwd(), "config")
    json_filename = "config.json"
    with open(os.path.join(json_path, json_filename), "r") as f:
        loaded_dict = json.load(f)

    saving_folder = askdirectory(title="Select Saving Folder")
    saving_path = os.path.join(saving_folder, loaded_dict["subject_ID"])
    if not os.path.isdir(saving_path):
        os.makedirs(saving_path)

    return saving_path


parameters = {}


def _update_and_save_multiple_params(dictionary, session_ID, saving_path):
    """
    This function is used to update the parameters dictionary and save it in a json file.

    Inputs:
        - dictionary: contains multiple keys and their values
        - session_ID: the session identifier
        - saving_path: the path where to save/find the json file
    """
    for key, value in dictionary.items():
        parameters[key] = value
    
    parameter_filename = "parameters_" + str(session_ID) + ".json"
    json_file_path = os.path.join(saving_path, parameter_filename)
    with open(json_file_path, "w") as json_file:
        json.dump(parameters, json_file, indent=4)



def _update_and_save_params(key, value, session_ID, saving_path):
    """
    This function is used to update the parameters dictionary and save it in a json file.

    Inputs:
        - key: the key of the parameter to update
        - value: the new value of the parameter
        - session_ID: the session identifier
        - saving_path: the path where to save/find the json file
    """

    parameters[key] = value
    parameter_filename = "parameters_" + str(session_ID) + ".json"
    json_file_path = os.path.join(saving_path, parameter_filename)
    with open(json_file_path, "w") as json_file:
        json.dump(parameters, json_file, indent=4)


import pandas as pd
def _check_for_empties(session_ID, fname_lfp, fname_external, ch_idx_lfp, BIP_ch_name, index):
    SKIP = False
    if pd.isna(session_ID):
        print(
            f"Skipping analysis for row {index + 2}" f" because session_ID is empty."
        )
        SKIP = True
    if pd.isna(fname_lfp):
        print(
            f"Skipping analysis for row {index + 2}" f" because fname_lfp is empty."
        )
        SKIP = True
    if pd.isna(fname_external):
        print(
            f"Skipping analysis for row {index + 2}"
            f" because fname_external is empty."
        )
        SKIP = True
    if pd.isna(ch_idx_lfp):
        print(
            f"Skipping analysis for row {index + 2}" f" because ch_idx_lfp is empty."
        )
        SKIP = True
    if pd.isna(BIP_ch_name):
        print(
            f"Skipping analysis for row {index + 2}"
            f" because BIP_ch_name is empty."
        )
        SKIP = True
    return SKIP


def _is_channel_in_list(channel_array, desired_channel_name):

    if desired_channel_name.lower() in (channel.lower() for channel in channel_array):
        return True
    else:
        return False


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


def _get_user_input(message: str) -> int:
    """Get user input."""

    while True:
        try:
            user_input = int(input(f"{message}? "))
            break
        except ValueError:
            print("Input must be an integer. Please provide a valid input.")

    return user_input
