import matplotlib.pyplot as plt
import numpy as np

from utils import _get_input_y_n


def interaction(timescale, data):
    pos = [] # collecting the clicked x and y values for one channel group of stn at one session

    fig, ax = plt.subplots()
    ax.scatter(timescale, data)
    ax.set_title('Click on the plot to select points, 20 seconds are provided.\n'
                 'If the sample was not selected in these 20s, \n'
                 'answer n to the user input window and \n'
                 'you will be given 10 more seconds')


    def onclick(event):
        pos.append([event.xdata,event.ydata])
            
    fig.canvas.mpl_connect('button_press_event', onclick)

    fig.tight_layout()

    plt.subplots_adjust(wspace=0, hspace=0)

    plt.show(block=False)
    plt.pause(20)
    condition_met = False

    input_y_or_n = _get_input_y_n("Artefacts found?")

    while not condition_met: # this loops every 10 seconds until user answers "y" 
        if input_y_or_n == "y":   # if user has found the artefact sample and puts "y" then it will proceed to next step
            condition_met=True
        else:
            plt.pause(10)    #else if the user answers "n", 10 more seconds are given to select the artefact sample
            input_y_or_n = _get_input_y_n("Artefacts found?")


    artifact_x = [x_list[0] for x_list in pos] # list of all clicked x values

    return artifact_x[-1]


def select_sample(signal, sf):
    signal_timescale_s = np.arange(0, (len(signal)/sf), (1/sf))
    selected_x = interaction(signal_timescale_s, signal)

    # Find the index of the closest value
    closest_index = np.argmin(np.abs(signal_timescale_s - selected_x))

    # Get the closest value
    closest_value = signal_timescale_s[closest_index]

    print(f"The closest value to {selected_x} is {closest_value}.")

    return closest_value