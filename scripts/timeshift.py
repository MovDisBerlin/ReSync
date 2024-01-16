import json
import numpy as np
import matplotlib.pyplot as plt

from utils import _filtering
from interactive import select_sample
from utils import _update_and_save_params

def check_timeshift(
        sub_ID, LFP_df_offset, sf_LFP, external_df_offset, sf_external, saving_path, SHOW_FIGURES
        ):


    #import settings
    json_filename = (saving_path + '\\parameters_' + str(sub_ID) + '.json')
    with open( json_filename, 'r') as f:
        loaded_dict =  json.load(f)

    # Reselect artefact channels in the aligned (= cropped) files:
    LFP_channel_offset = LFP_df_offset.iloc[:, loaded_dict["CH_IDX_LFP"]].to_numpy()  
    BIP_channel_offset = external_df_offset.iloc[:, loaded_dict["CH_IDX_EXTERNAL"]].to_numpy() 

    # Generate new timescales:
    LFP_timescale_offset_s = np.arange(
        start=0, 
        stop=len(LFP_channel_offset)/sf_LFP, 
        step=1/sf_LFP
    )
    external_timescale_offset_s = np.arange(
        start=0, 
        stop=len(external_df_offset)/sf_external, 
        step=1/sf_external
    )

    # detrend external recording with high-pass filter before processing:
    filtered_external_offset = _filtering(BIP_channel_offset)

    print ('Select the sample corresponding to the last artifact in the intracranial recording')
    last_artefact_lfp_x = select_sample(LFP_channel_offset, sf_LFP)
    print ('Select the sample corresponding to the last artifact in the external recording')
    last_artefact_external_x = select_sample(filtered_external_offset, sf_external) 

    timeshift_ms = (last_artefact_external_x - last_artefact_lfp_x)*1000

    _update_and_save_params("TIMESHIFT", timeshift_ms, sub_ID, saving_path)
    _update_and_save_params("REC DURATION FOR TIMESHIFT", last_artefact_external_x, sub_ID, saving_path)

    if abs(timeshift_ms) > 100:
        print('WARNING: the timeshift is unusually high, consider checking for packet loss in LFP data.')


    fig, (ax1, ax2) = plt.subplots(2, 1)
    fig.suptitle(str(sub_ID))
    fig.set_figheight(12)
    fig.set_figwidth(6)
    ax1.axes.xaxis.set_ticklabels([])
    ax2.set_xlabel('Time (s)')
    ax1.set_ylabel('Intracerebral LFP channel (µV)')
    ax2.set_ylabel('External bipolar channel (mV)')
    ax1.set_xlim(last_artefact_external_x - 0.1, last_artefact_external_x + 0.1) 
    ax2.set_xlim(last_artefact_external_x - 0.1, last_artefact_external_x + 0.1)
    #ax1.set_ylim(-300,100) 
    #ax2.set_ylim(-0.0050, 0.0050)
    ax1.plot(LFP_timescale_offset_s, LFP_channel_offset, color='peachpuff', zorder=1)
    ax1.scatter(LFP_timescale_offset_s, LFP_channel_offset, color='darkorange', s=4, zorder=2) 
    ax1.axvline(x=last_artefact_lfp_x, ymin=min(LFP_channel_offset), ymax=max(LFP_channel_offset), 
                color='black', linestyle='dashed', alpha=.3)
    ax2.plot(external_timescale_offset_s, filtered_external_offset, color='paleturquoise', zorder=1) 
    ax2.scatter(external_timescale_offset_s, filtered_external_offset, color='darkcyan', s=4, zorder=2) 
    ax2.axvline(x=last_artefact_external_x, color='black', linestyle='dashed', alpha=.3)
    ax1.text(0.05, 0.85, s='delay intra/exter: ' + str(round(timeshift_ms, 2)) + 'ms', fontsize=14, 
             transform=ax1.transAxes)
       
    plt.gcf()
    fig.savefig(saving_path + '\\FigA-Timeshift_Intracerebral and external recordings aligned_last artefact.png', 
                bbox_inches='tight', dpi=1200)

    if SHOW_FIGURES: 
        plt.show(block=False)
    else: 
        plt.close()

