import cv2
import numpy as np
import time
import zmq
from threading import Thread
from multiprocessing import Process, Pipe, Value



class Camera():

    def __init__(self, source, port):
        self.__image = None
        self.socket = self.create_socket(port)
        self.parent, self.child = Pipe()
        self.source = source
        self.cam_process = None
        self.data = None
        self.send_img = True
        self.cam_thread = Thread(target=self.run, args=())
        self.cam_thread.start()
        
    def capture(self, source, pipe):
        cap = cv2.VideoCapture(source)
        if not cap.isOpened():
            cap.release()
            pipe.send([None, None])
            print("could not open camera", source)
            return
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        while cap.isOpened():
            ret, frame = cap.read()
            if ret:
                processed, data = self.process(frame)
                img = cv2.imencode('.jpg', processed)[1]
                pipe.send([img, data]) 
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
            img, data = self.parent.recv()
            if img is None:
                self.cam_process.join()
                return
            self.socket.send(img)
            self.data = data
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

    def process(self, img):
        return img

    def get_data(self):
        return self.data


        
if __name__=="__main__":
    pass
    # cam = Camera(0, 7791)
    # cam.start()