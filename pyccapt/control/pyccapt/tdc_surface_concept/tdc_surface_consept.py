"""
This is the main script for reading TDC.
"""

import time
import numpy as np
from queue import Queue

from pyccapt.devices import initialize_devices
from pyccapt.tdc_surface_concept import scTDC

# define some constants to distinguish the type of element placed in the queue
QUEUE_DATA = 0
QUEUE_ENDOFMEAS = 1


class BufDataCB4(scTDC.buffered_data_callbacks_pipe):
    """
    The class inherits from python wrapper module scTDC and class: buffered_data_callbacks_pipe
    """

    def __init__(self, lib, dev_desc, raw_mode, dld_events,
                 max_buffered_data_len=500000):
        if not raw_mode:
            data_field_selection = \
                scTDC.SC_DATA_FIELD_DIF1 \
                | scTDC.SC_DATA_FIELD_DIF2 \
                | scTDC.SC_DATA_FIELD_TIME \
                | scTDC.SC_DATA_FIELD_START_COUNTER
        elif raw_mode:
            data_field_selection = \
                scTDC.SC_DATA_FIELD_TIME \
                | scTDC.SC_DATA_FIELD_CHANNEL \
                | scTDC.SC_DATA_FIELD_START_COUNTER

        '''
        Initialize the base class: scTDC.buffered_data_callbacks_pipe

        Attributes
            lib : scTDClib- a scTDClib object.
            dev_desc : int
                device descriptor as returned by sc_tdc_init_inifile(...).
            data_field_selection : int, optional
                a 'bitwise or' combination of SC_DATA_FIELD_xyz constants. The
                default is SC_DATA_FIELD_TIME.
            max_buffered_data_len : int, optional
                The number of events that are buffered before invoking the on_data
                callback. Less events can also be received in the on_data callback,
                when the user chooses to return True from the on_end_of_meas
                callback.
                The default is (1<<16).
            dld_events : bool, optional
                if True, receive DLD events. If False, receive TDC events.
                Depending on the configuration in the tdc_gpx3.ini file, only one
                type of events may be available. The default is True.
        '''
        super().__init__(lib, dev_desc, data_field_selection,  # <-- mandatory!
                         max_buffered_data_len, dld_events)  # <-- mandatory!

        # Initialize the queue object
        self.queue = Queue()
        # Setting the flag
        self.end_of_meas = False

    def on_data(self, d):
        """
        This class method fucntion
            1. Makes a dict that contains copies of numpy arrays in d ("deep copy")
            2. Start with an empty dict, insert basic values by simple assignment,
            3. Insert numpy arrays using the copy method of the source array

        Attributes:
            d: [dictionary]

        Returns:
            Does not return anything
        """

        dcopy = {}
        for k in d.keys():
            if isinstance(d[k], np.ndarray):
                dcopy[k] = d[k].copy()
            else:
                dcopy[k] = d[k]
        self.queue.put((QUEUE_DATA, dcopy))
        if self.end_of_meas:
            self.end_of_meas = False
            self.queue.put((QUEUE_ENDOFMEAS, None))

    def on_end_of_meas(self):
        """
        This class method set end_of_meas to True

        Attributes:
            Does not accept any argument

        Returns:
            True [boolean]
        """

        self.end_of_meas = True
        # setting end_of_meas, we remember that the next on_data delivers the
        # remaining data of this measurement
        return True


# -----------------------------------------------------------------------------


def experiment_measure(raw_mode, queue_x,
                       queue_y, queue_t,
                       queue_dld_start_counter,
                       queue_channel,
                       queue_time_data,
                       queue_tdc_start_counter,
                       queue_stop_measurement):
    """
    measurement function: This function is called in a process by 
                          apt_voltage.py tp read data from the queue.
    Attributes:
        DLD Queues: Queues that contains DLD data
            queue_y: Queue for grp: DLD and parameter: y
            queue_t: Queue for grp: DLD and parameter: t
            queue_dld_start_counter: Queue for grp: DLD and parameter: start_counter
            
        TDC Queues: Queues that contains TDC raw data
            queue_time_data: Queue for grp: TDC and parameter: time_data
            queue_tdc_start_counter: Queue for grp: TDC and parameter: start_counter

        Stop measurement flag: queue
            Queue for stop the measurement. This queue is set to True from apt_voltage.py

    Returns
        Does not return anything
    """

    device = scTDC.Device(autoinit=False)

    # initialize TDC --- and check for error!
    retcode, errmsg = device.initialize()
    if retcode < 0:
        print("error during init:", retcode, errmsg)
        print(
            f"{initialize_devices.bcolors.FAIL}Error: Restart the TDC manually (Turn it On and Off){initialize_devices.bcolors.ENDC}")
        return -1
    else:
        print("TDC is successfully initialized")

    # open a BUFFERED_DATA_CALLBACKS pipe
    bufdatacb = BufDataCB4(device.lib, device.dev_desc, raw_mode, dld_events=not raw_mode)

    def errorcheck(retcode):
        """
        This function define a closure that checks return codes for errors and does clean up.

        Attributes:
            retcode: Return code

        Returns:
            0: if success return code or return code > 0 [int]
            -1: if return code is error code or less than 0 [int]
        """
        if retcode < 0:
            print(device.lib.sc_get_err_msg(retcode))
            bufdatacb.close()
            device.deinitialize()
            return -1
        else:
            return 0

    # start a first measurement
    retcode = bufdatacb.start_measurement(300)
    if errorcheck(retcode) < 0:
        return -1

    while True:
        eventtype, data = bufdatacb.queue.get()  # waits until element available
        if eventtype == QUEUE_DATA:
            if not raw_mode:
                queue_x.put(data["dif1"])
                queue_y.put(data["dif2"])
                queue_t.put(data["time"])
                queue_dld_start_counter.put(data["start_counter"])
            elif raw_mode:
                queue_channel.put(data["channel"])
                queue_time_data.put(data["time"])
                queue_tdc_start_counter.put(data["start_counter"])
        elif eventtype == QUEUE_ENDOFMEAS:
            if queue_stop_measurement.empty():
                retcode = bufdatacb.start_measurement(300)
                if errorcheck(retcode) < 0:
                    return -1
            else:
                break
        else:  # unknown event
            break  # break out of the event loop
        # print('tdc process time:', time.time() - start)

    time.sleep(0.1)
    # clean up
    # closes the user callbacks pipe, method inherited from base class
    bufdatacb.close()
    device.deinitialize()

    return 0
