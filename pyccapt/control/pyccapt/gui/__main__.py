"""
This is the main script is load the GUI base on the configuration file.
"""

import sys
import os
import threading
from PyQt5 import QtWidgets
# Serial ports and Camera libraries
import serial.tools.list_ports
from pypylon import pylon

# Local module and scripts
from pyccapt.control_tools import variables, read_files
from pyccapt.devices import initialize_devices
from pyccapt.devices.camera import Camera
from pyccapt.gui import gui_simple
from pyccapt.gui import gui_advance


def main():

    try:
        # load the Json file
        configFile = 'config.json'
        p = os.path.abspath(os.path.join(__file__, "../../../.."))
        os.chdir(p)
        conf = read_files.read_json_file(configFile)
    except Exception as e:
        print("The config.json was not found")
        print(e)

    if conf['mode'] == 'advance':

        # Initialize global experiment variables
        variables.init(conf)
        variables.log_path = p
        # Config the port for cryo
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
            except Exception as e:
                print('Can not initialize the Cryovac')
                print(e)

        if conf['gauges'] != "off":
            if conf['COM_PORT_gauge_mc'] == "off":
                print('The main chamber gauge is off')
            else:
                # Config the port for Main and Buffer vacuum gauges
                try:
                    initialize_devices.initialize_pfeiffer_gauges()
                except Exception as e:
                    print('Can not initialize the Pfeiffer gauges')
                    print(e)
            if conf['COM_PORT_gauge_bc'] == "off":
                print('The buffer chamber gauge is off')
            else:
                # Config the port for Buffer chamber vacuum gauges
                try:
                    initialize_devices.initialize_edwards_tic_buffer_chamber(conf)
                except Exception as e:
                    print('Can not initialize the buffer vacuum gauges')
                    print(e)
            if conf['COM_PORT_gauge_ll'] == "off":
                print('The load lock gauge is off')
            else:
                # Config the port for Load Lock vacuum gauges
                try:
                    initialize_devices.initialize_edwards_tic_load_lock(conf)
                except Exception as e:
                    print('Can not initialize the load lock gauges')
                    print(e)
        else:
            print('Gauges are off')

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

            except Exception as e:
                print('Can not initialize the Cameras')
                print(e)

        lock1 = threading.Lock()
        if conf['gauges'] != "off":
            # Thread for reading gauges
            gauges_thread = threading.Thread(target=initialize_devices.gauges_update,
                                             args=(conf, lock1, com_port_idx_cryovac))
            gauges_thread.setDaemon(True)
            gauges_thread.start()

        app = QtWidgets.QApplication(sys.argv)
        # get display resolution
        screen_resolution = app.desktop().screenGeometry()
        # width, height = screen_resolution.width(), screen_resolution.height()
        # print('Screen size is:(%s,%s)' % (width, height))
        OXCART = QtWidgets.QMainWindow()
        lock = threading.Lock()
        if conf['camera'] != "off":
            try:
                ui = gui_advance.UI_APT_A(camera.devices, camera.tlFactory, camera.cameras, camera.converter, lock, app,
                                      conf)
            except Exception as e:
                print('Can not initialize the cameras')
                print(e)
                conf['camera'] = "off"
                ui = gui_advance.UI_APT_A(None, None, None, None, lock, app, conf)
        else:
            ui = gui_advance.UI_APT_A(None, None, None, None, lock, app, conf)
        ui.setupUi(OXCART)
        OXCART.show()
        sys.exit(app.exec_())

    elif conf['mode'] == 'simple':

        # Initialize global experiment variables
        variables.init(conf)
        variables.log_path = p
        app = QtWidgets.QApplication(sys.argv)
        APT_Physic = QtWidgets.QMainWindow()
        lock = threading.Lock()
        ui = gui_simple.UI_APT_S(lock, app, conf)
        ui.setupUi(APT_Physic)
        APT_Physic.show()
        sys.exit(app.exec_())


if __name__ == "__main__":
    pass
    #main()
