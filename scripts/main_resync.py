# import librairies
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import json
import pickle
from scipy.io import savemat
import pyedflib
from pyedflib import highlevel

#import custom-made functions
#from utils import *
from utils import _convert_index_to_time, _convert_time_to_index, _filtering, _get_input_y_n, _update_and_save_params
from find_artefacts import *
from plotting import *
from sync import crop_rec, align_external_on_LFP
from find_packet_loss import *
from interactive import select_sample

## set font sizes and other parameters for the figures
SMALL_SIZE = 12
MEDIUM_SIZE = 14
BIGGER_SIZE = 16

plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=MEDIUM_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=SMALL_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title

matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42


def run_resync(
    sub_ID,
    kernel,
    LFP_array, 
    lfp_sig, 
    LFP_rec_ch_names, 
    sf_LFP,
    external_file,
    BIP_channel, 
    external_rec_ch_names,
    sf_external,
    saving_path,
    saving_format,
    CROP_BOTH = True,
    SHOW_FIGURES = True
):

    """
    This function aligns the intracerebral recording with
    the external recording of the same session.

    Inputs:
        - LFP_array (np.ndarray with shape: (x, y)): the intracerebral recording 
            containing all recorded channels (x channels, y datapoints)
        - lfp_sig (np.ndarray with shape: (y,)): the channel of the intracerebral 
            recording to be used for alignment (the one containing deep brain 
            stimulation artefacts, y datapoints)
        - LFP_rec_ch_names (list of x names): the names of all the channels 
            recorded intracerebrally
        - sf_LFP (int): sampling frequency of intracranial recording
        - external_file (np.ndarray with shape: (x, y)): the external recording 
            containing all recorded channels (x channels, y datapoints)
        - BIP_channel (np.ndarray with shape (y,)): the channel of the external 
            recording to be used for alignment (the one containing deep brain 
            stimulation artefacts = the channel recorded with the bipolar 
            electrode, y datapoints)
        - external_rec_ch_names (list of x names): the names of all the channels 
            recorded externally
        - sf_external (int): sampling frequency of external recording
        - real_art_time_LFP (float): default 0, but can be changed in notebook via 
            interactive plotting to adjust artefact detection
        - SHOW_FIGURES: True or False, depending of whether the user wants the 
            figures to appear in the notebook directly or not.
    
    Outputs:
        - LFP_df_offset (np.ndarray with shape: (x, y2)): the intracerebral recording containing all recorded 
            channels, cropped one second before the first artefact
        - external_df_offset (np.ndarray with shape: (x, y2)): the external recording containing all recorded 
            channels, cropped one second before the first artefact
    """


    assert saving_format in ['csv','mat','pickle'], 'saving_format incorrect. Choose in: csv, mat, pickle'


    # Generate timescales:
    LFP_timescale_s = np.arange(
        start=0, 
        stop=(len(lfp_sig)/sf_LFP), 
        step=(1/sf_LFP)
    )
    external_timescale_s = np.arange(
        start=0, 
        stop=(len(BIP_channel)/sf_external), 
        step=(1/sf_external)
    )

    # PLOT 1 : plot the signal of the channel used for artefact detection in intracerebral recording:
    plot_LFP_artefact_channel(
        sub=sub_ID, 
        timescale=LFP_timescale_s, 
        data=lfp_sig, 
        color='darkorange', 
        savingpath=saving_path
    )
    #if SHOW_FIGURES: 
        #plt.show(block=False)
    #else: 
        #plt.close()
    plt.close()


    filtered_external = _filtering(BIP_channel) # apply a highpass filter at 1Hz to the external bipolar channel (detrending)

    # PLOT 2 : plot the signal of the channel used for artefact detection in external recording:
    plot_BIP_artefact_channel(
        sub=sub_ID, 
        timescale=external_timescale_s, 
        data=filtered_external,
        color='darkcyan',
        savingpath=saving_path
    )
    #if SHOW_FIGURES: 
        #plt.show(block=False)
    #else: 
        #plt.close()
    plt.close()


    ### DETECT ARTEFACTS ###

    # find artefacts in intracerebral channel
    art_idx_LFP = find_LFP_sync_artefact(
        lfp_data=lfp_sig,
        sf_LFP=sf_LFP,
        use_kernel=kernel, 
        consider_first_seconds_LFP=None
    )

    art_time_LFP = _convert_index_to_time(
        art_idx=art_idx_LFP,
        sf=sf_LFP
    ) 

    # PLOT 3 : plot the intracerebral channel with its artefacts detected:
    plot_channel(
        sub=sub_ID, 
        timescale=LFP_timescale_s, 
        data=lfp_sig,
        color='darkorange',
        scatter=False
    )
    plt.ylabel('Intracerebral LFP channel (µV)')
    for xline in art_time_LFP:
        plt.axvline(
            x=xline, 
            ymin=min(lfp_sig), 
            ymax=max(lfp_sig), 
            color='black', 
            linestyle='dashed',
            alpha=.3
        )
    plt.gcf()
    plt.savefig(
        saving_path 
        + '\\Fig3-Intracerebral channel with artefacts detected - kernel ' 
        + str(kernel) 
        + '.png',
        bbox_inches='tight'
    )
    if SHOW_FIGURES: 
        plt.show(block=False)
    else: 
        plt.close()
    

    # PLOT 4 : plot the first artefact detected in intracerebral channel for verification of sample choice:
    plot_channel(
        sub=sub_ID, 
        timescale=LFP_timescale_s, 
        data=lfp_sig, 
        color='darkorange',
        scatter=True
    )
    plt.ylabel('Intracerebral LFP channel (µV)')
    plt.xlim(art_time_LFP[0]-0.1, art_time_LFP[0]+0.3)
    for xline in art_time_LFP:
        plt.axvline(
            x=xline, 
            ymin=min(lfp_sig), 
            ymax=max(lfp_sig), 
            color='black', 
            linestyle='dashed', 
            alpha=.3
        )
    plt.gcf()
    plt.savefig(saving_path 
                + '\\Fig4-Intracerebral channel - first artefact detected - kernel ' 
                + str(kernel) 
                + '.png', 
                bbox_inches='tight'
    )
    if SHOW_FIGURES: 
        plt.show(block=False)
    else: 
        plt.close()

    # find artefacts in external bipolar channel:
    art_idx_BIP = find_external_sync_artefact(
        data=filtered_external, 
        sf_external=sf_external
    )
    
    
    art_time_BIP = _convert_index_to_time(
        art_idx=art_idx_BIP, 
        sf=sf_external
    )

    # PLOT 6 : plot the external channel with its artefacts detected:
    plot_channel(
        sub=sub_ID, 
        timescale=external_timescale_s, 
        data=filtered_external, 
        color='darkcyan',
        scatter=False
    )
    plt.ylabel('Artefact channel BIP (mV)')
    for xline in art_time_BIP:
        plt.axvline(
            x=xline, 
            color='black', 
            linestyle='dashed', 
            alpha=.3
        )
    plt.gcf()
    plt.savefig(
        saving_path 
        + '\\Fig6-External bipolar channel with artefacts detected.png',
        bbox_inches='tight'
    )
    if SHOW_FIGURES: 
        plt.show(block=False)
    else: 
        plt.close()

    # PLOT 7 : plot the first artefact detected in external channel for verification of sample choice:
    plot_channel(
        sub=sub_ID, 
        timescale=external_timescale_s, 
        data=filtered_external, 
        color='darkcyan',
        scatter=True
    )
    plt.ylabel('Artefact channel BIP - Voltage (mV)')
    plt.xlim(
        art_time_BIP[0]-(60/sf_external),
        art_time_BIP[0]+(60/sf_external)
    )
    for xline in art_time_BIP:
        plt.axvline(
            x=xline, 
            color='black', 
            linestyle='dashed', 
            alpha=.3
        )
    plt.gcf()
    plt.savefig(
        saving_path 
        + '\\Fig7-External bipolar channel - first artefact detected.png',
        bbox_inches='tight'
    )   
    if SHOW_FIGURES: 
        plt.show(block=False)
    else: 
        plt.close()


    AUTOMATIC_PROCESSING_GOOD = False

    artefact_correct = _get_input_y_n("Are artefacts properly selected ? ")
    if artefact_correct == 'y':
        AUTOMATIC_PROCESSING_GOOD = True
    
    if AUTOMATIC_PROCESSING_GOOD:
        if CROP_BOTH:
            # crop intracerebral and external recordings 1 second before first artefact
            (LFP_df_offset, 
            external_df_offset) = crop_rec(
                LFP_array, 
                external_file, 
                art_time_LFP, 
                art_time_BIP, 
                LFP_rec_ch_names, 
                external_rec_ch_names, 
                sf_LFP,
                sf_external,
                real_art_time_LFP=0
                )


        else:
            # only crop beginning and end of external recording to match LFP recording:
            (LFP_df_offset, 
            external_df_offset) = align_external_on_LFP(LFP_array, 
                external_file, 
                art_time_LFP, 
                art_time_BIP,  
                external_rec_ch_names, 
                sf_LFP,
                sf_external,
                real_art_time_LFP=0)


    else: 
        closest_value_lfp = select_sample(lfp_sig, sf_LFP)
        _update_and_save_params('REAL_ART_TIME_LFP_CORRECTED', 'yes', sub_ID, saving_path)
        _update_and_save_params('REAL_ART_TIME_LFP_VALUE', closest_value_lfp, sub_ID, saving_path)
                
        # PLOT 5 : plot the artefact adjusted by user in the intracerebral channel:
        if closest_value_lfp != 0 :
            plot_channel(
                sub=sub_ID, 
                timescale=LFP_timescale_s, 
                data=lfp_sig, 
                color='darkorange',
                scatter=True
            )
            plt.ylabel('Intracerebral LFP channel (µV)')
            plt.xlim(closest_value_lfp-0.1, closest_value_lfp+0.3)
            plt.axvline(
                x=closest_value_lfp, 
                ymin=min(lfp_sig), 
                ymax=max(lfp_sig), 
                color='black', 
                linestyle='dashed', 
                alpha=.3
            )

            plt.gcf()
            plt.savefig(
                saving_path 
                + '\\Fig5-Intracerebral channel - first artefact detected with correction by user - kernel ' 
                + str(kernel) 
                + '.png', 
                bbox_inches='tight'
            )
            if SHOW_FIGURES: 
                plt.show(block=False)
            else: 
                plt.close()

        if CROP_BOTH:
            # crop intracerebral and external recordings 1 second before first artefact
            (LFP_df_offset, 
            external_df_offset) = crop_rec(
                LFP_array, 
                external_file, 
                art_time_LFP, 
                art_time_BIP, 
                LFP_rec_ch_names, 
                external_rec_ch_names, 
                sf_LFP,
                sf_external,
                real_art_time_LFP=closest_value_lfp
                )

        else:
            # only crop beginning and end of external recording to match LFP recording:
            (LFP_df_offset, 
            external_df_offset) = align_external_on_LFP(LFP_array, 
                external_file, 
                art_time_LFP, 
                art_time_BIP,  
                external_rec_ch_names, 
                sf_LFP,
                sf_external,
                real_art_time_LFP=closest_value_lfp)
        
    ###  SAVE CROPPED RECORDINGS ###  
    _update_and_save_params('SAVING_FORMAT', saving_format, sub_ID, saving_path) 

    if CROP_BOTH:
        if saving_format == 'csv':
            LFP_df_offset['sf_LFP'] = sf_LFP
            external_df_offset['sf_external'] = sf_external
            LFP_df_offset.to_csv(saving_path + '\\Intracerebral_LFP_' + str(sub_ID) + '.csv', index=False) 
            external_df_offset.to_csv(saving_path + '\\External_data_' + str(sub_ID) + '.csv', index=False)

        if saving_format == 'pickle':
            LFP_df_offset['sf_LFP'] = sf_LFP
            external_df_offset['sf_external'] = sf_external
            LFP_filename = (saving_path + '\\Intracerebral_LFP_' + str(sub_ID) + '.pkl')
            external_filename = (saving_path + '\\External_data_' + str(sub_ID) + '.pkl')
            # Save the dataset to a pickle file
            with open(LFP_filename, 'wb') as file:
                pickle.dump(LFP_df_offset, file)
            with open(external_filename, 'wb') as file:
                pickle.dump(external_df_offset, file)            

        if saving_format == 'mat':
            LFP_filename = (saving_path + '\\Intracerebral_LFP_' + str(sub_ID) + '.mat')
            external_filename = (saving_path + '\\External_data_' + str(sub_ID) + '.mat')
            savemat(LFP_filename, {'data': LFP_df_offset.T,'fsample': sf_LFP, 'label': np.array(LFP_df_offset.columns.tolist(), dtype=object).reshape(-1,1)})
            savemat(external_filename, {'data': external_df_offset.T, 'fsample': sf_external, 'label': np.array(external_df_offset.columns.tolist(), dtype=object).reshape(-1,1)})

        print('Alignment performed, both recordings were cropped and saved 1s before first artefact !')

    else:
        if saving_format == 'csv':
            external_df_offset['sf_external'] = sf_external
            external_df_offset.to_csv(saving_path + '\\External_data_' + str(sub_ID) + '.csv', index=False)

        if saving_format == 'pickle':
            external_df_offset['sf_external'] = sf_external
            external_filename = (saving_path + '\\External_data_' + str(sub_ID) + '.pkl')
            # Save the dataset to a pickle file
            with open(external_filename, 'wb') as file:
                pickle.dump(external_df_offset, file)            

        if saving_format == 'mat':
            external_filename = (saving_path + '\\External_data_' + str(sub_ID) + '.mat')
            savemat(external_filename, {'data': external_df_offset.T, 'fsample': sf_external, 'label': np.array(external_df_offset.columns.tolist(), dtype=object).reshape(-1,1)})

        print('Alignment performed, only external recording as been cropped to match LFP recording !')


    return LFP_df_offset, external_df_offset
