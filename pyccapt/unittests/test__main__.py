import unittest
from unittest import main
from defer import return_value
from numpy import empty
import pytest
import io
import json
from unittest.mock import patch, Mock, MagicMock
import sys
from pypylon import pylon
from PyQt5 import QtWidgets

tlFactory = pylon.TlFactory.GetInstance()
sys.path.append("/home/harsh/researchAssistant/pyccapt")
sys.path.append("/home/harsh/researchAssistant/pyccapt/pyccapt")
import main
from devices import initialize_devices
from gui import gui_advance
from tools import variables

class Camera:
     def __init__(self, devices, tlFactory, cameras, converter):
        """
        Constructor function which intializes and setups all variables
        and parameter for the class.
        """
        self.devices = devices
        self.tlFactory = tlFactory
        self.cameras = cameras
        self.converter = converter


config =  {
        "mode": "advance",
        "visualization": "tof",
        "tdc": "on",
        "camera": "off",
        "pump": "on",
        "gates": "off",
        "v_dc": "off",
        "v_p": "on",
        "signal_generator": "on",
        "cryo": "on",
        "gauges": "on",
        "edge_counter": "on",
        "COM_PORT_gates": "Dev2/port0/",
        "COM_PORT_cryo": 3,
        "COM_PORT_V_dc": 4,
        "COM_PORT_V_p": "ASRL4::INSTR",
        "COM_PORT_gauge_mc": "COM5",
        "COM_PORT_gauge_bc": "COM2",
        "COM_PORT_gauge_ll": "COM1",
        "COM_PORT_signal_generator": "USB0::0xF4EC::0x1101::SDG6XBAD2R0601::INSTR",
        "COM_PORT_NI_counter": "Dev1/ctr0"
    }


@patch.object(main, "print_log")
def test_load_json_file_file_not_found(mock):
    #import main 
    config_file = 'wrong_config.json'
    
    config_response = main.load_json_file(config_file)
    mock.assert_called_with("Config file not found")


def test_load_json_file_check_valid_dict():
    import main 
    config_file = 'config.json'
    config_response = main.load_json_file(config_file)
    test_response = {
        "mode": "advance",
        "visualization": "tof",
        "tdc": "on",
        "camera": "off",
        "pump": "on",
        "gates": "off",
        "v_dc": "off",
        "v_p": "on",
        "signal_generator": "on",
        "cryo": "on",
        "gauges": "on",
        "edge_counter": "on",
        "COM_PORT_gates": "Dev2/port0/",
        "COM_PORT_cryo": 3,
        "COM_PORT_V_dc": 4,
        "COM_PORT_V_p": "ASRL4::INSTR",
        "COM_PORT_gauge_mc": "COM5",
        "COM_PORT_gauge_bc": "COM2",
        "COM_PORT_gauge_ll": "COM1",
        "COM_PORT_signal_generator": "USB0::0xF4EC::0x1101::SDG6XBAD2R0601::INSTR",
        "COM_PORT_NI_counter": "Dev1/ctr0"
    }
    assert type(test_response) == type(config_response)

@patch.object(main, "print_log")
def test_initialize_gauges_update_thread_key_error(mock):
    import threading
    dummy_response = {
        "mode": "advance",
        "visualization": "tof",
        "tdc": "on",
        "camera": "off"
    }
    threading.Thread = MagicMock()
    conf = MagicMock(return_value=dummy_response)
    lock = Mock()
    com_port_idx_cryovac = 2
    main.initialize_gauges_update_thread(conf,lock,com_port_idx_cryovac)
    mock.assert_called_with("Key not found")

@patch("threading.Thread")
def test_initialize_gauges_update_thread_gauges_equal_on(mock):
    import threading
    conf = {
        "mode": "advance",
        "visualization": "tof",
        "tdc": "on",
        "gauges":"on",
        "camera": "off"
    }
    lock = MagicMock()
    com_port_idx_cryovac = 2
    main.initialize_gauges_update_thread(conf,lock,com_port_idx_cryovac)
    mock.assert_called()

@patch("devices.initialize_devices.initialize_pfeiffer_gauges")
def test_check_gauges_com_port_mc_port_on(mock):
    conf = {
        "mode": "advance",
        "visualization": "tof",
        "tdc": "on",
        "gauges":"on",
        "COM_PORT_gauge_mc":"on",
        "camera": "off"
    }
    main.check_gauges_com_port_mc(conf)
    mock.assert_called()

@patch("devices.initialize_devices.initialize_pfeiffer_gauges", return_value=-1)
@patch.object(main, "print_log")
def test_check_gauges_com_port_mc_port_on_exception(mock_main,mock):
    conf = {
        "mode": "advance",
        "visualization": "tof",
        "tdc": "on",
        "gauges":"on",
        "COM_PORT_gauge_mc":"on",
        "camera": "off"
    }
    main.check_gauges_com_port_mc(conf)
    mock_main.assert_called_with("Can not initialize the Pfeiffer gauges")

@patch("devices.initialize_devices.initialize_edwards_tic_buffer_chamber")
def test_check_gauges_com_port_bc_port_on(mock):
    conf = {
        "mode": "advance",
        "visualization": "tof",
        "tdc": "on",
        "gauges":"on",
        "COM_PORT_gauge_bc":"on",
        "camera": "off"
    }
    main.check_gauges_com_port_bc(conf)
    mock.assert_called()

