# import librairies
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pickle
from scipy.io import savemat

#import custom-made functions
from utils import (_convert_index_to_time, _filtering, _get_input_y_n, 
_update_and_save_params)
from find_artifacts import *
from plotting import *
from sync import crop_rec, align_external_on_LFP
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
    session_ID: str,
    LFP_array: np.ndarray, 
    lfp_sig: np.ndarray, 
    LFP_rec_ch_names: list, 
    sf_LFP,
    external_file: np.ndarray,
    BIP_channel: np.ndarray, 
    external_rec_ch_names: list,
    sf_external,
    saving_path: str,
    saving_format: str,
    CROP_BOTH: bool = True,
    SHOW_FIGURES: bool = True
):

    """
    This function synchronizes the intracerebral recording with
    the external recording of the same session.

    Inputs:
        - LFP_array: nd.nparray, the intracerebral recording containing all 
        recorded channels
        - lfp_sig: np.ndarray, the channel of the intracerebral recording to be
        used for alignment (the one containing deep brain stimulation artifacts)
        - LFP_rec_ch_names: list, names of all channels recorded intracerebrally
        - sf_LFP: sampling frequency of intracranial recording
        - external_file: np.ndarray, the external recording containing all 
        recorded channels
        - BIP_channel: np.ndarray, the channel of the external recording to be 
        used for alignment (the one containing deep brain stimulation artifacts 
        = the channel recorded with the bipolar electrode)
        - external_rec_ch_names: list, names of all channels recorded externally
        - sf_external: sampling frequency of external recording
        - saving_path: str,
        - saving_format: str, choose between .csv, .mat or .pickle
        - CROP_BOTH: bool = True,
        - SHOW_FIGURES: True or False, depending of whether the user wants the 
            figures to appear while processing or not.
    
    Outputs:
        - LFP_df_offset: np.ndarray, the intracerebral recording containing all 
        recorded channels, aligned with external recording
        - external_df_offset: np.ndarray, the external recording containing all 
        recorded channels, aligned with intracerebral recording
    """


    assert saving_format in ['csv','mat','pickle'], 'saving_format incorrect.' \
    'Choose in: .csv, .mat, .pickle'


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

    # PLOT 1 : 
    # raw signal of the intracerebral channel used for artifact detection:
    plot_LFP_artifact_channel(
        sub=session_ID, 
        timescale=LFP_timescale_s, 
        data=lfp_sig, 
        color='darkorange', 
        savingpath=saving_path
    )
    plt.close()

    # apply a highpass filter at 1Hz to the external bipolar channel (detrending)
    filtered_external = _filtering(BIP_channel) 

    # PLOT 2 : 
    # plot the signal of the external channel used for artifact detection:
    plot_BIP_artifact_channel(
        sub=session_ID, 
        timescale=external_timescale_s, 
        data=filtered_external,
        color='darkcyan',
        savingpath=saving_path
    )
    plt.close()


    ### DETECT ARTIFACTS ###

    # find artifacts in external bipolar channel:
    art_idx_BIP = find_external_sync_artifact(
        data=filtered_external, 
        sf_external=sf_external
    )
    
    
    art_time_BIP = _convert_index_to_time(
        art_idx=art_idx_BIP, 
        sf=sf_external
    )

    # PLOT 3 : plot the external channel with its artifacts detected:
    plot_channel(
        sub=session_ID, 
        timescale=external_timescale_s, 
        data=filtered_external, 
        color='darkcyan',
        scatter=False
    )
    plt.ylabel('Artifact channel BIP (mV)')
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
        + '\\Fig3-External bipolar channel with artifacts detected.png',
        bbox_inches='tight'
    )
    if SHOW_FIGURES: 
        plt.show(block=False)
    else: 
        plt.close()

    # PLOT 4 : 
    # plot the first artifact detected in external channel (verification of sample choice):
    plot_channel(
        sub=session_ID, 
        timescale=external_timescale_s, 
        data=filtered_external, 
        color='darkcyan',
        scatter=True
    )
    plt.ylabel('Artifact channel BIP - Voltage (mV)')
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
        + '\\Fig4-External bipolar channel - first artifact detected.png',
        bbox_inches='tight'
    )   
    if SHOW_FIGURES: 
        plt.show(block=False)
    else: 
        plt.close()



    # find artifacts in intracerebral channel
    kernel = '2' # default kernel
    art_idx_LFP = find_LFP_sync_artifact(
        lfp_data=lfp_sig,
        sf_LFP=sf_LFP,
        use_kernel=kernel, 
        consider_first_seconds_LFP=None
    )

    art_time_LFP = _convert_index_to_time(
        art_idx=art_idx_LFP,
        sf=sf_LFP
    ) 

    # PLOT 5 : 
    # plot the intracerebral channel with its artifacts detected:
    plot_channel(
        sub=session_ID, 
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
        + '\\Fig5-Intracerebral channel with artifacts detected - kernel ' 
        + str(kernel) 
        + '.png',
        bbox_inches='tight'
    )
    if SHOW_FIGURES: 
        plt.show(block=False)
    else: 
        plt.close()
    

    # PLOT 6 : 
    # plot the first artifact detected in intracerebral channel (verification of sample choice):
    plot_channel(
        sub=session_ID, 
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
                + '\\Fig6-Intracerebral channel - first artifact detected - kernel ' 
                + str(kernel) 
                + '.png', 
                bbox_inches='tight'
    )
    if SHOW_FIGURES: 
        plt.show(block=False)
    else: 
        plt.close()

    
    AUTOMATIC_PROCESSING_GOOD = False

    artifact_correct = _get_input_y_n("Are artifacts properly selected ? ")
    if artifact_correct == 'y':
        AUTOMATIC_PROCESSING_GOOD = True

    else:
        print('Now trying with kernel 1')
        kernel = '1'
        # find artifacts in intracerebral channel
        art_idx_LFP = find_LFP_sync_artifact(
            lfp_data=lfp_sig,
            sf_LFP=sf_LFP,
            use_kernel=kernel, 
            consider_first_seconds_LFP=None
        )

        art_time_LFP = _convert_index_to_time(
            art_idx=art_idx_LFP,
            sf=sf_LFP
        ) 

        # PLOT 5 : plot the intracerebral channel with its artifacts detected:
        plot_channel(
            sub=session_ID, 
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
            + '\\Fig5-Intracerebral channel with artifacts detected - kernel ' 
            + str(kernel) 
            + '.png',
            bbox_inches='tight'
        )
        if SHOW_FIGURES: 
            plt.show(block=False)
        else: 
            plt.close()
        

        # PLOT 6 : 
        # plot the first artifact detected in intracerebral channel (verification of sample choice):
        plot_channel(
            sub=session_ID, 
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
                    + '\\Fig6-Intracerebral channel - first artifact detected - kernel ' 
                    + str(kernel) 
                    + '.png', 
                    bbox_inches='tight'
        )
        if SHOW_FIGURES: 
            plt.show(block=False)
        else: 
            plt.close()

        artifact_correct = _get_input_y_n("Are artifacts properly selected ? ")
        if artifact_correct == 'y':
            AUTOMATIC_PROCESSING_GOOD = True
    
    if AUTOMATIC_PROCESSING_GOOD:
        _update_and_save_params('ART_TIME_LFP_AUTOMATIC', art_time_LFP[0], 
                                session_ID, saving_path
                                )
        _update_and_save_params('KERNEL', kernel, session_ID, saving_path)
        _update_and_save_params('REAL_ART_TIME_LFP_CORRECTED', 'no', session_ID,
                                 saving_path)
        _update_and_save_params('SAMPLE_SHIFT', 'none', session_ID, saving_path)
        _update_and_save_params('REAL_ART_TIME_LFP_VALUE', 'same', session_ID, 
                                saving_path)
        if CROP_BOTH:
            # crop intracerebral and external recordings 1 second before first artifact
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
        print(f'Automatic detection of intracranial artifacts failed, use manual method./n'
              'In the pop up window, zoom on the first artifact until you can select properly /n'
              'the last sample before the deflexion, click on it and close the window.')
        closest_value_lfp = select_sample(lfp_sig, sf_LFP)
        # calculate sample_shift: 
        sample_shift = int(abs(closest_value_lfp-art_time_LFP[0])*sf_LFP)
        _update_and_save_params('ART_TIME_LFP_AUTOMATIC', art_time_LFP[0], 
                                session_ID, saving_path)
        _update_and_save_params('REAL_ART_TIME_LFP_CORRECTED', 'yes', session_ID,
                                saving_path)
        _update_and_save_params('SAMPLE_SHIFT', sample_shift, session_ID, 
                                saving_path)
        _update_and_save_params('REAL_ART_TIME_LFP_VALUE', closest_value_lfp, 
                                session_ID, saving_path)
                
        # PLOT 5 : plot the artifact adjusted by user in the intracerebral channel:
        if closest_value_lfp != 0 :
            plot_channel(
                sub=session_ID, 
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
                + '\\Fig5-Intracerebral channel - first artifact detected with correction by user - kernel ' 
                + str(kernel) 
                + '.png', 
                bbox_inches='tight'
            )
            if SHOW_FIGURES: 
                plt.show(block=False)
            else: 
                plt.close()

        if CROP_BOTH:
            # crop intracerebral and external recordings 1 second before first artifact
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
    _update_and_save_params('SAVING_FORMAT', saving_format, session_ID, saving_path) 

    if CROP_BOTH:
        if saving_format == 'csv':
            LFP_df_offset['sf_LFP'] = sf_LFP
            external_df_offset['sf_external'] = sf_external
            LFP_df_offset.to_csv(saving_path + '\\Intracerebral_LFP_' 
                                 + str(session_ID) 
                                 + '.csv', index=False) 
            external_df_offset.to_csv(saving_path + '\\External_data_' 
                                      + str(session_ID) + '.csv', index=False)

        if saving_format == 'pickle':
            LFP_df_offset['sf_LFP'] = sf_LFP
            external_df_offset['sf_external'] = sf_external
            LFP_filename = (saving_path + '\\Intracerebral_LFP_' 
                            + str(session_ID) + '.pkl')
            external_filename = (saving_path + '\\External_data_' 
                                 + str(session_ID) + '.pkl')
            # Save the dataset to a pickle file
            with open(LFP_filename, 'wb') as file:
                pickle.dump(LFP_df_offset, file)
            with open(external_filename, 'wb') as file:
                pickle.dump(external_df_offset, file)            

        if saving_format == 'mat':
            LFP_filename = (saving_path + '\\Intracerebral_LFP_' 
                            + str(session_ID) + '.mat')
            external_filename = (saving_path + '\\External_data_' 
                                 + str(session_ID) + '.mat')
            savemat(LFP_filename, {'data': LFP_df_offset.T,'fsample': sf_LFP, 
                                   'label': np.array(LFP_df_offset.columns.tolist(), 
                                                     dtype=object).reshape(-1,1)})
            savemat(external_filename, {'data': external_df_offset.T, 
                                        'fsample': sf_external, 
                                        'label': np.array(external_df_offset.columns.tolist(), 
                                                          dtype=object).reshape(-1,1)})

        print('Alignment performed, both recordings were cropped and saved 1s before first artifact !')

    else:
        if saving_format == 'csv':
            external_df_offset['sf_external'] = sf_external
            external_df_offset.to_csv(saving_path + '\\External_data_' 
                                      + str(session_ID) + '.csv', index=False)

        if saving_format == 'pickle':
            external_df_offset['sf_external'] = sf_external
            external_filename = (saving_path + '\\External_data_' 
                                 + str(session_ID) + '.pkl')
            # Save the dataset to a pickle file
            with open(external_filename, 'wb') as file:
                pickle.dump(external_df_offset, file)            

        if saving_format == 'mat':
            external_filename = (saving_path + '\\External_data_' 
                                 + str(session_ID) + '.mat')
            savemat(external_filename, {'data': external_df_offset.T, 
                                        'fsample': sf_external, 
                                        'label': np.array(external_df_offset.columns.tolist(), 
                                                          dtype=object).reshape(-1,1)})

        print('Alignment performed, only external recording as been cropped to match LFP recording !')


    return LFP_df_offset, external_df_offset
