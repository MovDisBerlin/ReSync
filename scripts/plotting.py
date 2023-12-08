import numpy as np
import matplotlib
import matplotlib.pyplot as plt
#plt.switch_backend('agg')
from matplotlib.pyplot import figure
import mne


def plot_LFP_artefact_channel(
    sub: str,
    timescale: np.ndarray,
    data: np.ndarray, 
    color: str,
    savingpath: str,
    saving_folder = True
):

    """
    Function that plots the selected intracerebral channel for quick visualization (and saving).

    Input:
        - sub: the subject ID
        - timescale: the timescale of the signal to be plotted (x) as np.ndarray
        - data: single channel as np.ndarray (y)
        - color: the color of the signal on the plot
        - savingpath: the folder where the plot has to be saved
        - saving_folder: Boolean, default = True, plots are automatically saved
    """

    figure(figsize=(12, 6), dpi=80)
    plt.plot(
        timescale, 
        data, 
        linewidth=1, 
        color=color
    )
    plt.xlabel('Time (s)')
    plt.title(str(sub))
    plt.ylabel('Intracerebral LFP channel (µV)')

    if saving_folder:
        plt.savefig(
            savingpath 
            + '\\Fig1-Intracerebral channel raw plot.png',
            bbox_inches='tight'
        )




### Plot a single channel with its associated timescale ###

def plot_BIP_artefact_channel(
    sub: str,
    timescale: np.ndarray,
    data: np.ndarray, 
    color: str,
    savingpath: str,
    saving_folder = True
):

    """
    Function that plots the external bipolar channel for quick visualization (and saving).

    Input:
        - sub: the subject ID
        - timescale: the timescale of the signal to be plotted (x) as np.ndarray
        - data: single channel as np.ndarray (y)
        - color: the color of the signal on the plot
        - savingpath: the folder where the plot has to be saved
        - saving_folder: Boolean, default = True, plots automatically saved
    """

    figure(figsize=(12, 6), dpi=80)
    plt.plot(
        timescale, 
        data, 
        linewidth=1, 
        color=color
    )
    plt.xlabel('Time (s)')
    plt.title(str(sub))
    plt.ylabel('External bipolar channel - voltage (mV)')

    if saving_folder:
        plt.savefig(
            savingpath 
            + '\\Fig2-External bipolar channel raw plot.png',
            bbox_inches='tight'
        )



### Plot both hemisphere LFP activity with stimulation amplitude ###

def plot_LFP_stim(
    sub: str,
    timescale: np.ndarray,
    LFP_rec: mne.io.array.array.RawArray,
    savingpath: str,
    saving_folder = True,
):
    
    """
    Function that plots all together the LFP and 
    the stimulation from the 2 hemispheres.

    Input:
        - sub: the subject ID
        - timescale: the timescale of the signal to be plotted (x) as np.ndarray
        - LFP_rec: mne.io.array.array.RawArray (LFP recording as MNE object)
        - savingpath: the folder where the plot has to be saved
        - saving_folder: Boolean, default = True, plots automatically saved

    
    Returns:
        - the plotted signal with the stim
    """

    LFP_L_channel = LFP_rec.get_data()[0]
    LFP_R_channel = LFP_rec.get_data()[1]
    stim_L_channel = LFP_rec.get_data()[4]
    stim_R_channel = LFP_rec.get_data()[5]
    figure(figsize=(12, 6), dpi=80)
    fig, (ax1, ax2, ax3, ax4) = plt.subplots(4,1)
    ax1.set_title(str(sub))
    ax1.plot(timescale, LFP_L_channel, linewidth=1, color='darkorange')
    ax2.plot(timescale, stim_L_channel, linewidth=1, color='darkorange', linestyle='dashed')
    ax3.plot(timescale, LFP_R_channel, linewidth=1, color='purple')
    ax4.plot(timescale, stim_R_channel, linewidth=1, color='purple', linestyle='dashed')
    ax1.axes.xaxis.set_ticklabels([])
    ax2.axes.xaxis.set_ticklabels([])
    ax3.axes.xaxis.set_ticklabels([])
    ax1.set_ylabel('LFP \n left (µV)')
    ax2.set_ylabel('stim \n left (mA)')
    ax3.set_ylabel('LFP \n right (µV)')
    ax4.set_ylabel('stim \n right (mA)')
    ax1.set_ylim(min(LFP_L_channel) - 50, max(LFP_L_channel) + 50)
    ax2.set_ylim(0, max(stim_L_channel) + 0.5)
    ax3.set_ylim(min(LFP_R_channel) - 50, max(LFP_R_channel) + 50)
    ax4.set_ylim(0, max(stim_R_channel) + 0.5)
    plt.xlabel('Time (s)')
    fig.tight_layout()

    if saving_folder:
        plt.savefig(
            savingpath 
            + '\\LFP and stim bilateral - raw plot.png',
            bbox_inches='tight'
        )
    return plt.gcf()


