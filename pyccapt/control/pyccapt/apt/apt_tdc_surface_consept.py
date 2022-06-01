"""
This is the main script for controlling the experiment.
It contains the main control loop of experiment.
"""

import time
import datetime
import multiprocessing
from multiprocessing.queues import Queue
import threading
import numpy as np

# Serial ports and NI
import serial.tools.list_ports
import pyvisa as visa
import nidaqmx

# Local project scripts
from pyccapt.devices import signal_generator, tweet_send
from pyccapt.devices import email_send, initialize_devices
from pyccapt.tdc_surface_concept import tdc_surface_consept
from pyccapt.drs import drs
from pyccapt.control_tools import experiment_statistics, variables, hdf5_creator, loggi


class APT_ADVANCE:
    """
    APT_VOLTAGE class is a main class for controlling voltage atom probe with Surface Consept TDC.
    """
    def __init__(self, queue_x, queue_y, queue_t, queue_dld_start_counter,
                 queue_channel, queue_time_data, queue_tdc_start_counter,
                 queue_ch0_time, queue_ch0_wave, queue_ch1_time, queue_ch1_wave,
                 queue_ch2_time, queue_ch2_wave, queue_ch3_time, queue_ch3_wave,
                 lock1, lock2, logger, conf):
        """
        This is the constructor class that accepts several initialized queues objects corresponding
        to various parameters of the groups like dld,TDC,DRS. This constructor also objects used for
        creating locks on resources to reduce concurrent access on resources and reduce dirty read.
        """
        # Queues for sharing data between tdc and main process
        # dld queues
        self.queue_x = queue_x
        self.queue_y = queue_y
        self.queue_t = queue_t
        self.queue_dld_start_counter = queue_dld_start_counter
        self.lock1 = lock1
        # TDC queues
        self.queue_channel = queue_channel
        self.queue_time_data = queue_time_data
        self.queue_tdc_start_counter = queue_tdc_start_counter
        self.lock2 = lock2
        # DRS queues
        self.queue_ch0_time = queue_ch0_time
        self.queue_ch0_wave = queue_ch0_wave
        self.queue_ch1_time = queue_ch1_time
        self.queue_ch1_wave = queue_ch1_wave
        self.queue_ch2_time = queue_ch2_time
        self.queue_ch2_wave = queue_ch2_wave
        self.queue_ch3_time = queue_ch3_time
        self.queue_ch3_wave = queue_ch3_wave
        self.logger = logger
        self.conf = conf
        #self.log_apt_tdc_surface_consept = loggi.logger_creator('apt_tdc_surface_consept', 'apt_tdc_surface_consept.log')
    def print_log(self,string_to_be_printed):
        print(string_to_be_printed)

    def initialize_v_dc(self):
        """
        This class method initializes the high voltage device:.
        The function utilizes the serial library to communicate over the
        COM port serially and read the corresponding v_dc parameter.
        The COM port number has to be enter in the config file.

        It exits if it is not able to connect on the COM Port.

        Attributes:
            Accepts only the self (class object)

        Returns:
            Does not return anything
        """
        #self.log_apt_tdc_surface_consept.info("Function - initialize_v_dc | Port selection -> {}".format(initialize_devices.com_ports[variables.COM_PORT_V_dc].device))
        # Setting the com port of V_dc
        self.com_port_v_dc = serial.Serial(
            port=initialize_devices.com_ports[variables.COM_PORT_V_dc].device,  # chosen COM port
            baudrate=115200,  # 115200
            bytesize=serial.EIGHTBITS,  # 8
            parity=serial.PARITY_NONE,  # N
            stopbits=serial.STOPBITS_ONE  # 1
        )
        #self.log_apt_tdc_surface_consept.info("Function - initialize_v_dc | Successful Port Open - O/p of serial variable - > {}".format(self.com_port_v_dc))

        # configure the COM port to talk to. Default values: 115200,8,N,1
        if self.com_port_v_dc.is_open:
            self.com_port_v_dc.flushInput()
            self.com_port_v_dc.flushOutput()

            cmd_list = [">S1 3.0e-4", ">S0B 0", ">S0 %s" % variables.vdc_min, "F0", ">S0?", ">DON?",
                        ">S0A?"]
            for cmd in range(len(cmd_list)):
                self.command_v_dc(cmd_list[cmd])
        else:
            #self.log_apt_tdc_surface_consept.error("Function - initialize_v_dc | Port error - O/p of serial variable - > {} ".format(self.com_port_v_dc))
            self.print_log("Could not open port")
            exit()

    def initialize_v_p(self):
        """
        This class method initializes the Pulser device:
        The function utilizes the serial library to communicate over the
        COM port serially and read the corresponding v_p parameter.
        The COM port number has to be enter in the config file.

        Attributes:
            Accepts only the self (class object)
        
        Returns:
            Does not return anything

        """

        # set the port for v_p
        resources = visa.ResourceManager('@py')
        self.com_port_v_p = resources.open_resource(variables.COM_PORT_V_p)

        try:
            self.com_port_v_p.query('*RST')
        except:
            self.com_port_v_p.write('VOLT %s' % (variables.v_p_min * (1 / variables.pulse_amp_per_supply_voltage)))

    def initialize_counter(self):
        """
        This class method initializes the edge counter of National Instrument.
        It helps to count the riding edges of a detector  signal.

        The function utilizes the nidaqmx library to communicate
        through NI Instruments to count the edges.

        NI-DAQmx can help you use National Instruments (NI) data acquisition and 
        signal conditioning hardware

        Attributes:
            Accepts only the self (class object)
        
        Returns:
            Returns the counted edges
            
        """
        task_counter = nidaqmx.Task()
        task_counter.ci_channels.add_ci_count_edges_chan(self.conf['COM_PORT_NI_counter'])
        # reference the terminal you want to use for the counter here
        task_counter.ci_channels[0].ci_count_edges_term = "PFI0"
        self.log_apt_tdc_surface_consept.info("Function - initialize_counter | task counter - > {}".format(task_counter))

        return task_counter


    def command_v_dc(self, cmd):
        """
        This class method is used to send commands on the high voltage parameter: v_dc.
        The function utilizes the serial library to communicate over the
        COM port serially and read the corresponding v_dc parameter.

        Attributes:
            Accepts only the self (class object)
        
        Returns:
            Returns the response code after executing the command.
        """
        self.com_port_v_dc.write(
            (cmd + '\r\n').encode())  # send cmd to device # might not work with older devices -> "LF" only needed!
        time.sleep(0.005)  # small sleep for response
        # Initialize the response to returned as string
        response = ''
        # Read the response code after execution(command write).
        try:

            while self.com_port_v_dc.in_waiting > 0:
                response = self.com_port_v_dc.readline()  # all characters received, read line till '\r\n'
        except Exception as error:
            self.log_apt_tdc_surface_consept.error("Function - command_v_dc | error reading lines - > {}".format(error))
        response  =  response.decode("utf-8")
        self.log_apt_tdc_surface_consept.info("Function - command_v_dc | response - > {}".format(response))

        return response

    def reader_queue_dld(self):
        """
        This class method runs in an infinite loop and listens and reads dld queues.
        over the queues for the group: dld

        This function is called continuously by a separate thread in the main function.

        The values read from the queues are updates in imported "variables" file

        Attributes:
            Accepts only the self (class object)
        
        Returns:
            Does not return anything
        """
        while True:
            # Check if any value is present in queue to read from
            while not self.queue_x.empty() or not self.queue_y.empty() or not self.queue_t.empty() or not self.queue_dld_start_counter.empty():
                # Utilize locking mechanism to avoid concurrent use of resources and dirty reads
                with self.lock1:
                    length = self.queue_x.get()
                    variables.x = np.append(variables.x, length)
                    variables.y = np.append(variables.y, self.queue_y.get())
                    variables.t = np.append(variables.t, self.queue_t.get())
                    variables.dld_start_counter = np.append(variables.dld_start_counter,
                                                            self.queue_dld_start_counter.get())
                    variables.main_v_dc_dld = np.append(variables.main_v_dc_dld,
                                                        np.tile(variables.specimen_voltage, len(length)))
                    variables.main_v_p_dld = np.append(variables.main_v_p_dld,
                                                       np.tile(variables.pulse_voltage, len(length)))
            # If end of experiment flag is set break the while loop
            if variables.end_experiment:
                break

    def reader_queue_drs(self):

        """
        This class method runs in an infinite loop and listens and reads DRS queues.
        over the queues for the group: DRS

        This function is called continuously by a separate thread in the main function.

        The values read from the queues are updates in imported "variables" file.
        Attributes:
            Accepts only the self (class object)
        
        Returns:
            Does not return anything
        """

        while True:
            # Check if any value is present in queue to read from
            while not self.queue_ch0_time.empty() or not self.queue_ch0_wave.empty() or not self.queue_ch1_time.empty() or not \
                    self.queue_ch1_wave.empty() or not self.queue_ch2_time.empty() or not \
                    self.queue_ch2_wave.empty() or not self.queue_ch3_time.empty() or not self.queue_ch3_wave.empty():
                # Utilize locking mechanism to avoid concurrent use of resources and dirty reads
                with self.lock1:
                    length = self.queue_ch0_time.get()
                    variables.ch0_time = np.append(variables.ch0_time, length)
                    variables.ch0_wave = np.append(variables.ch0_wave, self.queue_ch0_wave.get())
                    variables.ch1_time = np.append(variables.ch1_time, self.queue_ch1_time.get())
                    variables.ch1_wave = np.append(variables.ch1_wave, self.queue_ch1_wave.get())
                    variables.ch2_time = np.append(variables.ch2_time, self.queue_ch2_time.get())
                    variables.ch2_wave = np.append(variables.ch2_wave, self.queue_ch2_wave.get())
                    variables.ch3_time = np.append(variables.ch3_time, self.queue_ch3_time.get())
                    variables.ch3_wave = np.append(variables.ch3_wave, self.queue_ch3_wave.get())

                    variables.main_v_dc_drs = np.append(variables.main_v_dc_drs,
                                                        np.tile(variables.specimen_voltage, len(length)))
                    variables.main_v_p_drs = np.append(variables.main_v_p_drs,
                                                       np.tile(variables.pulse_voltage, len(length)))
            # If end of experiment flag is set break the while loop
            if variables.end_experiment:
                break

    def reader_queue_tdc(self):

        """
        This class method runs in an infinite loop and listens and reads TDC queues.
        TDC data is the raw data which contains the channel number and the time stamp.
        over the queues for the group: TDC

        This function is called continuously by a separate thread in the main function.

        The values read from the queues are updates in imported "variables" file.

        Attributes:
            Accepts only the self (class object)
        
        Returns:
            Does not return anything
        """

        while True:
            # Check if any value is present in queue to read from
            while not self.queue_channel.empty() or not self.queue_time_data.empty() or not self.queue_tdc_start_counter.empty():
                # Utilize locking mechanism to avoid concurrent use of resources and dirty reads
                with self.lock2:
                    length = self.queue_channel.get()
                    variables.channel = np.append(variables.channel, length)
                    variables.time_data = np.append(variables.time_data, self.queue_time_data.get())
                    variables.tdc_start_counter = np.append(variables.tdc_start_counter,
                                                            self.queue_tdc_start_counter.get())
                    variables.main_v_dc_tdc = np.append(variables.main_v_dc_tdc,
                                                        np.tile(variables.specimen_voltage, len(length)))
                    variables.main_v_p_tdc = np.append(variables.main_v_p_tdc,
                                                       np.tile(variables.pulse_voltage, len(length)))
            # If end of experiment flag is set break the while loop
            if variables.end_experiment:
                break

    def main_ex_loop(self, task_counter, counts_target):

        """
        This function is contaion all methods that itretively has to run to control the exprement.
        This class method:

        1. Read the number of detected Ions(in TDC or Counter mode)
        2- Calculate the error of detection rate of desire rate
        3- Regulate the high voltage and pulser

        This function is called in each loop of main function.

        Attributes:
            task_counter: Counter edges
            counts_target:
        
        Returns:
            Does not return anything

        """

        if variables.counter_source == 'TDC':
            variables.total_ions = len(variables.x)
        elif variables.counter_source == 'TDC_Raw':
            if len(variables.channel) > 0:
                variables.total_ions = int(len(variables.channel) / 4)
        elif variables.counter_source == 'Pulse Counter':
            # reading detector MCP pulse counter and calculating pulses since last loop iteration
            variables.total_ions = task_counter.read(number_of_samples_per_channel=1)[0]
        elif variables.counter_source == 'DRS':
            pass

        variables.count_temp = variables.total_ions - variables.count_last
        variables.count_last = variables.total_ions

        # saving the values of high dc voltage, pulse, and current iteration ions
        variables.main_v_dc = np.append(variables.main_v_dc, variables.specimen_voltage)
        variables.main_v_p = np.append(variables.main_v_p, variables.pulse_voltage)
        variables.main_counter = np.append(variables.main_counter, variables.count_temp)
        # averaging count rate of N_averg counts
        variables.avg_n_count = variables.ex_freq * (
                sum(variables.main_counter[-variables.cycle_avg:]) / variables.cycle_avg)

        counts_measured = variables.avg_n_count / (1 + variables.pulse_frequency * 1000)

        # variables.avg_n_count = np.sum(variables.main_counter[-variables.cycle_avg:])
        #
        # counts_measured = variables.avg_n_count / (1 + variables.pulse_frequency * 1000)

        counts_error = counts_target - counts_measured  # deviation from setpoint
        self.log_apt_tdc_surface_consept.info("Function - main_ex_loop | count_temp | value - {}| type - {}".format(variables.count_temp,type(variables.count_temp)))
        self.log_apt_tdc_surface_consept.info("Function - main_ex_loop | count_last | value - {}| type - {}".format(variables.count_last,type(variables.count_last)))
        self.log_apt_tdc_surface_consept.info("Function - main_ex_loop | main_v_dc | value - {}| type - {}".format(variables.main_v_dc,type(variables.main_v_dc)))
        self.log_apt_tdc_surface_consept.info("Function - main_ex_loop | main_counter | value - {}| type - {}".format(variables.main_counter,type(variables.main_counter)))
        self.log_apt_tdc_surface_consept.info("Function - main_ex_loop | avg_n_count | value - {}| type - {}".format(variables.avg_n_count,type(variables.avg_n_count)))
        self.log_apt_tdc_surface_consept.info("Function - main_ex_loop | ex_freq | value - {}| type - {}".format(variables.ex_freq,type(variables.ex_freq)))
        self.log_apt_tdc_surface_consept.info("Function - main_ex_loop | counts_measured | value - {}| type - {}".format(counts_measured,type(counts_measured)))
        self.log_apt_tdc_surface_consept.info("Function - main_ex_loop | counts_error | value - {}| type - {}".format(counts_error,type(counts_error)))

        # simple proportional control with averaging
        rate = ((variables.avg_n_count * 100) / (1 + variables.pulse_frequency * 1000))
        if rate < 0.01 and variables.specimen_voltage < 5000:
            ramp_speed_factor = 2.5
        else:
            ramp_speed_factor = 1
        if counts_error > 0:
            voltage_step = counts_error * variables.vdc_step_up * ramp_speed_factor
        elif counts_error <= 0:
            voltage_step = counts_error * variables.vdc_step_down * ramp_speed_factor

        # update v_dc
        if variables.specimen_voltage < variables.vdc_max:
            if variables.specimen_voltage >= variables.vdc_min:
                specimen_voltage_temp = variables.specimen_voltage + voltage_step
                if specimen_voltage_temp > variables.specimen_voltage:
                    # sending VDC via serial
                    if self.conf['v_dc'] != "off":
                        self.command_v_dc(">S0 %s" % specimen_voltage_temp)
                    variables.specimen_voltage = specimen_voltage_temp

        # update pulse voltage v_p
        new_vp = variables.specimen_voltage * variables.pulse_fraction * \
                 (1 / variables.pulse_amp_per_supply_voltage)
        if variables.pulse_voltage_max > new_vp > variables.pulse_voltage_min:
            if self.conf['v_p'] != "off":
                self.com_port_v_p.write('VOLT %s' % new_vp)
            variables.pulse_voltage = new_vp * variables.pulse_amp_per_supply_voltage

        variables.main_temperature = np.append(variables.main_temperature, variables.temperature)
        variables.main_chamber_vacuum = np.append(variables.main_chamber_vacuum, float(variables.vacuum_main))

    def clear_up(self, task_counter):
        """
        This function clears global variables and deinitialize high voltage and pulser function
        and clear up global variables

        Attributes:
            Does not accept any arguments
        Returns:
            Does not return anything
        
        """

        def cleanup_variables():
            """
            Clear up all the global variables
            """
            variables.stop_flag = False
            variables.end_experiment = False
            variables.start_flag = False
            # variables.elapsed_time = 0.0
            # variables.total_ions = 0
            # variables.specimen_voltage = 0.0
            # variables.total_count = 0
            # variables.avg_n_count = 0
            # variables.pulse_voltage = 0.0
            variables.detection_rate = 0.0
            variables.detection_rate_elapsed = 0.0
            variables.count = 0
            variables.count_temp = 0
            variables.count_last = 0
            variables.index_plot = 0
            variables.index_save_image = 0
            variables.index_wait_on_plot_start = 0
            variables.index_plot_save = 0
            variables.index_plot = 0

            variables.x = np.zeros(0)
            variables.y = np.zeros(0)
            variables.t = np.zeros(0)
            variables.dld_start_counter = np.zeros(0)

            variables.channel = np.zeros(0)
            variables.time_data = np.zeros(0)
            variables.tdc_start_counter = np.zeros(0)

            variables.ch0_time = np.zeros(0)
            variables.ch0_wave = np.zeros(0)
            variables.ch1_time = np.zeros(0)
            variables.ch1_wave = np.zeros(0)
            variables.ch2_time = np.zeros(0)
            variables.ch2_wave = np.zeros(0)
            variables.ch3_time = np.zeros(0)
            variables.ch3_wave = np.zeros(0)

            variables.main_v_dc = np.zeros(0)
            variables.main_v_p = np.zeros(0)
            variables.main_counter = np.zeros(0)
            variables.main_temperature = np.zeros(0)
            variables.main_chamber_vacuum = np.zeros(0)
            variables.main_v_dc_dld = np.zeros(0)
            variables.main_v_p_dld = np.zeros(0)
            variables.main_v_dc_tdc = np.zeros(0)
            variables.main_v_p_tdc = np.zeros(0)
            self.log_apt_tdc_surface_consept.info("Function - cleanup_variables | ch1 | value - {}| type - {}".format(variables.count_temp,type(variables.count_temp)))
            self.log_apt_tdc_surface_consept.info("Function - cleanup_variables | main_v_dc_tdc | value - {}| type - {}".format(variables.main_v_dc_tdc,type(variables.main_v_dc_tdc)))

        self.logger.info('starting to clean up')

        # save the data to the HDF5

        if self.conf['v_dc'] != "off":
            # Switch off the v_dc
            self.command_v_dc('F0')
            self.com_port_v_dc.close()

        if self.conf['v_p'] != "off":
            # Switch off the v_p
            self.com_port_v_p.write('VOLT 0')
            self.com_port_v_p.write('OUTPut OFF')
            self.com_port_v_p.close()

        if self.conf['edge_counter'] != "off":
            if variables.counter_source == 'Pulse Counter':
                # Close the task of counter
                task_counter.stop()
                task_counter.close()
        if self.conf['signal_generator'] != "off":
            # Turn off the signal generator
            signal_generator.turn_off_signal_generator()
        # Zero variables
        cleanup_variables()
        self.logger.info('Clean up is finished')


