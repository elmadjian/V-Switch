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



#------------------------------------------
class CameraThread():

    def __init__(self, source, port):
        self.__image = None
        self.socket = self.create_socket(port)
        self.parent, self.child = Pipe()
        self.source = source
        self.cam_process = None
        self.send_img = True
        self.cam_thread = Thread(target=self.run, args=())
        self.cam_thread.start()
        
    #TEMPORARY (needs a proper class)
    def capture(self, source, pipe):
        cap = cv2.VideoCapture(source)
        while not cap.isOpened():
            source = (source + 1) % 10
            cap = cv2.VideoCapture(source)
            time.sleep(0.25)
        while True:
            ret, frame = cap.read()
            if ret:
                #PROCESSING STUFF
                img = cv2.imencode('.jpg', frame)[1]
                pipe.send(img) 
            if pipe.poll():
                if pipe.recv() == "stop":
                    break
        cap.release()

    def create_socket(self, port):
        context = zmq.Context()
        socket = context.socket(zmq.PUSH)
        socket.bind("tcp://127.0.0.1:{}".format(port))
        print("publishing on localhost:{}".format(port))
        return socket

    def run(self):
        self.cam_process = Process(target=self.capture, args=(self.source, self.child,))
        time.sleep(np.random.random()*0.15)
        self.cam_process.start()
        while self.send_img:
            img = self.parent.recv()
            self.socket.send(img)
        self.parent.send("stop")
        self.cam_process.join()

    def stop(self):
        self.send_img = False
        self.cam_thread.join()

    def change_source(self, new_source):
        self.source = new_source
        self.send_img = True
        self.cam_thread = Thread(target=self.run, args=())
        self.cam_thread.start()

    def get_source(self):
        return self.source



        
if __name__=="__main__":
    pass
    # cam = Camera(0, 7791)
    # cam.start()