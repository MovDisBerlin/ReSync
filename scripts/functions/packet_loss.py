import numpy as np


def check_packet_loss(json_object):
    """
    Check for packet loss in BrainSense Streaming data.
    """

    prc_data_codes = {
        "signal_test": "CalibrationTests",
        "streaming": "BrainSenseTimeDomain",
        "survey": "LfpMontageTimeDomain",
        "indef_streaming": "IndefiniteStreaming",
    }

    mod = "streaming"
    list_of_streamings = json_object[prc_data_codes[mod]]

    for i_dat, dat in enumerate(list_of_streamings):
        print(i_dat)
        new_lfp = check_missings_in_lfp(dat)


def convert_list_string_floats(string_list):
    try:
        floats = [float(v) for v in string_list.split(",")]
    except:
        floats = [float(v) for v in string_list[:-1].split(",")]

    return floats


def check_missings_in_lfp(dat):

    ticksMsec = convert_list_string_floats(dat["TicksInMses"])
    ticksDiffs = np.diff(np.array(ticksMsec))
    data_is_missing = (ticksDiffs != 250).any()
    packetSizes = convert_list_string_floats(dat["GlobalPacketSizes"])
    lfp_data = dat["TimeDomainData"]

    if data_is_missing:
        print("LFP Data is missing!!")
    else:
        print(
            "No LFP data missing based on timestamp " "differences between data-packets"
        )
