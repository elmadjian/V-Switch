import sys
import cv2
import pynng
import numpy as np
import json
from threading import Thread

import videoio
import eye_camera
import scene_camera
import calibration
import camera


#TODO: encapsulate this file into a CLASS!
sceneCam = None
leftEyeCam = None
rightEyeCam = None


def create_socket(port):
    address = "ipc:///tmp/ui" + str(port) + ".ipc"
    socket = pynng.Pair0(listen=address)
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


def calibrate(calibrator, socket, sc, le, re):
    '''
    calibrator: calibrator object
    sc: scene camera
    le: left eye camera
    re: right eye camera
    '''
    keys = calibrator.get_keys()
    for idx in keys:
        calibrator.collect_target_data(idx, sc, le, re, 30)
        socket.send("calib:next".encode())
        print("move to next target")
        

#TODO: create proper dispatchers
def ui_listen(socket, video_source):
    calibrator = calibration.Calibrator(12, 30)
    while True:
        msg = socket.recv().decode()
        if msg.startswith("INPUT_CAMERA"):
            video_source.read_inputs()
            cameras = video_source.get_cameras_list()
            cam_list = json.dumps(cameras)
            socket.send(cam_list.encode())
        if msg.startswith("CHANGE_CAMERA"):
            command = msg.split(':')
            val = int(command[2])
            if command[1].startswith("scene"):
                change_cameras(sceneCam, leftEyeCam, rightEyeCam, val)
            elif command[1].startswith("le"):
                change_cameras(leftEyeCam, sceneCam, rightEyeCam, val)
            elif command[1].startswith("re"):
                change_cameras(rightEyeCam, sceneCam, leftEyeCam, val)
        if msg.startswith("START_CALIBRATION"):
            command = msg.split(':')
            if command[1].startswith("remote"):
                pass
            elif command[1].startswith("screen"):
                print("starting calibration")
                calibrate(calibrator, socket, sceneCam, leftEyeCam, rightEyeCam)
                print("finished calibration")




if __name__=='__main__':
    video_source = videoio.VideoIO()
    ids = video_source.get_camera_ids()
    [ids.append(9) for i in range(3-len(ids))]

    ui_socket = create_socket(7798)
    ui_listener = Thread(target=ui_listen, args=(ui_socket, video_source))
    ui_listener.start()    

    sceneCam = scene_camera.SceneCamera(99, 7791)
    leftEyeCam = eye_camera.EyeCamera(99, 7792)
    rightEyeCam = eye_camera.EyeCamera(99, 7793)

    ui_listener.join()



