# import librairies
import matplotlib.pyplot as plt
import numpy as np
from os.path import join
import pickle
from scipy.io import savemat
from pybv import write_brainvision

# import custom-made functions
from functions.find_artifacts import *
from functions.plotting import *
from functions.interactive import select_sample
from functions.utils import _detrend_data



def detect_artifacts_in_external_recording(
    session_ID: str,
    BIP_channel: np.ndarray,
    sf_external: int,
    saving_path: str,
    start_index: int = 0,
):
    """
    This function detects the artifacts in the external recording and plots it
    for verification.

    Inputs:
        - session_ID: str, session identifier
        - BIP_channel: np.ndarray, the channel of the external recording to be
        used for synchronization (the one containing deep brain stimulation
        artifacts = the channel recorded with the bipolar electrode)
        - sf_external: int, sampling frequency of external recording
        - saving_path: str, path to the folder where the figures will be saved
        - start_index: default is 0 when recording is properly started in StimOff,
        but it can be changed when this is not the case (back-up option)


    Output:
        - art_start_BIP: the timestamp when the artifact starts in external recording
    """

    # Generate timescale:
    external_timescale_s = np.arange(
        start=0, stop=(len(BIP_channel) / sf_external), step=(1 / sf_external)
    )

    # apply a highpass filter at 1Hz to the external bipolar channel (detrending)
    filtered_external = _detrend_data(BIP_channel)

    # PLOT 1 :
    # plot the signal of the external channel used for artifact detection:
    plot_channel(
        session_ID=session_ID,
        timescale=external_timescale_s,
        data=filtered_external,
        color="darkcyan",
        ylabel="External bipolar channel - voltage (mV)",
        title="Fig1-External bipolar channel raw plot.png",
        saving_path=saving_path,
        scatter=False
    )
    plt.close()

    ### DETECT ARTIFACTS ###

    # find artifacts in external bipolar channel:
    art_start_BIP = find_external_sync_artifact(
        data=filtered_external, sf_external=sf_external, start_index=start_index
    )

    # PLOT 2 : plot the external channel with the first artifact detected:
    plot_channel(
        session_ID=session_ID,
        timescale=external_timescale_s,
        data=filtered_external,
        color="darkcyan",
        ylabel="Artifact channel BIP (mV)", 
        title="Fig2-External bipolar channel with artifact detected.png", 
        saving_path=saving_path,
        scatter=False,
    )
    plt.axvline(x=art_start_BIP, color="black", linestyle="dashed", alpha=0.3)
    plt.show(block=False)

    # PLOT 3 :
    # plot the first artifact detected in external channel (verification of sample choice):
    idx_start = np.where(external_timescale_s == art_start_BIP - (60 / sf_external))[0][0]
    idx_end = np.where(external_timescale_s == art_start_BIP + (60 / sf_external))[0][0]    
    plot_channel(
        session_ID=session_ID,
        timescale=external_timescale_s[idx_start:idx_end],
        data=filtered_external[idx_start:idx_end],
        color="darkcyan",
        ylabel="Artifact channel BIP - Voltage (mV)",
        title="Fig3-External bipolar channel - first artifact detected.png",
        saving_path=saving_path,
        scatter=True,
    )
    plt.axvline(x=art_start_BIP, color="black", linestyle="dashed", alpha=0.3)
    plt.show(block=False)

    return art_start_BIP


