import numpy as np
from scipy.signal import find_peaks
from itertools import compress
from utils import _calculate_difference

# Detection of artefacts in TMSi

def find_external_sync_artefact(
    data: np.ndarray, 
    sf_external: int
):

    """ 
    Function that finds artefacts caused by increasing/reducing 
    stimulation from 0 to 1mA without ramp.
    For correct functioning, the external data recording should
    start in stim-off, and typically short pulses are given 
    (without ramping). 
    This function uses a fixed threshold ('thresh_external'), which
    has to be adapted to each data recorder in the config.json file. 
    The signal must be pre-processed previously with a high-pass 
    Butterworth filter (1Hz) to ensure removal of slow drifts
    and offset around 0.

    Inputs:
        - data: single external channel as np.ndarray (from bipolar electrode)
        - sf_external (int): sampling frequency of external recording
        - ignore_first_seconds_external : if given, the first n-seconds
            will be ignored (back-up, in case recording was started with stim ON, 
            or if there are huge artefacts in the beginning)
        - consider_first_seconds_external : if given, only artefacts in
            the first (and last) n-seconds are considered (in case the
            recording is StimON, it ignores the other amplitude changes)
    
    Returns:
        - index_artefact_start_external : a list containing the indexes of each
            artefact start detected. 

    """

    #initialize variables (lists and state)
    index_artefact_start_external = []
    stimON = False

    start_index = 0
    stop_index = len(data)-2

    # check polarity of artefacts before detection:
    # to be properly detected in external channel, artefacts have to look like a downward deflection 
    # (they are more negative than positive). If for some reason the data recorder picks up
    # the artefact as an upward deflection instead, then the signal has to be inverted before detecting artefacts.
    if abs(max(data)) > abs(min(data)):
        print('external signal is reversed')
        data = data * -1

    # define thresh_BIP as a value half of the minimal value
    difference = _calculate_difference(data, sf_external)
    thresh_BIP = -1.5*difference

    #start looking at each value one by one and append the timepoint to the list depending on the state and if thresh_BIP is crossed
    for q in range(start_index,stop_index):
        if ((stimON == False) 
                and (data[q] <= thresh_BIP) 
                and (data[q] < data[q + 1]) 
                and (data[q] < data[q - 1])):
            if q >= 0.2*sf_external:
                index_artefact_start_external.append(q)
                stimON = True
                q = q + 1
            #elif q < 0.2*sf_external:
                #print ('External recording started with stim already ON. Ignoring first artefact')
                #stimON = True
                #q = q + 1
        if (stimON
                and (data[q] <= thresh_BIP) 
                and (data[q] < data[q + 1]) 
                and (data[q] < data[q - 1])):
            if (all(data[(q + 2):(q + int(0.5*sf_external))] > thresh_BIP)):
                stimON = False
                q = q + 1
        else:
            q = q + 1


    return index_artefact_start_external





# Detection of artefacts in LFP

