"""
This is the main script is load the GUI base on the configuration file.
@author: Mehrpad Monajem <mehrpad.monajem@fau.de>
"""

from copy import error
from logging import raiseExceptions
import sys
import os
import threading
from PyQt5 import QtWidgets
# Serial ports and Camera libraries
import serial.tools.list_ports
#from pypylon import pylon

# Local module and scripts
from tools import variables
from tools import read_files
from devices.camera import Camera
from devices import initialize_devices
from gui import gui_simple
from gui import gui_advance

from tools.module_dir import MODULE_DIR


def print_log(string_to_be_printed):
    print(string_to_be_printed)


def load_json_file(configFile = None):
    try:      
        if configFile == None:
            configFile = 'config.json'  
        os.chdir(os.path.split(MODULE_DIR)[0])
        conf = read_files.read_json_file(configFile)
        return conf
    except FileNotFoundError as e:
        print_log("Config file not found")
        print(e)
    except Exception as e:
        print("Error in load_json_file",e)

def initialize_gauges_update_thread(conf,lock1,com_port_idx_cryovac):
    try:
        if "gauges" not in conf:
            raise KeyError
        if conf['gauges'] != "off":
            # Thread for reading gauges
            gauges_thread = threading.Thread(target=initialize_devices.gauges_update,
                                                args=(conf, lock1, com_port_idx_cryovac))
            gauges_thread.setDaemon(True)
            gauges_thread.start()
    except KeyError as error:
        print_log("Key not found")
        
    
def check_gauges_com_port_mc(conf):
    try:
        
        if conf['COM_PORT_gauge_mc'] == "off":
                print_log('The main chamber gauge is off')
        else:
                # Config the port for Main and Buffer vacuum gauges
                try:
                    response = initialize_devices.initialize_pfeiffer_gauges()
                    if response == -1:
                        raise Exception
                except Exception as e:
                    print_log('Can not initialize the Pfeiffer gauges')
                    print(e)
    except KeyError as error:
        print("Key not found",error)
        
def check_gauges_com_port_bc(conf):

    try:
        if conf['COM_PORT_gauge_bc'] == "off":
            print('The buffer chamber gauge is off')
        else:
            # Config the port for Buffer chamber vacuum gauges
            try:
                response  = initialize_devices.initialize_edwards_tic_buffer_chamber(conf)
                if response == -1:
                    raise Exception
            except Exception as e:
                print_log('Can not initialize the buffer vacuum gauges')
                print(e)
    except KeyError as error:
        print("Key not found -> ",error)

def check_gauges_com_port_ll(conf):
    try:

        if conf['COM_PORT_gauge_ll'] == "off":
                print('The load lock gauge is off')
        else:
            # Config the port for Load Lock vacuum gauges
            try:
                response = initialize_devices.initialize_edwards_tic_load_lock(conf)
                if response == -1:
                    raise Exception
            except Exception as e:
                print_log('Can not initialize the load lock gauges')
                print(e)
    except KeyError as error:
        print("Key not found",error)

def check_gauges(conf):

    try:
        if conf['gauges'] != "off":
            check_gauges_com_port_mc(conf)
            check_gauges_com_port_bc(conf)
            check_gauges_com_port_ll(conf)
        else:
            print('Gauges are off')
    except KeyError as error:
        print("Key not found",error)
        

def check_camera(conf):
    if conf['camera'] == "off":
            print('The camera is off')
    else:
        # Cameras thread
        try:
            # Limits the amount of cameras used for grabbing.
            # The bandwidth used by a FireWire camera device can be limited by adjusting the packet size.
            maxCamerasToUse = 2
            # The exit code of the sample application.
            exitCode = 0
            # Get the transport layer factory.
            tlFactory = pylon.TlFactory.GetInstance()
            # Get all attached devices and exit application if no device is found.
            devices = tlFactory.EnumerateDevices()

            if len(devices) == 0:
                raise pylon.RuntimeException("No camera present.")

            # Create an array of instant cameras for the found devices and avoid exceeding a maximum number of devices.
            cameras = pylon.InstantCameraArray(min(len(devices), maxCamerasToUse))

            # Create and attach all Pylon Devices.
            for i, cam in enumerate(cameras):
                cam.Attach(tlFactory.CreateDevice(devices[i]))
            converter = pylon.ImageFormatConverter()

            # converting to opencv bgr format
            converter.OutputPixelFormat = pylon.PixelType_BGR8packed
            converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

            camera = Camera(devices, tlFactory, cameras, converter)

            # Thread for reading cameras
            lock2 = threading.Lock()
            camera_thread = threading.Thread(target=camera.update_cameras, args=(lock2,))
            camera_thread.setDaemon(True)
            camera_thread.start()
            return camera
        except Exception as e:
            print('Can not initialize the Cameras')
            print(e)

def check_cryo(conf):
    if conf['cryo'] == "off":
            print('The cryo temperature monitoring is off')
            com_port_idx_cryovac = None
    else:
        # Cryovac initialized
        try:
            com_port_idx_cryovac = serial.Serial(
                port=initialize_devices.com_ports[variables.COM_PORT_cryo].device,  # chosen COM port
                baudrate=9600,  # 115200
                bytesize=serial.EIGHTBITS,  # 8
                parity=serial.PARITY_NONE,  # N
                stopbits=serial.STOPBITS_ONE  # 1
            )
            initialize_devices.initialize_cryovac(com_port_idx_cryovac)
            return com_port_idx_cryovac
        except Exception as e:
            print('Can not initialize the Cryovac')
            print(e)

def launch_gui(conf,camera):
    app = QtWidgets.QApplication(sys.argv)
    # get display resolution
    screen_resolution = app.desktop().screenGeometry()
    # width, height = screen_resolution.width(), screen_resolution.height()
    # print('Screen size is:(%s,%s)' % (width, height))
    OXCART = QtWidgets.QMainWindow()
    lock = threading.Lock()
    if conf['camera'] != "off":
        ui = gui_advance.UI_APT_A(camera.devices, camera.tlFactory, camera.cameras, camera.converter, lock, app,
                                    conf)
    else:
        ui = gui_advance.UI_APT_A(None, None, None, None, lock, app, conf)
    ui.setupUi(OXCART)
    OXCART.show()
    sys.exit(app.exec_())

def check_mode(conf):

    if conf['mode'] == 'advance':
        # Initialize global experiment variables
        variables.init(conf)
        # Config the port for cryo
        com_port_idx_cryovac = check_cryo(conf)
        check_gauges(conf)
        camera  = check_camera(conf)
        lock1 = threading.Lock()
        initialize_gauges_update_thread(conf,lock1,com_port_idx_cryovac)
        launch_gui(conf,camera)

    elif conf['mode'] == 'simple':

        # Initialize global experiment variables
        variables.init(conf)

        app = QtWidgets.QApplication(sys.argv)
        APT_Physic = QtWidgets.QMainWindow()
        lock = threading.Lock()
        ui = gui_simple.UI_APT_S(lock, app, conf)
        ui.setupUi(APT_Physic)
        APT_Physic.show()
        sys.exit(app.exec_())

def main():
    conf = load_json_file()
    check_mode(conf)

if __name__ == "__main__":
    main()
