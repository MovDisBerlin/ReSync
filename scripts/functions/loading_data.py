import json
import pandas as pd
from mne.io import read_raw_fieldtrip
from os.path import join

from functions.utils import _update_and_save_params, _update_and_save_multiple_params
from functions.tmsi_poly5reader import Poly5Reader

#### LFP DATASET ####


def load_intracranial(
        session_ID,
        fname_lfp,
        ch_idx_lfp,
        trial_idx_lfp,
        saving_path,
        source_path,
        PREPROCESSING
        ):
    
    """
    Inputs:
    ----------
    session_ID: str, subject ID
    fname_lfp: str, name of the LFP recording session
    ch_idx_lfp: int, index of the channel of interest in the LFP recording
    trial_idx_lfp: int, only used if PREPROCESSING is 'DBScope'. It corresponds to
    the number indicated in the DBScope viewer for Streamings, under 
    "Select recording" - 1.
    saving_path: str, path to save the parameters
    source_path: str, path to the source file
    PREPROCESSING: str, "Perceive" or "DBScope" depending on which toolbox was 
    used to extract the recording from the original json file

    ............................................................................
    
    Outputs
    -------
    LFP_array: the intracranial recording itself, containing all the recorded channels
    lfp_sig: the channel of the intracranial recording containing the stimulation artifacts
    LFP_rec_ch_names: the names of all the channels recorded intracerebrally
    sf_LFP: the sampling frequency of the intracranial recording

    """
    
    if fname_lfp.endswith(".mat") and PREPROCESSING == "Perceive":
        dataset_lfp = load_mat_file(
            session_ID=session_ID,
            filename=fname_lfp,
            saving_path=saving_path,
            source_path=source_path,
        )
        (LFP_array, lfp_sig, LFP_rec_ch_names, sf_LFP) = load_data_lfp(
            session_ID=session_ID,
            dataset_lfp=dataset_lfp,
            ch_idx_lfp=ch_idx_lfp,
            saving_path=saving_path,
        )
    if fname_lfp.endswith(".mat") and PREPROCESSING == "DBScope":
        (LFP_array, lfp_sig, LFP_rec_ch_names, sf_LFP) = load_data_lfp_DBScope(
            session_ID=session_ID,
            fname_lfp=fname_lfp,
            ch_idx_lfp=ch_idx_lfp,
            trial_idx_lfp=trial_idx_lfp,
            source_path=source_path,
            saving_path=saving_path,
        )
    if fname_lfp.endswith(".csv"):
        (LFP_array, lfp_sig, LFP_rec_ch_names, sf_LFP) = load_intracranial_csv_file(
            session_ID=session_ID,
            filename=fname_lfp,
            ch_idx_lfp=ch_idx_lfp,
            saving_path=saving_path,
            source_path=source_path,
        )    

    return LFP_array, lfp_sig, LFP_rec_ch_names, sf_LFP



def load_external(
        session_ID,
        fname_external,
        BIP_ch_name,
        saving_path,
        source_path
    ):

    """
    Inputs:
    ----------
    session_ID: str, subject ID
    fname_external: str, name of the external recording session
    BIP_ch_name: str, name of the external channel containing the sync artifacts
    saving_path: str, path to save the parameters
    source_path: str, path to the source file


    ............................................................................
    
    Outputs
    -------
    external_file: np.ndarray, the external recording containing all recorded
    channels
    BIP_channel: np.ndarray, the channel of the external recording to be used
    for synchronization (the one containing deep brain stimulation
    artifacts = the	channel recorded with the bipolar electrode)
    external_rec_ch_names: list, the names of all the channels recorded externally
    sf_external: int, sampling frequency of external recording
    ch_index_external: int, index of the bipolar channel in the external recording
    (BIP_channel)

    """

    if fname_external.endswith(".Poly5"):
        TMSi_data = Poly5Reader(join(source_path, fname_external))
        (
            external_file,
            BIP_channel,
            external_rec_ch_names,
            sf_external,
            ch_index_external,
        ) = load_TMSi_artifact_channel(
            session_ID=session_ID,
            TMSi_data=TMSi_data,
            fname_external=fname_external,
            BIP_ch_name=BIP_ch_name,
            saving_path=saving_path
        )
    if fname_external.endswith(".csv"):
        (
            external_file,
            BIP_channel,
            external_rec_ch_names,
            sf_external,
            ch_index_external,
        ) = load_external_csv_file(
            session_ID=session_ID,
            filename=fname_external,
            BIP_ch_name=BIP_ch_name,
            saving_path=saving_path,
            source_path=source_path,
        )

    return (external_file, BIP_channel, external_rec_ch_names, sf_external, ch_index_external)




