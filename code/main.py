import sys
from PySide2.QtGui import QGuiApplication
from PySide2.QtQml import QQmlApplicationEngine, qmlRegisterType
from PySide2.QtCore import QUrl, Property, Signal, QObject, Slot
import eye
import scene
import videoio_uvc
import calibration
import calibration_hmd
import vergence
import cv2
import time
import numpy as np
import multiprocessing as mp


if __name__=='__main__':
    #mp.set_start_method('spawn')
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    
    videoio   = videoio_uvc.VideoIO_UVC()
    cameras   = videoio.get_cameras()
    calib_ctl = calibration.Calibrator(3, 3, 60, 6)
    calib_hmd = calibration_hmd.HMDCalibrator(3, 3, 150, 4) 
    vergence  = vergence.VergenceCtl()

    scene_cam = scene.SceneCamera()
    le_cam    = eye.EyeCamera()
    re_cam    = eye.EyeCamera()
    videoio.set_active_cameras(scene_cam, le_cam, re_cam)
    calib_ctl.set_sources(scene_cam, le_cam, re_cam)
    calib_hmd.set_sources(le_cam, re_cam)
    calib_hmd.set_vergence_control(vergence)

    engine.rootContext().setContextProperty("camManager", videoio)
    engine.rootContext().setContextProperty("cameraSources", cameras)
    engine.rootContext().setContextProperty("sceneCam", scene_cam)
    engine.rootContext().setContextProperty("leftEyeCam", le_cam)
    engine.rootContext().setContextProperty("rightEyeCam", re_cam)
    engine.rootContext().setContextProperty("calibControl", calib_ctl)
    engine.rootContext().setContextProperty("calibHMD", calib_hmd)
    engine.rootContext().setContextProperty("vergenceControl", vergence)
    engine.addImageProvider('sceneimg', scene_cam)
    engine.addImageProvider('leyeimg', le_cam)
    engine.addImageProvider('reyeimg', re_cam)
    engine.load(QUrl("../UI/v_switch/main.qml"))


    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec_())