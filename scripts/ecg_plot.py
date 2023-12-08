
import json
import os
import numpy as np
import matplotlib.pyplot as plt
from os.path import join
from utils import _define_folders, _filtering


def ecg(
        LFP_df_offset, 
        sf_LFP,
        external_df_offset,
        sf_external,
        xmin,
        xmax,
        SHOW_FIGURES=True
):
    
    #import settings
    json_path = os.path.join(os.getcwd(), 'config')
    json_filename = 'config.json'  # dont forget json extension
    with open(os.path.join(json_path, json_filename), 'r') as f:
        loaded_dict =  json.load(f)

    #set saving path
    if not loaded_dict['SAVING_PATH']:
        saving_path = _define_folders()
    else:
        saving_path = os.path.join(os.path.normpath(loaded_dict['SAVING_PATH']), loaded_dict['SUBJECT_ID'])
        if not os.path.isdir(saving_path):
            os.makedirs(saving_path)

    # Reselect artefact channels in the aligned (= cropped) files
    LFP_channel_offset = LFP_df_offset.iloc[:, loaded_dict['LFP_CH_INDEX']].to_numpy()  
    BIP_channel_offset = external_df_offset.iloc[:, loaded_dict['BIP_CH_INDEX']].to_numpy() 

    # pre-processing of external bipolar channel before searching artefacts:
    filtered_external_offset = _filtering(BIP_channel_offset)

    # Generate new timescales:
    LFP_timescale_offset_s = np.arange(0, (len(LFP_channel_offset)/sf_LFP), 1/sf_LFP)
    external_timescale_offset_s = np.arange(0, (len(BIP_channel_offset)/sf_external), 1/sf_external)

    #make plot on beginning of recordings:
    fig, (ax1, ax2) = plt.subplots(2,1)
    fig.suptitle(str(loaded_dict['SUBJECT_ID']))
    fig.set_figheight(6)
    fig.set_figwidth(12)
    ax1.axes.xaxis.set_ticklabels([])
    ax2.set_xlabel('Time (s)')
    ax1.set_ylabel('Intracerebral LFP channel (µV)')
    ax2.set_ylabel('External bipolar channel (mV)')
    ax1.set_xlim(xmin, xmax) 
    ax2.set_xlim(xmin, xmax)
    #ax1.set_ylim(-50, 20) 
    ax1.plot(LFP_timescale_offset_s, LFP_channel_offset, color='darkorange', zorder=1, linewidth=1)
    ax2.plot(external_timescale_offset_s, filtered_external_offset, color='darkcyan', zorder=1, linewidth=1) 
    fig.savefig(saving_path + '\\Fig_ECG.png', bbox_inches='tight')
    if SHOW_FIGURES: plt.show()
    else: plt.close()

