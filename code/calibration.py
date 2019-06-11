import cv2
import numpy as np
import time
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process import kernels


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
        self.regressor = None


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
            if sc_data is not None and le_data is not None and re_data is not None:
                if self.__test_timestamp(sc_data[0], le_data[0], re_data[0]):
                    self.targets[idx] = np.vstack((self.targets[idx], sc_data[1]))
                    self.l_centers[idx] = np.vstack((self.l_centers[idx], le_data[1]))
                    self.r_centers[idx] = np.vstack((self.r_centers[idx], re_data[1]))
            time.sleep(self.sleep)


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


    def __test_timestamp(self, sc, le, re):
        if abs(sc - le) < self.sleep:
            if abs(sc - re) < self.sleep:
                if abs(le - re) < self.sleep:
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







    