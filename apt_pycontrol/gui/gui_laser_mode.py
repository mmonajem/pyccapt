"""
This is the main script of main GUI of the simple Atom Probe control GUI.
@author: Mehrpad Monajem <mehrpad.monajem@fau.de>
"""

import numpy as np
import threading
import datetime
import os
# PyQt and PyQtgraph libraries
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QScreen
import pyqtgraph as pg
import pyqtgraph.exporters

# Local module and scripts
from apt_pycontrol.apt import apt_laser
from apt_pycontrol.tools import variables
from apt_pycontrol.tools import tof2mc_simple
from apt_pycontrol.devices import initialize_devices
from apt_pycontrol.tools.module_dir import MODULE_DIR

class UI_APT_L(object):
    """
    The GUI class of laser mode (APT laser mode)
    """
    def __init__(self, lock, app, conf):
        self.lock = lock # Lock for thread ...
        self.app = app
        self.conf = conf

    def setupUi(self, APT_Physic):
        APT_Physic.setObjectName("APT_Physic")
        APT_Physic.resize(1675, 1383)
        self.centralwidget = QtWidgets.QWidget(APT_Physic)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label_43 = QtWidgets.QLabel(self.centralwidget)
        self.label_43.setObjectName("label_43")
        self.gridLayout_3.addWidget(self.label_43, 0, 0, 1, 1)
        self.ex_user = QtWidgets.QLineEdit(self.centralwidget)
        self.ex_user.setStyleSheet("QLineEdit{\n"
"background: rgb(223,223,233)\n"
"}")
        self.ex_user.setObjectName("ex_user")
        self.gridLayout_3.addWidget(self.ex_user, 0, 2, 1, 1)
        self.label_21 = QtWidgets.QLabel(self.centralwidget)
        self.label_21.setObjectName("label_21")
        self.gridLayout_3.addWidget(self.label_21, 1, 0, 1, 1)
        self.ex_name = QtWidgets.QLineEdit(self.centralwidget)
        self.ex_name.setStyleSheet("QLineEdit{\n"
"background: rgb(223,223,233)\n"
"}")
        self.ex_name.setObjectName("ex_name")
        self.gridLayout_3.addWidget(self.ex_name, 1, 2, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setObjectName("label_2")
        self.gridLayout_3.addWidget(self.label_2, 2, 0, 1, 2)
        self.ex_time = QtWidgets.QLineEdit(self.centralwidget)
        self.ex_time.setStyleSheet("QLineEdit{\n"
"background: rgb(223,223,233)\n"
"}")
        self.ex_time.setObjectName("ex_time")
        self.gridLayout_3.addWidget(self.ex_time, 2, 2, 1, 1)
        self.criteria_time = QtWidgets.QCheckBox(self.centralwidget)
        font = QtGui.QFont()
        font.setItalic(False)
        self.criteria_time.setFont(font)
        self.criteria_time.setMouseTracking(True)
        self.criteria_time.setStyleSheet("QCheckBox{\n"
"background: rgb(223,223,233)\n"
"}")
        self.criteria_time.setText("")
        self.criteria_time.setChecked(True)
        self.criteria_time.setObjectName("criteria_time")
        self.gridLayout_3.addWidget(self.criteria_time, 2, 3, 1, 1)
        self.label_41 = QtWidgets.QLabel(self.centralwidget)
        self.label_41.setObjectName("label_41")
        self.gridLayout_3.addWidget(self.label_41, 3, 0, 1, 2)
        self.max_ions = QtWidgets.QLineEdit(self.centralwidget)
        self.max_ions.setStyleSheet("QLineEdit{\n"
"background: rgb(223,223,233)\n"
"}")
        self.max_ions.setObjectName("max_ions")
        self.gridLayout_3.addWidget(self.max_ions, 3, 2, 1, 1)
        self.criteria_ions = QtWidgets.QCheckBox(self.centralwidget)
        font = QtGui.QFont()
        font.setItalic(False)
        self.criteria_ions.setFont(font)
        self.criteria_ions.setMouseTracking(True)
        self.criteria_ions.setStyleSheet("QCheckBox{\n"
"background: rgb(223,223,233)\n"
"}")
        self.criteria_ions.setText("")
        self.criteria_ions.setChecked(True)
        self.criteria_ions.setObjectName("criteria_ions")
        self.gridLayout_3.addWidget(self.criteria_ions, 3, 3, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setObjectName("label_3")
        self.gridLayout_3.addWidget(self.label_3, 4, 0, 1, 2)
        self.ex_freq = QtWidgets.QLineEdit(self.centralwidget)
        self.ex_freq.setStyleSheet("QLineEdit{\n"
"background: rgb(223,223,233)\n"
"}")
        self.ex_freq.setObjectName("ex_freq")
        self.gridLayout_3.addWidget(self.ex_freq, 4, 2, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setObjectName("label_4")
        self.gridLayout_3.addWidget(self.label_4, 5, 0, 1, 2)
        self.vdc_min = QtWidgets.QLineEdit(self.centralwidget)
        self.vdc_min.setStyleSheet("QLineEdit{\n"
"background: rgb(223,223,233)\n"
"}")
        self.vdc_min.setObjectName("vdc_min")
        self.gridLayout_3.addWidget(self.vdc_min, 5, 2, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setObjectName("label_5")
        self.gridLayout_3.addWidget(self.label_5, 6, 0, 1, 2)
        self.vdc_max = QtWidgets.QLineEdit(self.centralwidget)
        self.vdc_max.setStyleSheet("QLineEdit{\n"
"background: rgb(223,223,233)\n"
"}")
        self.vdc_max.setObjectName("vdc_max")
        self.gridLayout_3.addWidget(self.vdc_max, 6, 2, 1, 1)
        self.criteria_vdc = QtWidgets.QCheckBox(self.centralwidget)
        font = QtGui.QFont()
        font.setItalic(False)
        self.criteria_vdc.setFont(font)
        self.criteria_vdc.setMouseTracking(True)
        self.criteria_vdc.setStyleSheet("QCheckBox{\n"
"background: rgb(223,223,233)\n"
"}")
        self.criteria_vdc.setText("")
        self.criteria_vdc.setChecked(True)
        self.criteria_vdc.setObjectName("criteria_vdc")
        self.gridLayout_3.addWidget(self.criteria_vdc, 6, 3, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        self.label_6.setObjectName("label_6")
        self.gridLayout_3.addWidget(self.label_6, 7, 0, 1, 1)
        self.vdc_steps_up = QtWidgets.QLineEdit(self.centralwidget)
        self.vdc_steps_up.setStyleSheet("QLineEdit{\n"
"background: rgb(223,223,233)\n"
"}")
        self.vdc_steps_up.setObjectName("vdc_steps_up")
        self.gridLayout_3.addWidget(self.vdc_steps_up, 7, 2, 1, 1)
        self.label_28 = QtWidgets.QLabel(self.centralwidget)
        self.label_28.setObjectName("label_28")
        self.gridLayout_3.addWidget(self.label_28, 8, 0, 1, 1)
        self.vdc_steps_down = QtWidgets.QLineEdit(self.centralwidget)
        self.vdc_steps_down.setStyleSheet("QLineEdit{\n"
"background: rgb(223,223,233)\n"
"}")
        self.vdc_steps_down.setObjectName("vdc_steps_down")
        self.gridLayout_3.addWidget(self.vdc_steps_down, 8, 2, 1, 1)
        self.label_20 = QtWidgets.QLabel(self.centralwidget)
        self.label_20.setObjectName("label_20")
        self.gridLayout_3.addWidget(self.label_20, 9, 0, 1, 1)
        self.cycle_avg = QtWidgets.QLineEdit(self.centralwidget)
        self.cycle_avg.setStyleSheet("QLineEdit{\n"
"background: rgb(223,223,233)\n"
"}")
        self.cycle_avg.setObjectName("cycle_avg")
        self.gridLayout_3.addWidget(self.cycle_avg, 9, 2, 1, 1)
        self.label_25 = QtWidgets.QLabel(self.centralwidget)
        self.label_25.setObjectName("label_25")
        self.gridLayout_3.addWidget(self.label_25, 10, 0, 1, 1)
        self.pulse_fraction = QtWidgets.QLineEdit(self.centralwidget)
        self.pulse_fraction.setStyleSheet("QLineEdit{\n"
"background: rgb(223,223,233)\n"
"}")
        self.pulse_fraction.setObjectName("pulse_fraction")
        self.gridLayout_3.addWidget(self.pulse_fraction, 10, 2, 1, 1)
        self.label_23 = QtWidgets.QLabel(self.centralwidget)
        self.label_23.setObjectName("label_23")
        self.gridLayout_3.addWidget(self.label_23, 11, 0, 1, 2)
        self.pulse_frequency = QtWidgets.QLineEdit(self.centralwidget)
        self.pulse_frequency.setStyleSheet("QLineEdit{\n"
"background: rgb(223,223,233)\n"
"}")
        self.pulse_frequency.setObjectName("pulse_frequency")
        self.gridLayout_3.addWidget(self.pulse_frequency, 11, 2, 1, 1)
        self.label_17 = QtWidgets.QLabel(self.centralwidget)
        self.label_17.setObjectName("label_17")
        self.gridLayout_3.addWidget(self.label_17, 12, 0, 1, 2)
        self.detection_rate_init = QtWidgets.QLineEdit(self.centralwidget)
        self.detection_rate_init.setStyleSheet("QLineEdit{\n"
"background: rgb(223,223,233)\n"
"}")
        self.detection_rate_init.setObjectName("detection_rate_init")
        self.gridLayout_3.addWidget(self.detection_rate_init, 12, 2, 1, 1)
        self.label_22 = QtWidgets.QLabel(self.centralwidget)
        self.label_22.setObjectName("label_22")
        self.gridLayout_3.addWidget(self.label_22, 13, 0, 1, 1)
        self.doubleSpinBox = QtWidgets.QDoubleSpinBox(self.centralwidget)
        self.doubleSpinBox.setStyleSheet("QDoubleSpinBox{\n"
"background: rgb(223,223,233)\n"
"}")
        self.doubleSpinBox.setObjectName("doubleSpinBox")
        self.gridLayout_3.addWidget(self.doubleSpinBox, 13, 1, 1, 1)
        self.hit_displayed = QtWidgets.QLineEdit(self.centralwidget)
        self.hit_displayed.setStyleSheet("QLineEdit{\n"
"background: rgb(223,223,233)\n"
"}")
        self.hit_displayed.setObjectName("hit_displayed")
        self.gridLayout_3.addWidget(self.hit_displayed, 13, 2, 1, 1)
        self.label_26 = QtWidgets.QLabel(self.centralwidget)
        self.label_26.setObjectName("label_26")
        self.gridLayout_3.addWidget(self.label_26, 14, 0, 1, 1)
        self.email = QtWidgets.QLineEdit(self.centralwidget)
        self.email.setStyleSheet("QLineEdit{\n"
"background: rgb(223,223,233)\n"
"}")
        self.email.setText("")
        self.email.setObjectName("email")
        self.gridLayout_3.addWidget(self.email, 14, 2, 1, 1)
        self.label_42 = QtWidgets.QLabel(self.centralwidget)
        self.label_42.setObjectName("label_42")
        self.gridLayout_3.addWidget(self.label_42, 15, 0, 1, 1)
        self.counter_source = QtWidgets.QComboBox(self.centralwidget)
        self.counter_source.setObjectName("counter_source")
        self.counter_source.addItem("")
        self.gridLayout_3.addWidget(self.counter_source, 15, 2, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout_3)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout_2.addItem(spacerItem)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label_11 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_11.setFont(font)
        self.label_11.setObjectName("label_11")
        self.gridLayout.addWidget(self.label_11, 0, 0, 1, 1)
        self.speciemen_voltage = QtWidgets.QLineEdit(self.centralwidget)
        self.speciemen_voltage.setStyleSheet("QLineEdit{\n"
"background: rgb(223,223,233)\n"
"}")
        self.speciemen_voltage.setText("")
        self.speciemen_voltage.setObjectName("speciemen_voltage")
        self.gridLayout.addWidget(self.speciemen_voltage, 3, 1, 1, 1)
        self.elapsed_time = QtWidgets.QLineEdit(self.centralwidget)
        self.elapsed_time.setStyleSheet("QLineEdit{\n"
"background: rgb(223,223,233)\n"
"}")
        self.elapsed_time.setText("")
        self.elapsed_time.setObjectName("elapsed_time")
        self.gridLayout.addWidget(self.elapsed_time, 1, 1, 1, 1)
        self.label_13 = QtWidgets.QLabel(self.centralwidget)
        self.label_13.setObjectName("label_13")
        self.gridLayout.addWidget(self.label_13, 2, 0, 1, 1)
        self.label_12 = QtWidgets.QLabel(self.centralwidget)
        self.label_12.setObjectName("label_12")
        self.gridLayout.addWidget(self.label_12, 1, 0, 1, 1)
        self.label_14 = QtWidgets.QLabel(self.centralwidget)
        self.label_14.setObjectName("label_14")
        self.gridLayout.addWidget(self.label_14, 3, 0, 1, 1)
        self.total_ions = QtWidgets.QLineEdit(self.centralwidget)
        self.total_ions.setStyleSheet("QLineEdit{\n"
"background: rgb(223,223,233)\n"
"}")
        self.total_ions.setText("")
        self.total_ions.setObjectName("total_ions")
        self.gridLayout.addWidget(self.total_ions, 2, 1, 1, 1)
        self.label_15 = QtWidgets.QLabel(self.centralwidget)
        self.label_15.setObjectName("label_15")
        self.gridLayout.addWidget(self.label_15, 4, 0, 1, 1)
        self.detection_rate = QtWidgets.QLineEdit(self.centralwidget)
        self.detection_rate.setStyleSheet("QLineEdit{\n"
"background: rgb(223,223,233)\n"
"}")
        self.detection_rate.setText("")
        self.detection_rate.setObjectName("detection_rate")
        self.gridLayout.addWidget(self.detection_rate, 4, 1, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 1, 2, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem2)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout_2.addItem(spacerItem3)
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout_2.addItem(spacerItem4)
        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout_2.addItem(spacerItem5)
        spacerItem6 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem6)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        spacerItem7 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem7, 1, 0, 1, 1)
        self.stop_button = QtWidgets.QPushButton(self.centralwidget)
        self.stop_button.setStyleSheet("QPushButton{\n"
"background: rgb(193, 193, 193)\n"
"}")
        self.stop_button.setObjectName("stop_button")
        self.gridLayout_2.addWidget(self.stop_button, 2, 1, 1, 1)
        self.start_button = QtWidgets.QPushButton(self.centralwidget)
        self.start_button.setStyleSheet("QPushButton{\n"
"background: rgb(193, 193, 193)\n"
"}")
        self.start_button.setObjectName("start_button")
        self.gridLayout_2.addWidget(self.start_button, 1, 1, 1, 1)
        spacerItem8 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem8, 1, 2, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout_2)
        self.horizontalLayout_5.addLayout(self.verticalLayout_2)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        spacerItem9 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem9)
        self.label_7 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_7.setFont(font)
        self.label_7.setObjectName("label_7")
        self.horizontalLayout_4.addWidget(self.label_7)
        spacerItem10 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem10)
        spacerItem11 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem11)
        self.label_10 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_10.setFont(font)
        self.label_10.setObjectName("label_10")
        self.horizontalLayout_4.addWidget(self.label_10)
        spacerItem12 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem12)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        # self.vdc_time = QtWidgets.QWidget(self.centralwidget)
        self.vdc_time = pg.PlotWidget(self.centralwidget)
        self.vdc_time.setMinimumSize(QtCore.QSize(500, 500))
        self.vdc_time.setStyleSheet("QWidget{\n"
"border: 2px solid gray;\n"
"border-radius: 10px;\n"
"padding: 4 4px;\n"
"}")
        self.vdc_time.setObjectName("vdc_time")
        self.horizontalLayout_2.addWidget(self.vdc_time)
        # self.detection_rate_viz = QtWidgets.QWidget(self.centralwidget)
        self.detection_rate_viz = pg.PlotWidget(self.centralwidget)
        self.detection_rate_viz.setMinimumSize(QtCore.QSize(500, 500))
        self.detection_rate_viz.setStyleSheet("QWidget{\n"
"border: 2px solid gray;\n"
"border-radius: 10px;\n"
"padding: 4 4px;\n"
"}")
        self.detection_rate_viz.setObjectName("detection_rate_viz")
        self.horizontalLayout_2.addWidget(self.detection_rate_viz)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem13 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem13)
        self.label_19 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_19.setFont(font)
        self.label_19.setObjectName("label_19")
        self.horizontalLayout_3.addWidget(self.label_19)
        spacerItem14 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem14)
        spacerItem15 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem15)
        self.label_24 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_24.setFont(font)
        self.label_24.setObjectName("label_24")
        self.horizontalLayout_3.addWidget(self.label_24)
        spacerItem16 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem16)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        ###
        # self.visualization = QtWidgets.QWidget(self.centralwidget)
        self.visualization = pg.PlotWidget(self.centralwidget)
        self.visualization.setObjectName("visualization")
        self.detector_circle = pg.QtGui.QGraphicsEllipseItem(0, 0, 2400, 2400)  # x, y, width, height
        self.detector_circle.setPen(pg.mkPen(color=(255, 0, 0), width=1))
        self.visualization.addItem(self.detector_circle)
        ###
        self.visualization.setMinimumSize(QtCore.QSize(500, 500))
        self.visualization.setStyleSheet("QWidget{\n"
"border: 2px solid gray;\n"
"border-radius: 10px;\n"
"padding: 4 4px;\n"
"}")
        self.visualization.setObjectName("visualization")
        self.horizontalLayout.addWidget(self.visualization)
        # self.histogram = QtWidgets.QWidget(self.centralwidget)
        self.histogram = pg.PlotWidget(self.centralwidget)
        self.histogram.setMinimumSize(QtCore.QSize(500, 500))
        self.histogram.setStyleSheet("QWidget{\n"
"border: 2px solid gray;\n"
"border-radius: 10px;\n"
"padding: 4 4px;\n"
"}")
        self.histogram.setObjectName("histogram")
        self.horizontalLayout.addWidget(self.histogram)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.Error = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        font.setStrikeOut(False)
        self.Error.setFont(font)
        self.Error.setAlignment(QtCore.Qt.AlignCenter)
        self.Error.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse)
        self.Error.setObjectName("Error")
        self.verticalLayout.addWidget(self.Error)
        self.horizontalLayout_5.addLayout(self.verticalLayout)
        self.gridLayout_4.addLayout(self.horizontalLayout_5, 0, 0, 1, 1)
        APT_Physic.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(APT_Physic)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1675, 38))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        APT_Physic.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(APT_Physic)
        self.statusbar.setObjectName("statusbar")
        APT_Physic.setStatusBar(self.statusbar)
        self.actionExit = QtWidgets.QAction(APT_Physic)
        self.actionExit.setObjectName("actionExit")
        self.menuFile.addAction(self.actionExit)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(APT_Physic)
        QtCore.QMetaObject.connectSlotsByName(APT_Physic)

    def retranslateUi(self, APT_Physic):
        _translate = QtCore.QCoreApplication.translate
        APT_Physic.setWindowTitle(_translate("APT_Physic", "APT Control Software"))
        ###
        APT_Physic.setWindowIcon(QtGui.QIcon('../files/logo3.png'))
        self._translate = QtCore.QCoreApplication.translate
        self.start_button.clicked.connect(self.thread_main)
        self.thread = MainThread()
        self.thread.signal.connect(self.finished_thread_main)
        self.stop_button.setText(_translate("APT_Physic", "Stop"))
        self.stop_button.clicked.connect(self.stop_ex)
        ###
        self.label_43.setText(_translate("APT_Physic", "Experiment User"))
        self.ex_user.setText(_translate("APT_Physic", "user"))
        self.label_21.setText(_translate("APT_Physic", "Experiment Name"))
        self.ex_name.setText(_translate("APT_Physic", "test"))
        self.label_2.setText(_translate("APT_Physic", "Max. Experiment Time (S)"))
        self.ex_time.setText(_translate("APT_Physic", "90"))
        self.label_41.setText(_translate("APT_Physic", "Max. Number of Ions"))
        self.max_ions.setText(_translate("APT_Physic", "2000"))
        self.label_3.setText(_translate("APT_Physic", "Control refresh Freq.(Hz)"))
        self.ex_freq.setText(_translate("APT_Physic", "10"))
        self.label_4.setText(_translate("APT_Physic", "Specimen Start Voltage (V)"))
        self.vdc_min.setText(_translate("APT_Physic", "500"))
        self.label_5.setText(_translate("APT_Physic", "Specimen Stop Voltage (V)"))
        self.vdc_max.setText(_translate("APT_Physic", "4000"))
        self.label_6.setText(_translate("APT_Physic", "K_p Upwards"))
        self.vdc_steps_up.setText(_translate("APT_Physic", "100"))
        self.label_28.setText(_translate("APT_Physic", "K_p Downwards"))
        self.vdc_steps_down.setText(_translate("APT_Physic", "100"))
        self.label_20.setText(_translate("APT_Physic", "Cycle for Avg. (Hz)"))
        self.cycle_avg.setText(_translate("APT_Physic", "10"))
        self.label_25.setText(_translate("APT_Physic", "Pulse Fraction (%)"))
        self.pulse_fraction.setText(_translate("APT_Physic", "20"))
        self.label_23.setText(_translate("APT_Physic", "Pulse Frequency (KHz)"))
        self.pulse_frequency.setText(_translate("APT_Physic", "200"))
        self.label_17.setText(_translate("APT_Physic", "Detection Rate (%)"))
        self.detection_rate_init.setText(_translate("APT_Physic", "1"))
        self.label_22.setText(_translate("APT_Physic", "# Hits Displayed"))
        self.hit_displayed.setText(_translate("APT_Physic", "20000"))
        self.label_26.setText(_translate("APT_Physic", "Email"))
        self.label_42.setText(_translate("APT_Physic", "Counter Source"))
        self.counter_source.setItemText(0, _translate("APT_Physic", "TDC"))
        self.label_11.setText(_translate("APT_Physic", "Run Statistics"))
        self.label_13.setText(_translate("APT_Physic", "Total Ions"))
        self.label_12.setText(_translate("APT_Physic", "Elapsed Time (S):"))
        self.label_14.setText(_translate("APT_Physic", "Specimen Voltage (V)"))
        self.label_15.setText(_translate("APT_Physic", "Detection Rate (%)"))
        self.stop_button.setText(_translate("APT_Physic", "Stop"))
        self.start_button.setText(_translate("APT_Physic", "Start"))
        self.label_7.setText(_translate("APT_Physic", "Voltage"))
        self.label_10.setText(_translate("APT_Physic", "Detection Rate"))
        self.label_19.setText(_translate("APT_Physic", "Visualization"))
        self.label_24.setText(_translate("APT_Physic", "TOF"))
        self.Error.setText(_translate("APT_Physic", "<html><head/><body><p><br/></p></body></html>"))
        self.menuFile.setTitle(_translate("APT_Physic", "File"))
        self.actionExit.setText(_translate("APT_Physic", "Exit"))


   # High Voltage visualization ################
        self.x_vdc = np.arange(1000)  # 1000 time points
        self.y_vdc = np.zeros(1000)  # 1000 data points
        self.y_vdc[:] = np.nan
        # Add legend
        self.vdc_time.addLegend()
        pen_vdc = pg.mkPen(color=(255, 0, 0), width=6)
        self.data_line_vdc = self.vdc_time.plot(self.x_vdc, self.y_vdc, name="High Vol.", pen=pen_vdc)
        self.vdc_time.setBackground('w')
        # Add Axis Labels
        styles = {"color": "#f00", "font-size": "20px"}
        self.vdc_time.setLabel("left", "High Voltage (v)", **styles)
        self.vdc_time.setLabel("bottom", "Time (s)", **styles)
        # Add grid
        self.vdc_time.showGrid(x=True, y=True)
        # Add Range
        self.vdc_time.setXRange(0, 1000, padding=0.05)
        self.vdc_time.setYRange(0, 15000, padding=0.05)

        # Detection Visualization #########################
        self.x_dtec = np.arange(1000)  # 1000 time points
        self.y_dtec = np.zeros(1000)  # 1000 data points
        self.y_dtec[:] = np.nan
        pen_dtec = pg.mkPen(color=(255, 0, 0), width=6)
        self.data_line_dtec = self.detection_rate_viz.plot(self.x_dtec, self.y_dtec, pen=pen_dtec)
        self.detection_rate_viz.setBackground('w')
        # Add Axis Labels
        styles = {"color": "#f00", "font-size": "20px"}
        self.detection_rate_viz.setLabel("left", "Counts", **styles)
        self.detection_rate_viz.setLabel("bottom", "Time (s)", **styles)
        # Add grid
        self.detection_rate_viz.showGrid(x=True, y=True)
        # Add Range
        self.detection_rate_viz.setXRange(0, 1000, padding=0.05)
        self.detection_rate_viz.setYRange(0, 4000, padding=0.05)

        # Visualization #####################
        self.scatter = pg.ScatterPlotItem(
            size=self.doubleSpinBox.value(), brush=pg.mkBrush(255, 255, 255, 120))
        self.visualization.getPlotItem().hideAxis('bottom')
        self.visualization.getPlotItem().hideAxis('left')

        # timer plot, variables, and cameras
        self.timer2 = QtCore.QTimer()
        self.timer2.setInterval(1000)
        self.timer2.timeout.connect(self.update_plot_data)
        self.timer2.start()
        self.timer3 = QtCore.QTimer()
        self.timer3.setInterval(2000)
        self.timer3.timeout.connect(self.statistics)
        self.timer3.start()

    def thread_main(self):
        """
        Main thread for running experiment
        """
        self.start_button.setEnabled(False)  # Disable the start button in the GUI
        variables.plot_clear_flag = True  # Change the flag to clear the plots in GUI

        # Update global variables to do the experiments
        variables.user_name = self.ex_user.text()
        variables.ex_time = int(float(self.ex_time.text()))
        variables.ex_freq = int(float(self.ex_freq.text()))
        variables.max_ions = int(float(self.max_ions.text()))
        variables.vdc_min = int(float(self.vdc_min.text()))
        variables.detection_rate = float(self.detection_rate_init.text())
        variables.hit_display = int(float(self.hit_displayed.text()))
        variables.pulse_fraction = int(float(self.pulse_fraction.text())) / 100
        variables.pulse_frequency = float(self.pulse_frequency.text())
        variables.hdf5_path = self.ex_name.text()
        variables.email = self.email.text()
        variables.cycle_avg = int(float(self.cycle_avg.text()))
        variables.vdc_step_up = int(float(self.vdc_steps_up.text()))
        variables.vdc_step_down = int(float(self.vdc_steps_down.text()))
        variables.counter_source = str(self.counter_source.currentText())
        if self.criteria_time.isChecked():
            variables.criteria_time = True
        elif not self.criteria_time.isChecked():
            variables.criteria_time = False
        if self.criteria_ions.isChecked():
            variables.criteria_ions = True
        elif not self.criteria_ions.isChecked():
            variables.criteria_ions = False
        if self.criteria_vdc.isChecked():
            variables.criteria_vdc = True
        elif not self.criteria_vdc.isChecked():
            variables.criteria_vdc = False

        # Read the experiment counter
        with open('./files/counter_physic.txt') as f:
            variables.counter = int(f.readlines()[0])
        # Current time and date
        now = datetime.datetime.now()
        variables.exp_name = "%s_" % variables.counter + \
                             now.strftime("%b-%d-%Y_%H-%M") + "_%s" % variables.hdf5_path
        variables.path = os.path.join(os.path.split(MODULE_DIR)[0], 'data_laser_pulse_mode\\%s' % variables.exp_name)
        # Create folder to save the data
        if not os.path.isdir(variables.path):
            os.makedirs(variables.path, mode=0o777, exist_ok=True)
        # start the run methos of MainThread Class, which is main function of apt_voltage.py
        self.thread.start()

    def finished_thread_main(self):
        """
        The function that is run after end of experiment(MainThread)
        """
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(True)
        QScreen.grabWindow(self.app.primaryScreen(),
                           QApplication.desktop().winId()).save(variables.path + '/screenshot.png')

    def stop_ex(self):
        """
        The function that is run if STOP button is pressed
        """
        if variables.start_flag == True:
            variables.stop_flag = True  # Set the STOP flag
            self.stop_button.setEnabled(False)  # Disable the stop button


    def thread_worker(self, target):
        """
        The function for creating workers
        """
        return threading.Thread(target=target)

    def update_plot_data(self):
        """
        The function for updating plots
        """
        if variables.index_auto_scale_graph == 30:
            self.vdc_time.enableAutoRange(axis='x')
            self.detection_rate_viz.enableAutoRange(axis='x')
            variables.index_auto_scale_graph = 0

        self.vdc_time.disableAutoRange()
        self.detection_rate_viz.disableAutoRange()

        variables.index_auto_scale_graph += 1

        if variables.plot_clear_flag:
            self.x_vdc = np.arange(1000)  # 1000 time points
            self.y_vdc = np.zeros(1000)  # 1000 data points
            self.y_vdc[:] = np.nan

            self.data_line_vdc.setData(self.x_vdc, self.y_vdc)

            self.x_dtec = np.arange(1000)
            self.y_dtec = np.zeros(1000)
            self.y_dtec[:] = np.nan

            self.data_line_dtec.setData(self.x_dtec, self.y_dtec)

            self.histogram.clear()

            self.scatter.clear()
            self.visualization.clear()
            self.visualization.addItem(self.detector_circle)
            variables.plot_clear_flag = False

            variables.specimen_voltage = 0
            variables.pulse_voltage = 0
            variables.elapsed_time = 0
            variables.total_ions = 0
            variables.avg_n_count = 0

        if variables.start_flag:
            if variables.index_wait_on_plot_start <= 16:
                variables.index_wait_on_plot_start += 1

            if variables.index_wait_on_plot_start >= 8:
                # V_dc
                if variables.index_plot <= 999:
                    self.y_vdc[variables.index_plot] = int(variables.specimen_voltage)  # Add a new value.
                else:
                    self.x_vdc = np.append(self.x_vdc,
                                           self.x_vdc[-1] + 1)  # Add a new value 1 higher than the last.
                    self.y_vdc = np.append(self.y_vdc, int(variables.specimen_voltage))  # Add a new value.

                self.data_line_vdc.setData(self.x_vdc, self.y_vdc)

                # Detection Rate Visualization
                if variables.index_plot <= 999:
                    self.y_dtec[variables.index_plot] = int(variables.avg_n_count)  # Add a new value.
                else:
                    self.x_dtec = self.x_dtec[1:]  # Remove the first element.
                    self.x_dtec = np.append(self.x_dtec,
                                            self.x_dtec[-1] + 1)  # Add a new value 1 higher than the last.
                    self.y_dtec = self.y_dtec[1:]
                    self.y_dtec = np.append(self.y_dtec, int(variables.avg_n_count))

                self.data_line_dtec.setData(self.x_dtec, self.y_dtec)
                # Increase the index
                variables.index_plot += 1
            # Time of Flight
            if variables.counter_source == 'TDC' and variables.total_ions > 0 and variables.index_wait_on_plot_start > 16 \
                    and variables.index_wait_on_plot_start > 16 and not variables.raw_mode:
                if variables.index_wait_on_plot_start > 16:

                    try:
                        def replaceZeroes(data):
                            min_nonzero = np.min(data[np.nonzero(data)])
                            data[data == 0] = min_nonzero
                            return data

                        if self.conf["visualization"] == 'tof':
                            tof = variables.t * 27.432 / (1000 * 4)  # Time in ns
                            viz = tof[tof < 5000]
                        elif self.conf["visualization"] == 'mc':
                            max_lenght = max(len(variables.x), len(variables.y),
                                             len(variables.t), len(variables.main_v_dc_dld))
                            viz = tof2mc_simple.tof_bin2mc(variables.t[:max_lenght], 0,
                                                           variables.main_v_dc_dld[:max_lenght],
                                                           variables.x[:max_lenght], variables.x[:max_lenght],
                                                           flightPathLength=110)

                        self.y_tof, self.x_tof = np.histogram(viz, bins=512)
                        self.histogram.clear()
                        self.y_tof = replaceZeroes(self.y_tof)
                        self.histogram.addItem(
                            pg.BarGraphItem(x=self.x_tof[:-1], height=np.log(self.y_tof), width=0.1, brush='r'))

                    except:
                        print(
                            f"{initialize_devices.bcolors.FAIL}Error: Cannot plot Histogram correctly{initialize_devices.bcolors.ENDC}")

                    # Visualization
                    try:
                        # adding points to the scatter plot
                        self.scatter.clear()
                        self.scatter.setSize(self.doubleSpinBox.value())
                        x = variables.x
                        y = variables.y
                        min_length = min(len(x), len(y))
                        x = variables.x[-min_length:]
                        y = variables.y[-min_length:]
                        self.scatter.setData(x=x[-variables.hit_display:],
                                             y=y[-variables.hit_display:])
                        # add item to plot window
                        # adding scatter plot item to the plot window
                        self.visualization.clear()
                        self.visualization.addItem(self.scatter)
                        self.visualization.addItem(self.detector_circle)
                    except:
                        print(
                            f"{initialize_devices.FAIL}Error: Cannot plot Ions correctly{initialize_devices.bcolors.ENDC}")

            # save plots to the file
            if variables.index_plot_save % 100 == 0:
                exporter = pg.exporters.ImageExporter(self.vdc_time.plotItem)
                exporter.export(variables.path + '/v_dc_p_%s.png' % variables.index_plot_save)
                exporter = pg.exporters.ImageExporter(self.detection_rate_viz.plotItem)
                exporter.export(variables.path + '/detection_rate_%s.png' % variables.index_plot_save)
                exporter = pg.exporters.ImageExporter(self.visualization.plotItem)
                exporter.export(variables.path + '/visualization_%s.png' % variables.index_plot_save)
                exporter = pg.exporters.ImageExporter(self.histogram.plotItem)
                exporter.export(variables.path + '/tof_%s.png' % variables.index_plot_save)

            # Increase the index
            variables.index_plot_save += 1

        # Statistics Update
        self.speciemen_voltage.setText(str(float("{:.3f}".format(variables.specimen_voltage))))
        self.elapsed_time.setText(str(float("{:.3f}".format(variables.elapsed_time))))
        self.total_ions.setText((str(variables.total_ions)))
        self.detection_rate.setText(str
            (float("{:.3f}".format(
            (variables.avg_n_count * 100) / (1 + variables.pulse_frequency * 1000)))))

    def statistics(self):
        """
        The function for updating statistics in the GUI
        """

        # Clean up the error message
        if variables.index_warning_message == 15:
            _translate = QtCore.QCoreApplication.translate
            self.Error.setText(_translate("APT_Physic",
                                          "<html><head/><body><p><span style=\" "
                                          "color:#ff0000;\"></span></p></body></html>"))
            variables.index_warning_message = 0

        variables.index_warning_message += 1

        try:
            # Update the setup parameters
            variables.ex_time = int(float(self.ex_time.text()))
            variables.user_name = self.ex_user.text()
            variables.ex_freq = int(float(self.ex_freq.text()))
            variables.max_ions = int(float(self.max_ions.text()))
            variables.vdc_min = int(float(self.vdc_min.text()))

            variables.detection_rate = float(self.detection_rate_init.text())
            variables.hit_display = int(float(self.hit_displayed.text()))
            variables.pulse_fraction = int(float(self.pulse_fraction.text())) / 100
            variables.pulse_frequency = float(self.pulse_frequency.text())
            variables.hdf5_path = self.ex_name.text()
            variables.email = self.email.text()
            variables.cycle_avg = int(float(self.cycle_avg.text()))
            variables.vdc_step_up = int(float(self.vdc_steps_up.text()))
            variables.vdc_step_down = int(float(self.vdc_steps_down.text()))
            variables.counter_source = str(self.counter_source.currentText())

            if self.criteria_time.isChecked():
                variables.criteria_time = True
            elif not self.criteria_time.isChecked():
                variables.criteria_time = False
            if self.criteria_ions.isChecked():
                variables.criteria_ions = True
            elif not self.criteria_ions.isChecked():
                variables.criteria_ions = False
            if self.criteria_vdc.isChecked():
                variables.criteria_vdc = True
            elif not self.criteria_vdc.isChecked():
                variables.criteria_vdc = False

            # Show error message for V_dc higher than 20Kv
            if int(float(self.vdc_max.text())) > 20000:
                _translate = QtCore.QCoreApplication.translate
                self.Error.setText(_translate("OXCART",
                                              "<html><head/><body><p><span style=\" color:#ff0000;\">Maximum possible "
                                              "number is 20KV</span></p></body></html>"))
                self.vdc_max.setText(_translate("OXCART", str(variables.vdc_max)))
            else:
                variables.vdc_max = int(float(self.vdc_max.text()))
            # Show error message for V_p higher than 3281

        except:
            print(
                f"{initialize_devices.bcolors.FAIL}Error: Cannot update setup parameters{initialize_devices.bcolors.ENDC}")


class MainThread(QThread):
    """
    A class for creating main_thread for the APT experiments
    The run method create thread of main function in the experiment script
    """
    signal = pyqtSignal('PyQt_PyObject')
    def __init__(self, ):
        QThread.__init__(self, )
        # run method gets called when we start the thread

    def run(self):
        main_thread = apt_laser.main()
        self.signal.emit(main_thread)