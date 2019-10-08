import numpy as np
import cv2
import unprojection
import intersection
import geometry

"""
Python code based on the one provided by Yiu Yuk Hoi, Seyed-Ahmad Ahmadi, and Moustafa Aboulatta
(https://github.com/pydsgz/DeepVOG)

"""

class EyeFitter():

    def __init__(self, focal_length, image_shape, sensor, eye_z=50, 
                 min_fit=15, max_fit=90):
        self.min_fit = min_fit
        self.max_fit = max_fit
        self.mm2px_scaling = None
        self.sensor_size = sensor
        self.update_mm2px_scaling(image_shape)
        self.focal_length = focal_length * self.mm2px_scaling
        self.pupil_radius = 2 * self.mm2px_scaling
        self.eye_z = eye_z * self.mm2px_scaling
        self.aver_eye_radius = None
        self.eyeball = None
        self.geo = geometry.Geometry(self.focal_length, self.eye_z)
        self.curr_state = {
            "gaze_pos": None,
            "gaze_neg": None,
            "pupil3D_pos": None,
            "pupil3D_neg": None,
            "ell_center": None
        }
        self.data = {
            "gaze_pos": np.empty((0,3), float),
            "gaze_neg": np.empty((0,3), float),
            "pupil3D_pos": np.empty((0,3), float),
            "pupil3D_neg": np.empty((0,3), float),
            "ell_center": np.empty((0,2), float)
        }

    
    def update_mm2px_scaling(self, image_shape):
        '''
        0.
        '''
        img_scaled = np.linalg.norm(image_shape)
        sensor_scaled = np.linalg.norm(self.sensor_size)
        self.mm2px_scaling = img_scaled / sensor_scaled
    

    def unproject_ellipse(self, ellipse, image):
        '''
        1.a. Unprojects a single ellipse observation from image
        1.b. "
        '''
        if ellipse is not None:
            ((xc,yc), (w,h), radian) = ellipse
            print('center:', xc, yc, 'w:', w, 'h:', h, 'angle:', radian)
            xc = xc - image.shape[1]/2
            yc = yc - image.shape[0]/2
            #print('data:', xc, yc, w, h, radian)
            ell_co = self.geo.convert_ellipse_to_general(xc,yc,w,h,radian)
            #print('ell_co:', ell_co)
            vertex = [0,0,-self.focal_length]
            unprojected = self.geo.unproject_gaze(vertex, ell_co, self.pupil_radius)
            #print("unprojected_pos:", unprojected[0], "\nunprojected_neg:", unprojected[1])
            #print('---------------\n')
            unprojected = self.__normalize_and_to_real(unprojected)
            self.__update_current_state(unprojected, [xc,yc])
        else:
            self.__update_current_state(None, None)


    def add_to_fitting(self):
        '''
        2.a. Stores single ellipse observations
        '''
        if self.curr_state['ell_center'] is not None:
            self.data['gaze_pos'] = np.vstack((self.data['gaze_pos'], 
                self.curr_state['gaze_pos'].reshape(1,3)))
            self.data['gaze_neg'] = np.vstack((self.data['gaze_neg'], 
                self.curr_state['gaze_neg'].reshape(1,3)))
            self.data['pupil3D_pos'] = np.vstack((self.data['pupil3D_pos'], 
                self.curr_state['pupil3D_pos'].reshape(1,3)))
            self.data['pupil3D_neg'] = np.vstack((self.data['pupil3D_neg'], 
                self.curr_state['pupil3D_neg'].reshape(1,3)))
            self.data['ell_center'] = np.vstack((self.data['ell_center'],
                self.curr_state['ell_center'].reshape(1,2)))


    def fit_projected_centers(self, max_iters=1000, min_distance=2000):
        '''
        3.a. Finds a model with intersection between ellipse coordinate
             center (a) and orientation (n)
        '''
        if len(self.data['ell_center']) % self.min_fit == 0:
            a = np.vstack((self.data['ell_center'], 
                           self.data['ell_center']))
            n = np.vstack((self.data['gaze_pos'][:,0:2],
                           self.data['gaze_neg'][:,0:2]))
            samples_to_fit = np.ceil(a.shape[0]/6).astype(np.int)
            #THIS SHOULD BE THREADED - HEAVY!
            self.proj_eyeball_center = self.geo.fit_ransac(a,n,
                                max_iters, samples_to_fit, min_distance)
        if len(self.data['ell_center']) >= self.max_fit:
            self.__dump_samples()
        

    def estimate_eye_sphere(self, image):
        '''
        4.a. Reconstructs 3D sphere
        '''
        if len(self.data['ell_center']) % self.min_fit == 0 and\
            self.proj_eyeball_center is not None:
            proj_eyeball_center = self.proj_eyeball_center.copy()
            proj_eyeball_center[0] -= image.shape[1]/2
            proj_eyeball_center[1] -= image.shape[0]/2
            proj_eyeball_scaled = self.geo.reverse_reproject(proj_eyeball_center)
            eyeball_cam = np.append(proj_eyeball_scaled, self.eye_z).reshape(3,1)
            sel_gazes, sel_positions, rad_counter = [], [], []
            for i in range(self.data['gaze_pos'].shape[0]):
                gazes = [self.data['gaze_pos'][i,:].reshape(3,1),
                        self.data['gaze_neg'][i,:].reshape(3,1)]
                positions = [self.data['pupil3D_pos'][i,:].reshape(3,1),
                            self.data['pupil3D_neg'][i,:].reshape(3,1)]
                gaze, position = self.select_pupil(gazes,positions,eyeball_cam)
                sel_gazes, sel_positions = self.__stack_nx1_to_mxn(gazes,
                            positions, gaze, position, [3,3])
            for i in range(sel_gazes.shape[0]):
                gaze = sel_gazes[i,:].reshape(1,3)
                position = sel_positions[i,:].reshape(1,3)
                a_3Dfit  = np.vstack((eyeball_cam.reshape(1,3), position))
                n_3Dfit  = np.vstack((gaze, (position/np.linalg.norm(position))))
                intersected_center = self.geo.intersect(a_3Dfit, n_3Dfit)
                radius   = np.linalg.norm(intersected_center-eyeball_cam)
                rad_counter.append(radius)
                self.aver_eye_radius = np.mean(rad_counter)
                self.eyeball = eyeball_cam
                return self.aver_eye_radius, rad_counter

         
    def gen_consistent_pupil(self):
        '''
        2.b. Generates gaze position, gaze, radius and pupil consistence
        '''
        if self.eyeball is not None:
            gazes = [self.curr_state['gaze_pos'], self.curr_state['gaze_neg']]
            posis = [self.curr_state['pupil3D_pos'],self.curr_state['pupil3D_neg']]
            gaze, position = self.select_pupil(gazes, posis, self.eyeball)
            o = np.zeros((3,1))
            try:
                norm_position = position / np.linalg.norm(position)
                d1,d2 = self.geo.line_sphere_intersect(self.eyeball, 
                            self.aver_eye_radius, o, norm_position)
                new_pos_min = o + min([d1,d2]) * norm_position
                new_pos_max = o + max([d1,d2]) * norm_position
                new_rad_min = (self.pupil_radius/position[2,0])*new_pos_min[2,0]
                new_rad_max = (self.pupil_radius/position[2,0])*new_pos_max[2,0]
                new_gaze_min = new_pos_min - self.eyeball
                new_gaze_min = new_gaze_min / np.linalg.norm(new_gaze_min)
                new_gaze_max = new_pos_max - self.eyeball
                new_gaze_max = new_gaze_max / np.linalg.norm(new_gaze_max)
                consistence = True
            except Exception:
                new_pos_min, new_pos_max = position, position
                new_gaze_min, new_gaze_max = gaze, gaze
                new_rad_min, new_rad_max = self.pupil_radius, self.pupil_radius
                consistence = False
            return [new_pos_min, new_pos_max],[new_gaze_min, new_gaze_max],\
                        [new_rad_min, new_rad_max], consistence            


    def select_pupil(self, gazes, positions, globe_center):
        sel_gaze = gazes[0]
        sel_position = positions[0]
        proj_center = self.geo.reproject(globe_center)
        proj_gaze = self.geo.reproject(sel_position+sel_gaze)
        proj_gaze -= proj_center
        proj_position = self.geo.reproject(sel_position)
        if np.dot(proj_gaze.T, (proj_position - proj_center)) > 0:
            return sel_gaze, sel_position
        else:
            return gazes[1], positions[1]


    def __update_current_state(self, unprojected_data, center):
        if unprojected_data is not None:
            norm_pos, norm_neg, tc_pos, tc_neg = unprojected_data
            self.curr_state['gaze_pos'] = norm_pos
            self.curr_state['gaze_neg'] = norm_neg
            self.curr_state['pupil3D_pos'] = tc_pos
            self.curr_state['pupil3D_neg'] = tc_neg
            self.curr_state['ell_center'] = np.array(center).reshape(2,1)
        else:
            for key in self.curr_state.keys():
                self.curr_state[key] = None            


    def __normalize_and_to_real(self, unprojected_data):
        norm_pos, norm_neg, tc_pos, tc_neg = unprojected_data
        norm_pos = norm_pos / np.linalg.norm(norm_pos)
        norm_neg = norm_neg / np.linalg.norm(norm_neg)
        norm_pos = np.real(norm_pos)
        norm_neg = np.real(norm_neg)
        tc_pos = np.real(tc_pos)
        tc_neg = np.real(tc_neg)
        return (norm_pos, norm_neg, tc_pos, tc_neg)    


    def __stack_nx1_to_mxn(self, gazes, positions, s_gaze, s_position, dim):
        list_as_array = np.array([[gazes, positions]])
        new_stacked_list = []
        if np.all(list_as_array == None):
            for stacked_array, stacked_vector, n in zip([gazes, positions],
                                                [s_gaze, s_position], dim):
                stacked_array = stacked_vector.reshape(1,n)
                new_stacked_list.append(stacked_array)
        elif np.all(list_as_array != None):
            for stacked_array, stacked_vector, n in zip([gazes, positions], 
                                                [s_gaze, s_position], dim):
                stacked_array = np.vstack((stacked_array, 
                                stacked_vector.reshape(1,n)))
                new_stacked_list.append(stacked_array)
        else:
            print("Data error")
        print("new_stacked_list: ", new_stacked_list)
        return new_stacked_list

    
    def __dump_samples(self, dump=30):
        for k in self.data.keys():
            self.data[k] = self.data[k][dump:]



