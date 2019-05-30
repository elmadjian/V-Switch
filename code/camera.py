import cv2
import numpy as np
import time
import zmq
from threading import Thread
from multiprocessing import Process, Pipe, Value

#class Camera(Thread):
class CameraProc(Process):

    def __init__(self, source, port):
        #Thread.__init__(self)
        Process.__init__(self)
        self.__image = None
        self.source = source
        self.port = port
        self.parent, self.child = Pipe()


    #TEMPORARY (needs a proper class)
    def run(self):
        socket = self.create_socket(self.port)
        cap = cv2.VideoCapture(self.source)
        count = 0
        while not cap.isOpened():
            self.source = (self.source + 1) % 10
            time.sleep(0.5)
            cap = cv2.VideoCapture(self.source)
        while True:
            ret, frame = cap.read()
            count += 1
            if ret and count % 2 == 0:
                #PROCESSING STUFF
                img = cv2.imencode('.jpg', frame)[1]
                socket.send(img)
        cap.release()

    def create_socket(self, port):
        context = zmq.Context()
        socket = context.socket(zmq.PUSH)
        socket.bind("tcp://127.0.0.1:{}".format(port))
        print("publishing on localhost:{}".format(port))
        return socket

    def get_image(self):
        return self.__image

    def set_image(self, image):
        self.__image = image



#------------------------------------------
class CameraThread(Thread):

    def __init__(self, source, port):
        Thread.__init__(self)
        self.__image = None
        self.socket = self.create_socket(port)
        self.parent, self.child = Pipe()
        self.cam_process = Process(target=self.capture, args=(source, self.child,))
        self.cam_process.start()

    #TEMPORARY (needs a proper class)
    def capture(self, source, pipe):
        cap = cv2.VideoCapture(source)
        count = 0
        while not cap.isOpened():
            source = (source + 1) % 10
            time.sleep(0.5)
            cap = cv2.VideoCapture(source)
        while True:
            ret, frame = cap.read()
            count += 1
            if ret and count % 2 == 0:
                #PROCESSING STUFF
                img = cv2.imencode('.jpg', frame)[1]
                pipe.send(img)
                
            if pipe.poll():
                break
        cap.release()

    def create_socket(self, port):
        context = zmq.Context()
        socket = context.socket(zmq.PUSH)
        socket.bind("tcp://127.0.0.1:{}".format(port))
        print("publishing on localhost:{}".format(port))
        return socket

    def run(self):
        while True:
            img = self.parent.recv()
            self.socket.send(img)
        
    def get_image(self):
        return self.__image

    def set_image(self, image):
        self.__image = image


        
if __name__=="__main__":
    pass
    # cam = Camera(0, 7791)
    # cam.start()