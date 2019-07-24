import cv2

'''
Tracker module

It receives tracking data from Pupil and publishes it
'''

class PupilTracker():
    
    def __init__(self, tracker_type, fail_limit):
        self.fail_limit = fail_limit
        self.tracker = None
        if tracker_type == "KCF":
            self.tracker = cv2.TrackerKCF_create()
        elif tracker_type == "MOSSE":
            self.tracker = cv2.TrackerMOSSE_create()
        else:
            print("ERROR: unknown tracker type")
        self.tracking_status = fail_limit
       

    def __init_track(self, frame, bbox):
        print("inicializando tracker")
        ret = self.tracker.init(frame, bbox)
        if ret:
            print('iniciado')
            self.tracking_status = 0
        else:
            print("could not initiate tracking!")


    def track(self, frame, bbox):
        ret, bbox = self.tracker.update(frame)
        if ret:
            x1,y1 = int(bbox[0]), int(bbox[1])
            x2,y2 = int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3])
            cv2.rectangle(frame, (x1,y1), (x2,y2), (255,0,0), 2, 1)
            self.tracking_status = 0
            return bbox
        else:
            print("tracking failure...")
            self.__init_track(frame, bbox)

if __name__=="__main__":
    tracker = PupilTracker('KCF', 20)
    cap = cv2.VideoCapture(3)
    bbox = None
    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            if bbox is not None:
                bbox = tracker.track(frame,bbox)
            cv2.imshow('test', frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("s"):
                bbox = cv2.selectROI('test', frame, fromCenter=False, showCrosshair=True)
                tracker.track(frame, bbox)
                print(bbox)
            if key == ord("q"):
                break

        
            