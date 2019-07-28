import cv2
import numpy as np
import time
from PySide2.QtCore import QObject, Signal, Slot, Property
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process import kernels
from threading import Thread


class Calibrator(QObject):

    move_on = Signal()

    def __init__(self, v_targets, h_targets, samples, timeout):
        '''
        ntargets: number of targets that are going to be shown for calibration
        frequency: value of the tracker's frequency in Hz
        '''
        QObject.__init__(self)
        self.ntargets  = v_targets * h_targets
        self.targets   = {i:np.empty((0,2), float) for i in range(self.ntargets)}
        self.l_centers = {i:np.empty((0,2), float) for i in range(self.ntargets)}
        self.r_centers = {i:np.empty((0,2), float) for i in range(self.ntargets)}
        self.regressor = None
        self.target_list = self.__generate_target_list(v_targets, h_targets)
        self.current_target = -1
        self.scene, self.leye, self.reye = None, None, None
        self.samples = samples
        self.timeout = timeout
        self.collector = None

    def set_sources(self, scene, leye, reye):
        self.scene = scene
        self.leye  = leye
        self.reye  = reye

    def __generate_target_list(self, v, h):
        target_list = []
        for y in np.linspace(0.09, 0.91, v):
            for x in np.linspace(0.055, 0.935, h):
                target_list.append([x,y])
        return target_list


    def __get_target_data(self, frequency):
        '''
        scene: sceneCamera object
        le: left eyeCamera object
        re: right eyeCamera object
        thresh: amount of data to be collected per target
        '''
        idx = self.current_target
        t = time.time()
        while (len(self.targets[idx]) < self.samples) and (time.time()-t < self.timeout):
            print(time.time()-t)
            sc = self.scene.get_processed_data()
            le = self.leye.get_processed_data()
            re = self.reye.get_processed_data()
            if sc[0] is not None and le[0] is not None and re[0] is not None:
                if self.__test_timestamp(sc[0], le[0], re[0], 1/frequency):
                    self.targets[idx]   = np.vstack((self.targets[idx], sc[1]))
                    self.l_centers[idx] = np.vstack((self.l_centers[idx], le[1]))
                    self.r_centers[idx] = np.vstack((self.r_centers[idx], re[1]))
            time.sleep(1/frequency)
        self.move_on.emit()
        print("data collected")


    def clean_up_data(self, deviation, reye=None):
        '''
        remove misrepresented data associated with a target
        '''
        targets   = {i:np.empty((0,2), float) for i in range(self.ntg)}
        l_centers = {i:np.empty((0,2), float) for i in range(self.ntg)}
        r_centers = {i:np.empty((0,2), float) for i in range(self.ntg)}
        for t in self.targets.keys():
            nx, ny = self.__get_outliers(self.l_centers[t])
            for i in range(len(self.targets[t])):
                if nx[i] < deviation and ny[i] < deviation:
                    l_centers[t] = np.vstack((l_centers[t], self.l_centers[t][i]))
                    targets[t]   = np.vstack((targets[t], self.targets[t][i]))
                    if reye is not None:
                        r_centers[t] = np.vstack((r_centers[t], self.r_centers[t][i]))
        self.targets = targets
        self.l_centers = l_centers
        self.r_centers = r_centers


    def estimate_gaze(self):
        '''
        Finds a gaze estimation function to be used for 
        future predictions. Based on Gaussian Processes regression.
        '''
        kernel = 1.5*kernels.RBF(length_scale=1.0, length_scale_bounds=(0,3.0))
        clf = GaussianProcessRegressor(alpha=1e-5,
                                       optimizer=None,
                                       n_restarts_optimizer=9,
                                       kernel = kernel)
        targets = self.__dict_to_list(self.targets)                                       
        l_centers = self.__dict_to_list(self.l_centers)
        if self.binocular:
            r_centers = self.__dict_to_list(self.r_centers)
            input_data = np.hstack((l_centers, r_centers))
            clf.fit(input_data, targets)
        else:
            clf.fit(l_centers, targets)
        self.regressor = clf


    def predict(self, leye, reye=None, w=None, h=None):
        if self.regressor is not None:
            input_data = leye.reshape(1,-1)
            if reye is not None:
                input_data = np.hstack((leye, reye))
            coord = self.regressor.predict(input_data)[0]
            x = coord[0] * w
            y = coord[1] * h
            if len(coord) == 3:
                return coord 
            return (int(x), int(y))


    def get_keys(self):
        return self.targets.keys()


    def __test_timestamp(self, sc, le, re, thresh):
        if abs(sc - le) < thresh:
            if abs(sc - re) < thresh:
                if abs(le - re) < thresh:
                    return True
        return False

    
    def __get_outliers(self, data):
        d      = np.abs(data - np.median(data, axis=0))
        std    = np.std(d)
        nx, ny = d[:,0]/std, d[:,1]/std
        return nx, ny


    def __dict_to_list(self, dic):
        new_list = np.empty((dic[0].shape), float)
        for t in dic.keys():
            new_list = np.vstack((new_list, dic[t]))
        return new_list

    
    @Property('QVariantList')
    def target(self):
        if self.current_target >= len(self.target_list):
            return [-1,-1]
        tgt = self.target_list[self.current_target]
        converted = [float(tgt[0]), float(tgt[1])]
        return converted

    @Slot()
    def next_target(self):
        if self.collector is not None:
            self.collector.join()
        self.current_target += 1

    @Slot()
    def store_data_trigger(self):
        print("storing data")

    @Slot(int)
    def collect_data(self, frequency):
        self.collector = Thread(target=self.__get_target_data, args=(frequency,))
        self.collector.start()


   
