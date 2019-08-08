import cv2
import numpy as np
import time
from PySide2.QtCore import QObject, Signal, Slot, Property
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process import kernels
from threading import Thread


class Calibrator(QObject):

    move_on = Signal()

    def __init__(self, v_targets, h_targets, samples_per_tgt, timeout):
        '''
        ntargets: number of targets that are going to be shown for calibration
        frequency: value of the tracker's frequency in Hz
        '''
        QObject.__init__(self)
        self.ntargets  = v_targets * h_targets
        self.targets   = {i:np.empty((0,2), float) for i in range(self.ntargets)}
        self.l_centers = {i:np.empty((0,2), float) for i in range(self.ntargets)}
        self.r_centers = {i:np.empty((0,2), float) for i in range(self.ntargets)}
        self.l_regressor = None
        self.r_regressor = None
        self.target_list = self.__generate_target_list(v_targets, h_targets)
        self.current_target = -1
        self.scene, self.leye, self.reye = None, None, None
        self.samples = samples_per_tgt
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
        seed = np.random.randint(0,99)
        rnd  = np.random.RandomState(seed)
        rnd.shuffle(target_list)
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
            sc = self.scene.get_processed_data() 
            le = self.leye.get_processed_data()
            re = self.reye.get_processed_data()
            if sc is not None and le is not None and re is not None:
                if self.__check_timestamp(sc[1], le[1], re[1], 1/frequency):
                    self.targets[idx]   = np.vstack((self.targets[idx], sc[0]))
                    self.l_centers[idx] = np.vstack((self.l_centers[idx], le[0]))
                    self.r_centers[idx] = np.vstack((self.r_centers[idx], re[0]))
            time.sleep(1/frequency)
        self.move_on.emit()
        print("number of samples collected: {}".format(len(self.targets[idx])))


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


    def __check_timestamp(self, sc, le, re, thresh):
        if sc is None or le is None or re is None:
            return False
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

    @Slot()
    def perform_estimation(self):
        '''
        Finds a gaze estimation function to be used for 
        future predictions. Based on Gaussian Processes regression.
        '''
        clf_l = self.__get_clf()
        clf_r = self.__get_clf()                                  
        targets = self.__dict_to_list(self.targets)                                       
        l_centers = self.__dict_to_list(self.l_centers)
        r_centers = self.__dict_to_list(self.r_centers)
        clf_l.fit(l_centers, targets)
        clf_r.fit(r_centers, targets)
        self.l_regressor = clf_l
        self.r_regressor = clf_r
        print("Gaze estimation finished")
 
    def __get_clf(self):
        kernel = 1.5*kernels.RBF(length_scale=1.0, length_scale_bounds=(0,3.0))
        clf = GaussianProcessRegressor(alpha=1e-5,
                                       optimizer=None,
                                       n_restarts_optimizer=9,
                                       kernel = kernel)
        return clf


   