def load_sourceJSON(json_filename: str, source_path):
    """
    Reads source JSON file

    Input:
        - fname: str of JSON filename

    Returns:
        - json_object: loaded JSON file

    """

    with open(join(source_path, json_filename), "r") as f:
        json_object = json.loads(f.read())

    return json_object


def load_mat_file(session_ID: str, filename: str, saving_path: str, source_path):
    """ "
    Reads .mat-file in FieldTrip structure using mne-function

    Input:
        - session_ID: str
        - filename: str of only .mat-filename
                - saving_path: str of path to save the parameters
                - source_path: str of path to the source file

    Returns:
        - data: mne-object of .mat file
    """

    # Error if filename doesn´t end with .mat
    assert filename[-4:] == ".mat", f"filename no .mat INCORRECT extension: {filename}"

    dictionary = {"SUBJECT_ID": session_ID, "FNAME_LFP":filename}
    _update_and_save_multiple_params(dictionary,session_ID,saving_path)

    data = read_raw_fieldtrip(
        join(source_path, filename),
        info={},
        data_name="data",
    )

    return data


def load_intracranial_csv_file(
    session_ID: str, filename: str, ch_idx_lfp: int, saving_path: str, source_path
):
    """
    Takes a .csv file containing the LFP recording and extracts the LFP signal
    from the channel of interest. It also returns the whole LFP recording (in an
    array), the names of all the channels recorded, the sampling frequency of the
    LFP recording and the index of the channel of interest in the LFP recording.

    Inputs:
            - session_ID: str, subject ID
            - filename: str, name of the LFP recording session
            - ch_idx_lfp: int, index of the channel of interest in the LFP recording
            - saving_path: str, path to save the parameters
            - source_path: str, path to the source file

    Returns:
            - LFP_array: np.ndarray, the LFP recording containing
                    all recorded channels
            - lfp_sig: np.ndarray, the LFP signal from the channel
                    of interest
            - LFP_rec_ch_names: list, the names of all the channels
                    recorded
            - sf_LFP: int, sampling frequency of LFP recording
    """

    sf_LFP = int(filename[filename.find("Hz") - 3 : filename.find("Hz")])
    # load a csv file :
    dataset_lfp = pd.read_csv(join(source_path, filename))
    # convert to array :
    LFP_array = dataset_lfp.to_numpy()
    # transpose array:
    LFP_array = LFP_array.transpose()
    # store the first column of dataset_lfp in an array called lfp_sig:
    lfp_sig = LFP_array[ch_idx_lfp, :]
    LFP_rec_ch_names = list(dataset_lfp.columns)

    time_duration_LFP = len(lfp_sig) / sf_LFP

    """
    _update_and_save_params(
        key="SUBJECT_ID",
        value=session_ID,
        session_ID=session_ID,
        saving_path=saving_path,
    )
    _update_and_save_params(
        key="CH_IDX_LFP",
        value=ch_idx_lfp,
        session_ID=session_ID,
        saving_path=saving_path,
    )
    _update_and_save_params(
        key="LFP_REC_CH_NAMES",
        value=LFP_rec_ch_names,
        session_ID=session_ID,
        saving_path=saving_path,
    )
    _update_and_save_params(
        key="LFP_REC_DURATION",
        value=time_duration_LFP,
        session_ID=session_ID,
        saving_path=saving_path,
    )
    _update_and_save_params(
        key="sf_LFP", value=sf_LFP, session_ID=session_ID, saving_path=saving_path
    )
    """
    dictionary = {"SUBJECT_ID": session_ID, "FNAME_LFP": filename,
                   "CH_IDX_LFP": ch_idx_lfp, "LFP_REC_CH_NAMES": LFP_rec_ch_names,
                    "LFP_REC_DURATION": time_duration_LFP, "sf_LFP": sf_LFP}
    _update_and_save_multiple_params(dictionary, session_ID, saving_path)

    return LFP_array, lfp_sig, LFP_rec_ch_names, sf_LFP


