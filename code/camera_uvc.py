from PySide2.QtGui import QImage, QPixmap
from PySide2.QtCore import QObject, Signal, Slot, Property, QBasicTimer, QPoint
from PySide2.QtQuick import QQuickPaintedItem, QQuickImageProvider
import cv2
import numpy as np
import time
import uvc
from threading import Thread
from multiprocessing import Process, Pipe, Value

class Camera(QQuickImageProvider, QObject):

    def __init__(self, source):
        QObject.__init__(self)
        QQuickImageProvider.__init__(self, QQuickImageProvider.Image)
        self.source = source
        self.__image = self.to_QImage(cv2.imread("../UI/test.jpg"))
        self.stop_capture = False
        self.cam_thread = Thread(target=self.start, args=())
        self.cam_thread.start()
        
    def start(self):
        dev_list = uvc.device_list()
        cap = uvc.Capture(dev_list[self.source]['uid'])
        attempts = len(cap.avaible_modes)-1
        while attempts > 0 and not self.stop_capture:
            try:
                cap.frame_mode = cap.avaible_modes[attempts]
                while not self.stop_capture:
                    frame = cap.get_frame_robust()
                    qimage = self.to_QImage(frame.bgr)
                    if qimage is not None:
                        self.__image = qimage
            except Exception as e:
                attempts -= 1
                cap = None

    def requestImage(self, id, size, requestedSize):
        return self.__image

    def stop(self):
        self.stop_capture = True
        self.cam_thread.join()

    def get_source(self):
        return self.source

    def set_source(self, source):
        print('setting camera source to', source)
        self.stop_capture = False
        self.source = source
        self.cam_thread = Thread(target=self.start, args=())
        self.cam_thread.start()

    def to_QImage(self, img):
        if len(img.shape) == 3:
            w,h,_ = img.shape
            rgbimg = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            flipimg = cv2.flip(rgbimg,1)
            qimg = QImage(flipimg.data, h, w, QImage.Format_RGB888)
            return qimg


if __name__=="__main__":
    cam = Camera(2)