def detect_artifacts_in_intracranial_recording(
    session_ID: str, lfp_sig: np.ndarray, sf_LFP: int, saving_path: str, method: str
):
    """
    This function detects the first artifact in the intracranial recording and plots it.

    Inputs:
        - session_ID: str, session identifier
        - lfp_sig: np.ndarray, the channel of the intracranial recording to be
        used for synchronization (the one containing deep brain stimulation artifacts)
        - sf_LFP: int, sampling frequency of intracranial recording
        - saving_path: str, path to the folder where the figures will be saved
        - method: str, method used for artifact detection in intracranial recording
        (1, 2, thresh, manual)


    Returns:
        - art_start_LFP: the timestamp when the artifact starts in intracranial recording

    """

    # Generate timescale:
    LFP_timescale_s = np.arange(
        start=0, stop=(len(lfp_sig) / sf_LFP), step=(1 / sf_LFP)
    )

    # PLOT 4 :
    # raw signal of the intracranial channel used for artifact detection:
    plot_channel(
        session_ID=session_ID,
        timescale=LFP_timescale_s,
        data=lfp_sig,
        color="darkorange",
        ylabel="Intracerebral LFP channel (µV)",
        title="Fig4-Intracranial channel raw plot.png",
        saving_path=saving_path,
        scatter=False
    )
    plt.close()

    ### DETECT ARTIFACTS ###
    if method in ["1", "2", "thresh"]:
        art_start_LFP = find_LFP_sync_artifact(
            data=lfp_sig, sf_LFP=sf_LFP, use_method=method
        )

        # PLOT 5 :
        # plot the intracranial channel with its artifacts detected:
        plot_channel(
            session_ID=session_ID,
            timescale=LFP_timescale_s,
            data=lfp_sig,
            color="darkorange",
            ylabel="Intracranial LFP channel (µV)",
            title="Fig5-Intracranial channel with artifact detected - method " + str(method) + ".png",
            saving_path=saving_path,
            scatter=False,
        )
        plt.axvline(
            x=art_start_LFP,
            ymin=min(lfp_sig),
            ymax=max(lfp_sig),
            color="black",
            linestyle="dashed",
            alpha=0.3,
        )
        plt.gcf()
        plt.show(block=False)

        # PLOT 6 :
        # plot the first artifact detected in intracranial channel (verification of sample choice):
        idx_start = round(np.where(LFP_timescale_s == (art_start_LFP))[0][0] - (0.1*sf_LFP))
        idx_end = round(np.where(LFP_timescale_s == (art_start_LFP))[0][0] + (0.3*sf_LFP))
        plot_channel(
            session_ID=session_ID,
            timescale=LFP_timescale_s[idx_start:idx_end],
            data=lfp_sig[idx_start:idx_end],
            color="darkorange",
            ylabel="Intracranial LFP channel (µV)",
            title="Fig6-Intracranial channel - first artifact detected - method " + str(method) + ".png",
            saving_path=saving_path,
            scatter=True,
        )
        plt.axvline(
            x=art_start_LFP,
            ymin=min(lfp_sig),
            ymax=max(lfp_sig),
            color="black",
            linestyle="dashed",
            alpha=0.3,
        )
        plt.show(block=False)

    if method == "manual":
        print(
            f"Automatic detection of intracranial artifacts failed, using manual method. \n"
            f"In the pop up window, zoom on the first artifact until you can select properly  "
            f"the last sample before the deflection, click on it and close the window."
        )
        art_start_LFP = select_sample(
            signal=lfp_sig, sf=sf_LFP, color1="peachpuff", color2="darkorange"
        )

        # PLOT 7 : plot the artifact adjusted by user in the intracranial channel:
        idx_start = round(np.where(LFP_timescale_s == (art_start_LFP))[0][0] - (0.1*sf_LFP))
        idx_end = round(np.where(LFP_timescale_s == (art_start_LFP))[0][0] + (0.3*sf_LFP))
        plot_channel(
            session_ID=session_ID,
            timescale=LFP_timescale_s[idx_start:idx_end],
            data=lfp_sig[idx_start:idx_end],
            color="darkorange",
            ylabel="Intracranial LFP channel (µV)",
            title="Fig7-Intracranial channel - first artifact corrected by user.png",  
            saving_path=saving_path,
            scatter=True,
        )
        plt.axvline(
            x=art_start_LFP,
            ymin=min(lfp_sig),
            ymax=max(lfp_sig),
            color="black",
            linestyle="dashed",
            alpha=0.3,
        )

        plt.gcf()
        plt.show(block=False)

    return art_start_LFP


def synchronize_recordings(
    LFP_array: np.ndarray,
    external_file: np.ndarray,
    art_start_LFP: float,
    art_start_BIP: float,
    sf_LFP: int,
    sf_external: int,
    CROP_BOTH: bool,
):
    """
    This function synchronizes the intracranial recording with
    the external recording of the same session.

    Inputs:
        - LFP_array: np.ndarray, intracranial recording
        - external_file: np.ndarray, external recording
        - art_start_LFP: float, the timestamp when the artifact starts in intracranial recording
        - art_start_BIP: float, the timestamp when the artifact starts in external recording
        - sf_LFP: int, sampling frequency of intracranial recording
        - sf_external: int, sampling frequency of external recording
        - CROP_BOTH: bool, if True, both recordings are cropped 1 second before
        first artifact. If False, only external recording is cropped to match
        intracranial recording

    Returns:
        - LFP_synchronized: np.ndarray, intracranial recording synchronized with external recording
        - external_synchronized: np.ndarray, external recording synchronized with intracranial recording
    """

    if CROP_BOTH: 
        ## Intracranial ##
        # Crop beginning of LFP intracranial recording 1 second before first artifact:
        index_start_LFP = (art_start_LFP - 1) * sf_LFP
        LFP_cropped = LFP_array[:, int(index_start_LFP) :].T

        ## External ##
        # Crop beginning of external recordings 1s before first artifact:
        time_start_external = (art_start_BIP) - 1
        index_start_external = time_start_external * sf_external

        external_cropped = external_file[:, int(index_start_external) :].T

        # Check which recording is the longest,
        # crop it to give it the same duration as the other one:
        LFP_rec_duration = len(LFP_cropped) / sf_LFP
        external_rec_duration = len(external_cropped) / sf_external

        if LFP_rec_duration > external_rec_duration:
            index_stop_LFP = external_rec_duration * sf_LFP
            LFP_synchronized = LFP_cropped[: int(index_stop_LFP), :]
            external_synchronized = external_cropped
        elif external_rec_duration > LFP_rec_duration:
            index_stop_external = LFP_rec_duration * sf_external
            external_synchronized = external_cropped[: int(index_stop_external), :]
            LFP_synchronized = LFP_cropped
        else:
            LFP_synchronized = LFP_cropped
            external_synchronized = external_cropped
        
        print(
            "Alignment performed, both recordings were cropped 1s before first artifact !"
        )

    else:
        # find the timestamp in the external recording corresponding to the start of LFP recording :
        time_start_external = art_start_BIP - art_start_LFP
        index_start_external = time_start_external * sf_external

        external_cropped = external_file[:, int(index_start_external) :].T

        # check duration and crop external recording if longer:
        LFP_rec_duration = len(LFP_array.T) / sf_LFP
        external_rec_duration = len(external_cropped) / sf_external

        if external_rec_duration > LFP_rec_duration:
            rec_duration = LFP_rec_duration
            index_stop_external = rec_duration * sf_external
            external_synchronized = external_cropped[: int(index_stop_external), :]

        else:
            external_synchronized = external_cropped    
    
        LFP_synchronized = LFP_array.T

        print(
            "Alignment performed, only external recording as been cropped "
            "to match LFP recording !"
        )
    
    return LFP_synchronized, external_synchronized


