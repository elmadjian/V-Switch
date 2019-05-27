import sys
from PySide2.QtGui import QGuiApplication
from PySide2.QtQml import QQmlApplicationEngine, qmlRegisterType
from PySide2.QtCore import QUrl, Property, Signal
import camera_old as camera
import videoio
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

    videoio = videoio.VideoIO()
    cameras = videoio.get_cameras()

    # scene_cam = camera.Camera(0)
    # le_cam    = camera.Camera2(1)

    # scthread = Thread(target=start, args=(0, scene_cam,))
    # lethread = Thread(target=start, args=(1, le_cam,))

    # scthread.start()
    # lethread.start()

    # img = cv2.imread("../UI/test.jpg")
    # img2 = cv2.imread("../UI/test2.jpg")

    # scene_cam.set_image(img)
    # le_cam.set_image(img2)
    #imageChanged = Signal(np.ndarray)
    #scene_image = Property(np.ndarray, scene_cam.get_image, scene_cam.set_image, notify=imageChanged)
    #left_eye_cam = camera.QMLLeftEyeCamera(1)


    


    
    # img = cv2.imread("../UI/test.jpg")


    qmlRegisterType(camera.QMLCamera, "CVStuff", 1, 0, "SceneCamera")
    qmlRegisterType(camera.QMLCamera2, "CVStuff", 1, 0, "LeftEyeCamera")
    #qmlRegisterType(camera.QMLCamera, "CVStuff", 1, 0, "RightEyeCamera")

    # engine.rootContext().setContextProperty("sceneCamCV", scene_cam)
    # engine.rootContext().setContextProperty("leftEyeCamCV", le_cam)
    engine.rootContext().setContextProperty("cameraSources", cameras)
    engine.load(QUrl("../UI/v_switch/main.qml"))


    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec_())