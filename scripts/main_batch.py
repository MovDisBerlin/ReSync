from loading_data import (_load_mat_file, _load_data_lfp, _load_TMSi_artefact_channel, 
                          _load_sourceJSON)
from plotting import plot_LFP_external
from timeshift import check_timeshift
from ecg_plot import ecg
from utils import _update_and_save_params
from tmsi_poly5reader import Poly5Reader
import os
import pandas as pd
from os.path import join
from main_resync import run_resync
from packet_loss import check_packet_loss

def main_batch(
        excel_fname = 'recording_information.xlsx',
        kernel = '2',
        saving_format = 'csv',
        CROP_BOTH = False,
        CHECK_FOR_TIMESHIFT = False,
        CHECK_FOR_PACKET_LOSS = False,
        SHOW_FIGURES = True
):
    
    excel_file_path = join("sourcedata", excel_fname)
    df = pd.read_excel(excel_file_path)

    # Loop for all recording sessions present in the file provided, analyze one by one:
    for index, row in df.iterrows():
        done = row['done']
        if done == 'yes':
            continue
        session_ID = row['session_ID']
        fname_lfp = row['fname_lfp']
        fname_external = row['fname_external']
        ch_idx_lfp = row['ch_idx_LFP']
        print(ch_idx_lfp)
        print(type(ch_idx_lfp))
        BIP_ch_name = row['BIP_ch_name']
        
        if pd.isna(session_ID):
            print(f"Skipping analysis for row {index + 2} because session_ID is empty.")
            continue
        if pd.isna(fname_lfp):
            print(f"Skipping analysis for row {index + 2} because fname_lfp is empty.")
            continue        
        if pd.isna(fname_external):
            print(f"Skipping analysis for row {index + 2} because fname_external is empty.")
            continue        
        if pd.isna(ch_idx_lfp):
            print(f"Skipping analysis for row {index + 2} because ch_idx_lfp is empty.")
            continue        
        if pd.isna(BIP_ch_name):
            print(f"Skipping analysis for row {index + 2} because BIP_ch_name is empty.")
            continue        

        #  Set saving path
        saving_path = join("results", session_ID)
        if not os.path.isdir(saving_path):
            os.makedirs(saving_path)
        
        #  Load datasets
            ##  LFP (here Percept datas preprocessed in Matlab with Perceive toolbox)
        dataset_lfp = _load_mat_file(session_ID, fname_lfp, saving_path)
        (LFP_array, lfp_sig, 
         LFP_rec_ch_names, sf_LFP) = _load_data_lfp(session_ID, dataset_lfp, ch_idx_lfp, 
                                                    saving_path)
            ##  External data recorder
        source_path = "sourcedata"
        TMSi_data = Poly5Reader(join(source_path, fname_external))
        (BIP_channel, external_file, external_rec_ch_names, sf_external, 
         ch_index_external) = _load_TMSi_artefact_channel(session_ID, TMSi_data, fname_external, 
                                                          BIP_ch_name, saving_path)

        #  Sync recording sessions
        (LFP_df_offset, external_df_offset) = run_resync(session_ID, kernel, LFP_array, lfp_sig, 
                                                         LFP_rec_ch_names, sf_LFP, external_file, 
                                                         BIP_channel, external_rec_ch_names, sf_external, 
                                                         saving_path, saving_format, CROP_BOTH, 
                                                         SHOW_FIGURES = True)
        plot_LFP_external(session_ID, LFP_df_offset, external_df_offset, sf_LFP, sf_external, 
                          ch_idx_lfp, ch_index_external, saving_path, SHOW_FIGURES)

        #  OPTIONAL
        if CHECK_FOR_TIMESHIFT:
            print('Starting timeshift analysis...')
            check_timeshift(session_ID, LFP_df_offset, sf_LFP, 
                            external_df_offset, sf_external, saving_path, SHOW_FIGURES)

        if CHECK_FOR_PACKET_LOSS:
            fname_json = row['fname_json']
            _update_and_save_params('JSON_FILE', fname_json, session_ID, saving_path)
            json_object = _load_sourceJSON(fname_json)
            check_packet_loss(json_object)

        # OPTIONAL : plot cardiac artifact:
        #ecg(session_ID, LFP_df_offset, sf_LFP, external_df_offset, sf_external, saving_path, xmin= 0, xmax= 1.2, SHOW_FIGURES=True)



if __name__ == '__main__':
    main_batch()