def main(conf):
    """
    Main function for doing experiments
    1- Initialize all the devices (High voltage, pulser, TDC or Edge-Counter)
    2- Create and start reader DLD and TDC thread
    3- Create and start the TDC process if TDC is selected in GUI
    4- Iterate over the main loop of experiments and control the experiment frequency
    5- Stop the experiment if stop condition is achieved
    6- Deinitialize devices
    7- Save the data
    8- Send email and tweet
    """
    # Initialize logger
    logger = loggi.get_logging()
    logger.info('Experiment is starting')

    variables.start_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

    if conf['tdc'] != "off" and variables.counter_source != 'DRS' and variables.counter_source != 'Pulse Counter':
        # Create and start the TDC process and related queues
        if variables.counter_source == 'TDC':
            queue_x = Queue(maxsize=-1, ctx=multiprocessing.get_context())
            queue_y = Queue(maxsize=-1, ctx=multiprocessing.get_context())
            queue_t = Queue(maxsize=-1, ctx=multiprocessing.get_context())
            queue_dld_start_counter = Queue(maxsize=-1, ctx=multiprocessing.get_context())
            queue_channel = None
            queue_time_data = None
            queue_tdc_start_counter = None
            queue_stop_measurement = Queue(maxsize=1, ctx=multiprocessing.get_context())

            # Initialize and initiate a process(Refer to imported file 'tdc_new' for process function declaration )
            # Module used: multiprocessing
            tdc_process = multiprocessing.Process(target=tdc_surface_consept.experiment_measure,
                                                  args=(variables.raw_mode, queue_x,
                                                        queue_y, queue_t,
                                                        queue_dld_start_counter,
                                                        queue_channel,
                                                        queue_time_data,
                                                        queue_tdc_start_counter,
                                                        queue_stop_measurement))

        elif variables.counter_source == 'TDC_Raw':
            queue_x = None
            queue_y = None
            queue_t = None
            queue_dld_start_counter = None
            queue_channel = Queue(maxsize=-1, ctx=multiprocessing.get_context())
            queue_time_data = Queue(maxsize=-1, ctx=multiprocessing.get_context())
            queue_tdc_start_counter = Queue(maxsize=-1, ctx=multiprocessing.get_context())
            queue_stop_measurement = Queue(maxsize=1, ctx=multiprocessing.get_context())

            # Initialize and initiate a process(Refer to imported file 'tdc_new' for process function declaration )
            # Module used: multiprocessing
            tdc_process = multiprocessing.Process(target=tdc_surface_consept.experiment_measure,
                                                  args=(variables.raw_mode, queue_x,
                                                        queue_y, queue_t,
                                                        queue_dld_start_counter,
                                                        queue_channel,
                                                        queue_time_data,
                                                        queue_tdc_start_counter,
                                                        queue_stop_measurement))
        tdc_process.daemon = True
        tdc_process.start()

        queue_ch0_time = None
        queue_ch0_wave = None
        queue_ch1_time = None
        queue_ch1_wave = None
        queue_ch2_time = None
        queue_ch2_wave = None
        queue_ch3_time = None
        queue_ch3_wave = None
    elif variables.counter_source == 'DRS':
        queue_ch0_time = Queue(maxsize=-1, ctx=multiprocessing.get_context())
        queue_ch0_wave = Queue(maxsize=-1, ctx=multiprocessing.get_context())
        queue_ch1_time = Queue(maxsize=-1, ctx=multiprocessing.get_context())
        queue_ch1_wave = Queue(maxsize=-1, ctx=multiprocessing.get_context())
        queue_ch2_time = Queue(maxsize=-1, ctx=multiprocessing.get_context())
        queue_ch2_wave = Queue(maxsize=-1, ctx=multiprocessing.get_context())
        queue_ch3_time = Queue(maxsize=-1, ctx=multiprocessing.get_context())
        queue_ch3_wave = Queue(maxsize=-1, ctx=multiprocessing.get_context())
        queue_stop_measurement = Queue(maxsize=1, ctx=multiprocessing.get_context())

        queue_x = None
        queue_y = None
        queue_t = None
        queue_dld_start_counter = None
        queue_channel = None
        queue_time_data = None
        queue_tdc_start_counter = None

        # Initialize and initiate a process(Refer to imported file 'drs' for process function declaration)
        # Module used: multiprocessing
        drs_process = multiprocessing.Process(target=drs.experiment_measure, args=(queue_ch0_time, queue_ch0_wave,
                                                                                   queue_ch1_time, queue_ch1_wave,
                                                                                   queue_ch2_time, queue_ch2_wave,
                                                                                   queue_ch3_time, queue_ch3_wave,
                                                                                   queue_stop_measurement))
        drs_process.daemon = True
        drs_process.start()
    else:
        queue_x = None
        queue_y = None
        queue_t = None
        queue_dld_start_counter = None
        queue_channel = None
        queue_time_data = None
        queue_tdc_start_counter = None

        queue_ch0_time = None
        queue_ch0_wave = None
        queue_ch1_time = None
        queue_ch1_wave = None
        queue_ch2_time = None
        queue_ch2_wave = None
        queue_ch3_time = None
        queue_ch3_wave = None

    # Initialize lock that is used by TDC and DLD threads
    # Module used: threading 
    lock1 = threading.Lock()
    lock2 = threading.Lock()

    # Create the experiment object
    experiment = APT_ADVANCE(queue_x, queue_y, queue_t, queue_dld_start_counter,
                             queue_channel, queue_time_data, queue_tdc_start_counter,
                             queue_ch0_time, queue_ch0_wave, queue_ch1_time, queue_ch1_wave,
                             queue_ch2_time, queue_ch2_wave, queue_ch3_time, queue_ch3_wave,
                             lock1, lock2, logger, conf)

    if conf['signal_generator'] != "off":
        # Initialize the signal generator
        signal_generator.initialize_signal_generator(variables.pulse_frequency)

    if conf['v_dc'] != 'off':
        # Initialize high voltage
        experiment.initialize_v_dc()
        logger.info('High voltage is initialized')

    if conf['v_p'] != 'off':
        # Initialize pulser
        experiment.initialize_v_p()
        logger.info('Pulser is initialized')

    if variables.counter_source == 'Pulse Counter':
        task_counter = experiment.initialize_counter()
        logger.info('Edge counter is initialized')
    else:
        task_counter = None

    # start the timer for main experiment
    variables.specimen_voltage = variables.vdc_min
    variables.pulse_voltage_min = variables.v_p_min * (1 / variables.pulse_amp_per_supply_voltage)
    variables.pulse_voltage_max = variables.v_p_max * (1 / variables.pulse_amp_per_supply_voltage)
    variables.pulse_voltage = variables.v_p_min

    time_ex_s = np.zeros(0)
    time_ex_m = np.zeros(0)
    time_ex_h = np.zeros(0)
    time_counter = np.zeros(0)

    counts_target = ((variables.detection_rate / 100) * variables.pulse_frequency) / variables.pulse_frequency
    # counts_target = variables.detection_rate / 100
    logger.info('Starting the main loop')

    if conf['tdc'] != "off":
        # Initialize threads that will read from the queue for the group: dld
        if variables.counter_source == 'TDC':
            read_dld_queue_thread = threading.Thread(target=experiment.reader_queue_dld)
            read_dld_queue_thread.setDaemon(True)
            read_dld_queue_thread.start()
        # Initialize threads that will read from the queue for the group: tdc
        elif variables.counter_source == 'TDC_Raw':
            read_tdc_queue_thread = threading.Thread(target=experiment.reader_queue_tdc)
            read_tdc_queue_thread.setDaemon(True)
            read_tdc_queue_thread.start()
    # Initialize threads that will read from the queue for the group: drs
    elif variables.counter_source == 'DRS':
        read_drs_queue_thread = threading.Thread(target=experiment.reader_queue_drs)
        read_drs_queue_thread.setDaemon(True)
        read_drs_queue_thread.start()

    total_steps = variables.ex_time * variables.ex_freq
    steps = 0
    flag_achieved_high_voltage = 0
    index_time = 0
    ex_time_temp = variables.ex_time

    # Main loop of experiment
    while steps < total_steps:
        # Only for initializing every thing at firs iteration
        if steps == 0:
            # Turn on the v_dc and v_p
            if conf['v_p'] != "off":
                experiment.com_port_v_p.write('OUTPut ON')
                time.sleep(0.5)
            if conf['v_dc'] != "off":
                experiment.command_v_dc("F1")
                time.sleep(0.5)
            if conf['edge_counter'] != "off":
                if variables.counter_source == 'Pulse Counter':
                    # start the Counter
                    task_counter.start()

            variables.start_flag = True
            # Wait for 4 second to all devices get ready
            time.sleep(4)
            # Total experiment time variable
            start_main_ex = time.time()

            logger.info('Experiment is started')
        # Measure time
        start = datetime.datetime.now()
        # main loop function
        experiment.main_ex_loop(task_counter, counts_target)
        end = datetime.datetime.now()
        # If the main experiment function takes less than experiment frequency we have to waite
        if (1000 / variables.ex_freq) > ((end - start).microseconds / 1000):  # time in milliseconds
            sleep_time = ((1000 / variables.ex_freq) - ((end - start).microseconds / 1000))
            time.sleep(sleep_time / 1000)
        else:
            print(
                f"{initialize_devices.bcolors.WARNING}Warning: Experiment loop takes longer than %s Millisecond{initialize_devices.bcolors.ENDC}" % (
                    int(1000 / variables.ex_freq)))
            logger.error('Experiment loop takes longer than %s Millisecond' % (int(1000 / variables.ex_freq)))
            print('%s- The iteration time:' % index_time, ((end - start).microseconds / 1000))
            index_time += 1
        time_ex_s = np.append(time_ex_s, int(end.strftime("%S")))
        time_ex_m = np.append(time_ex_m, int(end.strftime("%M")))
        time_ex_h = np.append(time_ex_h, int(end.strftime("%H")))
        end_main_ex_loop = time.time()
        variables.elapsed_time = end_main_ex_loop - start_main_ex

        # Counter of iteration
        time_counter = np.append(time_counter, steps)
        steps += 1
        if variables.stop_flag:
            logger.info('Experiment is stopped by user')
            if conf['tdc'] != "off":
                if variables.counter_source == 'TDC' or variables.counter_source == 'TDC_Raw':
                    queue_stop_measurement.put(True)
            time.sleep(1)
            break

        if variables.criteria_ions:
            if variables.max_ions <= variables.total_ions:
                logger.info('Total number of Ions is achieved')
                if conf['tdc'] != "off":
                    if variables.counter_source == 'TDC' or variables.counter_source == 'TDC_Raw':
                        queue_stop_measurement.put(True)
                time.sleep(1)
                break
        if variables.criteria_vdc:
            if variables.vdc_max <= variables.specimen_voltage:
                if flag_achieved_high_voltage > variables.ex_freq * 10:
                    logger.info('High Voltage Max. is achieved')
                    if conf['tdc'] != "off":
                        if variables.counter_source == 'TDC' or variables.counter_source == 'TDC_Raw':
                            queue_stop_measurement.put(True)
                    time.sleep(1)
                    break
                flag_achieved_high_voltage += 1
        if variables.ex_time != ex_time_temp:
            total_steps = variables.ex_time * variables.ex_freq - steps
            ex_time_temp = variables.ex_time
        # Because experiment time is not a stop criteria, increase total_steps
        if not variables.criteria_time and steps + 1 == total_steps:
            total_steps += 1

    if conf['tdc'] != "off":
        # Stop the TDC process
        try:
            if variables.counter_source == 'TDC' or variables.counter_source == 'TDC_Raw':
                tdc_process.join(3)
                if tdc_process.is_alive():
                    tdc_process.terminate()
                    tdc_process.join(1)
                    # Release all the resources of the TDC process
                    tdc_process.close()
            elif variables.counter_source == 'DRS':
                drs_process.join(3)
                if drs_process.is_alive():
                    drs_process.terminate()
                    drs_process.join(1)
                    # Release all the resources of the TDC process
                    drs_process.close()
        except Exception as e:
            print(
                f"{initialize_devices.bcolors.WARNING}Warning: The TDC or DRS process cannot be terminated properly{initialize_devices.bcolors.ENDC}")
            print(e)
    variables.end_experiment = True
    time.sleep(1)
    if conf['tdc'] != "off":
        # Stop the TDC and DLD thread
        if variables.counter_source == 'TDC':
            read_dld_queue_thread.join(1)
        elif variables.counter_source == 'TDC_Raw':
            read_tdc_queue_thread.join(1)
    elif variables.counter_source == 'DRS':
        read_drs_queue_thread.join(1)

    if conf['tdc'] != "off":
        if variables.counter_source == 'TDC':
            variables.total_ions = len(variables.x)
        elif variables.counter_source == 'TDC_Raw':
            variables.total_ions = int(len(variables.channel) / 4)
    elif variables.counter_source == 'DRS':
        pass

    time.sleep(1)
    logger.info('Experiment is finished')

    # Check the length of arrays to be equal
    if variables.counter_source == 'TDC':
        if all(len(lst) == len(variables.x) for lst in [variables.x, variables.y,
                                                        variables.t, variables.dld_start_counter,
                                                        variables.main_v_dc_dld, variables.main_v_p_dld]):
            logger.warning('dld data have not same length')
    elif variables.counter_source == 'TDC_Raw':
        if all(len(lst) == len(variables.channel) for lst in [variables.channel, variables.time_data,
                                                              variables.tdc_start_counter,
                                                              variables.main_v_dc_tdc, variables.main_v_p_tdc]):
            logger.warning('tdc data have not same length')
    elif variables.counter_source == 'DRS':
        if all(len(lst) == len(variables.ch0_time) for lst in [variables.ch0_wave, variables.ch1_time,
                                                               variables.ch1_wave, variables.ch2_time,
                                                               variables.ch2_wave, variables.ch3_time,
                                                               variables.ch3_wave,
                                                               variables.main_v_dc_drs, variables.main_v_p_drs]):
            logger.warning('tdc data have not same length')

    logger.info('HDF5 file is created')
    variables.end_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

    # Save new value of experiment counter
    with open('./files/counter_oxcart.txt', 'w') as f:
        f.write(str(variables.counter + 1))
        logger.info('Experiment counter is increased')

    # Adding results of the experiment to the log file
    logger.info('Total number of Ions is: %s' % variables.total_ions)
    # send a Tweet
    if variables.tweet:
        message_tweet = 'The Experiment %s finished\n' \
                        'Total number of Ions is: %s' % (variables.hdf5_path,
                                                         variables.total_ions)
        tweet_send.tweet_send(message_tweet)
        logger.info('Tweet is sent')

    # send an email
    subject = 'Oxcart Experiment {} Report'.format(variables.hdf5_path)
    elapsed_time_temp = float("{:.3f}".format(variables.elapsed_time))
    message = 'The experiment was started at: {}\n' \
              'The experiment was ended at: {}\n' \
              'Experiment duration: {}\n' \
              'Total number of ions: {}\n'.format(variables.start_time,
                                                  variables.end_time, elapsed_time_temp, variables.total_ions)

    if len(variables.email) > 3:
        logger.info('Email is sent')
        email_send.send_email(variables.email, subject, message)

    # save data in hdf5 file
    hdf5_creator.hdf_creator_oxcart(time_counter, time_ex_s, time_ex_m, time_ex_h)

    # save setup parameters and run statistics in a txt file
    experiment_statistics.save_statistics_apt_oxcart()

    # Clear up all the variables and deinitialize devices
    experiment.clear_up(task_counter)
    logger.info('Variables and devices is cleared')
