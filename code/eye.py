import cv2
import time
import numpy as np
from skimage import exposure
import camera_proc as camera
import tracker

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
        self.blob_detector = self.__init_blob_detector()
        self.bbox = None
        self.tracking = False
        self.lost_tracking = 0
        


    def process(self, img):
        height, width = img.shape[0], img.shape[1]
        img = self.__improve_contrast(img)
        if not self.tracking:
            pupil = self.__find_pupil(img)
            if pupil is not None:
                p, size = pupil
                self.__draw_tracking_info(p, size, img)
                self.tracking = True
        else:
            #img = self.__remove_glint(self.bbox, img)
            x,y,w,h = self.bbox
            pupil = self.__find_contours(self.bbox, img)
            if pupil is not None:
                p = pupil[0]
                p = (p[0]+x+3, p[1]+y+3)
                size = min(pupil[1])
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


    def __init_blob_detector(self):
        params = cv2.SimpleBlobDetector_Params()
        params.minThreshold = 10
        params.maxThreshold = 200
        params.filterByArea = True
        params.minArea = 0.02 * (self.mode[0] * self.mode[1])
        params.filterByCircularity = True
        params.minCircularity = 0.15
        params.filterByConvexity = True
        params.minConvexity = 0.7
        return cv2.SimpleBlobDetector_create(params)


    def __get_bbox(self, point, size, img):
        x1 = point[0]-size
        y1 = point[1]-size
        x2 = point[0]+size
        y2 = point[1]+size
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

    def __remove_glint(self, bbox, frame):
        x,y,w,h = bbox
        crop = frame[y+3:y+h-3, x+3:x+w-3]
        cropgray = crop
        if len(cropgray.shape) > 2:
            cropgray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        filtered = cv2.bilateralFilter(cropgray, 7, 20, 20)
        thresh   = cv2.threshold(filtered, 185, 255, cv2.THRESH_BINARY)[1]
        kernel   = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
        thresh   = cv2.dilate(thresh, kernel, iterations=2)
        #painted  = cv2.inpaint(cropgray, thresh, 7, cv2.INPAINT_TELEA)
        #painted  = cv2.cvtColor(painted, cv2.COLOR_GRAY2BGR)
        p = (int(crop.shape[0]/2),int(crop.shape[1]/2))
        cropgray[thresh >= 255] = cropgray[p]
        painted = cv2.cvtColor(cropgray, cv2.COLOR_GRAY2BGR)
        cv2.imshow('thresh', thresh)
        frame[y+3:y+h-3, x+3:x+w-3] = painted
        return frame

    def __improve_contrast(self, img):
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l,a,b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=1.0, tileGridSize=(8,8))
        cl = clahe.apply(l)
        limg = cv2.merge((cl,a,b))
        return cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)


    def __find_contours(self, bbox, frame):
        x,y,w,h = bbox
        crop = frame[y+3:y+h-3, x+3:x+w-3]
        cropgray = crop
        if len(cropgray.shape) > 2:
            cropgray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        filtered = cv2.bilateralFilter(cropgray, 7, 20, 20)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3))
        lower,_,_,_ = cv2.minMaxLoc(filtered)
        sigma = 0.4
        v = np.median(cropgray)
        lower = int(max(0, (1.0 - sigma) * v))
        upper = int(min(255, (1.0 + sigma) * v))
        edges  = cv2.Canny(filtered, lower, upper, L2gradient=True)
        thresh = cv2.threshold(filtered, 150, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, kernel)
        edges[thresh == 255] = 0
        dilate = cv2.dilate(edges, kernel, iterations=2)
        cnt,_ = cv2.findContours(dilate, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
        cnts  = [(cv2.contourArea(c), c) for c in cnt]
        cv2.imshow('canny', dilate)
        if cnts:
            biggest = max(cnts, key=lambda x: x[0])[1]
            hull = cv2.convexHull(biggest)
            if len(hull) >= 5:
                ellipse = cv2.fitEllipseDirect(hull)
                painted = cv2.cvtColor(cropgray, cv2.COLOR_GRAY2BGR)
                frame[y+3:y+h-3, x+3:x+w-3] = painted
                if ellipse is not None and max(ellipse[1]) > 15:
                    return ellipse


    def __find_pupil(self, frame):
        keypoints = self.blob_detector.detect(frame)
        klist = [[k.pt, k.size] for k in keypoints]
        if klist:
            print(klist)
            kp, ks = klist[0]
            return kp, ks  

            

