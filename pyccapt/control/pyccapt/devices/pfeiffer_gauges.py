"""
This module contains drivers for the following equipment from Pfeiffer
Vacuum:
* TPG 262 and TPG 261 Dual Gauge. Dual-Channel Measurement and Control
    Unit for Compact Gauges
"""

import time
import serial

# Code translations constants
MEASUREMENT_STATUS = {
    0: 'Measurement data okay',
    1: 'Underrange',
    2: 'Overrange',
    3: 'Sensor error',
    4: 'Sensor off (IKR, PKR, IMR, PBR)',
    5: 'No sensor (output: 5,2.0000E-2 [mbar])',
    6: 'Identification error'
}
GAUGE_IDS = {
    'TPR': 'Pirani Gauge or Pirani Capacitive gauge',
    'IKR9': 'Cold Cathode Gauge 10E-9 ',
    'IKR11': 'Cold Cathode Gauge 10E-11 ',
    'PKR': 'FullRange CC Gauge',
    'PBR': 'FullRange BA Gauge',
    'IMR': 'Pirani / High Pressure Gauge',
    'CMR': 'Linear gauge',
    'noSEn': 'no SEnsor',
    'noid': 'no identifier'
}
PRESSURE_UNITS = {0: 'mbar/bar', 1: 'Torr', 2: 'Pascal'}


