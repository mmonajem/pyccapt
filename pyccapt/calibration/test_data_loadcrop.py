import unittest
from urllib import response
from defer import return_value
import pytest
from unittest.mock import patch, Mock, MagicMock
import sys
import os
sys.path.append('/home/harsh/researchAssistant/pyccapt/pyccapt/calibration/pyccapt/calibration_tools/')
path = '/home/harsh/researchAssistant/pyccapt/pyccapt/calibration'
os.chdir(path)

import matplotlib.pyplot as plt
import data_loadcrop
import data_tools

def test_fetch_dataset_from_dld_grp_check_returnType():
    filename = '../files/AL_data_b.h5'
    response = data_loadcrop.fetch_dataset_from_dld_grp(filename)
    assert isinstance(response,list)

@patch.object(data_loadcrop.logger, "critical")
def test_fetch_dataset_from_dld_grp_check_key_missing(mock):
    filename = '../files/AL_data_b.h5'
    data = data_tools.read_hdf5(filename)
    data.pop('dld/high_voltage')
    data_loadcrop.data_tools.read_hdf5 = MagicMock(return_value = data)
    response = data_loadcrop.fetch_dataset_from_dld_grp(filename)
    mock.assert_called_with("[*]Keys missing in the dataset")


@patch.object(data_loadcrop.logger, "critical")
def test_fetch_dataset_from_dld_grp_file_not_found(mock):
    file_name = 'not_existing_file.h5'
    response = data_loadcrop.fetch_dataset_from_dld_grp(file_name)
    mock.assert_called_with("[*] HDF5 file not found")


def test_crop_dataset_check_functionality():
    import pandas as pd
    d = {'col1': [1, 2], 'col2': [3, 4],'col3': [4, 5],'col4': [6, 4]}
    df = pd.DataFrame(data=d)
    data_loadcrop.variables.selected_x1 = MagicMock(return_value = 0)
    data_loadcrop.variables.selected_x2 = MagicMock(return_value = 0)
    response = data_loadcrop.crop_dataset(df)
    print("response",response)
    #assert len(response) == 1