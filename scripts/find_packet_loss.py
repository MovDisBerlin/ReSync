from os.path import join, exists
from os import listdir
from mne.io import read_raw_fieldtrip
import json
import numpy as np
    

def load_sourceJSON_bis(sub: str, filename: str):

    """
    Reads source JSON file 

    Input:
        - subject = str, e.g. "024"
        - fname = str of filename, e.g. "Report_Json_Session_Report_20221205T134700.json"

    Returns: 
        - data: json.loads() loaded JSON file

    """

    # Error check: 
    # Error if sub str is not exactly 3 letters e.g. 024
    assert len(sub) == 3, f'Subject string ({sub}) INCORRECT' 
    
    # Error if filename doesn´t end with .json
    assert filename[-5:] == '.json', (
        f'filename no .json INCORRECT extension: {filename}'
    )


    # find the path to the folder with raw JSONs of a subject
    datapath = "C:\\Users\\Juliette\\OneDrive - Charité - Universitätsmedizin Berlin\\Percept_Data_structured\\sourcedata"
    json_path = join(datapath, f'sub-{sub}') # same path as to perceive files, all in sourcedata folder

    if exists(join(json_path, filename)):
        with open(join(json_path, filename), 'r') as f:
            json_object = json.loads(f.read())
    
    elif exists(join(json_path, 'raw_jsons', filename)):
        with open(join(json_path,'raw_jsons', filename), 'r') as f:
            json_object = json.loads(f.read())
    
    else:
        raise ValueError(f'JSON file ({filename}) not found '
                         f'in {json_path}, and "raw_jsons" folder')
    

    return json_object





def convert_list_string_floats(
    string_list
):
    try:
        floats = [float(v) for v in string_list.split(',')]
    except:
        floats = [float(v) for v in string_list[:-1].split(',')]

    return floats


def check_missings_in_lfp (dat):
    ticksMsec = convert_list_string_floats(dat['TicksInMses'])
    ticksDiffs = np.diff(np.array(ticksMsec))
    data_is_missing = (ticksDiffs != 250).any()
    packetSizes = convert_list_string_floats(dat['GlobalPacketSizes'])
    lfp_data = dat['TimeDomainData']

    if data_is_missing:
        print('LFP Data is missing!!')
    else:
        print('No LFP data missing based on timestamp '
                'differences between data-packets')
        
