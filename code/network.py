import socket
import time
from threading import Thread

'''
This module is a bridge between the calibration module and UWP in Unity.
'''

class Network():
    
    def __init__(self, remote_ip="127.0.0.1", remote_port=50022):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.local_address  = ("127.0.0.1", 50021)
        self.remote_address = (remote_ip, remote_port)
        self.__bind()
        self.breakout = False
        self.listener = Thread(target=self.listen, args=())
        self.listener.start()

    
    def __bind(self):
        try:
            self.socket.bind(self.local_address)
        except Exception as e:
            print("[__bind]:", e)

    
    def send(self, msg):
        tosend = msg + "\r\n"
        try:
            self.socket.sendto(tosend.encode(), self.remote_address)
        except Exception as e:
            print("[send]:", e)

    
    def recv(self):
        try:
            data = self.socket.recvfrom(2048)[0]
            return data.decode()
        except Exception as e:
            print("[recv]:", e)


    def stop(self):
        self.breakout = True
        self.listener.join()
        self.socket.close()


    def listen(self):
        while not self.breakout:
            data = self.recv()
            if data.startswith("C"):
                self.breakout = True


#DEBUG
if __name__=="__main__":
    n = Network()
    start = False
    while True:
        if not start:
            n.send("C")
            start = True
            time.sleep(2)
        n.send("N")
        time.sleep(2)
        if n.breakout:
            n.stop()
            break


'''
Message CODES:

C -> start calibration screen in Unity
C <- stop calibration in Unity
N -> next target
P -> preview data on Unity
'''
    
    

    
    
    