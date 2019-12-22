import cv2
import numpy as np
import time
import os
import socket
import data_storage as ds
from PySide2.QtCore import QObject, Signal, Slot, Property
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process import kernels
from threading import Thread


class HMDCalibrator(QObject):

    move_on = Signal()
    conn_status = Signal(bool)

    def __init__(self, v_targets, h_targets, samples_per_tgt, timeout):
        '''
        ntargets: number of targets that are going to be shown for calibration
        frequency: value of the tracker's frequency in Hz
        '''
        QObject.__init__(self)
        ntargets  = v_targets * h_targets
        self.target_list = self.__generate_target_list(v_targets, h_targets)
        self.storer = ds.Storer(ntargets, self.target_list)
        self.l_regressor = None
        self.r_regressor = None
        self.current_target = -1
        self.leye, self.reye = None, None
        self.samples = samples_per_tgt
        self.timeout = timeout
        self.collector = None
        self.predictor = None
        self.stream = False
        self.vergence = None
        self.mode_3D = False
        self.storage = False
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ip, self.port = self.load_network_options()


    def set_sources(self, leye, reye):
        self.leye = leye
        self.reye = reye
        self.storer.set_sources(None, leye, reye)

    def set_vergence_control(self, vergence):
        self.vergence = vergence

    def load_network_options(self):
        ip, port = "", ""
        if os.path.isfile('config/hmd_config.txt'):
            with open('config/hmd_config.txt', 'r') as hmd_config:
                data = hmd_config.readline()
                ip, port = data.split(':')
        return ip, int(port)
    

    def __generate_target_list(self, v, h):
        target_list = []
        for y in np.linspace(0,1, v):
            for x in np.linspace(0,1, h):
                target_list.append(np.array([x,y], dtype=np.float32))
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
        tgt = self.storer.targets

        while (len(tgt[idx]) < self.samples) and (time.time()-t < self.timeout):
            self.storer.collect_data(idx, self.mode_3D, minfreq)
            tgt = self.storer.targets
            time.sleep(1/maxfreq)
        self.move_on.emit()
        print("number of samples collected: l->{}, r->{}".format(
            len(self.storer.l_centers[idx]),
            len(self.sotrer.r_centers[idx])))

    
    @Property('QVariantList')
    def target(self):
        if self.current_target >= len(self.target_list):
            return [-9,-9]
        tgt = self.target_list[self.current_target]
        converted = [float(tgt[0]), float(tgt[1])]
        return converted

    def start_calibration(self):
        print('reseting calibration')
        self.storer.initialize_storage()
        self.l_regressor = None
        self.r_regressor = None
        if self.predictor is not None:
            self.stream = False
            self.predictor.join()
        self.current_target = -1

    @Slot()
    def next_target(self):
        if self.collector is not None:
            self.collector.join()
        self.current_target += 1
        if self.current_target >= len(self.target_list):
            self.socket.sendto("F".encode(), (self.ip, self.port))
            return
        tgt = self.target_list[self.current_target]
        msg = 'N:' + str(tgt[0]) + ':' + str(tgt[1])
        self.socket.sendto(msg.encode(), (self.ip, self.port))


    @Slot(int, int)
    def collect_data(self, minfq, maxfq):
        msg = 'R'.encode()
        self.socket.sendto(msg, (self.ip, self.port))
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
        targets = self.storer.get_targets_list()                         
        if self.leye.is_cam_active():           
            l_centers = self.storer.get_l_centers_list(self.mode_3D)     
            clf_l.fit(l_centers, targets)
            self.l_regressor = clf_l
        if self.reye.is_cam_active():
            r_centers = self.storer.get_r_centers_list(self.mode_3D)
            clf_r.fit(r_centers, targets)
            self.r_regressor = clf_r
        print("Gaze estimation finished")
        if self.storage:
            self.storer.store_calibration()
        if self.l_regressor is not None or self.r_regressor is not None:
            self.stream = True
            self.predictor = Thread(target=self.predict, args=())
            self.predictor.start()

    @Slot()
    def calibrate_planes(self):
        for i in range(self.vergence.planes):
            try:
                msg = 'P:' + str(i)
                self.socket.sento(msg.encode(), (self.ip, self.port))
                plane_calibrator = Thread(target=self.vergence.get_plane_data, args=(i,))
                plane_calibrator.start()
                plane_calibrator.join()
            except Exception as e:
                print('Could not send plane id')
        self.socket.sendto('F'.encode(), (self.ip, self.port))


    def predict(self):
        count = 0
        while self.stream:
            try:
                demand = self.socket.recv(1024).decode()
                if demand.startswith('G'):
                    data = self.__predict()
                    x1, y1 = data[0], data[1]
                    x2, y2 = data[2], data[3]
                    x1, y1 = '{:.8f}'.format(x1), '{:.8f}'.format(y1)
                    x2, y2 = '{:.8f}'.format(x2), '{:.8f}'.format(y2)
                    msg = 'G:'+x1+':'+y1+':'+x2+':'+y2
                    self.socket.sendto(msg.encode(), (self.ip, self.port))
            except Exception as e:
                print("no request from HMD...", e)
                count += 1
                if count > 3:
                    break
        

    def __predict(self):
        data = [-9,-9,-9,-9]
        pred = [-9,-9,-9,-9]
        if self.l_regressor:
            le = self.leye.get_processed_data()
            if le is not None:
                input_data = le[:2].reshape(1,-1)
                le_coord = self.l_regressor.predict(input_data)[0]
                data[0], data[1] = input_data[0]
                pred[0], pred[1] = float(le_coord[0]), float(le_coord[1])
        if self.r_regressor:
            re = self.reye.get_processed_data()
            if re is not None:
                input_data = re[:2].reshape(1,-1)
                re_coord = self.r_regressor.predict(input_data)[0]
                data[2], data[3] = input_data[0]
                pred[2], pred[3] = float(re_coord[0]), float(re_coord[1])
        self.vergence.update(pred)
        if self.storage:
            l_gz, r_gz   = pred[:2], pred[2:]
            l_raw, r_raw = data[:2], data[2:]
            self.storer.append_session_data(l_gz, r_gz, l_raw, r_raw)
        return pred


    def __get_clf(self):
        kernel = 1.5*kernels.RBF(length_scale=1.0, length_scale_bounds=(0.0,1.0))
        clf = GaussianProcessRegressor(alpha=1e-5,
                                       optimizer=None,
                                       n_restarts_optimizer=3,
                                       kernel = kernel)
        return clf

    @Property(str)
    def hmd_ip(self):
        return self.ip

    @Property(int)
    def hmd_port(self):
        return self.port        


    @Slot(str, str)
    def update_network(self, ip, port):
        self.ip, self.port = ip, int(port)
        with open('hmd_config.txt', 'w') as hmd_config:
            text = ip + ':' + port
            hmd_config.write(text)


    @Slot()
    def connect(self):
        self.socket.settimeout(4)
        self.socket.sendto('C'.encode(), (self.ip, self.port))
        try:
            response = self.socket.recv(1024).decode()
            if response:
                self.conn_status.emit(True)
                self.start_calibration()
        except Exception:
            self.conn_status.emit(False)

    @Slot()
    def toggle_3D(self):
        self.mode_3D = not self.mode_3D

    @Slot()
    def toggle_storage(self):
        self.storage = not self.storage

    @Slot()
    def save_session(self):
        if self.storage:
            self.storer.store_session()

                


   
