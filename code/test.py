import cv2
import sys
import uvc
import numpy as np
import eye

#RECORDING
if sys.argv[1] == "--rec":
    dev_list = uvc.device_list()
    cap = uvc.Capture(dev_list[0]['uid'])
    cap.frame_mode = (400,400,120)
    cap.bandwidth_factor = 1.3
    out = cv2.VideoWriter('test.avi', cv2.VideoWriter_fourcc('M','J','P','G'), 120, (400,400))
    while True:
        frame = cap.get_frame()
        out.write(frame.bgr)
        cv2.imshow('recording', frame.bgr)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.close()
    out.release()
    cv2.destroyAllWindows()

#TESTING
if sys.argv[1] == "--track":
    cap = cv2.VideoCapture('test.avi')
    WIDTH  = 400
    HEIGHT = 400
    lut = np.empty((1,256), np.uint8)
    gamma = 0.65
    params = cv2.SimpleBlobDetector_Params()
    params.minThreshold = 10
    params.maxThreshold = 200
    params.filterByArea = True
    params.minArea = 0.01 * (WIDTH * HEIGHT)
    params.filterByCircularity = True
    params.minCircularity = 0.15
    params.filterByConvexity = True
    params.minConvexity = 0.8
    detector = cv2.SimpleBlobDetector_create(params)
    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            for i in range(256):
                lut[0,i] = np.clip(pow(i/255.0, gamma) *255.0, 0, 255)
            img = cv2.LUT(gray, lut)
            cv2.imshow("tracking", img)
            cv2.waitKey(5)

            #MAX_TREE
            keypoints = detector.detect(img)
            detected = cv2.drawKeypoints(img, keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
            cv2.imshow('keypoints', detected)         
            if cv2.waitKey(5) & 0xFF == ord('q'):
                break

if sys.argv[1] == "--eye":
    cap = cv2.VideoCapture('test.avi')
    lut = np.empty((1,256), np.uint8)
    gamma = 0.65
    eyeobj = eye.EyeCamera()
    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            for i in range(256):
                lut[0,i] = np.clip(pow(i/255.0, gamma) *255.0, 0, 255)
            img = cv2.LUT(frame, lut)
            img, centroid = eyeobj.process(img)
            cv2.imshow('test', img)
            cv2.waitKey(1)