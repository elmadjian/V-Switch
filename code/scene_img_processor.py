import cv2
import numpy as np
import img_processor as imp
import time
import sys

class SceneImageProcessor(imp.ImageProcessor):

    def __init__(self, source, mode, pipe, array, pos, cap):
        super().__init__(source, mode, pipe, array, pos, cap)
        self.bbox = None
        

    def process(self, img, mode_3D=False):
        height, width = img.shape[0], img.shape[1]
        target_pos = self.__find_marker2(img)
        if target_pos is not None:
            self.__find_ROI(img, target_pos, 40)
            cv2.circle(img, target_pos, 2, (0,255,0), -1)
            x = target_pos[0]/width
            y = target_pos[1]/height
            target_pos = np.array([x,y,time.monotonic()],dtype='float32')
        else:
            self.bbox = None
        return img, target_pos

    def __grab_contours(self, cnts):
        if len(cnts) == 2:
            cnts = cnts[0]
        elif len(cnts) == 3:
            cnts = cnts[1]
        else:
            raise Exception(("Contours tuple must have length 2 or 3"))
        return cnts


    def __find_marker2(self, img):
        imgcopy = img.copy()
        if self.bbox is not None:
            x,y,w,h = self.bbox
            imgcopy = img[y:y+h,x:x+w]
        gray = cv2.cvtColor(imgcopy, cv2.COLOR_BGR2GRAY)
        gray2 = self.__adjust_histogram(gray)
        kernel = np.ones((3,3), np.uint8)
        thresh = cv2.threshold(gray2, 225, 255, cv2.THRESH_BINARY)[1]
        cnts = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = self.__grab_contours(cnts)
        for c in cnts:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.1 * peri, True)
            hull = cv2.convexHull(c, returnPoints=False)
            defects = cv2.convexityDefects(c, hull)
            if defects is not None:
                if peri > 65 and peri < 95 and len(approx) == 4 and\
                len(defects) == 4 and np.std(defects[:,:,-1]) < 300:
                    #print('defects:', len(defects), 'peri:', peri, 'approx:', len(approx))
                    #print(defects.shape)
                    #print('defects:', np.std(defects[:,:,-1]))
                    cv2.drawContours(img, [c], -1, (0,255,0), 2)
        #print('-------')
    



    def __find_marker(self, img):
        imgcopy = img.copy()
        if self.bbox is not None:
            x,y,w,h = self.bbox
            imgcopy = img[y:y+h,x:x+w]
        gray = cv2.cvtColor(imgcopy, cv2.COLOR_BGR2GRAY)
        gray2 = self.__adjust_histogram(gray)
        kernel = np.ones((3,3), np.uint8)
        thresh = cv2.threshold(gray2, 230, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
        #cv2.imshow('thresh', thresh)
        _,labels, stats,_ = cv2.connectedComponentsWithStats(thresh)
        stats = stats[1:]
        length, idx, = 0, 0
        target_pos = None
        #print('len(status):', len(stats))
        if self.bbox is not None and len(stats) > 1:
            return 
        if len(stats) > 0:
            for i in range(len(stats)):
                ratio = stats[i,2]/stats[i,3]
                max_area = stats[i,2] * stats[i,3]
                area = stats[i,4]
                #print('area:', area, 'max_area:', max_area, 'ratio:', ratio)
                if (ratio < 0.83 or ratio > 1.17) or\
                area < 40 or area > 400 or\
                max_area < 2*area or max_area > 1000 or max_area < 400:
                    idx = i+1
                    thresh[labels==idx] = 0
                else:
                    x = stats[i,0] + stats[i,2]//2
                    y = stats[i,1] + stats[i,3]//2
                    target_pos = (x,y)
                    if self.bbox is not None:
                        target_pos = (x+self.bbox[0], y+self.bbox[1])
            #print('---------------')
        return target_pos


    def __find_ROI(self, img, coord, offset):
        x1 = int(coord[0] - offset)
        y1 = int(coord[1] - offset)
        off_x = 2*offset
        off_y = 2*offset
        if x1 < 0: x1 = 0
        if y1 < 0: y1 = 0
        if x1 + off_x >= img.shape[1]: off_x = img.shape[1]-x1-1
        if y1 + off_y >= img.shape[0]: off_y = img.shape[0]-y1-1
        bbox = (x1, y1, off_x, off_y)
        cv2.rectangle(img, bbox, (0,255,0), 2,1)
        self.bbox = bbox





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