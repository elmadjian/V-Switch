import cv2
import numpy as np
import time
import sys
import camera_proc as camera
from scene_img_processor import SceneImageProcessor


class SceneCamera(camera.Camera):

    def __init__(self, mode=(640,480,30)):
        super().__init__()
        self.mode = mode
        self.cam_process = None

    def init_process(self, source, pipe, queue, mode):
        self.cam_process = SceneImageProcessor(source, mode, pipe, queue)
        self.cam_process.start()    

    def join_process(self):
        self.cam_process.join(1)
        


