import uvc
from multiprocessing import Process, Pipe, Array
import traceback
import cv2
import sys
import time
import numpy as np
import ctypes


class ImageProcessor(Process):

    def __init__(self, source, mode, pipe, array, pos):
        Process.__init__(self)
        self.eye_cam = False
        self.source = source
        self.mode = mode
        self.pipe = pipe
        self.shared_array = array
        self.shared_pos = pos
    
    def __get_shared_np_array(self):
        nparray = np.frombuffer(self.shared_array, dtype=ctypes.c_uint8)
        w, h = self.mode[0], self.mode[1]
        return nparray.reshape((h,w,3))

    def __adjust_gamma(self, img, gamma):
        lut = np.empty((1,256), np.uint8)
        for i in range(256):
            lut[0,i] = np.clip(pow(i/255.0, gamma) * 255.0, 0, 255)
        return cv2.LUT(img, lut)

    def __cvtBlackWhite(self, img, color):
        if color:
            return img
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    def __reset_mode(self, cap):
        print("resetting...")
        mode = cap.frame_mode
        cap.close()
        time.sleep(0.4)
        dev_list = uvc.device_list()
        cap = uvc.Capture(dev_list[self.source]['uid'])
        print("MODE:", mode)
        cap.frame_mode = mode
        cap.bandwidth_factor = 1.3

    def __setup_eye_cam(self, cap):
        if self.eye_cam:
            print('changing eye cam settings')
            controls_dict = dict([(c.display_name, c) for c in cap.controls])
            controls_dict['Auto Exposure Mode'].value = 1
            controls_dict['Gamma'].value = 200

    def run(self):
        dev_list = uvc.device_list()
        cap = uvc.Capture(dev_list[self.source]['uid'])
        self.__setup_eye_cam(cap)
        cap.frame_mode = self.mode
        cap.bandwidth_factor = 1.3
        attempt, attempts = 0, 8
        gamma, color = 1, True 
        while attempt < attempts:      
            try:
                frame    = cap.get_frame()
                img      = self.__adjust_gamma(frame.bgr, gamma)
                img      = self.__cvtBlackWhite(img, color)
                img, pos = self.process(img)                
                if img is not None:
                    shared_img = self.__get_shared_np_array()
                    shared_pos = np.frombuffer(self.shared_pos, 
                                               dtype=ctypes.c_float)
                    np.copyto(shared_img, img)
                    if pos is not None:
                        np.copyto(shared_pos, pos)
            except Exception as e:
                print(e)
                traceback.print_exc(file=sys.stdout)
                self.__reset_mode(cap)
                attempt += 1               
            if self.pipe.poll():
                msg = self.pipe.recv()
                if msg == "stop":
                    cap.stop_stream()
                    break
                elif msg == "gamma":
                    gamma = self.pipe.recv()
                elif msg == "color":
                    color = self.pipe.recv()
        cap.close()
        print("camera", self.source, "closed")


    def process(self, frame):
        return frame, None
    
