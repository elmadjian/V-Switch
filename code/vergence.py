import numpy as np
from PySide2.QtCore import QObject, Signal, Slot, Property

class VergenceCtl(QObject):

    def __init__(self):
        QObject.__init__(self)
        self.buffer = []
        self.fixation = False
        self.plane = 0
        self.frequency = None

    def is_fixating(self, l, r):
        l_std = np.std(l, axis=0)
        r_std = np.std(r, axis=0)
        if np.mean(l_std) < 0.1 and np.mean(r_std) < 0.1:
            return True
        return False 

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

    

    

