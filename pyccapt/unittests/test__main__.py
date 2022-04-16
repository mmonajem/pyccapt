import unittest
from unittest import main
from defer import return_value
import pytest
import io
import json
from unittest.mock import patch, Mock, MagicMock
import sys


sys.path.append("/home/harsh/researchAssistant/pyccapt")
sys.path.append("/home/harsh/researchAssistant/pyccapt/pyccapt")
import main



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

