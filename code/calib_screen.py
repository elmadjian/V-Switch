from PySide2.QtCore import Object, Signal, Slot
import numpy as np


class CalibScreen(QObject):

    def __init__(self, v_targets, h_targets):
        self.window = None
        self.engine = QQmlApplicationEngine()
        self.v_targets = v_targets
        self.h_targets = h_targets

    @Slot()
    def calibrate(self):
        print("starting calibration")