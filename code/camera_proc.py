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

    update_image = Signal()

    def __init__(self):
        QObject.__init__(self)
        QQuickImageProvider.__init__(self, QQuickImageProvider.Image)
        self.__image = self.to_QImage(cv2.imread("../UI/test.jpg"))
        self.capturing = False
        self.dev_list = uvc.device_list()
        self.fps_res = {}
        self.modes = {}
        self.mode = None    # --> subclassed property!
        self.source = None
        self.cap = None
        self.pipe, self.child = Pipe()
        

    def start(self, source, pipe, mode):
        attempt, attempts = 0, 10
        dev_list = uvc.device_list()
        cap = uvc.Capture(dev_list[source]['uid'])
        cap.frame_mode = mode
        cap.bandwidth_factor = 1.25
        while attempt < attempts:
            try:
                frame  = cap.get_frame()
                img,_  = self.process(frame.bgr)
                if img is not None:
                    data = cv2.imencode('.jpg', img)[1]
                    pipe.send(data)
            except Exception as e:
                print("exception:", e)
                self.__reset_mode(cap, source)
                attempt += 1                
            if pipe.poll():
                if pipe.recv() == "stop":
                    break
        cap.close()


    def run(self):
        while self.capturing:
            if self.pipe.poll(1):
                data = self.pipe.recv()
                img = cv2.imdecode(data, cv2.IMREAD_COLOR)
                qimage = self.to_QImage(img)
                if qimage is not None:
                    self.__image = qimage
                    self.update_image.emit()

    
    def process(self, frame):
        return frame, None


    def requestImage(self, id, size, requestedSize):
        return self.__image


    def __reset_mode(self, cap, source):
        print("resetting...")
        mode = cap.frame_mode
        cap.close()
        time.sleep(0.4)
        dev_list = uvc.device_list()
        cap = uvc.Capture(dev_list[source]['uid'])
        print("MODE:", mode)
        cap.frame_mode = mode


    def stop(self):
        if self.capturing:
            self.pipe.send("stop")
            self.capturing = False
            self.cam_process.join()
            self.cam_thread.join()


    def get_source(self):
        return self.source


    def set_source(self, source):
        print('setting camera source to', source)
        self.source = source
        self.__set_fps_modes()
        self.capturing = True
        self.cam_process = Process(target=self.start, args=(source,self.child,self.mode))
        self.cam_process.start()
        self.cam_thread = Thread(target=self.run, args=())
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
        self.cam_process = Thread(target=self.start, args=(self.source,self.child,self.mode))
        self.cam_process.start()
        self.cam_thread = Thread(target=self.run, args=())
        self.cam_thread.start()

    def to_QImage(self, img):
        if len(img.shape) == 3:
            w,h,_ = img.shape
            rgbimg = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            flipimg = cv2.flip(rgbimg,1)
            qimg = QImage(flipimg.data, h, w, QImage.Format_RGB888)
            return qimg
    


if __name__=="__main__":
    #cam = Camera(2)
    dev_list = uvc.device_list()
    cap = uvc.Capture(dev_list[2]['uid'])
    print(cap.avaible_modes)


