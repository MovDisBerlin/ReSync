import pandas as pd    
import numpy as np

def sync_by_cropping_both(
    LFP_array: np.ndarray,
    external_file: np.ndarray,
    art_start_LFP,
    art_start_BIP,
    LFP_rec_ch_names: list,
    external_rec_ch_names: list,
    sf_LFP,
    sf_external
):

    """
    This function is used to crop the external recording and the
    intracerebral recording one second before the first artifact
    detected. The end of the longest one of those two recordings
    is also cropped, to have the same duration for the two recordings.

    Inputs:
        - LFP_array: np.ndarray, the intracerebral recording containing all 
        recorded channels
        - external_file: np.ndarray, the external recording containing all 
        recorded channels
        - art_time_LFP: float, the timepoint when the artifact starts in the 
        intracerebral recording
        - art_time_BIP: float, the timepoint when the artifact starts in the 
        external recording
        - LFP_rec_ch_names: list, the names of all the channels recorded 
        intracerebrally (to rename the cropped recording accordingly)
        - external_rec_ch_names: list, the names of all externally recorded 
        channels (to rename the cropped recording accordingly)
        - sf_LFP: sampling frequency of intracranial recording
        - sf_external: sampling frequency of external recording

    Returns:
        - LFP_df_offset2: np.ndarray, the cropped intracerebral recording with 
        all its recorded channels, after synchronization with external recording
        - external_df_offset2: np.ndarray, the cropped external recording with 
        all its recorded channels, after synchronization with intracerebral recording

    """

    ## Intracranial ##
    # Crop beginning of LFP intracranial recording 1 second before first artifact:

    time_start_LFP_0 = art_start_LFP-1 # 1s before first artifact
    index_start_LFP = time_start_LFP_0*(sf_LFP)

    LFP_df = pd.DataFrame(LFP_array) # convert np.ndarray to dataframe
    LFP_df_transposed = pd.DataFrame.transpose(LFP_df) # invert rows and columns

    # remove all rows before first artifact
    LFP_df_offset = LFP_df_transposed.truncate(before=index_start_LFP) 
    LFP_df_offset = LFP_df_offset.reset_index(drop=True) # reset indexes

    ## External ##
    # Crop beginning of external recordings 1s before first artifact:

    # find the index of the row corresponding to 1 second before first artifact
    time_start_external = (art_start_BIP)-1
    index_start_external = time_start_external*sf_external

    external_df = pd.DataFrame(external_file) # convert np.ndarray to dataframe
    external_df_transposed = pd.DataFrame.transpose(external_df) # invert rows and columns
    # remove all rows before first artifact
    external_df_offset = external_df_transposed.truncate(before=index_start_external) 
    external_df_offset = external_df_offset.reset_index(drop=True) # reset indexes

    # Check which recording is the longest,
    # crop it to give it the same duration as the other one:
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
    else: 
        LFP_df_offset2 = LFP_df_offset
        external_df_offset2 = external_df_offset    


    # rename properly columns in both cropped recordings:
    LFP_df_offset2.columns = LFP_rec_ch_names
    LFP_df_offset2 = LFP_df_offset2.reset_index(drop=True)
    external_df_offset2.columns = external_rec_ch_names
    external_df_offset2 = external_df_offset2.reset_index(drop=True)

    
    return LFP_df_offset2, external_df_offset2


def align_external_on_LFP(
    LFP_array: np.ndarray,
    external_file: np.ndarray,
    art_start_LFP,
    art_start_BIP,
    external_rec_ch_names: list,
    sf_LFP: int,
    sf_external: int
):
    

    """
    This function is used to crop ONLY the external recording so that it starts
    at the same time than the intracerebral one. 
    The end of the external recording is also cropped to match the duration of
    the intracerebral one, if it's longer.

    Inputs:
        - LFP_array: np.ndarray, the intracerebral recording containing all 
        recorded channels
        - external_file: np.ndarray, the external recording containing all 
        recorded channels
        - art_time_LFP: float, the timepoint when the artifact starts in the 
        intracerebral recording
        - art_time_BIP: float, the timepoint when the artifact starts in the 
        external recording
        - external_rec_ch_names: list, the names of all externally recorded 
        channels (to rename the cropped recording accordingly)
        - sf_LFP: sampling frequency of intracranial recording
        - sf_external: sampling frequency of external recording

    Returns:
        - LFP_df2: np.ndarray, the intracerebral recording with all its recorded 
        channels
        - external_df_offset2: np.ndarray, the cropped external recording with 
        all its recorded channels, after synchronization with intracerebral 
        recording

    """

    # find the timestamp in the external recording corresponding to the start of LFP recording :
    time_start_external = art_start_BIP- art_start_LFP
    index_start_external = time_start_external*sf_external

    # Crop beginning of external recordings to match with the beginning of the LFP recording:
    external_df = pd.DataFrame(external_file) # convert np.ndarray to dataframe
    external_df_transposed = pd.DataFrame.transpose(external_df) # invert rows and columns
    # remove all rows before first artifact
    external_df_offset = external_df_transposed.truncate(before=index_start_external) 
    external_df_offset = external_df_offset.reset_index(drop=True) # reset indexes

    # check duration and crop external recording if longer:
    LFP_df = pd.DataFrame(LFP_array)
    LFP_df2 = pd.DataFrame.transpose(LFP_df) # invert rows and columns
    LFP_rec_duration = len(LFP_df2)/sf_LFP
    external_rec_duration = len(external_df_offset)/sf_external

    if external_rec_duration > LFP_rec_duration:
        rec_duration = LFP_rec_duration
        index_stop_external = rec_duration*sf_external
        external_df_offset2 = external_df_offset.truncate(after=index_stop_external-1)

    else: 
        external_df_offset2 = external_df_offset

    # rename properly columns in external cropped recording:
    external_df_offset2.columns = external_rec_ch_names
    external_df_offset2 = external_df_offset2.reset_index(drop=True)

    #LFP_df2.columns = LFP_rec_ch_names

    return LFP_df2, external_df_offset2
