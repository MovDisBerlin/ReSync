# import librairies
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from os.path import join
import pickle
import scipy
from scipy.io import savemat
from pybv import write_brainvision

# import custom-made functions
from functions.find_artifacts import *
from functions.plotting import *
from functions.sync import sync_by_cropping_both, align_external_on_LFP
from functions.interactive import select_sample

## set font sizes and other parameters for the figures
SMALL_SIZE = 12
MEDIUM_SIZE = 14
BIGGER_SIZE = 16

plt.rc("font", size=SMALL_SIZE)  # controls default text sizes
plt.rc("axes", titlesize=MEDIUM_SIZE)  # fontsize of the axes title
plt.rc("axes", labelsize=SMALL_SIZE)  # fontsize of the x and y labels
plt.rc("xtick", labelsize=SMALL_SIZE)  # fontsize of the tick labels
plt.rc("ytick", labelsize=SMALL_SIZE)  # fontsize of the tick labels
plt.rc("legend", fontsize=SMALL_SIZE)  # legend fontsize
plt.rc("figure", titlesize=BIGGER_SIZE)  # fontsize of the figure title

matplotlib.rcParams["pdf.fonttype"] = 42
matplotlib.rcParams["ps.fonttype"] = 42


def detect_artifacts_in_external_recording(
    session_ID: str,
    BIP_channel: np.ndarray,
    sf_external,
    saving_path: str,
    start_index: int = 0,
):
    """
    This function synchronizes the intracranial recording with
    the external recording of the same session.

    Inputs:
        - session_ID: str, session identifier
        - BIP_channel: np.ndarray, the channel of the external recording to be
        used for synchronization (the one containing deep brain stimulation
        artifacts = the channel recorded with the bipolar electrode)
        - sf_external: sampling frequency of external recording
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
    b, a = scipy.signal.butter(1, 0.05, "highpass")
    filtered_external = scipy.signal.filtfilt(b, a, BIP_channel)

    # PLOT 1 :
    # plot the signal of the external channel used for artifact detection:
    plot_BIP_artifact_channel(
        session_ID=session_ID,
        timescale=external_timescale_s,
        data=filtered_external,
        color="darkcyan",
        saving_path=saving_path,
    )
    plt.close()

    ### DETECT ARTIFACTS ###

    # find artifacts in external bipolar channel:
    art_start_BIP = find_external_sync_artifact(
        data=filtered_external, sf_external=sf_external, start_index=start_index
    )

    # PLOT 2 : plot the external channel with its artifacts detected:
    plot_channel(
        session_ID=session_ID,
        timescale=external_timescale_s,
        data=filtered_external,
        color="darkcyan",
        scatter=False,
    )
    plt.ylabel("Artifact channel BIP (mV)")
    plt.axvline(x=art_start_BIP, color="black", linestyle="dashed", alpha=0.3)
    plt.gcf()
    filename = "Fig2-External bipolar channel with artifact detected.png"
    plt.savefig(join(saving_path, filename), bbox_inches="tight")
    plt.show(block=False)

    # PLOT 3 :
    # plot the first artifact detected in external channel (verification of sample choice):
    plot_channel(
        session_ID=session_ID,
        timescale=external_timescale_s,
        data=filtered_external,
        color="darkcyan",
        scatter=True,
    )
    plt.ylabel("Artifact channel BIP - Voltage (mV)")
    plt.xlim(art_start_BIP - (60 / sf_external), art_start_BIP + (60 / sf_external))
    plt.axvline(x=art_start_BIP, color="black", linestyle="dashed", alpha=0.3)
    plt.gcf()
    filename = "Fig3-External bipolar channel - first artifact detected.png"
    plt.savefig(join(saving_path, filename), bbox_inches="tight")
    plt.show(block=False)

    return art_start_BIP


def detect_artifacts_in_intracranial_recording(
    session_ID: str, lfp_sig: np.ndarray, sf_LFP, saving_path: str, kernel: str
):
    """
    This function synchronizes the intracranial recording with
    the external recording of the same session.

    Inputs:
        - session_ID: str, session identifier
        - lfp_sig: np.ndarray, the channel of the intracranial recording to be
        used for synchronization (the one containing deep brain stimulation artifacts)
        - sf_LFP: sampling frequency of intracranial recording
        - saving_path: str, path to the folder where the figures will be saved
        - kernel: str, method used for artifact detection in intracranial recording
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
    plot_LFP_artifact_channel(
        session_ID=session_ID,
        timescale=LFP_timescale_s,
        data=lfp_sig,
        color="darkorange",
        saving_path=saving_path,
    )
    plt.close()

    ### DETECT ARTIFACTS ###
    if kernel in ["1", "2", "thresh"]:
        art_start_LFP = find_LFP_sync_artifact(
            data=lfp_sig, sf_LFP=sf_LFP, use_kernel=kernel
        )

        # PLOT 5 :
        # plot the intracranial channel with its artifacts detected:
        plot_channel(
            session_ID=session_ID,
            timescale=LFP_timescale_s,
            data=lfp_sig,
            color="darkorange",
            scatter=False,
        )
        plt.ylabel("Intracranial LFP channel (µV)")
        plt.axvline(
            x=art_start_LFP,
            ymin=min(lfp_sig),
            ymax=max(lfp_sig),
            color="black",
            linestyle="dashed",
            alpha=0.3,
        )
        plt.gcf()
        filename = (
            "Fig5-Intracranial channel with artifact detected - kernel "
            + str(kernel)
            + ".png"
        )
        plt.savefig(join(saving_path, filename), bbox_inches="tight")
        plt.show(block=False)

        # PLOT 6 :
        # plot the first artifact detected in intracranial channel (verification of sample choice):
        plot_channel(
            session_ID=session_ID,
            timescale=LFP_timescale_s,
            data=lfp_sig,
            color="darkorange",
            scatter=True,
        )
        plt.ylabel("Intracranial LFP channel (µV)")
        plt.xlim(art_start_LFP - 0.1, art_start_LFP + 0.3)
        plt.axvline(
            x=art_start_LFP,
            ymin=min(lfp_sig),
            ymax=max(lfp_sig),
            color="black",
            linestyle="dashed",
            alpha=0.3,
        )
        plt.gcf()
        filename = (
            "Fig6-Intracranial channel - first artifact detected - kernel "
            + str(kernel)
            + ".png"
        )
        plt.savefig(join(saving_path, filename), bbox_inches="tight")
        plt.show(block=False)

    if kernel == "manual":
        print(
            f"Automatic detection of intracranial artifacts failed, using manual method. \n"
            f"In the pop up window, zoom on the first artifact until you can select properly  "
            f"the last sample before the deflection, click on it and close the window."
        )
        art_start_LFP = select_sample(
            signal=lfp_sig, sf=sf_LFP, color1="peachpuff", color2="darkorange"
        )

        # PLOT 7 : plot the artifact adjusted by user in the intracranial channel:
        plot_channel(
            session_ID=session_ID,
            timescale=LFP_timescale_s,
            data=lfp_sig,
            color="darkorange",
            scatter=True,
        )
        plt.ylabel("Intracranial LFP channel (µV)")
        plt.xlim(art_start_LFP - 0.1, art_start_LFP + 0.3)
        plt.axvline(
            x=art_start_LFP,
            ymin=min(lfp_sig),
            ymax=max(lfp_sig),
            color="black",
            linestyle="dashed",
            alpha=0.3,
        )

        plt.gcf()
        filename = "Fig7-Intracranial channel - first artifact corrected by user.png"
        plt.savefig(join(saving_path, filename), bbox_inches="tight")
        plt.show(block=False)

    return art_start_LFP


