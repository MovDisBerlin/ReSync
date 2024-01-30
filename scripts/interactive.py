import matplotlib.pyplot as plt
import numpy as np

from utils import _get_input_y_n

def select_sample(
        signal: np.ndarray, 
        sf: int
        ):
    
    """
    This function allows the user to select a sample from a plot representing
    the given signal with the sampling frequency provided.
    The user can zoom in and out, and the last click before answering
    y will be the selected sample.
    """

    signal_timescale_s = np.arange(0, (len(signal)/sf), (1/sf))
    selected_x = interaction(signal, signal_timescale_s)

    # Find the index of the closest value
    closest_index = np.argmin(np.abs(signal_timescale_s - selected_x))

    # Get the closest value
    closest_value = signal_timescale_s[closest_index]

    print(f"The closest value to {selected_x} is {closest_value}.")

    return closest_value


def interaction(
        data: np.ndarray,
        timescale: np.ndarray
        ):
    
    """
    This function draws an interactive plot representing the given data with 
    the timescale provided.The user can zoom in and out, and the last click 
    before answering y will be the selected sample.
    """

    # collecting the clicked x and y values
    pos = [] 

    fig, ax = plt.subplots()
    ax.scatter(timescale, data, s=8, c='darkorchid')
    ax.set_title('Click on the plot to select the sample \n' 
                 'where the artifact starts. You can use the zoom, \n'
                 'as long as the black "+" is placed on the correct sample \n'
                 'before answering "y" in the terminal')

    plus_symbol, = ax.plot([], [], 'k+', markersize=10)

    def onclick(event):
        if event.xdata is not None and event.ydata is not None:
            pos.append([event.xdata, event.ydata])
            
            # Update the position of the black "+" symbol
            closest_index_x = np.argmin(np.abs(timescale - event.xdata))
            closest_value_x = timescale[closest_index_x]
            closest_value_y = data[closest_index_x]
            plus_symbol.set_data(closest_value_x, closest_value_y)
            plt.draw()
            
    fig.canvas.mpl_connect('button_press_event', onclick)

    fig.tight_layout()

    plt.subplots_adjust(wspace=0, hspace=0)

    plt.show(block=False)
    condition_met = False

    input_y_or_n = _get_input_y_n("Artifact found?")

    while not condition_met:  
        if input_y_or_n == "y":   
            condition_met=True
        else:
            input_y_or_n = _get_input_y_n("Artifact found?")


    artifact_x = [x_list[0] for x_list in pos] # list of all clicked x values

    return artifact_x[-1]

