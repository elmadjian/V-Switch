import sys
from PySide2.QtGui import QGuiApplication
from PySide2.QtQml import QQmlApplicationEngine, qmlRegisterType
from PySide2.QtCore import QUrl, Property, Signal, QObject, Slot
import eye
import scene
import videoio_uvc
import cv2
import time
import numpy as np


if __name__=='__main__':
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    
    videoio = videoio_uvc.VideoIO_UVC()
    cameras = videoio.get_cameras()

    scene_cam = scene.SceneCamera()
    le_cam    = eye.EyeCamera()
    re_cam    = eye.EyeCamera()
    videoio.set_active_cameras(scene_cam, le_cam, re_cam)

    engine.rootContext().setContextProperty("camManager", videoio)
    engine.rootContext().setContextProperty("cameraSources", cameras)
    engine.rootContext().setContextProperty("sceneCam", scene_cam)
    engine.rootContext().setContextProperty("leftEyeCam", le_cam)
    engine.rootContext().setContextProperty("rightEyeCam", re_cam)
    engine.addImageProvider('sceneimg', scene_cam)
    engine.addImageProvider('leyeimg', le_cam)
    engine.addImageProvider('reyeimg', re_cam)
    engine.load(QUrl("../UI/v_switch/main.qml"))


    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec_())