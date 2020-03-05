import cv2
import numpy as np
import img_processor as imp
import time
import sys

class SceneImageProcessor(imp.ImageProcessor):

    def __init__(self, source, mode, pipe, array, pos, cap):
        super().__init__(source, mode, pipe, array, pos, cap)
        

    def process(self, img, mode_3D=False):
        height, width = img.shape[0], img.shape[1]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray2 = self.__adjust_histogram(gray)
        thresh = cv2.threshold(gray2, 180, 255, cv2.THRESH_BINARY_INV)[1]
        _,labels, stats,_ = cv2.connectedComponentsWithStats(thresh)
        stats = stats[1:]
        length, idx, = 0, 0
        target_pos = None
        if len(stats) > 0:
            for i in range(len(stats)):
                ratio = stats[i,2]/stats[i,3]
                max_area = stats[i,2] * stats[i,3]
                area = stats[i,4]
                if (ratio < 0.85 or ratio > 1.15) or\
                area < 30 or area > 150 or\
                max_area < 2*area:
                    idx = i+1
                    thresh[labels==idx] = 0
                else:
                    x = stats[i,0] + stats[i,2]//2
                    y = stats[i,1] + stats[i,3]//2
                    target_pos = (x,y)

        if target_pos is not None:
            cv2.circle(img, target_pos, 2, (0,255,0), -1)
            x = target_pos[0]/width
            y = target_pos[1]/height
            target_pos = np.array([x,y,time.monotonic()],dtype='float32')
        return img, target_pos


    def __adjust_histogram(self, img):
        hist = np.bincount(img.ravel(),minlength=256)
        win  = 16
        hmax, hmin, cutoff = 100, sys.maxsize, 0
        for i in range(0,256-win,2):
            sample = hist[i:i+win]
            ssum   = np.sum(sample)
            if ssum > hmax:
                hmax = ssum
            elif hmax > 100 and ssum < hmin:
                hmin = ssum
            if hmax > 100 and ssum > hmin:
                cutoff = i + win/2
                break
        lower, upper = img.copy(), img.copy()
        lower, upper = lower.astype('float32'), upper.astype('float32')
        lower[lower > cutoff] = 30
        upper[upper <= cutoff] = -30
        lower -= 50
        upper += 50
        lower = np.clip(lower, 0, 255)
        upper = np.clip(upper, 0, 255)
        lower, upper = lower.astype('uint8'), upper.astype('uint8')
        merged = cv2.add(lower, upper)
        return merged