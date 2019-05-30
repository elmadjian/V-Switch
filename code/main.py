import sys
import cv2
import zmq
import numpy as np
import json
from threading import Thread

import videoio
import camera

def create_socket(port):
    context = zmq.Context()
    socket = context.socket(zmq.PAIR)
    socket.bind("tcp://127.0.0.1:{}".format(port))
    print("listening on localhost:{}".format(port))
    return socket

def ui_listen(socket):
    video_source = videoio.VideoIO()
    while True:
        msg = socket.recv()
        if msg.decode().startswith("INPUT_CAMERA"):
            cameras = video_source.get_cameras_list()
            cam_list = json.dumps(cameras)
            socket.send_json(cam_list)



if __name__=='__main__':
    ui_socket = create_socket(7798)
    ui_listener = Thread(target=ui_listen, args=(ui_socket,))
    ui_listener.start()    

    sceneCam = camera.CameraThread(0, 7791)
    leftEyeCam = camera.CameraThread(1, 7792)
    rightEyeCam = camera.CameraThread(2, 7793)

    sceneCam.start()
    leftEyeCam.start()
    rightEyeCam.start()

    sceneCam.join()
    leftEyeCam.join()
    rightEyeCam.join()
    ui_listener.join()

    # addr = 'tcp://127.0.0.1:4242'
    # s = zerorpc.Server(Test())
    # s.bind(addr)
    # s.run()


