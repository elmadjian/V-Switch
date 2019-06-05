import cv2
import numpy as np
import time
import marker_detector

import camera 

class SceneCamera(camera.Camera):

    def __init__(self, source, port):
        super().__init__(source, port)
        self.cv = cv
        self.detector = marker_detector.MarkerDetector()
        self.target = None
        self.code = [
            [1,1,1],
            [1,1,1],
            [1,1,0]
        ] 

    def process(self, img, width, height):
        target = self.detector.detect(img, self.code, True)
        if target is not None:
            self.target = [time.monotonic_ns(), target]
        return img

    
    def get_data(self):
        return self.target