def load_external_csv_file(
    session_ID: str, filename: str, BIP_ch_name: str, saving_path: str, source_path
):
    """
    Takes a .csv file containing the external recording and extracts the channel
    containing the artifacts, which will be used for synchronization.
    It also returns the whole external recording (in an array),
    the names of all the channels recorded externally, the sampling
    frequency of the external recording and the index of the bipolar channel
    in the external recording.

    Inputs:
            - session_ID: str, subject ID
            - filename: str, name of the external recording session
            - BIP_ch_name: str, name of the bipolar channel, containing the artifacts
            - saving_path: str, path to save the parameters
            - source_path: str, path to the source file

    Returns:
            - external_file: np.ndarray, the external recording containing all recorded
                    channels
            - BIP_channel: np.ndarray, the channel of the external recording to be used
                    for synchronization (the one containing deep brain stimulation
                    artifacts = the	channel recorded with the bipolar electrode)
            - external_rec_ch_names: list, the names of all the channels recorded externally
            - sf_external: int, sampling frequency of external recording
            - ch_index_external: int, index of the bipolar channel in the external recording
                    (BIP_channel)
    """

    sf_external = int(filename[filename.find("Hz") - 4 : filename.find("Hz")])
    # load a csv file :
    dataset_external = pd.read_csv(join(source_path, filename))
    external_file = dataset_external.to_numpy()
    external_file = external_file.transpose()
    external_rec_ch_names = list(dataset_external.columns)

    ch_index_external = external_rec_ch_names.index(BIP_ch_name)
    BIP_channel = external_file[ch_index_external, :]

    time_duration_external_s = len(BIP_channel) / sf_external

    """
    _update_and_save_params(
        key="FNAME_EXTERNAL",
        value=filename,
        session_ID=session_ID,
        saving_path=saving_path,
    )
    _update_and_save_params(
        key="EXTERNAL_REC_CH_NAMES",
        value=external_rec_ch_names,
        session_ID=session_ID,
        saving_path=saving_path,
    )
    _update_and_save_params(
        key="EXTERNAL_REC_DURATION",
        value=time_duration_external_s,
        session_ID=session_ID,
        saving_path=saving_path,
    )
    _update_and_save_params(
        key="sf_EXTERNAL",
        value=sf_external,
        session_ID=session_ID,
        saving_path=saving_path,
    )
    _update_and_save_params(
        key="CH_IDX_EXTERNAL",
        value=ch_index_external,
        session_ID=session_ID,
        saving_path=saving_path,
    )
    """
    dictionary = {
        "FNAME_EXTERNAL": filename, 
        "EXTERNAL_REC_CH_NAMES": external_rec_ch_names, 
        "EXTERNAL_REC_DURATION": time_duration_external_s, 
        "sf_EXTERNAL": sf_external, 
        "CH_IDX_EXTERNAL": ch_index_external
        }
    _update_and_save_multiple_params(dictionary, session_ID, saving_path)

    return (
        external_file,
        BIP_channel,
        external_rec_ch_names,
        sf_external,
        ch_index_external,
    )


