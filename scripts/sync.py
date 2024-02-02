import pandas as pd    
import numpy as np

def sync_by_cropping_both(
    LFP_array: np.ndarray,
    external_file: np.ndarray,
    art_start_LFP,
    art_start_BIP,
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
        - sf_LFP: sampling frequency of intracranial recording
        - sf_external: sampling frequency of external recording

    Returns:
        - LFP_synchronized: np.ndarray, the cropped intracerebral recording with 
        all its recorded channels, after synchronization with external recording
        - external_synchronized: np.ndarray, the cropped external recording with 
        all its recorded channels, after synchronization with intracerebral recording

    """

    ## Intracranial ##
    # Crop beginning of LFP intracranial recording 1 second before first artifact:
    time_start_LFP_0 = art_start_LFP-1 # 1s before first artifact
    index_start_LFP = time_start_LFP_0*(sf_LFP)

    LFP_cropped = LFP_array[:, int(index_start_LFP):].T

    ## External ##
    # Crop beginning of external recordings 1s before first artifact:
    time_start_external = (art_start_BIP)-1
    index_start_external = time_start_external*sf_external

    external_cropped = external_file[:, int(index_start_external):].T

    # Check which recording is the longest,
    # crop it to give it the same duration as the other one:
    LFP_rec_duration = len(LFP_cropped)/sf_LFP

    external_rec_duration = len(external_cropped)/sf_external

    if LFP_rec_duration > external_rec_duration:
        rec_duration = external_rec_duration
        index_stop_LFP = rec_duration*sf_LFP
        LFP_synchronized = LFP_cropped[:int(index_stop_LFP),:]
        external_synchronized = external_cropped
    elif external_rec_duration > LFP_rec_duration:
        rec_duration = LFP_rec_duration
        index_stop_external = rec_duration*sf_external
        external_synchronized = external_cropped[:int(index_stop_external),:]
        LFP_synchronized = LFP_cropped
    else: 
        LFP_synchronized = LFP_cropped
        external_synchronized = external_cropped  

    return LFP_synchronized, external_synchronized




def align_external_on_LFP(
    LFP_array: np.ndarray,
    external_file: np.ndarray,
    art_start_LFP,
    art_start_BIP,
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
        - sf_LFP: sampling frequency of intracranial recording
        - sf_external: sampling frequency of external recording

    Returns:
        - LFP_array: np.ndarray, the intracerebral recording with all its recorded 
        channels
        - external_synchronized: np.ndarray, the cropped external recording with 
        all its recorded channels, after synchronization with intracerebral 
        recording

    """

    # find the timestamp in the external recording corresponding to the start of LFP recording :
    time_start_external = art_start_BIP- art_start_LFP
    index_start_external = time_start_external*sf_external

    external_cropped = external_file[:, int(index_start_external):].T

    # check duration and crop external recording if longer:
    LFP_rec_duration = len(LFP_array.T)/sf_LFP
    external_rec_duration = len(external_cropped)/sf_external

    if external_rec_duration > LFP_rec_duration:
        rec_duration = LFP_rec_duration
        index_stop_external = rec_duration*sf_external
        external_synchronized = external_cropped[:int(index_stop_external),:]

    else: 
        external_synchronized = external_cropped


    return LFP_array.T, external_synchronized
