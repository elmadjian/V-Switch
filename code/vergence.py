import numpy as np
from PySide2.QtCore import QObject, Signal, Slot, Property

class VergenceCtl(QObject):

    def __init__(self):
        QObject.__init__(self)
        self.buffer = []
        self.fixation = False
        self.plane = 0
        self.frequency

    def is_fixating(self):
        x = self.buffer[:,0]
        y = self.buffer[:,1]

    def update(self, data):
        if data[0] != -9 and data[2] != -9:
            l = np.array([data[0], data[1]])
            r = np.array([data[2], data[3]])
            dist = np.linalg.norm(l-r)
            self.__update_buffer(dist)
    
    def __update_buffer(self, data):
        if len(self.buffer) == self.frequency:
            self.buffer.pop(0)
        self.buffer.append(data)

    @Slot(int)
    def set_frequency(self, freq):
        self.frequency = freq

    

    