# extract variables from LFP recording:
def load_data_lfp(session_ID: str, dataset_lfp, ch_idx_lfp, saving_path: str):
    """
    Takes a .mat file containing the LFP recording and extracts the LFP signal
    from the channel of interest. It also returns the whole LFP recording (in an
    array), the names of all the channels recorded, the sampling frequency of the
    LFP recording and the index of the channel of interest in the LFP recording.

    Inputs:
            - session_ID: str, subject ID
            - dataset_lfp: mne-object of .mat file
            - ch_idx_lfp: int, index of the channel of interest in the LFP recording
            - saving_path: str, path to save the parameters

    Returns:
            - LFP_array: np.ndarray, the LFP recording containing
                    all recorded channels
            - lfp_sig: np.ndarray, the LFP signal from the channel
                    of interest
            - LFP_rec_ch_names: list, the names of all the channels
                    recorded
            - sf_LFP: int, sampling frequency of LFP recording
    """

    if type(ch_idx_lfp) == float:
        ch_idx_lfp = int(ch_idx_lfp)

    LFP_array = dataset_lfp.get_data()
    lfp_sig = dataset_lfp.get_data()[ch_idx_lfp]
    LFP_rec_ch_names = dataset_lfp.ch_names
    sf_LFP = int(dataset_lfp.info["sfreq"])
    time_duration_LFP = (dataset_lfp.n_times / dataset_lfp.info["sfreq"]).astype(float)

    """
    _update_and_save_params(
        key="CH_IDX_LFP",
        value=ch_idx_lfp,
        session_ID=session_ID,
        saving_path=saving_path,
    )
    _update_and_save_params(
        key="LFP_REC_CH_NAMES",
        value=LFP_rec_ch_names,
        session_ID=session_ID,
        saving_path=saving_path,
    )
    _update_and_save_params(
        key="LFP_REC_DURATION",
        value=time_duration_LFP,
        session_ID=session_ID,
        saving_path=saving_path,
    )
    _update_and_save_params(
        key="sf_LFP", value=sf_LFP, session_ID=session_ID, saving_path=saving_path
    )
    """

    dictionary = {
        "SUBJECT_ID": session_ID,
        "CH_IDX_LFP": ch_idx_lfp, 
        "LFP_REC_CH_NAMES": LFP_rec_ch_names, 
        "LFP_REC_DURATION": time_duration_LFP, 
        "sf_LFP": sf_LFP
        }
    _update_and_save_multiple_params(dictionary, session_ID, saving_path)

    return LFP_array, lfp_sig, LFP_rec_ch_names, sf_LFP


import scipy.io
def load_data_lfp_DBScope(
    session_ID: str,
    fname_lfp,
    ch_idx_lfp,
    trial_idx_lfp,
    source_path: str,
    saving_path: str,
):

    if type(ch_idx_lfp) == float:
        ch_idx_lfp = int(ch_idx_lfp)
    if type(trial_idx_lfp) == float:
        trial_idx_lfp = int(trial_idx_lfp)

    # load the mat file from DBScope:
    mat = scipy.io.loadmat(join(source_path, fname_lfp))

    # extract the necessary information needed for synchronization:
    # We need: LFP_array, lfp_sig, LFP_rec_ch_names, sf_LFP
    sf_LFP = mat["lfp_raw"]["hdr"][0][0]["fs"][0][0][0][0]
    LFP_rec_ch_names = [
        mat["lfp_raw"]["hdr"][0][0]["channel_names"][0][0][0][trial_idx_lfp][0][0][0],
        mat["lfp_raw"]["hdr"][0][0]["channel_names"][0][0][0][trial_idx_lfp][0][1][0],
    ]
    LFP_array = mat["lfp_raw"]["trial"][0][0][0][trial_idx_lfp]
    lfp_sig = mat["lfp_raw"]["trial"][0][0][0][trial_idx_lfp][ch_idx_lfp]
    time_duration_LFP = len(lfp_sig) / sf_LFP

    """
    _update_and_save_params(
        key="CH_IDX_LFP",
        value=ch_idx_lfp,
        session_ID=session_ID,
        saving_path=saving_path,
    )
    _update_and_save_params(
        key="TRIAL_IDX_LFP",
        value=trial_idx_lfp,
        session_ID=session_ID,
        saving_path=saving_path,
    )
    _update_and_save_params(
        key="LFP_REC_CH_NAMES",
        value=LFP_rec_ch_names,
        session_ID=session_ID,
        saving_path=saving_path,
    )
    _update_and_save_params(
        key="LFP_REC_DURATION",
        value=time_duration_LFP,
        session_ID=session_ID,
        saving_path=saving_path,
    )
    _update_and_save_params(
        key="sf_LFP",
        value=float(sf_LFP),
        session_ID=session_ID,
        saving_path=saving_path,
    )
    """

    dictionary = {
        "SUBJECT_ID": session_ID,
        "CH_IDX_LFP": ch_idx_lfp, 
        "TRIAL_IDX_LFP": trial_idx_lfp, 
        "LFP_REC_CH_NAMES": LFP_rec_ch_names, 
        "LFP_REC_DURATION": time_duration_LFP, 
        "sf_LFP": sf_LFP
        }
    _update_and_save_multiple_params(dictionary, session_ID, saving_path)

    return LFP_array, lfp_sig, LFP_rec_ch_names, sf_LFP


