import zmq, socket, cv2
import numpy as np
from msgpack import loads, unpackb

'''
Tracker module

It receives tracking data from Pupil and publishes it
'''

class Tacker():
    
    def __init__(self, context, port=50020):
        self.socket = self.__setup_socket(context, port)
        self.breakpoint = False


    def __setup_socket(self, context, port):
        '''
        This function configures a socket to subscribe to Pupil server
        -------------------------------------------
        context (object): ZMQ context
        port (int): socket port
        '''
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://127.0.0.1:" + str(port))
        socket.send_string('SUB_PORT')
        sub_port = socket.recv_string()
        sub_socket = context.socket(zmq.SUB)
        sub_socket.connect("tcp://127.0.0.1:" + sub_port)
        sub_socket.setsockopt_string(zmq.SUBSCRIBE, '')
        return sub_socket


    def read_2D(self):
        '''
        Reading test for 2D calibration
        --------------------------------------
        socket (object): ZMQ SUB socket
        '''
        l_normal, l_diameter, l_axes = [], [], []
        r_normal, r_diameter, r_axes = [], [], []
        while True:
            try:
                topic, msg = recv_payload(self.socket)
                if topic.startswith('pupil.0'):
                    l_normal, l_diameter, l_axes = self.__get_2D_data(msg)
                if topic.startswith('pupil.1'):
                    r_normal, r_diameter, r_axes = self.__get_2D_data(msg)
                print('left:', l_normal, '\nright:', r_normal)
                print('\n===============================\n')
            except Exception as e:
                print("Pupil socket issue: ", e)
                break


    def __get_2D_data(self, msg):
        normal = msg['norm_pos']
        diameter = msg['diameter']
        axes = msg['ellipse']['axes']
        return normal, diameter, axes


    def read_3D(self):
        '''
        Reading test for 3D calibration
        --------------------------------------
        socket (object): ZMQ SUB socket
        '''
        while True:
            try:
                topic, msg = recv_payload(self.socket)
                if topic.startswith('gaze.3d.01'):
                    el, er, nl, nr, pog = get_gaze_data(msg)
                    print("eyeball_left:", el)
                    print("eyeball_right:", er)
                    print("normal_left:", nl)
                    print("normal_right:", nr)    
                    print("pog:", pog)        
            except Exception as e:
                print("Pupil socket issue: ", e)
                break


    def recv_payload(self, socket):
        '''
        Processes received packet through socket
        --------------------------------------
        socket (object): ZMQ SUB socket
        '''
        topic = socket.recv_string()
        payload = unpackb(socket.recv(), encoding='utf-8')
        extra_frames = []
        while socket.get(zmq.RCVMORE):
            extra_frames.append(socket.recv())
        if extra_frames:
            payload['__raw_data__'] = extra_frames
        return topic, payload


    def get_gaze_data(self, msg):
        '''
        Checks integrity of gaze data once calibrated
        ----------------------------------
        msg (str): pupil msg
        '''
        RIGHT = 0
        LEFT  = 1
        eyeball_left, normal_left   = -1,-1
        eyeball_right, normal_right = -1,-1
        pog = -1
        eyeballs = msg['eye_centers_3d']
        normals  = msg['gaze_normals_3d']
        pog      = msg['gaze_point_3d']
        if RIGHT in eyeballs.keys():
            eyeball_right = eyeballs[RIGHT]
            normal_right  = normals[RIGHT]
        if LEFT in eyeballs.keys():
            eyeball_left  = eyeballs[LEFT]
            normal_left   = normals[LEFT]
        return eyeball_left, eyeball_right, normal_left, normal_right, pog