def save_synchronized_recordings(
    session_ID: str,
    LFP_synchronized: np.ndarray,
    external_synchronized: np.ndarray,
    LFP_rec_ch_names: list,
    external_rec_ch_names: list,
    sf_LFP: int,
    sf_external: int,
    saving_format: str,
    saving_path: str,
):
    """
    This function saves the synchronized intracranial and external recordings.
    Available saving formats are: csv, mat, pickle, brainvision.
    Both recordings are saved in a separate file.

    Inputs:
        - session_ID: str, session identifier
        - LFP_synchronized: np.ndarray, intracranial recording synchronized with external recording
        - external_synchronized: np.ndarray, external recording synchronized with intracranial recording
        - LFP_rec_ch_names: list, names of the intracranial recording channels
        - external_rec_ch_names: list, names of the external recording channels
        - sf_LFP: int, sampling frequency of intracranial recording
        - sf_external: int, sampling frequency of external recording
        - saving_format: str, format in which the recordings will be saved
        - saving_path: str, path to the folder where the recordings will be saved

    """

    assert saving_format in ["csv", "mat", "pickle", "brainvision"], (
        "saving_format incorrect." "Choose in: csv, mat, pickle, brainvision"
    )

    LFP_df_offset = pd.DataFrame(LFP_synchronized)
    LFP_df_offset.columns = LFP_rec_ch_names
    external_df_offset = pd.DataFrame(external_synchronized)
    external_df_offset.columns = external_rec_ch_names

    if saving_format == "csv":
        LFP_df_offset["sf_LFP"] = sf_LFP
        external_df_offset["sf_external"] = sf_external
        LFP_df_offset.to_csv(
            join(saving_path, ("Intracranial_LFP_" + str(session_ID) + ".csv")),
            index=False,
        )
        external_df_offset.to_csv(
            join(saving_path, ("External_data_" + str(session_ID) + ".csv")),
            index=False,
        )
        print("Data saved in csv format")

    if saving_format == "pickle":
        LFP_df_offset["sf_LFP"] = sf_LFP
        external_df_offset["sf_external"] = sf_external
        LFP_filename = join(
            saving_path, ("Intracranial_LFP_" + str(session_ID) + ".pkl")
        )
        external_filename = join(
            saving_path, ("External_data_" + str(session_ID) + ".pkl")
        )
        # Save the dataset to a pickle file
        with open(LFP_filename, "wb") as file:
            pickle.dump(LFP_df_offset, file)
        with open(external_filename, "wb") as file:
            pickle.dump(external_df_offset, file)
        print("Data saved in pickle format")

    if saving_format == "mat":
        LFP_filename = join(
            saving_path, ("Intracranial_LFP_" + str(session_ID) + ".mat")
        )
        external_filename = join(
            saving_path, ("External_data_" + str(session_ID) + ".mat")
        )
        savemat(
            LFP_filename,
            {
                "data": LFP_df_offset.T,
                "fsample": sf_LFP,
                "label": np.array(
                    LFP_df_offset.columns.tolist(), dtype=object
                ).reshape(-1, 1),
            },
        )
        savemat(
            external_filename,
            {
                "data": external_df_offset.T,
                "fsample": sf_external,
                "label": np.array(
                    external_df_offset.columns.tolist(), dtype=object
                ).reshape(-1, 1),
            },
        )
        print("Data saved in mat format")

    if saving_format == "brainvision":
        LFP_filename = "Intracranial_LFP_" + str(session_ID)
        write_brainvision(
            data=LFP_synchronized.T,
            sfreq=float(sf_LFP),
            ch_names=LFP_rec_ch_names,
            fname_base=LFP_filename,
            folder_out=saving_path,
            overwrite=True,
        )
        external_filename = "External_data_" + str(session_ID)
        write_brainvision(
            data=external_synchronized.T,
            sfreq=float(sf_external),
            ch_names=external_rec_ch_names,
            fname_base=external_filename,
            folder_out=saving_path,
            overwrite=True,
        )
        print("Data saved in brainvision format")
