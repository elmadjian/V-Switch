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
        try:
            binout = subprocess.check_output(["v4l2-ctl", "--list-devices"], stderr=subprocess.STDOUT)
        except Exception as e:
            binout = e.output
        out = binout.decode().split('\n\n')
        self.cameras = {}
        for cam in out:
            name_group = re.findall('(.*) \\(', cam)
            source_group = re.findall('video(\\d+)', cam)
            if name_group and source_group:
                name = name_group[0]
                for source in source_group:
                    self.cameras[source] = name
    

    def get_cameras(self):
        return self.cameras

    def get_cameras_list(self):
        return ["{}: {}".format(i, self.cameras[i]) for i in self.cameras.keys()]

    def get_camera_ids(self):
        return [int(i) for i in self.cameras.keys()]

    def get_camera_name(self, idx):
        return self.cameras[idx]



if __name__=="__main__":
    v = VideoIO()
    print(v.get_cameras())