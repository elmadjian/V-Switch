from PySide2.QtGui import QImage, QPixmap
from PySide2.QtCore import QObject, Signal, Slot, Property, QBasicTimer, QPoint
from PySide2.QtQuick import QQuickPaintedItem
import cv2
import numpy as np
import time
from threading import Thread
from multiprocessing import Process, Pipe, Value

class Camera(QObject):

    def __init__(self, source):
        QObject.__init__(self)
        self.source = source
        self.__image = None
        self.stop_capture = False
        # self.cam_thread = Thread(target=self.start, args=())
        # self.cam_thread.start()

    #TEMPORARY (needs a proper class)
    def start(self):
        cap = cv2.VideoCapture(self.source)
        img = cv2.imread("../UI/test.jpg")
        while not cap.isOpened() and self.source < 10:
            self.source += 1
            time.sleep(0.2)
            cap = cv2.VideoCapture(self.source)
            print("tentando novo input...")
        print("entrei no loop")
        while not self.stop_capture:
            ret, frame = cap.read()
            if ret:
                #PROCESSING STUFF
                self.__image = img
        cap.release()
        print("sai do loop")

    def get_image(self):
        return self.__image

    def set_image(self, image):
        self.__image = image

    @Signal
    def image_changed(self):
        scene_image.emit()

    @Slot(int)
    def set_camera_source(self, source):
        pass
        # self.stop_capture = True
        # self.cam_thread.join()
        # self.stop_capture = False
        # self.source = source
        # self.cam_thread = Thread(target=self.start, args=())
        # self.cam_thread.start()

    scene_image = Property(np.ndarray, get_image, set_image, notify=image_changed)

#---------------------------------------------------------
class Camera2(QObject):

    def __init__(self, source):
        QObject.__init__(self)
        self.source = source
        self.__image2 = None
        self.stop_capture = False
        # self.cam_thread = Thread(target=self.start, args=())
        # self.cam_thread.start()

    #TEMPORARY (needs a proper class)
    def start(self):
        img = cv2.imread("../UI/test2.jpg")
        cap = cv2.VideoCapture(self.source)
        while not cap.isOpened() and self.source < 10:
            self.source += 1
            time.sleep(0.2)
            cap = cv2.VideoCapture(self.source)
            print("tentando novo input...")
        print("entrei no loop 2")
        while not self.stop_capture:
            ret, frame = cap.read()
            if ret:
                #PROCESSING STUFF
                self.__image2 = img
        cap.release()
        print("sai do loop 2")

    def get_image(self):
        return self.__image2

    def set_image(self, image):
        self.__image2 = image

    @Slot(int)
    def set_camera_source(self, source):
        pass
        # self.stop_capture = True
        # self.cam_thread.join()
        # self.stop_capture = False
        # self.source = source
        # self.cam_thread = Thread(target=self.start, args=())
        # self.cam_thread.start()

    eye_image = Property(np.ndarray, get_image, set_image)


#-------------------------------------------------------------------------
class QMLSceneCamera(QObject):

    imageChanged = Signal(np.ndarray)

    def __init__(self, source):
        QObject.__init__(self)
        self.__image = None
        self.camera = Camera(source)
        self.cam_thread = Thread(target=self.camera.run, args=())
        self.cam_thread.start()

    def get_image(self):
        return self.camera.image

    def set_image(self, image):
        self.__image = image

    @Slot(int)
    def set_camera_source(self, source):
        self.camera.stop_capture = True
        self.cam_thread.join()
        self.camera.stop_capture = False
        self.camera.source = source
        self.cam_thread = Thread(target=self.camera.run, args=())
        self.cam_thread.start()
      
    image = Property(np.ndarray, get_image, set_image, notify=imageChanged)

#-------------------------------------------------------------------------
class QMLLeftEyeCamera(QObject):

    imageChanged = Signal(np.ndarray)

    def __init__(self, source):
        QObject.__init__(self)
        self.__image = None
        self.camera = Camera(source)
        self.cam_thread = Thread(target=self.camera.run, args=())
        self.cam_thread.start()

    def get_image(self):
        return self.camera.image

    def set_image(self, image):
        self.__image = image

    @Slot(int)
    def set_camera_source(self, source):
        self.camera.stop_capture = True
        self.cam_thread.join()
        self.camera.stop_capture = False
        self.camera.source = source
        self.cam_thread = Thread(target=self.camera.run, args=())
        self.cam_thread.start()
      
    image = Property(np.ndarray, get_image, set_image, notify=imageChanged)

