import subprocess
import re
import uvc
from PySide2.QtCore import QObject, Signal, Slot

class VideoIO_UVC(QObject):

    def __init__(self):
        QObject.__init__(self)
        self.cameras = {}
        self.read_inputs()
        self.scene = None
        self.leye  = None
        self.reye  = None

    
    def read_inputs(self):
        dev_list = uvc.device_list()
        for i in range(len(dev_list)):
            name = dev_list[i]['name']
            self.cameras[i] = name


    def get_cameras(self):
        return ["{}: {}".format(i, self.cameras[i]) for i in self.cameras.keys()]


    def get_camera_name(self, source):
        return self.cameras[source]

    
    def set_active_cameras(self, scene, leye, reye):
        self.scene = scene
        self.leye  = leye
        self.reye  = reye

    @Slot()
    def stop_cameras(self):
        print(">>> Closing cameras...")
        self.scene.stop()
        self.leye.stop()
        self.reye.stop()
        print(">>> Finished!")


    @Slot(str, int)
    def set_camera_source(self, cam_id, source):
        if cam_id.startswith("Scene"):
            self.__change_cameras(self.scene, self.leye, self.reye, source)
        elif cam_id.startswith("Left"):
            self.__change_cameras(self.leye, self.scene, self.reye, source)
        else:
            self.__change_cameras(self.reye, self.scene, self.leye, source)
        

    def __change_cameras(self, cam1, cam2, cam3, source):
        '''
        cam1: camera to be changed
        cam2 and cam3: non-selected cameras that might also have to change
        value: camera source 
        '''
        cam1.stop()
        prev_source = cam1.get_source()
        if source == cam2.get_source():
            cam2.stop()
            cam2.set_source(prev_source)
        elif source == cam3.get_source():
            cam3.stop()
            cam3.set_source(prev_source)
        cam1.set_source(source)



if __name__=="__main__":
    v = VideoIO_UVC()
    print(v.get_cameras())