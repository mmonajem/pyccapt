import unittest
from urllib import response
import pytest
from unittest.mock import patch, Mock, MagicMock
import sys
import os
sys.path.append('/home/harsh/researchAssistant/pyccapt/pyccapt/calibration/pyccapt/calibration_tools/')
path = '/home/harsh/researchAssistant/pyccapt/pyccapt/calibration'
os.chdir(path)
import data_tools
from subprocess import PIPE,run
import pandas as pd
import scipy
from deepdiff import DeepDiff



@patch.object(data_tools.logger, "critical")
def test_read_hdf5_file_not_found(mock):
    file_name = 'not_existing_file.h5'
    response = data_tools.read_hdf5(file_name)
    mock.assert_called_with("[*] HDF5 File could not be found")

def test_read_hdf5_no_grp_keys():
    response = data_tools.read_hdf5('../files/AL_data_b.h5')
    assert isinstance(response,dict) 

def test_read_hdf5_through_pandas_check_returnType():
    response = data_tools.read_hdf5_through_pandas('../files/isotopeTable.h5')
    assert isinstance(response,pd.core.frame.DataFrame)

@patch.object(data_tools.logger, "critical")   
def test_read_hdf5_through_pandas_file_not_found(mock):
    response = data_tools.read_hdf5_through_pandas('../files/not_existing_file.h5')
    mock.assert_called_with("[*] HDF5 File could not be found")

def test_read_hdf5_through_pandas_check_response():
    filename = '../files/isotopeTable.h5'
    test_response = pd.read_hdf(filename, mode='r')
    response = data_tools.read_hdf5_through_pandas('../files/isotopeTable.h5')
    assert test_response.equals(response)

@patch.object(data_tools.logger, "critical")   
def test_read_mat_files_file_not_found(mock):
    response = data_tools.read_mat_files('../files/not_existing_file.mat')
    mock.assert_called_with("[*] Mat File could not be found")

def test_read_mat_files_check_response():
    filename = '../files/isotopeTable.mat'
    test_response = scipy.io.loadmat(filename)
    response = data_tools.read_mat_files(filename)
    diff = DeepDiff(test_response,response)
    assert len(diff) == 0
    
def test_read_mat_files_check_returnType():
    response = data_tools.read_mat_files('../files/isotopeTable.mat')
    assert isinstance(response, dict)

def test_convert_mat_to_df_check_returnType():
    data = data_tools.read_mat_files('../files/isotopeTable.mat')
    print(data['None'])
    data_tools.store_df_to_hdf = MagicMock()
    response = data_tools.convert_mat_to_df(data)
    assert isinstance(response,pd.core.frame.DataFrame)

def test_store_df_to_hdf_check_response():
    matFileResponse = data_tools.read_mat_files('../files/isotopeTable.mat')
    pdDataframe = pd.DataFrame(matFileResponse['None'])
    data_tools.store_df_to_hdf('../files/unittests_dummy.h5',pdDataframe,'data')
    response = data_tools.read_hdf5_through_pandas('../files/unittests_dummy.h5')
    assert pdDataframe.equals(response)