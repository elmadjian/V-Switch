import cv2
import numpy as np
import time


class Calibrator():

    def __init__(self, ntargets, frequency):
        '''
        ntargets: number of targets that are going to be shown for calibration
        frequency: value of the tracker's frequency in Hz
        '''
        self.ntargets  = ntargets
        self.targets   = {i:np.empty((0,2), float) for i in range(ntargets)}
        self.l_centers = {i:np.empty((0,2), float) for i in range(ntargets)}
        self.r_centers = {i:np.empty((0,2), float) for i in range(ntargets)}
        self.sleep = 1/frequency


    def collect_target_data(self, idx, scene, le, re, thresh):
        '''
        scene: sceneCamera object
        le: left eyeCamera object
        re: right eyeCamera object
        thresh: amount of data to be collected per target
        '''
        while len(self.targets[idx]) < thresh:
            sc_data = scene.get_data()
            le_data = le.get_data()
            re_data = re.get_data()
            #print(sc_data, le_data, re_data)
            if sc_data is not None and le_data is not None and re_data is not None:
                print("found all data")
                if self.__test_timestamp(sc_data[0], le_data[0], re_data[0]):
                    print("all data synced")
                    # print(sc_data[1], self.targets[idx])
                    # print(le_data[1], self.l_centers[idx])
                    # print(re_data[1], self.r_centers[idx])
                    # print('-----------------')
                    self.targets[idx] = np.vstack((self.targets[idx], sc_data[1]))
                    self.l_centers[idx] = np.vstack((self.l_centers[idx], le_data[1]))
                    self.r_centers[idx] = np.vstack((self.r_centers[idx], re_data[1]))
            print(len(self.targets[idx]))
            time.sleep(self.sleep)


    def __test_timestamp(self, sc, le, re):
        if abs(sc - le) < self.sleep:
            if abs(sc - re) < self.sleep:
                if abs(le - re) < self.sleep:
                    return True
        return False


    def get_keys(self):
        return self.targets.keys()







    