import cv2

'''
Tracker module

It receives tracking data from Pupil and publishes it
'''

class PupilTracker():
    
    def __init__(self, tracker_type):
        self.tracker = None
        self.tracker_type = tracker_type
        self.tracking = False

    def create_tracker(self):
        if self.tracker_type == "KCF":
            self.tracker = cv2.TrackerKCF_create()
        elif self.tracker_type == "MOSSE":
            self.tracker = cv2.TrackerMOSSE_create()
        else:
            print("ERROR: unknown tracker type")
       

    def init_track(self, frame, bbox):
        print("starting tracker")
        self.create_tracker()
        ret = self.tracker.init(frame, bbox)
        if ret:
            self.tracking = True
        else:
            print("Failure while trying to start tracker!")


    def track(self, frame, extbbox):
        if self.tracking:
            ret, bbox = self.tracker.update(frame)
            bbox = self.__to_int(bbox)
            if ret:
                x1,y1 = bbox[0], bbox[1]
                x2,y2 = bbox[0] + bbox[2], bbox[1] + bbox[3]
                cv2.rectangle(frame, (x1,y1), (x2,y2), (255,120,120), 2, 1)
                return bbox
            else:
                self.tracking = False
                print("tracking failure...", extbbox)
        else:
            self.init_track(frame, extbbox)

    
    def __to_int(self, bbox):
        x = int(bbox[0])
        y = int(bbox[1])
        w = int(bbox[2])
        h = int(bbox[3])
        return (x,y,w,h)


if __name__=="__main__":
    tracker = PupilTracker('KCF')
    cap = cv2.VideoCapture(1)
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

        
            