### Plot a single channel with its associated timescale ###

def plot_channel(
    sub: str,
    timescale: np.ndarray,
    data: np.ndarray, 
    color: str,
    scatter = False,
):

    """
    Function that plots the selected channel for quick visualization (and saving).

    Input:
        - sub: the subject ID
        - timescale: the timescale of the signal to be plotted (x) as np.ndarray
        - data: single channel as np.ndarray (y)
        - color: the color of the signal on the plot
        - scatter: True or False, if the user wants to see the 
        samples instead of a continuous line
    
    Returns:
        - the plotted signal
    """

    figure(figsize=(12, 6), dpi=80)
    if scatter:
        plt.scatter(timescale, data, color=color)
    else:
        plt.plot(timescale, data, linewidth=1, color=color)
    plt.xlabel('Time (s)')
    plt.title(str(sub))

    return plt.gcf()




from utils import _filtering

def plot_LFP_external(
        sub_ID, LFP_df_offset, external_df_offset, sf_LFP, sf_external, ch_idx_lfp, ch_index_external, saving_path, SHOW_FIGURES = True
):
    # Reselect artefact channels in the aligned (= cropped) files
    LFP_channel_offset = LFP_df_offset.iloc[:,ch_idx_lfp].to_numpy()  
    BIP_channel_offset = external_df_offset.iloc[:,ch_index_external].to_numpy() 

     # pre-processing of external bipolar channel :
    filtered_external_offset = _filtering(BIP_channel_offset)

    # Generate new timescales:
    LFP_timescale_offset_s = np.arange(0,(len(LFP_channel_offset)/sf_LFP),1/sf_LFP)
    external_timescale_offset_s = np.arange(0,(len(BIP_channel_offset)/sf_external),1/sf_external)

    # PLOT 8: Both signals aligned with all their artefacts detected:
    fig, ax1 = plt.subplots()
    fig.suptitle(str(sub_ID))
    fig.set_figheight(6)
    fig.set_figwidth(12)
    #ax1.axes.xaxis.set_ticklabels([])
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Intracerebral LFP channel (µV)')
    ax1.set_xlim(0,len(LFP_channel_offset)/sf_LFP) 
    #ax2.set_xlim(0,len(LFP_channel_offset)/sf_LFP) 
    ax1.plot(LFP_timescale_offset_s,LFP_channel_offset,color='darkorange',zorder=1, linewidth=0.3)
    ax2 = ax1.twinx()
    ax2.plot(external_timescale_offset_s,filtered_external_offset, color='darkcyan',zorder=1, linewidth=0.1)
    ax2.set_ylabel('External bipolar channel (mV)')
    fig.savefig(saving_path + '\\Fig8-Intracerebral and external recordings aligned.png',bbox_inches='tight')
    if SHOW_FIGURES: plt.show()
    else: plt.close()

