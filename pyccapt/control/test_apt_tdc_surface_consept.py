import sys
import os

from defer import return_value
sys.path.append('/home/harsh/researchAssistant/pyccapt/pyccapt/control/pyccapt/apt')
path = '/home/harsh/researchAssistant/pyccapt/pyccapt/control/'
os.chdir(path)
import apt_tdc_surface_consept
import unittest
import pytest
import serial
from unittest.mock import patch, Mock, MagicMock



@pytest.fixture
def APT_ADVANCE_obj():
    queue_x = Mock()
    queue_y= Mock() 
    queue_t= Mock() 
    queue_dld_start_counter= Mock()
    queue_channel= Mock()
    queue_time_data= Mock()
    queue_tdc_start_counter= Mock()
    queue_ch0_time= Mock()
    queue_ch0_wave= Mock()
    queue_ch1_time= Mock() 
    queue_ch1_wave= Mock()
    queue_ch2_time= Mock()
    queue_ch2_wave= Mock() 
    queue_ch3_time= Mock() 
    queue_ch3_wave= Mock()
    lock1= Mock() 
    lock2= Mock()
    logger= Mock()
    conf= Mock()
    class_object = apt_tdc_surface_consept.APT_ADVANCE(queue_x, queue_y, queue_t, queue_dld_start_counter,
                 queue_channel, queue_time_data, queue_tdc_start_counter,
                 queue_ch0_time, queue_ch0_wave, queue_ch1_time, queue_ch1_wave,
                 queue_ch2_time, queue_ch2_wave, queue_ch3_time, queue_ch3_wave,
                 lock1, lock2, logger, conf)
    print(vars(class_object))
    return class_object


@patch.object(apt_tdc_surface_consept.APT_ADVANCE, "print_log")
@patch("serial.Serial")
def test_initialize_v_dc_port_not_open(serial_obj,mock,APT_ADVANCE_obj):
    serial_obj.return_value(None)
    APT_ADVANCE_obj.initialize_v_dc()
    mock.assert_called()
    #MagicMock(return_value=dummy_response)

