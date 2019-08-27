import cv2
import numpy as np
import img_processor as imp
import time

class SceneImageProcessor(imp.ImageProcessor):

    def __init__(self, source, mode, pipe, array, pos):
        super().__init__(source, mode, pipe, array, pos)
        

    def process(self, img):
        height, width = img.shape[0], img.shape[1]
        dict4 = cv2.aruco.DICT_4X4_50
        aruco_dict = cv2.aruco.getPredefinedDictionary(dict4)
        corners, ids,_ = cv2.aruco.detectMarkers(img, aruco_dict)
        target_pos,_ = None, False
        if ids is not None:
            cv2.aruco.drawDetectedMarkers(img, corners, ids)
            mean = np.mean(corners[0][0], axis=0)
            x = mean[0]/width
            y = mean[1]/height
            target_pos = np.array([x, y, time.monotonic()], float)
        return img, target_pos