from pickletools import string1
import numpy as np
import h5py
import pandas as pd
import scipy.io
import logging_library

logger = logging_library.logger_creator('data_tools')


def read_hdf5(filename:"type: string - Path to hdf5(.h5) file")->"type: dataframe - Pandas dataframe converted from H5 file":
    """
    This function differs from read_hdf5_through_pandas as it does not assume that 
    the contents of the HDF5 file as argument was created using pandas. It could 
    be have been created using other tools like h5py/MATLAB.
    """
    try:
        TOFFACTOR = 27.432 / (1000 * 4)  # 27.432 ps/bin, tof in ns, data is TDC time sum
        DETBINS = 4900
        BINNINGFAC = 2
        XYFACTOR = 78 / DETBINS * BINNINGFAC  # XXX mm/bin
        XYBINSHIFT = DETBINS / BINNINGFAC / 2  # to center detector
        dataframeStorage = {}
        groupDict = {}
        dataframeStorageSubgroup = {}

        with h5py.File(filename, 'r') as hdf:
            groups = list(hdf.keys())

            subGroupList = []
            for item in groups:
                groupDict[item] = list(hdf[item].keys())
            for key, value in groupDict.items():
                for item in value:
                    dataset = pd.DataFrame(np.array(hdf['{}/{}'.format(key, item)]), columns=['values'])
                    if key == 'dld' and item == 't':
                        dataset = dataset * TOFFACTOR
                    elif key == 'dld' and item == 'x':
                        dataset = (dataset - XYBINSHIFT) * XYFACTOR
                    elif key == 'dld' and item == 'y':
                        dataset = (dataset - XYBINSHIFT) * XYFACTOR
                    else:
                        dataset = dataset
                    dataframeStorage["{}/{}".format(key, item)] = dataset

            return dataframeStorage
    except FileNotFoundError as error:
        logger.critical(error)
        logger.critical("[*] HDF5 File could not be found")
        
    except IndexError as error:
        logger.critical(error)
        logger.critical("[*] No Group keys could be found in HDF5 File")


def read_hdf5_through_pandas(filename:"type:string - Path to hdf5(.h5) file")->"type: dataframe - Pandas Dataframe":
    """
    This function is different from read_hdf5 function. As it assumes, the content 
    of the HDF5 file passed as argument was created using the pandas library.
    """
    try:
        hdf5FileResponse = pd.read_hdf(filename, mode='r')
        return hdf5FileResponse
    except FileNotFoundError as error:
        logger.info(error)
        logger.critical("[*] HDF5 File could not be found")


def read_mat_files(filename:"type:string - Path to .mat file") -> " type: dict - Returns the content .mat file":
    try:
        matFileResponse = scipy.io.loadmat(filename)
        return matFileResponse
    except FileNotFoundError as error:
        logger.critical(error)
        logger.critical("[*] Mat File could not be found")


def convert_mat_to_df(matFileResponse:"type: dict - content of .mat file"):
    pdDataframe = pd.DataFrame(matFileResponse['None'])
    key = 'dataframe/isotope'
    filename = 'isotopeTable.h5'
    store_df_to_hdf(filename, pdDataframe, key)
    return pdDataframe


def store_df_to_hdf(filename:"type: string - name of hdf5 file", 
                    dataframe:"dataframe which is to be stored in h5 file", 
                    key:"DirectoryStructure/columnName of content"):
    dataframe.to_hdf(filename, key, mode='w')


