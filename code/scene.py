import cv2
import numpy as np
import time
import sys
from PySide2.QtCore import Signal, Slot, Property
import camera_proc as camera


class SceneCamera(camera.Camera):

    def __init__(self, calibration=None, mode=(1024,768,30)):
        super().__init__()
        self.cam_calibration = calibration
        self.gray = None
        self.mode = mode
        dict4 = cv2.aruco.DICT_4X4_50
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(dict4)

    
    def process(self, img):
        height, width = img.shape[0], img.shape[1]
        corners, ids, reject = cv2.aruco.detectMarkers(img, self.aruco_dict)
        target_pos, detected = None, False
        if ids is not None:
            cv2.aruco.drawDetectedMarkers(img, corners, ids)
            mean = np.mean(corners[0][0], axis=0)
            x = mean[0]/width
            y = mean[1]/height
            target_pos = [np.array([x,y], float), time.monotonic()]
        return img, target_pos
        


