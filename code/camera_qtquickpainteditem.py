from PySide2.QtGui import QImage
from PySide2.QtCore import QObject, Signal, Slot, Property, QBasicTimer, QPoint
from PySide2.QtQuick import QQuickPaintedItem
import cv2
import numpy as np
import time
from threading import Thread

class Camera(QQuickPaintedItem):

    imageChanged = Signal()

    def __init__(self):
        QQuickPaintedItem.__init__(self)
        self.frame = None
        self.__image = QImage()
        self.stop_capture = False
        self.cap = cv2.VideoCapture()
        #self.cam_thread = Thread(target=self.start, args=(0,))
        #self.cam_thread.start()
        print("iniciei a thread...")
        self.timer = QBasicTimer()
        self.timer.start(60, self)

    #TEMPORARY (needs a proper class)
    def start(self, source):
        self.cap = cv2.VideoCapture(source)
        if self.cap.isOpened():
            print("entrei no loop")
            while not self.stop_capture:
                ret, frame = self.cap.read()
                if ret:
                    #PROCESSING STUFF
                    self.frame = frame
        #self.cap.release()
        print("saí da thread...")
        
    def paint(self, painter):
        image = self.__image.scaled(self.size().toSize())
        painter.drawImage(QPoint(), image)

    def timerEvent(self, event):
        if event.timerId() != self.timer.timerId():
            return
        self.set_image(self.frame)

    def get_image(self):
        return self.__image

    def set_image(self, image):
        if image is None:
            return
        img = self.to_QImage(image)
        self.__image = img
        self.imageChanged.emit()
        self.update()

    def to_QImage(self, img):
        if len(img.shape) == 3:
            w,h,_ = img.shape
            rgbimg = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            flipimg = cv2.flip(rgbimg,1)
            qimg = QImage(flipimg.data, h, w, QImage.Format_RGB888)
            return qimg

    @Slot(int)
    def set_camera_source(self, source):
        #self.stop_capture = True
        #self.cam_thread.join()
        self.stop_capture = False
        self.cam_thread = Thread(target=self.start, args=(source,))
        self.cam_thread.start()
        

    image = Property(QImage, get_image, set_image, notify=imageChanged)
    

