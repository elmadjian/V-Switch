from PySide2.QtGui import QImage, QPixmap
from PySide2.QtCore import QObject, Signal, Slot, Property, QBasicTimer, QPoint
from PySide2.QtQuick import QQuickPaintedItem, QQuickImageProvider
import cv2
import numpy as np
import time
import uvc
from threading import Thread, Lock
from multiprocessing import Process, Pipe, Value, Condition, Array
import sys
import traceback
import ctypes

class Camera(QQuickImageProvider, QObject):

    update_image = Signal()

    def __init__(self):
        QQuickImageProvider.__init__(self, QQuickImageProvider.Image)
        QObject.__init__(self)
        self.__image = self.to_QImage(cv2.imread("../UI/test.jpg"))
        self.__pos_data = None
        self.capturing = False
        self.dev_list = uvc.device_list()
        self.fps_res = {}
        self.modes = {}
        self.mode = None         # --> subclassed property
        self.shared_array = None # --> subclassed property
        self.source = None
        self.cap = None
        self.pipe, self.child = Pipe()
        self.cam_process = None
        self.cam_thread = None

    def thread_loop(self):
        while self.capturing:
            time.sleep(0.033)
            img = self.__get_shared_np_array()
            qimage = self.to_QImage(img)
            if qimage is not None:
                self.__image = qimage
                self.update_image.emit()

    def __get_shared_np_array(self):
        nparray = np.frombuffer(self.shared_array, dtype=ctypes.c_uint8)
        w, h = self.mode[0], self.mode[1]
        return nparray.reshape((h,w,3))
    
    def requestImage(self, id, size, requestedSize):
        return self.__image

    def get_processed_data(self):
        return self.__pos_data

    def init_process(self, source, pipe, mode): #abstract
        return 

    def join_process(self): #abstract
        return

    def stop(self):
        if self.capturing:
            self.pipe.send("stop")
            self.join_process()
            if self.cam_process.is_alive():
                self.cam_process.terminate()
            self.capturing = False
            self.cam_thread.join(1)

    def get_source(self):
        return self.source
    
    def is_cam_active(self):
        if self.cam_thread is not None:
            if self.cam_thread.is_alive():
                return True
        return False

    def set_source(self, source):
        print('setting camera source to', source)
        self.source = source
        self.__set_fps_modes()
        self.capturing = True
        self.init_process(source, self.child, self.shared_array, self.mode)
        self.cam_thread = Thread(target=self.thread_loop, args=())
        self.cam_thread.start()

    def __set_fps_modes(self):
        self.fps_res, self.modes = {}, {}
        dev_list = uvc.device_list()
        cap = uvc.Capture(dev_list[self.source]['uid'])
        for i in range(len(cap.avaible_modes)):
            mode = cap.avaible_modes[i]
            fps  = mode[2]
            if fps not in self.fps_res.keys():
                self.fps_res[fps] = []
                self.modes[fps]   = []
            resolution = str(mode[0]) + " x " + str(mode[1])
            self.modes[fps].append(mode)
            self.fps_res[fps].append(resolution)
        cap.close()

    @Property('QVariantList')
    def fps_list(self):
        return sorted(list(self.fps_res.keys()))

    @Property('QVariantList')
    def modes_list(self):
        curr_fps = self.mode[2]
        return self.fps_res[curr_fps]

    @Property(int)
    def current_fps_index(self):
        curr_fps = self.mode[2]
        fps_list = sorted(list(self.fps_res.keys()))
        return fps_list.index(curr_fps)

    @Property(int)
    def current_fps(self):
        curr_fps = self.mode[2]
        return curr_fps

    @Property(int)
    def current_res_index(self):
        w,h,fps  = self.mode
        curr_res = str(w) + " x " + str(h)
        res_list = self.fps_res[fps]
        return res_list.index(curr_res)

    @Slot(str, str)
    def set_mode(self, fps, resolution):
        self.stop()
        res  = resolution.split('x')
        self.mode = (int(res[0]), int(res[1]), int(fps))
        self.__set_fps_modes()
        print("setting mode:", self.mode)
        if resolution not in self.fps_res[int(fps)]:
            print("setting mode:", self.modes[int(fps)][0])
            self.mode = self.modes[int(fps)][0]
        self.capturing = True
        self.init_process(self.source, self.child, self.shared_array, self.mode)
        self.cam_thread = Thread(target=self.thread_loop, args=())
        self.cam_thread.start()

    @Slot(float)
    def set_gamma(self, value):
        self.pipe.send("gamma")
        self.pipe.send(value)

    @Slot(float)
    def set_color(self, value):
        self.pipe.send("color")
        self.pipe.send(bool(value))


    def to_QImage(self, img):
        if len(img.shape) == 3:
            w,h,_ = img.shape
            rgbimg = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            #flipimg = cv2.flip(rgbimg,1)
            qimg = QImage(rgbimg.data, h, w, QImage.Format_RGB888)
            return qimg
    


if __name__=="__main__":
    cam = Camera()
    cam.set_source(0)
    cam.start()
    # dev_list = uvc.device_list()
    # cap = uvc.Capture(dev_list[2]['uid'])
    # print(cap.avaible_modes)


