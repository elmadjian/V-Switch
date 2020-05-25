import sys
import os
import numpy as np
import cv2


class DataLoader():

    def __init__(self, dir_path):
        '''
        dir_path: user path containing all compressed .npz data

        vars:
        tgt -> target coordinates in the scene image (x,y,timestamp)
        leye -> left eye data (pupil_x, pupil_y, Nx, Ny, Nz, timestamp)
        reye -> right eye data (pupil_x, pupil_y, Nx, Ny, Nz, timestamp)
        tgt_img -> scene image
        leye_img -> left eye image
        reye_img -> right_eye image
        '''
        self.dir_path = dir_path
        self.tgt = {}
        self.leye = {}
        self.reye = {}
        self.tgt_img = {}
        self.leye_img = {}
        self.reye_img = {}
        

    def __check_key_and_append(self, dic, key, value):
        if key not in dic.keys():
            dic[key] = []
        dic[key].append(value)


    def parse_dir(self):
        for subdir, firs, files in os.walk(self.dir_path):
            for filename in files:
                src = os.path.join(subdir, filename)
                x,y,t = filename.split('_')
                coord = x + '~' + y
                file_array = np.load(src)
                for f in file_array['arr_0']:
                    if "tgt" in src:
                        self.__check_key_and_append(self.tgt, coord, f)
                    elif "leye" in src:
                        self.__check_key_and_append(self.leye, coord, f)
                    elif "reye" in src:
                        self.__check_key_and_append(self.reye, coord, f)
                    elif "imgscn" in src:
                        self.__check_key_and_append(self.tgt_img, coord, f)
                    elif "imgle" in src:
                        self.__check_key_and_append(self.leye_img, coord, f)
                    elif "imgre" in src:
                        self.__check_key_and_append(self.reye_img, coord, f)


    def show_data(self, data, img=False):
        '''
        Shows the contents of data parameter.
        This parameter can be either
        self.tgt, self.leye, self.reye, self.tgt_img,
        self.leye_img, or self.reye_img.
        If the parameter is an image collection, img=True is required.
        '''
        print(">>> Total number of points:", len(data.keys()))
        input(">>> Press any key to show the data")
        for k in data.keys():
            print(">>> Showing data for key:", k)
            for el in data[k]:
                if img:
                    cv2.imshow("data", el)
                    cv2.waitKey(60)
                else:
                    for i in el:
                        print("{:.5f}".format(i), end=" ")
                    print()
            input("\n\n>>> Done. Press any key to continue\n---------")


if __name__=="__main__":
    dl = DataLoader(sys.argv[1])
    print("Loading data (this may take a while)...")
    dl.parse_dir()
    dl.show_data(dl.reye)
    #dl.show_data(dl.reye_img, img=True)