def synchronize_recordings(
    LFP_array: np.ndarray,
    external_file,
    art_start_LFP,
    art_start_BIP,
    sf_LFP,
    sf_external,
    CROP_BOTH,
):
    """
    This function synchronizes the intracranial recording with
    the external recording of the same session.

    Inputs:
        - LFP_array: np.ndarray, intracranial recording
        - external_file: np.ndarray, external recording
        - art_start_LFP: the timestamp when the artifact starts in intracranial recording
        - art_start_BIP: the timestamp when the artifact starts in external recording
        - sf_LFP: sampling frequency of intracranial recording
        - sf_external: sampling frequency of external recording
        - CROP_BOTH: bool, if True, both recordings are cropped 1 second before
        first artifact. If False, only external recording is cropped to match
        intracranial recording

    Returns:
        - LFP_synchronized: np.ndarray, intracranial recording synchronized with external recording
        - external_synchronized: np.ndarray, external recording synchronized with intracranial recording
    """

    if CROP_BOTH:
        # crop intracranial and external recordings 1 second before first artifact
        (LFP_synchronized, external_synchronized) = sync_by_cropping_both(
            LFP_array=LFP_array,
            external_file=external_file,
            art_start_LFP=art_start_LFP,
            art_start_BIP=art_start_BIP,
            sf_LFP=sf_LFP,
            sf_external=sf_external,
        )

    else:
        # only crop beginning and end of external recording to match LFP recording:
        (LFP_synchronized, external_synchronized) = align_external_on_LFP(
            LFP_array=LFP_array,
            external_file=external_file,
            art_start_LFP=art_start_LFP,
            art_start_BIP=art_start_BIP,
            sf_LFP=sf_LFP,
            sf_external=sf_external,
        )

    return LFP_synchronized, external_synchronized


