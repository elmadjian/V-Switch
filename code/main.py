import sys
from PySide2.QtGui import QGuiApplication
from PySide2.QtQml import QQmlApplicationEngine, qmlRegisterType
from PySide2.QtCore import QUrl, Property, Signal
import camera_uvc as camera
import videoio_uvc
import cv2
import time
from threading import Condition, Thread
import numpy as np

global scene_cam
global le_cam

def start(source, cam):
    cap = cv2.VideoCapture(source)
    while not cap.isOpened() and source < 10:
        source += 1
        time.sleep(0.2)
        cap = cv2.VideoCapture(source)
    while True:
        ret, frame = cap.read()
        if ret:
            #PROCESSING STUFF
            cam.set_image(frame)     
    cap.release()


if __name__=='__main__':
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    
    videoio = videoio_uvc.VideoIO_UVC()
    cameras = videoio.get_cameras()

    scene_cam = camera.Camera(2)
    le_cam    = camera.Camera(0)
    re_cam    = camera.Camera(1)
    videoio.set_active_cameras(scene_cam, le_cam, re_cam)

    engine.addImageProvider('sceneimg', scene_cam)
    engine.addImageProvider('leyeimg', le_cam)
    engine.addImageProvider('reyeimg', re_cam)
    engine.rootContext().setContextProperty("camManager", videoio)
    engine.rootContext().setContextProperty("cameraSources", cameras)
    engine.load(QUrl("../UI/v_switch/main.qml"))


    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec_())