def find_LFP_sync_artefact(
    lfp_data: np.ndarray,
    sf_LFP,
    use_kernel: str,
    consider_first_seconds_LFP=None,
):
    """
    Function that finds artefacts caused by
    augmenting-reducing stimulation from 0 to 1mA without ramp.
    For correct functioning, the LFP data should
    start in stim-off, and typically short pulses
    are given (without ramping).
    The function uses a kernel which mimics the stimulation-
    artefact. This kernel is multiplied with time-series
    snippets of the same length. If the time-serie is
    similar to the kernel, the dot-product is high, and this
    indicates a stim-artefact.

    Input:
        - lfp_data: single channel as np.ndarray (the function
            automatically inverts the signal if first a positive
            peak is found, this indicates an inverted signal)
        - sf_LFP (int): sampling frequency of intracranial recording
        - use_kernel: decides whether kernel 1 or 2 is used,
            kernel 1 is straight-forward and finds a steep decrease,
            kernel 2 mimics the steep decrease and slow recovery of the signal. 
            In our tests, kernel 2 was the best in 52.7% of the cases.
        - consider_first_seconds_LFP: if given, only artefacts in the first
            (and last) n-seconds are considered
    
    Returns:
        - stim_idx: a list with all stim-artefact starts. 
    """
    
    signal_inverted = False  # defaults false

    # checks correct input for use_kernel variable
    assert use_kernel in ['1', '2'], 'use_kernel incorrect'

    # kernel 1 only searches for the steep decrease
    # kernel 2 is more custom and takes into account the steep decrease and slow recover
    kernels = {'1': np.array([1, -1]),
               '2': np.array([1, 0, -1] + list(np.linspace(-1, 0, 20)))
    }
    ker = kernels[use_kernel]
    
    # get dot-products between kernel and time-serie snippets
    res = []  # store results of dot-products
    for i in np.arange(0, len(lfp_data) - len(ker)):
        res.append(ker @ lfp_data[i: i + len(ker)])  # calculate dot-product of vectors
        # the dot-product result is high when the timeseries snippet
        # is very similar to the kernel
    res = np.array(res)  # convert list to array

    # # normalise dot product results
    res = res / max(res)

    # calculate a ratio between std dev and maximum during
    # the first seconds to check whether an stim-artef was present 
    ratio_max_sd = np.max(res[:sf_LFP*30] / np.std(res[:sf_LFP*5]))
    
    # use peak of kernel dot products    
    pos_idx = find_peaks(
        x=res, 
        height=.3 * max(res),
        distance=sf_LFP
    )[0]
    neg_idx = find_peaks(
        x=-res, 
        height=-.3 * min(res),
        distance=sf_LFP
    )[0]

    # check whether signal is inverted
    if neg_idx[0] < pos_idx[0]:
        # the first peak should be POSITIVE (this is for the dot-product results)
        # actual signal is first peak negative
        # if NEG peak before POS then signal is inverted
        print('signal is inverted')
        signal_inverted = True
        #print(pos_idx[0], neg_idx[0])
        # re-check inverted for difficult cases with small pos-lfp peak before negative stim-artefact
        if (pos_idx[0] - neg_idx[0]) < 50:  # if first positive and negative are very close
            width_pos = 0
            r_i = pos_idx[0]
            while res[r_i] > (max(res) * .3):
                r_i += 1
                width_pos += 1
            width_neg = 0
            r_i = neg_idx[0]
            while res[r_i] < (min(res) * .3):
                r_i += 1
                width_neg += 1
            # undo invertion if negative dot-product (pos lfp peak) is very narrow
            if width_pos > (2 * width_neg):
                signal_inverted = False
                print('invertion undone')
            
           
    # return either POS or NEG peak-indices based on normal or inverted signal
    if not signal_inverted:
        stim_idx = pos_idx  # this is for 'normal' signal

    elif signal_inverted:
        stim_idx = neg_idx

    

    # check warn if NO STIM artefacts are suspected
    if len(stim_idx) > 20 and ratio_max_sd < 8:
        print('WARNING: probably the LFP signal did NOT'
              ' contain any artefacts. Many incorrect timings'
              ' could be returned')


    if consider_first_seconds_LFP:
        border_start = sf_LFP*consider_first_seconds_LFP
        border_end = len(lfp_data) - (sf_LFP*consider_first_seconds_LFP)
        sel = np.logical_or(np.array(stim_idx) < border_start,
                             np.array(stim_idx) > border_end)
        stim_idx = list(compress(stim_idx, sel))


    # filter out inconsistencies in peak heights (assuming sync-stim-artefacts are stable)
    abs_heights = [max(abs(lfp_data[i - 5: i + 5])) for i in stim_idx]
    diff_median = np.array([abs(p - np.median(abs_heights)) for p in abs_heights])
    sel_idx = diff_median < (np.median(abs_heights)*.66)
    stim_idx = list(compress(stim_idx, sel_idx))
    # check polarity of peak
    if not signal_inverted:
        sel_idx = np.array([min(lfp_data[i - 5: i + 5]) for i in stim_idx]) < (np.median(abs_heights) * -.5)
    elif signal_inverted:
        sel_idx = np.array([max(lfp_data[i - 5: i + 5]) for i in stim_idx])  > (np.median(abs_heights) * .5)
    stim_idx = list(compress(stim_idx, sel_idx))


    return stim_idx