class TPG26x(object):
    r"""Abstract class that implements the common driver for the TPG 261 and
    TPG 262 dual channel measurement and control unit. The driver implements
    the following 6 commands out the 39 in the specification:
    * PNR: Program number (firmware version)
    * PR[1,2]: Pressure measurement (measurement data) gauge [1, 2]
    * PRX: Pressure measurement (measurement data) gauge 1 and 2
    * TID: Transmitter identification (gauge identification)
    * UNI: Pressure unit
    * RST: RS232 test
    This class also contains the following class variables, for the specific
    characters that are used in the communication:
    :var ETX: End text (Ctrl-c), chr(3), \\x15
    :var CR: Carriage return, chr(13), \\r
    :var LF: Line feed, chr(10), \\n
    :var ENQ: Enquiry, chr(5), \\x05
    :var ACK: Acknowledge, chr(6), \\x06
    :var NAK: Negative acknowledge, chr(21), \\x15
    """

    ETX = chr(3)  # \x03
    CR = chr(13)
    LF = chr(10)
    ENQ = chr(5)  # \x05
    ACK = chr(6)  # \x06
    NAK = chr(21)  # \x15

    def __init__(self, port='/dev/ttyUSB0', baudrate=9600):
        """
        The constructor class method which initialize internal variables and
        serial connection

        Attributes:
            param port: The COM port to open. See the documentation for
                `pyserial <http://pyserial.sourceforge.net/>`_ for an explanation
                of the possible value. The default value is '/dev/ttyUSB0'.
                :type port: [str or int]
            baud-rate: Data transmission rate (9600, 19200, 38400 where 9600 is the default)
                :type baudrate: [int]
        """

        # The serial connection should be setup with the following parameters:
        # 1 start bit, 8 data bits, No parity bit, 1 stop bit, no hardware
        # handshake. These are all default for Serial and therefore not input
        # below
        self.serial = serial.Serial(port=port, baudrate=baudrate, timeout=1)

    def _cr_lf(self, string):
        """
        Pad carriage return and line feed to a string

        Attributes:
            string: String to pad [str]

        Returns:
            string : the padded string [string]
        """
        return string + self.CR + self.LF

    def _send_command(self, command):
        """
        Send a command and check if it is positively acknowledged

        Attributes:

            command: The command to be sent [str]

        Raises Exception:
            raises IOError: if the negative acknowledged or an unknown response
            is returned
        Returns:
            Does not return anything
        
        """
        # Write (execute command) through serial communication
        self.serial.write(self._cr_lf(command).encode())
        response = self.serial.readline().decode()
        if response == self._cr_lf(self.NAK):
            message = 'Serial communication returned negative acknowledge'
            raise IOError(message)
        elif response != self._cr_lf(self.ACK):
            message = 'Serial communication returned unknown response:\n{}'\
                ''.format(repr(response))
            raise IOError(message)

    def _get_data(self):
        """
        Get the data that is ready on the device

        Attributes:
            Does not accept any arguments

        Returns:
            data: raw data from serial communication line [str]
        """
        self.serial.write(self.ENQ.encode())
        data = self.serial.readline().decode()
        return data.rstrip(self.LF).rstrip(self.CR)

    def _clear_output_buffer(self):
        """
        Clear the output buffer
        """

        time.sleep(0.1)
        just_read = 'start value'
        out = ''
        while just_read != '':
            just_read = self.serial.read()
            out += just_read
        return out

    def program_number(self):
        """
        Return the firmware version

        Attributes:
            Does not accept any arguments

        Returns:
            :the firmware version [str]
        """

        self._send_command('PNR')
        return self._get_data()

    def pressure_gauge(self, gauge=1):
        """
        Return the pressure measured by gauge X

        Attributes:
            gauge: The gauge number, 1 or 2 [int]
        Raises Exception:
            :raises ValueError: if gauge is not 1 or 2
        
        Returns:
            :a tuple the value of pressure along with status code and message
                (value, (status_code, status_message)) [tuple]
        """

        if gauge not in [1, 2]:
            message = 'The input gauge number can only be 1 or 2'
            raise ValueError(message)
        self._send_command('PR' + str(gauge))
        reply = self._get_data()
        status_code = int(reply.split(',')[0])
        value = float(reply.split(',')[1])
        return value, (status_code, MEASUREMENT_STATUS[status_code])

    def pressure_gauges(self):
        """
        Return the pressures measured by the gauges

        Attributes:
            Does not accept any arguments

        Returns:
            :(value1, (status_code1, status_message1), value2,
                (status_code2, status_message2)) [tuple]
        """
        self._send_command('PRX')
        reply = self._get_data()
        # The reply is on the form: x,sx.xxxxEsxx,y,sy.yyyyEsyy
        status_code1 = int(reply.split(',')[0])
        value1 = float(reply.split(',')[1])
        status_code2 = int(reply.split(',')[2])
        value2 = float(reply.split(',')[3])
        return (value1, (status_code1, MEASUREMENT_STATUS[status_code1]),
                value2, (status_code2, MEASUREMENT_STATUS[status_code2]))

    def gauge_identification(self):
        """
        Return the gauge identification

        Attributes:
            Does not accept any arguments

        Returns:
            :(id_code_1, id_1, id_code_2, id_2) [tuples]

        """
        self._send_command('TID')
        reply = self._get_data()
        id1, id2 = reply.split(',')
        return id1, GAUGE_IDS[id1], id2, GAUGE_IDS[id2]

    def pressure_unit(self):
        """
        Return the pressure unit

        Attributes:
            Does not accept any arguments

        Returns:
            :the pressure unit [str]
        """

        self._send_command('UNI')
        unit_code = int(self._get_data())
        return PRESSURE_UNITS[unit_code]

    def rs232_communication_test(self):
        """
        This function tests the RS232 communication.
        Attributes:

            Does not accept any arguments

        Returns:
            :the status of the communication test [boolean]
        """

        # reset serial communication
        self._send_command('RST')
        self.serial.write(self.ENQ)
        # Clear output buffer
        self._clear_output_buffer()
        test_string_out = ''
        # Test serial communication
        for char in 'a1':
            self.serial.write(char)
            test_string_out += self._get_data().rstrip(self.ENQ)
        self._send_command(self.ETX)
        return test_string_out == 'a1'


class TPG362(TPG26x):
    """Driver for the TPG 261 dual channel measurement and control unit"""

    def __init__(self, port='/dev/ttyUSB0', baudrate=9600):
        """
        This construction method initializes internal variables and serial connection.

        Attributes:

            port: The COM port to open. See the documentation for
                `pyserial <http://pyserial.sourceforge.net/>`_ for an explanation
                of the possible value. The default value is '/dev/ttyUSB0'. [str or int]

            baud-rate: data transmission rate (9600, 19200, 38400 where 9600 is the default) [int]
        """
        super(TPG362, self).__init__(port=port, baudrate=baudrate)






