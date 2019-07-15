import cv2
import numpy as np
import time
import pynng
import uvc
from threading import Thread
from multiprocessing import Process, Pipe, Value



class UVCCamera():

    def __init__(self, source, port, fps):
        self.__image = None
        #self.socket = self.create_socket(port)
        self.parent, self.child = Pipe()
        self.source = source
        self.cam_process = None
        self.data = None
        self.send_img = True
        self.fps = fps
        self.cam_thread = Thread(target=self.run, args=())
        self.cam_thread.start()
        
    def capture(self, source, pipe, fps):
        cap = cv2.VideoCapture(source)
        if not cap.isOpened():
            cap.release()
            pipe.send([None, None])
            print("could not open camera", source)
            return
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        cap.set(cv2.CAP_PROP_FPS, fps)
        print("starting camera", source)
        while cap.isOpened():
            ret, frame = cap.read()
            if ret:
                processed, data = self.process(frame)
                cv2.imshow('tst', processed)
                cv2.waitKey(1)
                _,img = cv2.imencode('.jpg', processed, [cv2.IMWRITE_JPEG_QUALITY, 15])
                pipe.send([img, data]) 
            if pipe.poll():
                if pipe.recv() == "stop":
                    break
        cap.release()

    def create_socket(self, port):
        address = "ipc:///tmp/camera" + str(port) + ".ipc"#"tcp://127.0.0.1:{}".format(port)
        socket = pynng.Push0(listen=address)
        return socket

    def run(self):
        print("Starting cam process")
        self.cam_process = Process(target=self.capture, args=(self.source, self.child, self.fps,))
        time.sleep(np.random.random()*0.15)
        self.cam_process.start()
        while self.send_img:
            img, data = self.parent.recv()
            # if img is None:
            #    self.cam_process.join()
            #    return
            # self.socket.send(img.tobytes())
            # self.data = data
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
        return img, None

    def get_data(self):
        return self.data


        
if __name__=="__main__":
    dev_list = uvc.device_list()
    for d in dev_list:
         print(d)
    try:
        cap = uvc.Capture(dev_list[0]['uid'])
    #     controls_dict = dict([(c.display_name, c) for c in cap.controls])
    #     controls_dict['Auto Exposure Mode'].value = 1
    #     controls_dict['Gamma'].value = 200
    #     print(cap.avaible_modes)
    # except Exception as e:
    #     print("ERRO!", e)

    
    
    #cam = Camera(1, 7791, 200)
    