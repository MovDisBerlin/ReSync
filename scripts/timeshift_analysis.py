
### OUT OF DATE FUNCTION: ### 


def run_timeshift_analysis(
    LFP_df_offset, 
    sf_LFP,
    external_df_offset,
    sf_external,
    SHOW_FIGURES = True
):
    
    """"
    This function looks for timeshift between the intracerebral
    recording and the external recording. It is useful to check 
    for potential difference in clocking systems between the two
    recorders, or to detect packet loss in intracerebral recordings.

    Inputs:
        - LFP_df_offset: the intracerebral recording containing 
            all recorded channels, cropped one second before the 
            first artefact (after processing with run_resync function)
        - external_df_offset: the external recording containing 
            all recorded channels, cropped one second before the 
            first artefact (after processing with run_resync function)
        - SHOW_FIGURES: True or False, depending of whether the user
        wants the figures to appear in the notebook directly or not.
    
    Output:
        - timeshift: the timeshift of the last detected artefact in
        aligned recordings
    """

    plt.rcParams['svg.fonttype'] = 'none'

    #import settings
    json_path = os.path.join(os.getcwd(), 'config')
    json_filename = 'config.json'  # dont forget json extension
    with open(os.path.join(json_path, json_filename), 'r') as f:
        loaded_dict =  json.load(f)

    #set saving path
    if loaded_dict['SAVING_PATH'] == False:
        saving_path = utils._define_folders()
    else:
        saving_path = os.path.join(os.path.normpath(loaded_dict['SAVING_PATH']), loaded_dict['SUBJECT_ID'])
        if not os.path.isdir(saving_path):
            os.makedirs(saving_path)


    ### DETECT ARTEFACTS ###

    # Reselect artefact channels in the aligned (= cropped) files
    LFP_channel_offset = LFP_df_offset.iloc[:,loaded_dict['LFP_CH_INDEX']].to_numpy()  
    BIP_channel_offset = external_df_offset.iloc[:,loaded_dict['BIP_CH_INDEX']].to_numpy() 


    # find artefacts again in cropped intracerebral LFP channel:
    art_idx_LFP_offset = artefact.find_LFP_sync_artefact(lfp_data=LFP_channel_offset,
                                                         sf_LFP=sf_LFP,
                                                         use_kernel=loaded_dict['KERNEL'],
                                                         consider_first_seconds_LFP=None
    )

    art_time_LFP_offset = utils._convert_index_to_time(art_idx_LFP_offset,
                                                      sf_LFP
    )

    # pre-processing of external bipolar channel before searching artefacts:
    filtered_external_offset = utils._filtering(BIP_channel_offset)

    # find artefacts again in cropped external bipolar channel:
    art_idx_BIP_offset = artefact.find_external_sync_artefact(data = filtered_external_offset, 
                                                              sf_external = sf_external,
                                                              ignore_first_seconds_external=None, 
                                                              consider_first_seconds_external=None
    )
    art_time_BIP_offset = utils._convert_index_to_time(art_idx_BIP_offset, 
                                                      sf_external
    )


    ## PLOTTING ##

    # Generate new timescales:
    LFP_timescale_offset_s = np.arange(0,(len(LFP_channel_offset)/sf_LFP),1/sf_LFP)
    external_timescale_offset_s = np.arange(0,(len(BIP_channel_offset)/sf_external),1/sf_external)

    # PLOT 8: Both signals aligned with all their artefacts detected:
    fig, (ax1, ax2) = plt.subplots(2,1)
    fig.suptitle(str(loaded_dict['SUBJECT_ID']))
    fig.set_figheight(6)
    fig.set_figwidth(12)
    ax1.axes.xaxis.set_ticklabels([])
    ax2.set_xlabel('Time (s)')
    ax1.set_ylabel('Intracerebral LFP channel (µV)')
    ax2.set_ylabel('External bipolar channel (mV)')
    ax1.set_xlim(0,len(LFP_channel_offset)/sf_LFP) 
    ax2.set_xlim(0,len(LFP_channel_offset)/sf_LFP) 
    #ax1.set_xlim(143.6,144.2) 
    #ax2.set_xlim(143.6,144.2) 
    ax1.plot(LFP_timescale_offset_s,LFP_channel_offset,color='darkorange',zorder=1, linewidth=0.3)
    for xline in art_time_LFP_offset:
        ax1.axvline(x=xline, ymin=min(LFP_channel_offset), ymax=max(LFP_channel_offset),
                    color='black', linestyle='dashed', alpha=.3,)
    ax2.plot(external_timescale_offset_s,filtered_external_offset, color='darkcyan',zorder=1, linewidth=0.05) 
    for xline in art_time_BIP_offset:
        ax2.axvline(x=xline, color='black', linestyle='dashed', alpha=.3,)

    fig.savefig(saving_path + '\\Fig8-Intracerebral and external recordings aligned with artefacts detected.svg',bbox_inches='tight', dpi=1200)
    if SHOW_FIGURES: plt.show()
    else: plt.close()



    ### SELECT CORRECT ARTEFACTS ###
    # the algorithm might detect "artefacts" that are not really artefacts. 
    # With the images saved, the user can select the ones that are correct 
    # and enter their index in the config.json file.

    # first, let's check that the values in the config file are corresponding to real artefacts detected:
    if len(loaded_dict['index_real_artefacts_LFP']) > len(art_time_LFP_offset):
        raise ValueError(
            'Indexes incorrect for intracerebral recording. \n'
            f'LFP contains {len(art_time_LFP_offset)} artefacts. \n'
            'Please check Fig8 to find the real indexes of detected artefacts, \n'
            'and change config file accordingly'
        )
    if len(loaded_dict['index_real_artefacts_BIP']) > len(art_time_BIP_offset):
        raise ValueError(
            'Indexes incorrect for external recording. \n'
            f'external recording contains {len(art_time_BIP_offset)} artefacts. \n'
            'Please check Fig8 to find the real indexes of detected artefacts, \n'
            'and change config file accordingly'
        )
    if len(loaded_dict['index_real_artefacts_BIP']) != len(loaded_dict['index_real_artefacts_LFP']):
        raise ValueError(
            'The number of artefacts should be the same in intracerebral and external recordings. \n'
            'Please check Fig8 to find the real indexes of detected artefacts, \n'
            'and change config file accordingly. \n'
            'If an artefact is detected only in one of the recordings, do not select it.'
            f'LFP contains {len(art_time_LFP_offset)} artefacts. \n'
            f'external recording contains {len(art_time_BIP_offset)} artefacts. \n'
        )

    

    real_art_time_LFP_offset= utils._extract_elements(art_time_LFP_offset,
                                                     loaded_dict['index_real_artefacts_LFP']
    ) 
    real_art_time_BIP_offset= utils._extract_elements(art_time_BIP_offset, 
                                                     loaded_dict['index_real_artefacts_BIP']
    )


    ### ASSESS TIMESHIFT ###

    # once the artefacts are all correctly selected, the timeshift can be computed:
    delay = []
    for i in (np.arange(0,len(real_art_time_LFP_offset))):
        delay.append(real_art_time_BIP_offset[i]-real_art_time_LFP_offset[i])
    delay_ms = []
    for i in (np.arange(0,len(delay))):
        delay_ms.append(delay[i]*1000)
    
    mean_diff = sum(delay_ms)/len(delay_ms)

    timeshift = delay_ms[-1]

    if abs(mean_diff) > 100:
        raise ValueError(
            f'The artefacts selected might not be correct because the mean timeshift is very high: {mean_diff}ms \n'
            'Please check again Fig8 and adjust indexes in config file. \n'
            'If an artefact is detected only in one of the recordings, do not select it. \n'
            f'LFP contains {len(art_time_LFP_offset)} artefacts, and external recording contains {len(art_time_BIP_offset)} artefacts. \n'            
            'If the artefacts selected are correct, then the recording might contain packet loss. \n'
            f'The current timeshift is estimated to be of {timeshift}ms. \n'
        )
    

    # find the time of the last artefact detected:
    last_art_time = real_art_time_LFP_offset[-1]


    ## PLOTTING ##

    # PLOT 9: All artefacts detected and their associated timeshift
    plt.figure(figsize=(30, 10))
    plt.tight_layout()
    plt.subplots_adjust(hspace=0.2, wspace=0.5)
    plt.suptitle(str(loaded_dict['subject_ID']) + '\n\nThe mean difference is: ' +str(round(mean_diff,2))+ 'ms')
    # loop through the index to make new plots for each artefact:
    for n, m in zip(range(0,len(delay_ms),1),range(len(delay_ms),(len(delay_ms))*2,1)) :
        # add a new subplot iteratively
        ax1 = plt.subplot(2, len(delay_ms), n + 1)
        ax2 = plt.subplot(2, len(delay_ms), m + 1)
        #ax1.axes.xaxis.set_ticklabels([])
        ax2.axes.xaxis.set_major_formatter('{:.2f}'.format)
        ax2.set_xlabel('Time (s)')
        ax1.set_ylabel('Intracerebral LFP channel (µV)')
        ax2.set_ylabel('External bipolar channel (mV)')
        ax1.set_title('artefact ' + str((loaded_dict['index_real_artefacts_LFP'][n])+1))
        ax1.set_xlim((real_art_time_BIP_offset[n]-0.050),(real_art_time_BIP_offset[n]+0.1))
        ax2.set_xlim((real_art_time_BIP_offset[n]-0.050),(real_art_time_BIP_offset[n]+0.1))
        ax1.plot(LFP_timescale_offset_s,LFP_channel_offset,color='peachpuff',zorder=1)
        ax1.scatter(LFP_timescale_offset_s,LFP_channel_offset,color='darkorange',s=4,zorder=2) 
        ax1.scatter(LFP_timescale_offset_s,LFP_channel_offset,color='darkorange',s=4,zorder=2) 
        for xline in real_art_time_LFP_offset:
            ax1.axvline(x=xline, ymin=min(LFP_channel_offset), ymax=max(LFP_channel_offset),
                color='black', linestyle='dashed', alpha=.3,)
        ax2.plot(external_timescale_offset_s,filtered_external_offset, color='paleturquoise',zorder=1) 
        ax2.scatter(external_timescale_offset_s,filtered_external_offset, color='darkcyan',s=4,zorder=2)
        for xline in real_art_time_BIP_offset:
            ax2.axvline(x=xline, color='black', linestyle='dashed', alpha=.3,)


        ax1.text(0.05,0.85,s='delay intra/exter: ' +str(round(delay_ms[n],2))+ 'ms',fontsize=14,transform=ax1.transAxes)

    plt.gcf()
    plt.savefig(saving_path + '\\Fig9-Intracerebral and external aligned channels-timeshift all artefacts.pdf',bbox_inches='tight', dpi=1200)
    if SHOW_FIGURES: plt.show()
    else: plt.close()

    print(
        f'Timeshift analysis performed ! \n'
        f'The result is: {timeshift} ms delay at the last detected artefact, \n'
        f'after a recording duration of {last_art_time}s.'
    )



