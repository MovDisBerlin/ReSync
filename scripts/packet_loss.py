from find_packet_loss import load_sourceJSON, check_missings_in_lfp

def check_packet_loss(
        json_fname: str,
        sub: str
):
    
    j = load_sourceJSON(sub, json_fname)

    prc_data_codes = {
        'signal_test': 'CalibrationTests',
        'streaming': 'BrainSenseTimeDomain',
        'survey': 'LfpMontageTimeDomain',
        'indef_streaming': 'IndefiniteStreaming'
    }

    mod = 'streaming'
    list_of_streamings = j[prc_data_codes[mod]]

    for i_dat, dat in enumerate(list_of_streamings):
        print(i_dat)
        new_lfp = check_missings_in_lfp(dat)

