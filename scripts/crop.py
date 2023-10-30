import pandas as pd    
import numpy as np
import os
import json  

def crop_rec(
    LFP_array: np.ndarray,
    external_file: np.ndarray,
    art_time_LFP: float,
    art_time_BIP: float,
    LFP_rec_ch_names: list,
    external_rec_ch_names: list,
    real_art_time_LFP: float,
    sf_LFP: int,
    sf_external: int
):

    """
    This function is used to crop the external recording and the
    intracerebral recording one second before the first artefact
    detected. The end of the longest one of those two recordings
    is also cropped, to have the same duration for the two recordings.
    The two cropped recordings are saved as .csv files.

    Inputs:
        - LFP_array (np.ndarray with shape: (x, y)): the intracerebral recording 
            containing all recorded channels (x channels, y datapoints)
        - external_file (np.ndarray with shape: (x, y)): the external recording 
            containing all recorded channels (x channels, y datapoints)
        - art_time_LFP (float): the timepoint when the artefact starts in the intracerebral 
            recording (found previously using the function find_LFP_sync_artefact)
        - art_time_BIP (float): the timepoint when the artefact starts in the external 
            recording (found previously using the function find_external_sync_artefact)
        - LFP_rec_ch_names (list of x names): the names of all the channels 
            recorded intracerebrally (to rename the cropped recording accordingly)
        - external_rec_ch_names (list of x names): the names of all externally recorded channels 
            (to rename the cropped recording accordingly)
        - real_art_time_LFP (float): default 0, but can be changed in notebook via 
            interactive plotting to adjust artefact detection
        - sf_LFP (int): sampling frequency of intracranial recording
        - sf_external (int): sampling frequency of external recording


    Returns:
        - LFP_df_offset2 (np.ndarray with shape: (x, y2)): the cropped intracerebral 
            recording with all its recorded channels
        - external_df_offset2 (np.ndarray with shape: (x, y2)): the cropped external 
            recording with all its recorded channels

    """

    # LFP #
    # Crop beginning of LFP recording 1 second before first artefact:
    if real_art_time_LFP == 0:
        time_start_LFP_0 = art_time_LFP[0]-1 # 1s before first artefact
        index_start_LFP = time_start_LFP_0*(sf_LFP)
    elif real_art_time_LFP != 0:
        diff_art_time = real_art_time_LFP - art_time_LFP[0]
        diff_art_idx = diff_art_time*(sf_LFP)
        time_start_LFP_0 = art_time_LFP[0]-1 # 1s before first artefact
        index_start_LFP_0 = time_start_LFP_0*(sf_LFP)
        index_start_LFP = index_start_LFP_0 + diff_art_idx

    LFP_df = pd.DataFrame(LFP_array) # convert np.ndarray to dataframe
    LFP_df_transposed = pd.DataFrame.transpose(LFP_df) # invert rows and columns

    LFP_df_offset = LFP_df_transposed.truncate(before=index_start_LFP) # remove all rows before first artefact
    LFP_df_offset = LFP_df_offset.reset_index(drop=True) # reset indexes


    ## TMSi ##
    # Crop beginning of external recordings 1s before first artefact:

    # find the index of the row corresponding to 1 second before first artefact
    time_start_external = (art_time_BIP[0])-1
    index_start_external = time_start_external*sf_external

    external_df = pd.DataFrame(external_file) # convert np.ndarray to dataframe
    external_df_transposed = pd.DataFrame.transpose(external_df) # invert rows and columns

    external_df_offset = external_df_transposed.truncate(before=index_start_external) # remove all rows before first artefact
    external_df_offset = external_df_offset.reset_index(drop=True) # reset indexes

    #### Check which recording is the longest, and crop it to give it the same duration as the other one:
    LFP_rec_duration = len(LFP_df_offset)/sf_LFP
    external_rec_duration = len(external_df_offset)/sf_external

    if LFP_rec_duration > external_rec_duration:
        rec_duration = external_rec_duration
        index_stop_LFP = rec_duration*sf_LFP
        LFP_df_offset2 = LFP_df_offset.truncate(after=index_stop_LFP-1)
        external_df_offset2 = external_df_offset
    elif external_rec_duration > LFP_rec_duration:
        rec_duration = LFP_rec_duration
        index_stop_external = rec_duration*sf_external
        external_df_offset2 = external_df_offset.truncate(after=index_stop_external-1)
        LFP_df_offset2 = LFP_df_offset


    # rename properly columns in both cropped recordings:
    LFP_df_offset2.columns = LFP_rec_ch_names
    LFP_df_offset2 = LFP_df_offset2.reset_index(drop=True)
    external_df_offset2.columns = external_rec_ch_names
    external_df_offset2 = external_df_offset2.reset_index(drop=True)

    
    return LFP_df_offset2, external_df_offset2