import cv2
import numpy as np
import time
from threading import Thread
from multiprocessing import Process, Pipe, Value

class Camera(Thread):


    def __init__(self, source):
        QObject.__init__(self)
        Thread.__init__(self)
        self.__image = None
        self.parent, self.child = Pipe()
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
        self.cam_process = Process(target=self.capture, args=(source, self.child,))
        self.cam_process.start()
        