#-------------------------------------------------------------------------
class QMLCamera(QQuickPaintedItem):

    def __init__(self):
        QQuickPaintedItem.__init__(self)
        img = cv2.imread("../UI/test.jpg")
        self.__image = self.to_QImage(img)
        self.frame = None
        self.source = 0
        self.stop_capture = False
        self.timer = QBasicTimer()
        self.timer.start(60, self)
        self.cam_thread = Thread(target=self.start, args=())
        self.cam_thread.start()
        renderTarget = QQuickPaintedItem.RenderTarget(1)
        self.setRenderTarget(renderTarget)

    #TEMPORARY (needs a proper class)
    def start(self):
        print("1: source-> ", self.source)
        cap = cv2.VideoCapture(self.source)
        # img = cv2.imread("../UI/test.jpg")
        while not cap.isOpened() and self.source < 3:
            self.source += 1
            time.sleep(0.2)
            cap = cv2.VideoCapture(self.source)
        while not self.stop_capture:
            ret, frame = cap.read()
            if ret:
                #PROCESSING STUFF
                self.frame = frame# = img
        cap.release()
        print("sai do loop")

    def get_image(self):
        return self.__image

    def timerEvent(self, event):
        if event.timerId() == self.timer.timerId():
            #print("timer1")
            self.set_image(self.frame)

    @Slot(int)
    def set_camera_source(self, source):
        self.timer.stop()
        self.stop_capture = True
        self.cam_thread.join()
        self.stop_capture = False
        self.source = source
        self.cam_thread = Thread(target=self.start, args=())
        self.cam_thread.start()
        self.timer.start(60, self)

    def paint(self, painter):
        image = self.__image.scaled(self.size().toSize())
        img = QPixmap()
        img.convertFromImage(image)
        #painter.drawImage(QPoint(), image)
        painter.drawPixmap(QPoint(), img)

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

    image = Property(np.ndarray, get_image, set_image)

#-------------------------------------------------------------------------
class QMLCamera2(QQuickPaintedItem):

    def __init__(self):
        QQuickPaintedItem.__init__(self)
        img = cv2.imread("../UI/test2.jpg")
        self.__image = self.to_QImage(img)
        self.frame = None
        self.source = 1
        self.stop_capture = False
        self.timer = QBasicTimer()
        self.timer.start(60, self)
        self.cam_thread = Thread(target=self.start, args=())
        self.cam_thread.start()
        self.delay = 10
        renderTarget = QQuickPaintedItem.RenderTarget(1)
        self.setRenderTarget(renderTarget)

    #TEMPORARY (needs a proper class)
    def start(self):
        print("2: source->", self.source)
        try:
            cap = cv2.VideoCapture(self.source)
        except Exception as e:
            print("ERRO:", e)
        # img = cv2.imread("../UI/test.jpg")
        while not cap.isOpened() and self.source < 10:
            self.source += 1
            time.sleep(0.2)
            cap = cv2.VideoCapture(self.source)
        while not self.stop_capture:
            ret, frame = cap.read()
            if ret:
                #PROCESSING STUFF
                self.frame = frame# = img
        cap.release()
        print("sai do loop")

    def get_image(self):
        return self.__image

    def timerEvent(self, event):
        if self.delay > 0:
            self.delay -= 1
            return
        if event.timerId() == self.timer.timerId():
            #print("timer2")
            self.set_image(self.frame)

    @Slot(int)
    def set_camera_source(self, source):
        self.timer.stop()
        self.stop_capture = True
        self.cam_thread.join()
        print("thread encerrada")
        self.stop_capture = False
        self.source = source
        self.cam_thread = Thread(target=self.start, args=())
        self.cam_thread.start()
        self.timer.start(60, self)

    def paint(self, painter):
        image = self.__image.scaled(self.size().toSize())
        img = QPixmap()
        img.convertFromImage(image)
        painter.drawPixmap(QPoint(), img)

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

    image = Property(np.ndarray, get_image, set_image)

