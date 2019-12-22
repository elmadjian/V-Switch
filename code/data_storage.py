import numpy as np 
import os

class Storer():
    '''
    Important:
    ---------
    -> 2D: x, y, time, 0, 0, 0, 0
    -> 3D: x_p, y_p, z_p, x_n, y_n, z_n, time
    '''

    def __init__(self, ntargets, target_list):
        self.ntargets = ntargets
        self.target_list = target_list
        self.targets, self.l_centers, self.r_centers = None, None, None
        self.t_imgs, self.l_imgs, self.r_imgs = None, None, None
        self.l_sess, self.r_sess, self.l_raw, self.r_raw = [],[],[],[]
        self.initialize_storage()
        self.scene, self.leye, self.reye = None, None, None
   
    def initialize_storage(self):
        self.targets   = {i:np.empty((0,2), dtype='float32') for i in range(self.ntargets)}
        self.l_centers = {i:np.empty((0,6), dtype='float32') for i in range(self.ntargets)}
        self.r_centers = {i:np.empty((0,6), dtype='float32') for i in range(self.ntargets)}
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
        #print('targets:', self.targets[idx])
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
        new_list = np.empty((0,dic[0].shape[1]), dtype='float32')
        for t in dic.keys():
            new_list = np.vstack((new_list, dic[t]))
        return new_list

    def get_targets_list(self):
        return self.__dict_to_list(self.targets)

    def get_l_centers_list(self, mode_3D):
        data = self.__dict_to_list(self.l_centers)
        if not mode_3D:
            data = np.array(data[:,:2])
        return data

    def get_r_centers_list(self,mode_3D):
        data = self.__dict_to_list(self.r_centers)
        if not mode_3D:
            data = np.array(data[:,:2])
        return data

    def append_session_data(self, l_gaze, r_gaze, l_raw, r_raw):
        self.l_sess.append(l_gaze)
        self.r_sess.append(r_gaze)
        self.l_raw.append(l_raw)
        self.r_raw.append(r_raw)

    
    def store_calibration(self):
        path = self.__check_or_create_path(1, 'calibration')
        for k in self.targets.keys():
            perc = int(k/len(self.targets.keys()) * 100)
            print(">>> {}%...".format(perc), end="\r", flush=True)
            c1, c2 = self.target_list[k]
            prefix = str(c1) + "_" + str(c2) + "_"
            # np.savez_compressed(path+prefix+ "img_scene", self.t_imgs[k])
            # np.savez_compressed(path+prefix+ "img_leye", self.l_imgs[k])
            # np.savez_compressed(path+prefix+ "img_reye", self.r_imgs[k])
            np.savez_compressed(path+prefix+ "tgt", self.targets[k])
            if len(self.l_centers[k]) > 0:
                np.savez_compressed(path+prefix+"leye", self.l_centers[k])
            if len(self.r_centers[k]) > 0:
                np.savez_compressed(path+prefix+"reye", self.r_centers[k])
        print("")

    def store_session(self):
        if len(self.l_sess) > 0:        
            print(">>> Saving session...")
            path = self.__check_or_create_path(1, 'session')
            np.savez_compressed(path+'_left_gaze', self.l_sess)
            np.savez_compressed(path+'_right_gaze', self.r_sess)
            np.savez_compressed(path+'_left_eye', self.l_raw)
            np.savez_compressed(path+'_right_eye', self.r_raw)
            print('>>> Session saved.')


    def __check_or_create_path(self, uid, kind):
        path = os.getcwd() + "/data/user_" + str(uid) + "/"+kind
        while os.path.exists(path):
            uid += 1
            path = os.getcwd() + "/data/user_"+str(uid)+"/"+kind
        os.makedirs(path)
        return path