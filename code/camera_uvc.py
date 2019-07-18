from PySide2.QtGui import QImage, QPixmap
from PySide2.QtCore import QObject, Signal, Slot, Property, QBasicTimer, QPoint
from PySide2.QtQuick import QQuickPaintedItem, QQuickImageProvider
import cv2
import numpy as np
import time
import uvc
from threading import Thread, Lock
from multiprocessing import Process, Pipe, Value

class Camera(QQuickImageProvider, QObject):

    def __init__(self):
        QObject.__init__(self)
        QQuickImageProvider.__init__(self, QQuickImageProvider.Image)
        self.__image = self.to_QImage(cv2.imread("../UI/test.jpg"))
        self.stop_capture = True
        self.dev_list = uvc.device_list()
        self.fps_res = {}
        self.modes = {}
        self.source = None
        self.cap = None
        

    def start(self):
        attempt  = 0
        attempts = len(self.cap.avaible_modes) 
        while not self.stop_capture and attempt < attempts:
            try:
                frame = self.cap.get_frame_robust()
                qimage = self.to_QImage(frame.bgr)
                if qimage is not None:
                    self.__image = qimage
            except Exception as e:
                attempt += 1
                self.__set_to_next_mode(attempt)
        self.cap.close()


    def requestImage(self, id, size, requestedSize):
        return self.__image

    def __set_to_next_mode(self, mode):
        print("resetting...")
        self.cap.close()
        time.sleep(0.4)
        self.cap = uvc.Capture(self.dev_list[self.source]['uid'])
        self.cap.frame_mode = self.cap.avaible_modes[mode]


    def stop(self):
        if not self.stop_capture:
            self.stop_capture = True
            self.cam_thread.join()


    def get_source(self):
        return self.source


    def set_source(self, source):
        print('setting camera source to', source)
        self.cap = uvc.Capture(self.dev_list[source]['uid'])
        self.__set_fps_modes()
        self.stop_capture = False
        self.source = source
        self.cam_thread = Thread(target=self.start, args=())
        self.cam_thread.start()


    def __set_fps_modes(self):
        for i in range(len(self.cap.avaible_modes)):
            mode = self.cap.avaible_modes[i]
            fps  = mode[2]
            if fps not in self.fps_res.keys():
                self.fps_res[fps] = []
                self.modes[fps]   = []
            resolution = str(mode[0]) + " x " + str(mode[1])
            self.modes[fps].append(mode)
            self.fps_res[fps].append(resolution)


    @Property('QVariantList')
    def fps_list(self):
        return sorted(list(self.fps_res.keys()))

    @Property('QVariantList')
    def modes_list(self):
        curr_fps = self.cap.frame_mode[2]
        return self.fps_res[curr_fps]

    @Property(int)
    def current_fps_index(self):
        curr_fps = self.cap.frame_mode[2]
        fps_list = sorted(list(self.fps_res.keys()))
        return fps_list.index(curr_fps)

    @Property(int)
    def current_res_index(self):
        w,h,fps  = self.cap.frame_mode
        curr_res = str(w) + " x " + str(h)
        res_list = self.fps_res[fps]
        return res_list.index(curr_res)

    @Slot(str, str)
    def set_mode(self, fps, resolution):
        self.stop()
        res = resolution.split('x')
        mode = (int(res[0]), int(res[1]), int(fps))
        self.cap = uvc.Capture(self.dev_list[self.source]['uid'])
        self.stop_capture = False
        if resolution in self.fps_res[int(fps)]:
            print("setting mode:", mode)
            self.cap.frame_mode = mode
        else:
            print("setting mode:", self.modes[int(fps)][0])
            self.cap.frame_mode = self.modes[int(fps)][0]
        self.cam_thread = Thread(target=self.start, args=())
        self.cam_thread.start()

    def to_QImage(self, img):
        if len(img.shape) == 3:
            w,h,_ = img.shape
            rgbimg = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            flipimg = cv2.flip(rgbimg,1)
            qimg = QImage(flipimg.data, h, w, QImage.Format_RGB888)
            return qimg

    # fps_list = Property(QVariantList, get_fps)
    # modes_list = Property(QVariantList, get_modes)
    

    


if __name__=="__main__":
    #cam = Camera(2)
    dev_list = uvc.device_list()
    cap = uvc.Capture(dev_list[2]['uid'])
    print(cap.avaible_modes)


