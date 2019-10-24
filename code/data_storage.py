import numpy as np 
import os

class Storer():

    def __init__(self, ntargets):
        self.ntargets = ntargets
        self.targets, self.l_centers, self.r_centers = None, None, None
        self.t_imgs, self.l_imgs, self.r_imgs = None, None, None
        self.initialize_storage()
        self.scene, self.leye, self.reye = None, None, none
   
    def initialize_storage(self):
        self.targets   = {i:np.empty((0,2), float) for i in range(self.ntargets)}
        self.l_centers = {i:np.empty((0,6), float) for i in range(self.ntargets)}
        self.r_centers = {i:np.empty((0,6), float) for i in range(self.ntargets)}
        self.t_imgs = {i:[] for i in range(self.ntargets)}
        self.l_imgs = {i:[] for i in range(self.ntargets)}
        self.r_imgs = {i:[] for i in range(self.ntargets)}

    def set_sources(self, scene, leye, reye):
        self.scene = scene
        self.leye  = leye
        self.reye  = reye

    def collect_data(self, idx, mode3D, minfreq):
        sc = self.scene.get_processed_data() 
        le = self.leye.get_processed_data()
        re = self.reye.get_processed_data()
        sc_img = self.scene.get_np_image()
        le_img = self.leye.get_np_image()
        re_img = self.reye.get_np_image()
        if self.__check_data_n_timestamp(sc, le, re, mode3D, 1/minfreq):
            self.__add_data(sc, le, re, idx)
            self.__add_imgs(sc_img, le_img, re_img, idx)
    
    def __add_data(self, sc, le, re, idx):
        scd = np.array(self.target_list[idx])
        if self.scene.is_cam_active():
            scd = np.array([sc[0], sc[1]], dtype='float')
            self.targets[idx] = np.vstack((self.targets[idx], scd))
        if self.leye.is_cam_active():
            led = np.array([le[0],le[1],le[2],le[3],le[4],le[5]])
            self.l_centers[idx] = np.vstack((self.l_centers[idx], led))
        if self.reye.is_cam_active():
            red = np.array([re[0],re[1],re[2],le[3],le[4],le[5]])
            self.r_centers[idx] = np.vstack((self.r_centers[idx], red))

    def __add_imgs(self, sc, le, re, idx):
        if self.scene.is_cam_active():
            self.t_imgs[idx].append(sc)
        if self.leye.is_cam_active():
            self.l_imgs[idx].append(le)
        if self.reye.is_cam_active():
            self.r_imgs[idx].append(re)
            
   
    def __check_data_n_timestamp(self, sc, le, re, mode3D, thresh):
        if le is None and self.leye.is_cam_active():
            return False
        if re is None and self.reye.is_cam_active():
            return False
        if not self.scene.is_cam_active():
            return True
        sc_t, le_t, re_t = sc[2], le[2], re[2]
        if mode3D:
            le_t, re_t = le[6], re[6]
        if sc is not None:
            if le is not None and re is not None:
                if abs(sc_t - le_t) < thresh:
                    if abs(sc_t - re_t) < thresh:
                        return True
            if le is not None and re is None:
                if abs(sc_t - le_t) < thresh:
                    return True
            if le is None and re is not None:
                if abs(sc_t - re_t) < thresh:
                    return True
        return False

    def __dict_to_list(self, dic):
        new_list = np.empty((dic[0].shape), float)
        for t in dic.keys():
            new_list = np.vstack((new_list, dic[t]))
        return new_list

    def get_targets_list(self):
        return self.__dict_to_list(self.targets)

    def get_l_centers_list(self):
        return self.__dict_to_list(self.l_centers)

    def get_r_centers_list(self):
        return self.__dict_to_list(self.r_centers)

    
    def store_data(self):
        path = os.getcwd() + "/data/user_" + uid + "/"
        if os.path.exists(path):


    def __check_or_create_path(self, uid):
        path = os.getcwd() + "/data/user_" + str(uid) + "/"
        while os.path.exists(path):
            uid += 1
            path = os.getcwd() + "/data/user_" + str(uid) + "/"