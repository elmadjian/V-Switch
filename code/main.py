import sys
import cv2
import zmq
import numpy as np
import json
from threading import Thread

import videoio
import camera


#TODO: encapsulate this file into a CLASS!
sceneCam = None
leftEyeCam = None
rightEyeCam = None


def create_socket(port):
    context = zmq.Context()
    socket = context.socket(zmq.PAIR)
    socket.bind("tcp://127.0.0.1:{}".format(port))
    print("listening on localhost:{}".format(port))
    return socket

def change_cameras(cam1, cam2, cam3, value):
    '''
    cam1: camera to be changed
    cam2 and cam3: non-selected cameras that might also have to change
    value: camera source 
    '''
    cam1.stop()
    source = cam1.get_source()
    if value == cam2.get_source():
        cam2.stop()
        cam2.change_source(source)
    elif value == cam3.get_source():
        cam3.stop()
        cam3.change_source(source)
    cam1.change_source(value)
        

def ui_listen(socket):
    video_source = videoio.VideoIO()
    while True:
        msg = socket.recv().decode()
        if msg.startswith("INPUT_CAMERA"):
            cameras = video_source.get_cameras_list()
            cam_list = json.dumps(cameras)
            socket.send_json(cam_list)
        if msg.startswith("CHANGE_CAMERA"):
            command = msg.split(':')
            val = int(command[2])
            if command[1].startswith("scene"):
                change_cameras(sceneCam, leftEyeCam, rightEyeCam, val)
            elif command[1].startswith("le"):
                change_cameras(leftEyeCam, sceneCam, rightEyeCam, val)
            elif command[1].startswith("re"):
                change_cameras(rightEyeCam, sceneCam, leftEyeCam, val)




if __name__=='__main__':
    ui_socket = create_socket(7798)
    ui_listener = Thread(target=ui_listen, args=(ui_socket,))
    ui_listener.start()    

    sceneCam = camera.CameraThread(0, 7791)
    leftEyeCam = camera.CameraThread(1, 7792)
    rightEyeCam = camera.CameraThread(2, 7793)

    ui_listener.join()



