import numpy as np
import cv2
import unprojection
import intersection
from .draw_ellipse import fit_ellipse_compact, fit_ellipse
from .unprojection import convert_ell_to_general, unprojectGazePositions, reproject, reverse_reproject
from .intersection import NoIntersectionError, intersect, fit_ransac, line_sphere_intersect
from .CheckEllipse import computeEllipseConfidence

"""
Unless specified, all units are in pixels. 
All calculations are in camera frame (conversion would be commented)

Python code based on the one provided by Yiu Yuk Hoi, Seyed-Ahmad Ahmadi, and Moustafa Aboulatta
(https://github.com/pydsgz/DeepVOG)

"""


class SingleEyeFitter(object):

    def __init__(self, focal_length, pupil_radius, initial_eye_z, image_shape=(640, 480)):
        self.focal_length = focal_length
        self.image_shape = image_shape

        self.pupil_radius = pupil_radius
        self.vertex = [0, 0, -focal_length]
        self.initial_eye_z = initial_eye_z

        # (p,n) of unprojected gaze vector and pupil 3D position in SINGLE OBSERVATION
        self.current_gaze_pos = 0  # reserved for (3,1) np.array in camera frame
        self.current_gaze_neg = 0  # reserved for (3,1) np.array in camera frame
        self.current_pupil_3Dcenter_pos = 0  # reserved for (3,1) np.array in camera frame
        self.current_pupil_3Dcenter_neg = 0  # reserved for (3,1) np.array in camera frame
        self.current_ellipse_center = 0  # reserved for numpy array (2,1) in numpy indexing frame

        # List of parameters across a number (m) of observations
        self.unprojected_gaze_vectors = []  # A list: ["gaze_positive"~np(m,3), "gaze_negative"~np(m,3)]
        self.unprojected_3D_pupil_positions = []  # [ "pupil_3Dcenter_positive"~np(m,3), "pupil_3Dcenter_negative"~np(m,3) ]
        self.ellipse_centers = None  # reserved for numpy array (m,2) in numpy indexing frame,
        # m = number of fitted ellipse centers corresponding to the projected gaze lines
        self.selected_gazes = None  # reserved for (m,3) np.array in camera frame
        self.selected_pupil_positions = None  # reserved for (m,3) np.array in camera frame

        # Parameters of the eye model for consistent pupil estimate after initialisation
        self.projected_eye_center = None  # reserved for numpy array (2,1). center coordinate in numpy indexing frame.
        self.eye_center = None  # reserved for (3,1) numpy array. 3D center coordinate in camera frame
        self.aver_eye_radius = None  # Scaler

        # Results of consistent pupil estimate
        self.pupil_new_position_max = None  # numpy array (3,1)
        self.pupil_new_position_min = None  # numpy array (3,1)
        self.pupil_new_radius_max = None  # scalar
        self.pupil_new_radius_min = None  # scalar
        self.pupil_new_gaze_max = None  # numpy array (3,1)
        self.pupil_new_gaze_min = None  # numpy array (3,1)


    def unproject_single_observation(self, ellipse):
        # We unproject the gaze vectors and pupil center only if an ellipse has been detected
        if ellipse is not None:
            (center, (w, h), radian) = ellipse

            # Convert center coordinates from numpy indexing frame to camera frames
            xc, yc = center
            xc = xc - self.image_shape[1] / 2
            yc = yc - self.image_shape[0] / 2

            # Convert ellipse parameters to the coefficients of the general form of ellipse equation
            A, B, C, D, E, F = unprojection.convert_ell_to_general(xc,yc,w,h,radian)
            ell_co = (A, B, C, D, E, F)

            # Unproject the ellipse to obtain 2 ambiguous gaze vectors with numpy shape (3,1),
            # and pupil_center with numpy shape (3,1)
            unprojected_data = unprojection.unprojectGazePositions(self.vertex, ell_co, self.pupil_radius)
            unp_gaze_pos, unp_gaze_neg, unp_pupil_3D_pos, unp_pupil_3D_neg = unprojected_data 

            # Normalize the gaze vectors and only take their real component
            unp_gaze_pos = unp_gaze_pos / np.linalg.norm(unp_gaze_pos)
            unp_gaze_neg = unp_gaze_neg / np.linalg.norm(unp_gaze_neg)

            unp_gaze_pos, unp_gaze_neg, unp_pupil_3D_pos, unp_pupil_3D_neg = np.real(
                unp_gaze_pos), np.real(unp_gaze_neg), np.real(unp_pupil_3D_pos), np.real(
                unp_pupil_3D_neg)
            self.current_gaze_pos = unp_gaze_pos
            self.current_gaze_neg = unp_gaze_neg
            self.current_pupil_3Dcenter_pos = unp_pupil_3D_pos
            self.current_pupil_3Dcenter_neg = unp_pupil_3D_neg
            self.current_ellipse_center = np.array(center).reshape(2, 1)
        else:
            self.current_gaze_pos = None
            self.current_gaze_neg = None
            self.current_pupil_3Dcenter_pos = None
            self.current_pupil_3Dcenter_neg = None
            self.current_ellipse_center = None


    def add_to_fitting(self):
        # Append parameterised gaze lines for fitting
        if (self.current_gaze_pos is None) or (self.current_gaze_neg is None) or (
                self.current_pupil_3Dcenter_pos is None) or (self.current_pupil_3Dcenter_neg is None) or (
                self.current_ellipse_center is None):
            raise TypeError(
                'No ellipse was caught in this observation, thus "None" is being added for fitting set, which is not allowed. Please manually skip this condition.')

        # Store the gaze vectors and pupil 3D centers
        if (len(self.unprojected_gaze_vectors) == 0) or (len(self.unprojected_3D_pupil_positions) == 0) or (
                self.ellipse_centers is None):
            self.unprojected_gaze_vectors.append(self.current_gaze_pos.reshape(1, 3))
            self.unprojected_gaze_vectors.append(self.current_gaze_neg.reshape(1, 3))
            self.unprojected_3D_pupil_positions.append(self.current_pupil_3Dcenter_pos.reshape(1, 3))
            self.unprojected_3D_pupil_positions.append(self.current_pupil_3Dcenter_neg.reshape(1, 3))
            self.ellipse_centers = self.current_ellipse_center.reshape(1, 2)
        else:
            self.unprojected_gaze_vectors[0] = np.vstack(
                (self.unprojected_gaze_vectors[0], self.current_gaze_pos.reshape(1, 3)))
            self.unprojected_gaze_vectors[1] = np.vstack(
                (self.unprojected_gaze_vectors[1], self.current_gaze_neg.reshape(1, 3)))
            self.unprojected_3D_pupil_positions[0] = np.vstack(
                (self.unprojected_3D_pupil_positions[0], self.current_pupil_3Dcenter_pos.reshape(1, 3)))
            self.unprojected_3D_pupil_positions[1] = np.vstack(
                (self.unprojected_3D_pupil_positions[1], self.current_pupil_3Dcenter_neg.reshape(1, 3)))
            self.ellipse_centers = np.vstack((self.ellipse_centers, self.current_ellipse_center.reshape(1, 2)))


    def fit_projected_eye_center(self, ransac=False, max_iters=1000, min_distance=2000):
        # You will need to determine when to fit outside of the class
        if (self.unprojected_gaze_vectors is None) or (self.ellipse_centers is None):
            msg = "No unprojected gaze lines or ellipse centers were found (not yet initalized). It is likely that the network fails to segment the pupil from the video. Please ensure your input video contains only a single eye but not other facial/body features."
            raise TypeError(msg)

        # Combining positive and negative gaze vectors
        a = np.vstack((self.ellipse_centers, self.ellipse_centers))
        n = np.vstack((self.unprojected_gaze_vectors[0][:, 0:2],
                       self.unprojected_gaze_vectors[1][:, 0:2]))  # [:, 0:2] takes only 2D projection

        # Normalisation of the 2D projection of gaze vectors is done inside intersect()
        if ransac == True:
            samples_to_fit = np.ceil(a.shape[0]/5).astype(np.int)  # Assuming 20% of outliners
            self.projected_eye_center = intersection.fit_ransac(a, n, max_iters, 
                                                                samples_to_fit, min_distance)
        else:
            self.projected_eye_center = intersection.intersect(a, n)
        if (self.projected_eye_center is None):
            raise TypeError("Projected_eye_center was not fitted. You may need -v and -m argument to check whether the pupil segmentation works properly.")
        return self.projected_eye_center

    def estimate_eye_sphere(self):
        # This function is called once after fit_projected_eye_center()
        # self.initial_eye_z is required (in pixel unit)
        # self.initial_eye_z shall be the z-distance between the point and camera vertex (in camera frame)
        if (self.projected_eye_center is None):
            # pdb.set_trace()
            raise TypeError('Projected_eye_center must be initialized first')

        # Unprojecting the 2D projected eye center to 3D.
        # Converting the projected_eye_center from numpy indexing frame to camera frame
        projected_eye_center_camera_frame = self.projected_eye_center.copy()
        projected_eye_center_camera_frame[0] = projected_eye_center_camera_frame[0] - self.image_shape[1] / 2
        projected_eye_center_camera_frame[1] = projected_eye_center_camera_frame[1] - self.image_shape[0] / 2

        # Unprojection: Nearest intersection of two lines. 
        # a = [eye_center, pupil_3Dcenter], n =[gaze_vector, pupil_3D_center]
        projected_eye_center_camera_frame_scaled = unprojection.reverse_reproject(projected_eye_center_camera_frame,
                                                                     self.initial_eye_z, self.focal_length)
        eye_center_camera_frame = np.append(projected_eye_center_camera_frame_scaled, self.initial_eye_z).reshape(3, 1)

        # Reconstructed selected gaze vectors and pupil positions by rejecting those pointing away from projected eyecenter
        m = self.unprojected_gaze_vectors[0].shape[0]
        for i in range(m):
            gazes = [self.unprojected_gaze_vectors[0][i, :].reshape(3, 1),
                     self.unprojected_gaze_vectors[1][i, :].reshape(3, 1)]
            positions = [self.unprojected_3D_pupil_positions[0][i, :].reshape(3, 1),
                         self.unprojected_3D_pupil_positions[1][i, :].reshape(3, 1)]
            selected_gaze, selected_position = self.select_pupil_from_single_observation(gazes, positions,
                                                                                         eye_center_camera_frame)

            self.selected_gazes, self.selected_pupil_positions = self.stacking_from_nx1_to_mxn(
                [self.selected_gazes, self.selected_pupil_positions],
                [selected_gaze, selected_position],
                [3, 3])

        radius_counter = []
        for i in range(self.selected_gazes.shape[0]):
            gaze = self.selected_gazes[i, :].reshape(1, 3)
            position = self.selected_pupil_positions[i, :].reshape(1, 3)

            # Before stacking, you must reshape (3,1) to (1,3)
            a_3Dfitting = np.vstack((eye_center_camera_frame.reshape(1, 3), position))
            n_3Dfitting = np.vstack((gaze, (position / np.linalg.norm(position))))

            intersected_pupil_3D_center = intersection.intersect(a_3Dfitting, n_3Dfitting)
            radius = np.linalg.norm(intersected_pupil_3D_center - eye_center_camera_frame)
            radius_counter.append(radius)
        aver_radius = np.mean(radius_counter)

        self.aver_eye_radius = aver_radius
        self.eye_center = eye_center_camera_frame
        return aver_radius, radius_counter

    def gen_consistent_pupil(self):
        # This function must be called after using unproject_single_observation() to update surrent observation
        if (self.eye_center is None) or (self.aver_eye_radius is None):
            raise TypeError("Call estimate_eye_sphere() to initialize eye_center and eye_radius first.")
        else:
            selected_gaze, selected_position = self.select_pupil_from_single_observation(
                [self.current_gaze_pos, self.current_gaze_neg],
                [self.current_pupil_3Dcenter_pos, self.current_pupil_3Dcenter_neg], self.eye_center)
            o = np.zeros((3, 1))

            try:
                d1, d2 = intersection.line_sphere_intersect(self.eye_center, self.aver_eye_radius, o,
                                               selected_position / np.linalg.norm(selected_position))
                new_position_min = o + min([d1, d2]) * (selected_position / np.linalg.norm(selected_position))
                new_position_max = o + max([d1, d2]) * (selected_position / np.linalg.norm(selected_position))
                new_radius_min = (self.pupil_radius / selected_position[2, 0]) * new_position_min[2, 0]
                new_radius_max = (self.pupil_radius / selected_position[2, 0]) * new_position_max[2, 0]

                new_gaze_min = new_position_min - self.eye_center
                new_gaze_min = new_gaze_min / np.linalg.norm(new_gaze_min)

                new_gaze_max = new_position_max - self.eye_center
                new_gaze_max = new_gaze_max / np.linalg.norm(new_gaze_max)
                self.pupil_new_position_min, self.pupil_new_position_max = new_position_min, new_position_max
                self.pupil_new_radius_min, self.pupil_new_radius_max = new_radius_min, new_radius_max
                self.pupil_new_gaze_min, self.pupil_new_gaze_max = new_gaze_min, new_gaze_max
                consistence = True

            except(NoIntersectionError):
                # print("Cannot find line-sphere interception. Old pupil parameters are used.")
                new_position_min, new_position_max = selected_position, selected_position
                new_gaze_min, new_gaze_max = selected_gaze, selected_gaze
                new_radius_min, new_radius_max = self.pupil_radius, self.pupil_radius
                consistence = False

            return [new_position_min, new_position_max], [new_gaze_min, new_gaze_max], [new_radius_min,
                                                                                        new_radius_max], consistence

    def plot_gaze_lines(self, ax):
        t = np.linspace(-1000, 1000, 1000)
        a = np.vstack((self.ellipse_centers, self.ellipse_centers))
        n = np.vstack((self.unprojected_gaze_vectors[0][:, 0:2],
                       self.unprojected_gaze_vectors[1][:, 0:2]))  # [:, 0:2] takes only 2D projection

        for i in range(a.shape[0]):
            a_each = a[i, :]
            n_each = n[i, :]

            points = np.array(a_each).reshape(2, 1) + (t * n_each[0:2].reshape(2, 1))
            ax.plot(points[0, :], points[1, :])
        ax.set_xlim(0, self.image_shape[1])
        ax.set_ylim(self.image_shape[0], 0)
        return ax

    def select_pupil_from_single_observation(self, gazes, positions, eye_center_camera_frame):
        # gazes is a list ~ [gaze_vector_pos~(3,1), gaze_vector_neg~(3,1)]
        # positions is a list ~ [pupil_position_pos~(3,1), pupil_position_neg~(3,1)]
        # eye_center_camera_frame ~ numpy array~(3,1)

        selected_gaze = gazes[0]
        selected_position = positions[0]
        projected_center = unprojection.reproject(eye_center_camera_frame, self.focal_length)
        projected_gaze = unprojection.reproject(selected_position + selected_gaze, self.focal_length) - projected_center
        projected_position = unprojection.reproject(selected_position, self.focal_length)
        if np.dot(projected_gaze.T, (projected_position - projected_center)) > 0:
            return selected_gaze, selected_position
        else:
            return gazes[1], positions[1]

    @staticmethod
    def stacking_from_nx1_to_mxn(stacked_arrays_list, stacked_vectors_list, dims_list):
        list_as_array = np.array([stacked_arrays_list])
        new_stacked_arrays_list = []
        if np.all(list_as_array == None):
            for stacked_array, stacked_vector, n in zip(stacked_arrays_list, stacked_vectors_list, dims_list):
                stacked_array = stacked_vector.reshape(1, n)
                new_stacked_arrays_list.append(stacked_array)
        elif np.all(list_as_array != None):
            for stacked_array, stacked_vector, n in zip(stacked_arrays_list, stacked_vectors_list, dims_list):
                stacked_array = np.vstack((stacked_array, stacked_vector.reshape(1, n)))
                new_stacked_arrays_list.append(stacked_array)
        elif np.any(list_as_array == None):
            print("Error list =\n", stacked_arrays_list)
            raise TypeError("Some lists are initialized, some are not ('None'). Error has happened!")
        else:
            print("Error list =\n", stacked_arrays_list)
            raise TypeError("Unknown Error Occurred.")
        return new_stacked_arrays_list
