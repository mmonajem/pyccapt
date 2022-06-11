"""
This is the main script for global variables.
"""

def init():

    global selected_x_fdm
    global selected_y_fdm
    global roi_fdm

    global selected_x1
    global selected_x2

    # List that stores mass/weights of added elements
    global listMaterial

    global peaks_idx

    global result_path
    global path


    init.selected_x_fdm = 0
    selected_y_fdm = 0
    roi_fdm = 0

    selected_x1 = 0
    selected_x2 = 0


    listMaterial = []

    peaks_idx = []

    result_path = ''
    path = ''
