import sys
import os
print(os.getcwd())
sys.path.append('/home/harsh/researchAssistant/pyccapt/pyccapt/control/pyccapt/apt')
path = '/home/harsh/researchAssistant/pyccapt/pyccapt/control/'
os.chdir(path)
print(os.getcwd())
import apt_tdc_surface_consept
import unittest
import pytest
from unittest.mock import patch, Mock, MagicMock

#@pytest.fixture
def APT_ADVANCE_Class():
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
    print(class_object)
    return class_object


#def test_initialize_v_dc_port_not_open(class_object):
#    class_object = apt_tdc_surface_consept.APT_ADVANCE()
#    serial.Serial = MagicMock()
#    MagicMock(return_value=dummy_response)

a = APT_ADVANCE_Class()
print(a)