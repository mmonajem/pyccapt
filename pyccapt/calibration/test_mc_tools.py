import pytest
from unittest.mock import patch, Mock, MagicMock
import sys
import os
sys.path.append('/home/harsh/researchAssistant/pyccapt/pyccapt/calibration/pyccapt/mc/')
#path = '/home/harsh/researchAssistant/pyccapt/pyccapt/calibration'
#os.chdir(path)
import mc_tools


def test_tof2mcSimple_check_return_type():
    import numpy as np
    t = 200
    t0 = 100
    V = 12
    xDet = 100
    yDet = 50
    flightPathLength = 20
    response = mc_tools.tof2mcSimple(t,t0,V,xDet,yDet,flightPathLength)
    assert isinstance(response,np.float64)


@patch.object(mc_tools.logger, "critical")
def test_tof2mcSimple_check_data_type_of_args(mock):
    import numpy as np
    t = "200" # String passed while the the function is expecting int/float
    t0 = 100
    V = 12
    xDet = 100
    yDet = 50
    flightPathLength = 20
    response = mc_tools.tof2mcSimple(t,t0,V,xDet,yDet,flightPathLength)
    mock.assert_called_with("Data type of the passed argument is incorrect")

def test_tof2mc_check_return_type():
    import numpy as np
    t = 200
    t0 = 100
    V = 12
    V_pulse = 12
    xDet = 100
    yDet = 50
    flightPathLength = 20
    response = mc_tools.tof2mc(t,t0,V,V_pulse,xDet,yDet,flightPathLength)
    assert isinstance(response,np.float64)


@patch.object(mc_tools.logger, "critical")
def test_tof2mc_check_data_type_of_args(mock):
    import numpy as np
    t = "200" # String passed while the the function is expecting int/float
    t0 = 100
    V = 12
    V_pulse = 12
    xDet = 100
    yDet = 50
    flightPathLength = 20
    response = mc_tools.tof2mc(t,t0,V,V_pulse,xDet,yDet,flightPathLength)
    mock.assert_called_with("Data type of the passed argument is incorrect")

@patch.object(mc_tools.logger, "critical")
def test_tof2mc_check_mode(mock):
    import numpy as np
    t = 200 
    t0 = 100
    V = 12
    V_pulse = 12
    xDet = 100
    yDet = 50
    flightPathLength = 20
    mode = "wrong_mode"
    response = mc_tools.tof2mc(t,t0,V,V_pulse,xDet,yDet,flightPathLength,mode)
    mock.assert_called_with("Enter correct mode type")