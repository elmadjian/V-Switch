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


    def __get_target_data(self, maxfreq, minfreq):
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
            if self.__check_data_and_timestamp(sc, le, re, 1/minfreq):
                self.__add_data(sc, le, re, idx)
            time.sleep(1/maxfreq)
        self.move_on.emit()
        print("number of samples collected: {}".format(len(self.targets[idx])))


    def __add_data(self, sc, le, re, idx):
        self.targets[idx] = np.vstack((self.targets[idx], sc[0]))
        if self.leye.is_cam_active():
            self.l_centers[idx] = np.vstack((self.l_centers[idx], le[0]))
        if self.reye.is_cam_active():
            self.r_centers[idx] = np.vstack((self.r_centers[idx], re[0]))


    def get_keys(self):
        return self.targets.keys()


    def __check_data_and_timestamp(self, sc, le, re, thresh):
        if le is None and self.leye.is_cam_active():
            return False
        if re is None and self.reye.is_cam_active():
            return False
        if sc is not None:
            if le is not None and re is not None:
                if abs(sc[1] - le[1]) < thresh:
                    if abs(sc[1] - re[1]) < thresh:
                        return True
            if le is not None and re is None:
                if abs(sc[1] - le[1]) < thresh:
                    return True
            if le is None and re is not None:
                if abs(sc[1] - re[1]) < thresh:
                    return True
        return False

    
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
    def start_calibration(self):
        print('reseting calibration')
        self.targets   = {i:np.empty((0,2), float) for i in range(self.ntargets)}
        self.l_centers = {i:np.empty((0,2), float) for i in range(self.ntargets)}
        self.r_centers = {i:np.empty((0,2), float) for i in range(self.ntargets)}
        self.l_regressor = None
        self.r_regressor = None
        self.current_target = -1

    @Slot()
    def next_target(self):
        if self.collector is not None:
            self.collector.join()
        self.current_target += 1

    @Slot()
    def store_data_trigger(self):
        print("storing data")

    @Slot(int, int)
    def collect_data(self, minfq, maxfq):
        print(minfq, maxfq)
        self.collector = Thread(target=self.__get_target_data, args=(minfq,maxfq,))
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
        if self.leye.is_cam_active():                                       
            l_centers = self.__dict_to_list(self.l_centers)
            clf_l.fit(l_centers, targets)
            self.l_regressor = clf_l
        if self.reye.is_cam_active():
            r_centers = self.__dict_to_list(self.r_centers)
            clf_r.fit(r_centers, targets)
            self.r_regressor = clf_r
        print("Gaze estimation finished")


    @Property('QVariantList')
    def predict(self):
        data = [-1,-1,-1,-1]
        if self.l_regressor:
            le = self.leye.get_processed_data()
            if le is not None:
                input_data = le[0].reshape(1,-1)
                le_coord = self.l_regressor.predict(input_data)[0]
                data[0], data[1] = float(le_coord[0]), float(le_coord[1])
        if self.r_regressor:
            re = self.reye.get_processed_data()
            if re is not None:
                input_data = re[0].reshape(1,-1)
                re_coord = self.r_regressor.predict(input_data)[0]
                data[2], data[3] = float(re_coord[0]), float(re_coord[1])
        return data


    def __get_clf(self):
        kernel = 1.5*kernels.RBF(length_scale=1.0, length_scale_bounds=(0,3.0))
        clf = GaussianProcessRegressor(alpha=1e-5,
                                       optimizer=None,
                                       n_restarts_optimizer=9,
                                       kernel = kernel)
        return clf


   
