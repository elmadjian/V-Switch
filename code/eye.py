import cv2
import time
import numpy as np
import camera_proc as camera
import tracker
import sys 
from matplotlib import pyplot as plt
from eye_img_processor import EyeImageProcessor


class EyeCamera(camera.Camera):

    def __init__(self, mode=(400,400,120)):
        super().__init__()
        self.mode = mode
        self.cam_process = None

    def init_process(self, source, pipe, queue, mode):
        self.cam_process = EyeImageProcessor(source, mode, pipe, queue)
        self.cam_process.start()    

    def join_process(self):
        self.cam_process.join(1)



            