@patch("devices.initialize_devices.initialize_edwards_tic_buffer_chamber", return_value=-1)
@patch.object(main, "print_log")
def test_check_gauges_com_port_bc_port_on_exception(mock_main,mock):
    conf = {
        "mode": "advance",
        "visualization": "tof",
        "tdc": "on",
        "gauges":"on",
        "COM_PORT_gauge_bc":"on",
        "camera": "off"
    }
    main.check_gauges_com_port_bc(conf)
    mock_main.assert_called_with("Can not initialize the buffer vacuum gauges")

@patch("devices.initialize_devices.initialize_edwards_tic_load_lock")
def test_check_gauges_com_port_ll_port_on(mock):
    conf = {
        "mode": "advance",
        "visualization": "tof",
        "tdc": "on",
        "gauges":"on",
        "COM_PORT_gauge_ll":"on",
        "camera": "off"
    }
    main.check_gauges_com_port_ll(conf)
    mock.assert_called()

@patch("devices.initialize_devices.initialize_edwards_tic_load_lock", return_value=-1)
@patch.object(main, "print_log")
def test_check_gauges_com_port_ll_port_on_exception(mock_main,mock):
    conf = {
        "mode": "advance",
        "visualization": "tof",
        "tdc": "on",
        "gauges":"on",
        "COM_PORT_gauge_ll":"on",
        "camera": "off"
    }
    main.check_gauges_com_port_ll(conf)
    mock_main.assert_called_with("Can not initialize the load lock gauges")

@patch.object(main,"check_gauges_com_port_mc")
@patch.object(main,"check_gauges_com_port_bc")
@patch.object(main,"check_gauges_com_port_ll")
def test_check_gauges_gauges_equal_on(mock_ll,mock_bc,mock_mc):
    conf = {
        "mode": "advance",
        "visualization": "tof",
        "tdc": "on",
        "gauges":"on",
        "COM_PORT_gauge_mc":"on",
        "COM_PORT_gauge_bc":"on",
        "COM_PORT_gauge_ll":"on",
        "camera": "off"
    }
    main.check_gauges(conf)
    mock_ll.assert_called()
    mock_bc.assert_called()
    mock_mc.assert_called()


@pytest.mark.xfail(raises=pylon.RuntimeException)
def test_check_camera_zero_device_exception():
    conf = {
        "mode": "advance",
        "visualization": "tof",
        "tdc": "on",
        "cryo":"on",
        "COM_PORT_gauge_mc":"on",
        "COM_PORT_gauge_bc":"on",
        "COM_PORT_gauge_ll":"on",
        "camera": "on"
    }
    tlFactory = pylon.TlFactory.GetInstance()
    empty_tuple = ()
    tlFactory.EnumerateDevices  = MagicMock(return_value = empty_tuple)
    main.check_camera(conf)
'''
#@patch("main.tlFactory.EnumerateDevices",return_value=('40063823','40063423'))
@patch("threading.Thread")
def test_check_camera_zero_device_successful_spawn(mock):
    import threading
    conf = {
        "mode": "advance",
        "visualization": "tof",
        "tdc": "on",
        "cryo":"on",
        "COM_PORT_gauge_mc":"on",
        "COM_PORT_gauge_bc":"on",
        "COM_PORT_gauge_ll":"on",
        "camera": "on"
    }
    tlFactory = pylon.TlFactory.GetInstance()
    tlFactory.EnumerateDevices  = Mock(return_value = ('40063823','40063423'))
    Camera = MagicMock()
    threading.Lock = MagicMock()
    main.check_camera(conf)
    mock.assert_called()

'''
@patch("main.return_chosen_port",return_value='COM1')
def test_check_cryo_assert_port_not_open(mock):
    import serial
    from tools import variables
    from devices import initialize_devices
    conf = {
        "mode": "advance",
        "visualization": "tof",
        "tdc": "on",
        "cryo":"on",
        "COM_PORT_gauge_mc":"on",
        "COM_PORT_gauge_bc":"on",
        "COM_PORT_gauge_ll":"on",
        "camera": "off"
    }
    
    response  = main.check_cryo(conf)
    assert response == None

@patch("main.return_chosen_port",return_value='COM1')
@patch.object(main,"print_log")
def test_check_cryo_assert_cryo_off(mock,mock_port_func):
    import serial
    from tools import variables
    from devices import initialize_devices
    conf = {
        "mode": "advance",
        "visualization": "tof",
        "tdc": "on",
        "cryo":"off",
        "COM_PORT_gauge_mc":"on",
        "COM_PORT_gauge_bc":"on",
        "COM_PORT_gauge_ll":"on",
        "camera": "off"
    }
    
    response  = main.check_cryo(conf)
    assert response == None
    mock.assert_called_with("The cryo temperature monitoring is off")

@patch.object(variables,"init")
@patch.object(main,"check_cryo")
@patch.object(main,"check_gauges")
@patch.object(main,"check_camera")
@patch.object(main,"launch_gui")
def test_check_mode_advance(mock_gui,mock_camera,mock_gauges,mock_cryo,mock_variable):
    conf = {
        "mode": "advance",
        "visualization": "tof",
        "tdc": "on",
        "cryo":"off",
        "COM_PORT_gauge_mc":"on",
        "COM_PORT_gauge_bc":"on",
        "COM_PORT_gauge_ll":"on",
        "camera": "off"
    }
    main.check_mode(conf)
    mock_gui.assert_called()
    mock_camera.assert_called()
    mock_gauges.assert_called()
    mock_cryo.assert_called()
    mock_variable.assert_called()

