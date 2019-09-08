import cv2
import numpy as np
import time
import sys
import camera_proc as camera
from scene_img_processor import SceneImageProcessor
from multiprocessing import Array
import ctypes


class SceneCamera(camera.Camera):

    def __init__(self, mode=(1024,768,30)):
        super().__init__()
        self.mode = mode
        self.cam_process = None
        self.shared_array = self.create_shared_array(mode)
        self.shared_pos = self.create_shared_pos()

    def init_process(self, source, pipe, array, pos, mode, cap):
        self.cam_process = SceneImageProcessor(source, mode, pipe, 
                                               array, pos, cap)
        self.cam_process.start()    

    def join_process(self):
        self.cam_process.join(1)

    def create_shared_array(self, mode):
        w = mode[0]
        h = mode[1]
        return Array(ctypes.c_uint8, h*w*3, lock=False)

    def create_shared_pos(self):
        return Array(ctypes.c_float, 3, lock=False)
        


