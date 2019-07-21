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
        ret = self.tracker.init(frame, bbox)
        if not ret:
            print("could not initiate tracking!")


    def track(self, frame, bbox):
        if self.tracking_status >= self.fail_limit:
            self.__init_track(frame, bbox)
            return
        ret, bbox = self.tracker.update(frame)
        if ret:
            x1,y1 = int(bbox[0]), int(bbox[1])
            x2,y2 = int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3])
            cv2.rectangle(frame, (x1,y1), (x2,y2), (255,0,0), 2, 1)
            self.tracking_status = 0
            return [x1,y1,x2,y2]
        else:
            print("tracking failure...")
            self.tracking_status += 1
