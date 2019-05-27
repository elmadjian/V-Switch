import subprocess
import re

class VideoIO():

    def __init__(self):
        self.cameras = {}
        self.read_inputs()

    
    def read_inputs(self):
        '''
        Only works on Linux.
        TODO: solution for Mac and Windows
        '''
        binout = subprocess.check_output(["v4l2-ctl", "--list-devices"])
        out = binout.decode().split('\n\n')
        for cam in out:
            group = re.findall('(.*)\\(usb.*\n.*video(\\d+)', cam)
            if group:
                name = group[0][0]
                source = group[0][1]
                self.cameras[source] = name


    def get_cameras(self):
        return ["{}: {}".format(i, self.cameras[i]) for i in self.cameras.keys()]


    def get_camera_name(self, source):
        return self.cameras[source]



if __name__=="__main__":
    v = VideoIO()
    print(v.get_cameras())