def save_synchronized_recordings(
    session_ID,
    LFP_synchronized,
    external_synchronized,
    LFP_rec_ch_names,
    external_rec_ch_names,
    sf_LFP,
    sf_external,
    saving_format,
    saving_path,
    CROP_BOTH,
):
    """
    This function saves the synchronized intracranial and external recordings.

    Inputs:
        - session_ID: str, session identifier
        - LFP_synchronized: np.ndarray, intracranial recording synchronized with external recording
        - external_synchronized: np.ndarray, external recording synchronized with intracranial recording
        - LFP_rec_ch_names: list, names of the intracranial recording channels
        - external_rec_ch_names: list, names of the external recording channels
        - sf_LFP: sampling frequency of intracranial recording
        - sf_external: sampling frequency of external recording
        - saving_format: str, format in which the recordings will be saved
        - saving_path: str, path to the folder where the recordings will be saved
        - CROP_BOTH: bool, if True, both recordings are cropped 1 second before
        first artifact. If False, only external recording is cropped to match
        intracranial recording

    """

    assert saving_format in ["csv", "mat", "pickle", "brainvision"], (
        "saving_format incorrect." "Choose in: csv, mat, pickle, brainvision"
    )

    if CROP_BOTH:
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

        print(
            "Alignment performed, both recordings were cropped and saved 1s before first artifact !"
        )

    else:
        external_df_offset = pd.DataFrame(external_synchronized)
        external_df_offset.columns = external_rec_ch_names

        if saving_format == "csv":
            external_df_offset["sf_external"] = sf_external
            external_df_offset.to_csv(
                join(saving_path, ("External_data_" + str(session_ID) + ".csv")),
                index=False,
            )

        if saving_format == "pickle":
            external_df_offset["sf_external"] = sf_external
            external_filename = join(
                saving_path, ("External_data_" + str(session_ID) + ".pkl")
            )
            # Save the dataset to a pickle file
            with open(external_filename, "wb") as file:
                pickle.dump(external_df_offset, file)

        if saving_format == "mat":
            external_filename = join(
                saving_path, ("External_data_" + str(session_ID) + ".mat")
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

        if saving_format == "brainvision":
            external_filename = "External_data_" + str(session_ID)
            write_brainvision(
                data=external_synchronized.T,
                sfreq=sf_external,
                ch_names=external_rec_ch_names,
                fname_base=external_filename,
                folder_out=saving_path,
                overwrite=True,
            )

        print(
            "Alignment performed, only external recording as been cropped "
            "to match LFP recording !"
        )