#### External data recorder dataset ####


def load_TMSi_artifact_channel(
    session_ID: str, TMSi_data, fname_external: str, BIP_ch_name: str, saving_path: str
):
    """
    Takes a poly5 object containing all the external channels recorded.
    It extracts the channel containing the artifacts, which will be used for
    synchronization. It also returns the whole external recording (in an array),
    the names of all the channels recorded externally, the sampling frequency
    of the external recording and the index of the bipolar channel in the
    external recording.

    Input:
            - session_ID: str, subject ID
            - TMSi_data: TMSiFileFormats.file_readers.poly5reader.Poly5Reader
            - fname_external: str, name of the external recording session
            - BIP_ch_name: str, name of the bipolar channel, containing the artifacts
            - saving_path: str, path to save the parameters

    Returns:
            - BIP_channel: np.ndarray, the channel of the external
        recording to be used for synchronization (the one containing deep brain
        stimulation artifacts = the channel recorded with the bipolar
        electrode)
    - external_file: np.ndarray, the external recording
        containing all recorded channels
            - external_rec_ch_names: list, the names of all the channels
        recorded externally
            - sf_external: int, sampling frequency of external recording
            - ch_index: int, index of the bipolar channel in the external recording
                    (BIP_channel)
    """

    # Conversion of .Poly5 to MNE raw array
    toMNE = True
    TMSi_rec = TMSi_data.read_data_MNE()
    external_rec_ch_names = TMSi_rec.ch_names
    
    assert BIP_ch_name in external_rec_ch_names, "{} is not in externally recorded channels. Please choose from the available channels: {}".format(BIP_ch_name, external_rec_ch_names)

    time_duration_TMSi_s = (TMSi_rec.n_times / TMSi_rec.info["sfreq"]).astype(float)
    sf_external = int(TMSi_rec.info["sfreq"])
    ch_index = TMSi_rec.ch_names.index(BIP_ch_name)

    dictionary = {
        "FNAME_EXTERNAL": fname_external, 
        "EXTERNAL_REC_CH_NAMES": external_rec_ch_names, 
        "EXTERNAL_REC_DURATION": time_duration_TMSi_s, 
        "sf_EXTERNAL": sf_external, 
        "CH_IDX_EXTERNAL": ch_index
        }
    _update_and_save_multiple_params(dictionary, session_ID, saving_path)

    BIP_channel = TMSi_rec.get_data()[ch_index]
    external_file = TMSi_rec.get_data()

    return (external_file, BIP_channel, external_rec_ch_names, sf_external, ch_index)
