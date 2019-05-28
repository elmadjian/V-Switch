import sys
import videoio
import cv2
import zerorpc
import numpy as np

class Test(object):
    def printSomething(self):
        return "Estou dando ola do Python!"

if __name__=='__main__':

    videoio = videoio.VideoIO()
    cameras = videoio.get_cameras()

    addr = 'tcp://127.0.0.1:4242'
    s = zerorpc.Server(Test())
    s.bind(addr)
    print("running server at", addr)
    s.run()


