from PySide2.QtGui import QImage
from PySide2.QtCore import QObject, Signal, Slot, Property, QBasicTimer, QPoint
from PySide2.QtQuick import QQuickPaintedItem
import cv2
import numpy as np
import time
from threading import Thread
from multiprocessing import Process, Pipe, Value

class Camera(QObject, Thread):

    imageChanged = Signal(np.ndarray)

    def __init__(self, source):
        QObject.__init__(self)
        Thread.__init__(self)
        self.__image = None
        self.parent, child = Pipe()
        self.cam_process = Process(target=self.capture, args=(source, child,))
        self.cam_process.start()


    #TEMPORARY (needs a proper class)
    def capture(self, source, pipe):
        cap = cv2.VideoCapture(source)
        while not cap.isOpened():
            source = (source + 1) % 10
            time.sleep(0.5)
            cap = cv2.VideoCapture(source)
        while True:
            ret, frame = cap.read()
            if ret:
                #PROCESSING STUFF
                pipe.send(frame)
            if pipe.poll():
                break
        cap.release()

    def run(self):
        while True:
            img = self.parent.recv()
            self.set_image(img)
        
    def get_image(self):
        return self.__image

    def set_image(self, image):
        self.__image = image


    @Slot(int)
    def set_camera_source(self, source):
        self.parent.send("stop_capture")
        self.cam_process.join()
        self.cam_process = Process(target=self.capture, args=(source, child,))
        self.cam_process.start()
        
    image = Property(np.ndarray, get_image, set_image, notify=imageChanged)
    

#-------------------------------------------------------------------------
class QMLCamera(QQuickPaintedItem):

    def __init__(self):
        QQuickPaintedItem.__init__(self)
        img = cv2.imread("../UI/test.jpg")
        self.__image = self.to_QImage(img)

    def paint(self, painter):
        image = self.__image.scaled(self.size().toSize())
        painter.drawImage(QPoint(), image)

    @Slot(np.ndarray)
    def set_image(self, image):
        if image is None:
            return
        image = self.to_QImage(image)
        self.__image = image
        self.update()

    def to_QImage(self, img):
        if len(img.shape) == 3:
            w,h,_ = img.shape
            rgbimg = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            flipimg = cv2.flip(rgbimg,1)
            qimg = QImage(flipimg.data, h, w, QImage.Format_RGB888)
            return qimg

#-------------------------------------------------------------------------
class QMLCamera2(QQuickPaintedItem):

    def __init__(self):
        QQuickPaintedItem.__init__(self)
        img = cv2.imread("../UI/test.jpg")
        self.__image = self.to_QImage(img)

    def paint(self, painter):
        image = self.__image.scaled(self.size().toSize())
        painter.drawImage(QPoint(), image)

    @Slot(np.ndarray)
    def set_image(self, image):
        if image is None:
            return
        image = self.to_QImage(image)
        self.__image = image
        self.update()

    def to_QImage(self, img):
        if len(img.shape) == 3:
            w,h,_ = img.shape
            rgbimg = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            flipimg = cv2.flip(rgbimg,1)
            qimg = QImage(flipimg.data, h, w, QImage.Format_RGB888)
            return qimg

