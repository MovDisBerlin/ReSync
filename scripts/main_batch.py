'''
main_batch.py is the main function of ReSync for performing batch analysis of
multiple sessions. Use main.py for one-by-one session analysis. 

Usage:
1. complete all the parameters in the main function according to your needs
    excel_fname: string, name of the excel file containing the recording

	saving_format: string, format of the output files (csv, pickle or mat)

	CROP_BOTH: boolean, if True, crop both LFP and external data to the shortest
				if False, crop only the external data to match the intracranial

	CHECK_FOR_TIMESHIFT: boolean, if True, perform timeshift analysis

	CHECK_FOR_PACKET_LOSS: boolean, if True, perform packet loss analysis

	SHOW_FIGURES: boolean, if True, show figures, if False only save them

2. run main_batch.py

Result:
The results will be saved in the results folder, in a sub-folder named after 
each session_ID parameter contained in the excel file.

'''

import os
import pandas as pd
from os.path import join

from loading_data import (
    load_mat_file, 
    load_data_lfp, 
    load_TMSi_artifact_channel, 
    load_sourceJSON, 
    load_intracranial_csv_file, 
    load_external_csv_file
    )
from plotting import plot_LFP_external, ecg
from timeshift import check_timeshift
from utils import _update_and_save_params
from tmsi_poly5reader import Poly5Reader
from resync_function import run_resync
from packet_loss import check_packet_loss

def main_batch(
        excel_fname = 'recording_information.xlsx',
        saving_format = 'csv',
        CROP_BOTH = True,
        CHECK_FOR_TIMESHIFT = True,
        CHECK_FOR_PACKET_LOSS = False,
        SHOW_FIGURES = True
):
    
    excel_file_path = join("sourcedata", excel_fname)
    df = pd.read_excel(excel_file_path)

    # Loop for all recording sessions present in the file provided, 
    # analyze one by one:
    for index, row in df.iterrows():
        done = row['done']
        if done == 'yes':
            continue
        session_ID = row['session_ID']
        fname_lfp = row['fname_lfp']
        fname_external = row['fname_external']
        ch_idx_lfp = row['ch_idx_LFP']
        if type(ch_idx_lfp) == float: ch_idx_lfp = int(ch_idx_lfp)
        BIP_ch_name = row['BIP_ch_name']
        
        if pd.isna(session_ID):
            print(f"Skipping analysis for row {index + 2}"
                  f"because session_ID is empty.")
            continue
        if pd.isna(fname_lfp):
            print(f"Skipping analysis for row {index + 2}"
                  f"because fname_lfp is empty.")
            continue        
        if pd.isna(fname_external):
            print(f"Skipping analysis for row {index + 2}"
                  f"because fname_external is empty.")
            continue        
        if pd.isna(ch_idx_lfp):
            print(f"Skipping analysis for row {index + 2}"
                  f"because ch_idx_lfp is empty.")
            continue        
        if pd.isna(BIP_ch_name):
            print(f"Skipping analysis for row {index + 2}"
                  f"because BIP_ch_name is empty.")
            continue        

        #  Set saving path
        saving_path = join("results", session_ID)
        if not os.path.isdir(saving_path):
            os.makedirs(saving_path)

        #  Set source path
        source_path = "sourcedata"

        #  Loading datasets
            ##  Intracranial data
        if fname_lfp.endswith('.mat'):
            dataset_lfp = load_mat_file(session_ID, fname_lfp, saving_path, 
                                       source_path)
            (LFP_array, lfp_sig, 
             LFP_rec_ch_names, sf_LFP) = load_data_lfp(session_ID, dataset_lfp, 
                                                        ch_idx_lfp, saving_path
                                                        )
        if fname_lfp.endswith('.csv'):
            (LFP_array, lfp_sig, 
             LFP_rec_ch_names, sf_LFP) = load_intracranial_csv_file(session_ID, 
                                                                    fname_lfp, 
                                                                    ch_idx_lfp, 
                                                                    saving_path,
                                                                    source_path
                                                                    )


            ##  External data recorder
        if fname_external.endswith('.Poly5'):
            TMSi_data = Poly5Reader(join(source_path, fname_external)) 
            (BIP_channel, external_file, 
             external_rec_ch_names, sf_external, 
             ch_index_external) = load_TMSi_artifact_channel(session_ID, 
                                                             TMSi_data,
                                                             fname_external, 
                                                             BIP_ch_name, 
                                                             saving_path
                                                             )
        if fname_external.endswith('.csv'):
            (BIP_channel, external_file, 
             external_rec_ch_names, sf_external, 
             ch_index_external) = load_external_csv_file(session_ID, 
                                                          fname_external, 
                                                          BIP_ch_name, 
                                                          saving_path,
                                                          source_path
                                                          )

        
        #  Sync recording sessions
        (LFP_df_offset, external_df_offset) = run_resync(session_ID, LFP_array, 
                                                         lfp_sig, 
                                                         LFP_rec_ch_names, 
                                                         sf_LFP, external_file, 
                                                         BIP_channel, 
                                                         external_rec_ch_names, 
                                                         sf_external, 
                                                         saving_path, 
                                                         saving_format, 
                                                         CROP_BOTH, 
                                                         SHOW_FIGURES = True
                                                         )
        plot_LFP_external(session_ID, LFP_df_offset, external_df_offset, sf_LFP,
                           sf_external, ch_idx_lfp, ch_index_external, 
                           saving_path, SHOW_FIGURES)

        #  OPTIONAL
        if CHECK_FOR_TIMESHIFT:
            print('Starting timeshift analysis...')
            check_timeshift(session_ID, LFP_df_offset, sf_LFP, 
                            external_df_offset, sf_external, saving_path, 
                            SHOW_FIGURES
                            )

        if CHECK_FOR_PACKET_LOSS:
            fname_json = row['fname_json']
            _update_and_save_params('JSON_FILE', fname_json, session_ID, 
                                    saving_path
                                    )
            json_object = load_sourceJSON(fname_json, source_path)
            check_packet_loss(json_object)

        # OPTIONAL : plot cardiac artifact:
        #ecg(session_ID, LFP_df_offset, sf_LFP, external_df_offset, sf_external,
             #saving_path, xmin= 0, xmax= 1.2, SHOW_FIGURES=True)



if __name__ == '__main__':
    main_batch()
