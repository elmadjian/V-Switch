import cv2
import time
import numpy as np
from skimage import exposure
import camera_proc as camera
import tracker
import sys 
from matplotlib import pyplot as plt


class EyeCamera(camera.Camera):

    def __init__(self, conf=0.8, cutout=600, mode=(400,400,120)):
        super().__init__()
        self.centroids = np.empty((0,2), float)
        self.conf      = conf
        self.cutout    = cutout
        self.centroid  = None
        self.timestamp = None
        self.excentricity = 1.0
        self.mode = mode
        self.bbox = None
        self.tracking = False
        self.lost_tracking = 0
        

    def process(self, img):
        height, width = img.shape[0], img.shape[1]
        if not self.tracking:
            self.bbox = self.__find_ROI(img)
            self.tracking = True
        else:
            x,y,w,h = self.bbox
            pupil = self.__find_contours(self.bbox, img)
            if pupil is not None:
                p = pupil[0]
                p = (p[0]+x+3, p[1]+y+3)
                size = max(pupil[1])
                self.__draw_tracking_info(p, size, img)
                return img, [p, time.monotonic()]
            else:
                self.lost_tracking += 1
                if self.lost_tracking > 20:
                    self.tracking = False
                    self.lost_tracking = 0
        return img, None


    def __draw_tracking_info(self, p, size, img):
        cv2.drawMarker(img, (int(p[0]), int(p[1])), (0,255,0),\
                    cv2.MARKER_CROSS, 12, 1)
        self.bbox = self.__get_bbox(p, size, img)
        cv2.rectangle(img, self.bbox, (255,120,120), 2, 1)


    def __get_bbox(self, point, size, img):
        x1 = point[0]-size*0.8
        y1 = point[1]-size*0.8
        x2 = point[0]+size*0.8
        y2 = point[1]+size*0.8
        x1 = self.__test_boundaries(x1, img.shape[1])
        y1 = self.__test_boundaries(y1, img.shape[0])
        x2 = self.__test_boundaries(x2, img.shape[1])
        y2 = self.__test_boundaries(y2, img.shape[0])
        w = x2-x1
        h = y2-y1
        return int(x1),int(y1),int(w),int(h)

    def __test_boundaries(self, x, lim):
        if x < 0:
            return 0
        if x >= lim:
            return lim-1
        return x

    def __remove_glint(self, img, edges):
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3))
        thresh = cv2.threshold(img, 180, 255, cv2.THRESH_BINARY)[1]
        dilate = cv2.dilate(thresh, kernel)
        edges[dilate >= 255] = 0
        return edges


    def __find_contours(self, bbox, frame):
        x,y,w,h = bbox
        crop = frame[y+3:y+h-3, x+3:x+w-3]
        cropgray = crop
        if len(cropgray.shape) > 2:
            cropgray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        filtered = cv2.bilateralFilter(cropgray, 7, 20, 20)
        adjusted = self.__adjust_histogram(filtered)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3))
        upper, thresh = cv2.threshold(adjusted, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        lower = 0.5*upper
        edges  = cv2.Canny(adjusted, lower, upper)
        edges  = self.__remove_glint(filtered, edges)
        edges  = self.__filter_edges(edges)
        dilate = cv2.dilate(edges, kernel, iterations=2)
        cnt,_ = cv2.findContours(dilate, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
        cnts  = [(cv2.contourArea(c), c) for c in cnt]
        if cnts:
            biggest = max(cnts, key=lambda x: x[0])[1]
            hull = cv2.convexHull(biggest)
            if len(hull) >= 5:
                ellipse = cv2.fitEllipseDirect(hull)
                painted = cv2.cvtColor(cropgray, cv2.COLOR_GRAY2BGR)
                frame[y+3:y+h-3, x+3:x+w-3] = painted
                if ellipse is not None:
                    return ellipse


    def __find_ROI(self, frame):
        h = int(frame.shape[0]/3)
        w = int(frame.shape[1]/3)
        hfs = int(h/6)
        wfs = int(w/6)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        minval = sys.maxsize
        bbox = None
        for y in range(13):
            for x in range(13):
                crop = gray[y*hfs:y*hfs+h, x*wfs:x*wfs+w]
                integral = cv2.integral(crop)
                copy = frame.copy()
                if integral[-1,-1] < minval:
                    minval = integral[-1,-1]
                    bbox = (x*wfs, y*hfs, w, h)
        cv2.rectangle(frame, bbox, (255,120,120), 2, 1)
        return bbox

    
    def __filter_edges(self, edges):
        cutoff = (edges.shape[0] + edges.shape[1])/8
        _,labels, stats,_ = cv2.connectedComponentsWithStats(edges)
        filtered = np.zeros(edges.shape, np.uint8)
        stats = stats[1:]
        length, idx, = 0, 0
        if len(stats) > 0:
            for i in range(len(stats)):
                ratio = stats[i,2]/stats[i,3]
                if (0.33 < ratio < 3) and stats[i,4] > cutoff:
                    idx = i+1
                    filtered[labels==idx] = 255
        return filtered


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
        lower -= 30
        upper += 30
        lower = np.clip(lower, 0, 255)
        upper = np.clip(upper, 0, 255)
        lower, upper = lower.astype('uint8'), upper.astype('uint8')
        merged = cv2.add(lower, upper)
        return merged
        



            

