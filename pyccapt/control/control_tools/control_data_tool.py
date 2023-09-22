import h5py
import numpy as np


def rename_subcategory(hdf5_file_path, old_name, new_name):
    """
        rename subcategory

        Args:
            hdf5_file_path: path to the hdf5 file
            old_name: old name of the subcategory
            new_name: new name of the subcategory

        Returns:
            None
    """

    with h5py.File(hdf5_file_path, 'r+') as file:
        if old_name in file:
            file[new_name] = file[old_name]
            del file[old_name]
            print(f"Subcategory '{old_name}' renamed to '{new_name}'")
        else:
            print(f"Subcategory '{old_name}' not found in the HDF5 file.")


def correct_surface_concept_old_data(hdf5_file_path):
    """
        correct surface concept old data

        Args:
            hdf5_file_path: path to the hdf5 file

        Returns:
            None
    """
    # surface concept tdc specific binning and factors
    TOFFACTOR = 27.432 / (1000.0 * 4.0)  # 27.432 ps/bin, tof in ns, data is TDC time sum
    DETBINS = 4900.0
    BINNINGFAC = 2.0
    XYFACTOR = 80.0 / DETBINS * BINNINGFAC  # XXX mm/bin
    XYBINSHIFT = DETBINS / BINNINGFAC / 2.0  # to center detector

    with h5py.File(hdf5_file_path, 'r+') as file:
        data_x = file['dld/x']
        data_y = file['dld/y']
        data_t = file['dld/t']

        data_x = np.array(data_x)
        data_y = np.array(data_y)
        data_t = np.array(data_t)

        modified_t = (data_t.astype(np.float64) * TOFFACTOR)
        del file['dld/t']
        file.create_dataset('dld/t', data=modified_t, dtype=np.float64)
        modified_x = ((data_x.astype(np.float64) - XYBINSHIFT) * XYFACTOR) / 10.0
        del file['dld/x']
        file.create_dataset('dld/x', data=modified_x, dtype=np.float64)
        modified_y = ((data_y.astype(np.float64) - XYBINSHIFT) * XYFACTOR) / 10.0
        del file['dld/y']
        file.create_dataset('dld/y', data=modified_y, dtype=np.float64)


def copy_npy_to_hdf(path, hdf5_file_name):
    """
        copy npy data to hdf5 file

        Args:
            path: path to the npy files
            hdf5_file_name: name of the hdf5 file

        Returns:
            None
    """
    TOFFACTOR = 27.432 / (1000 * 4)  # 27.432 ps/bin, tof in ns, data is TDC time sum
    DETBINS = 4900
    BINNINGFAC = 2
    XYFACTOR = 80 / DETBINS * BINNINGFAC  # XXX mm/bin
    XYBINSHIFT = DETBINS / BINNINGFAC / 2  # to center detector

    hdf5_file_path = path + hdf5_file_name
    high_voltage = np.load(path + 'voltage_data.npy')
    pulse = np.load(path + 'pulse_data.npy')
    t = np.load(path + 't_data.npy')
    x_det = np.load(path + 'x_data.npy')
    y_det = np.load(path + 'y_data.npy')

    xx_tmp = (((x_det - XYBINSHIFT) * XYFACTOR) * 0.1)  # from mm to in cm by dividing by 10
    yy_tmp = (((y_det - XYBINSHIFT) * XYFACTOR) * 0.1)  # from mm to in cm by dividing by 10
    tt_tmp = (t * TOFFACTOR)  # in ns

    with h5py.File(hdf5_file_path, 'r+') as file:
        del file['dld/t']
        del file['dld/x']
        del file['dld/y']
        del file['dld/pulse']
        del file['dld/high_voltage']
        del file['dld/start_counter']
        file.create_dataset('dld/t', data=tt_tmp, dtype=np.float64)
        file.create_dataset('dld/x', data=xx_tmp, dtype=np.float64)
        file.create_dataset('dld/y', data=yy_tmp, dtype=np.float64)
        file.create_dataset('dld/pulse', data=pulse, dtype=np.float64)
        file.create_dataset('dld/high_voltage', data=high_voltage, dtype=np.float64)
        file.create_dataset('dld/start_counter', data=np.zeros(len(high_voltage)), dtype=np.float64)


def correct_surface_concept_old_data(hdf5_file_path, max_laser_intensity):
    """
        correct surface concept old data

        Args:
            hdf5_file_path: path to the hdf5 file

        Returns:
            None
    """


    with h5py.File(hdf5_file_path, 'r+') as file:
        laser_angle = file['dld/pulse']
        laser_angle = np.array(laser_angle)
        OD = ((laser_angle - 242) / 270) * 2
        scale = 10 ** OD
        scaled_intensity = max_laser_intensity * scale
        del file['dld/pulse']
        file.create_dataset('dld/pulse', data=scaled_intensity, dtype=np.float64)



if __name__ == '__main__':
    path = '../../../tests/data/'
    # name = 'data_115_Jul-27-2022_17-44_Powersweep3.h5'
    # name = 'data_124_Apr-18-2023_18-46_LFIM1.h5'
    name = 'data_130_Sep-19-2023_14-58_W_12fs.h5'
    # copy_npy_to_hdf(path, name)
    # rename_subcategory(path + name, 'dld/AbsoluteTimeStamp', 'dld/start_counter')
    # 3.4e13 W/cm^2 --> 171 fs
    # 1.4e13 W/cm^2 --> 12 fs
    correct_surface_concept_old_data(path + name, 3.4e13)
    print('Done')