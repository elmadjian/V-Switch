import nanogui
import math
import time
import gc
import cv2
import numpy as np

from PIL import Image

from OpenGL.GL import *

from nanogui import Color, ColorPicker, Screen, Window, GroupLayout, BoxLayout, \
                    ToolButton, Label, Button, Widget, \
                    Popup, PopupButton, CheckBox, MessageDialog, VScrollPanel, \
                    ImagePanel, ImageView, ComboBox, ProgressBar, Slider, \
                    TextBox, ColorWheel, Graph, GridLayout, \
                    Alignment, Orientation, TabWidget, IntBox, GLShader

from nanogui import gl, glfw, entypo

class Camera():

    def __init__(self, parent, x, y, width, height, name):
        self.window = Window(parent, name)
        self.window.setPosition((x,y))
        self.window.setSize((width, height))
        self.window.setLayout(GroupLayout())
        self.feed = 0
        self.img = ImageView(self.window, self.feed)

    def set_feed(self, img):
        self.feed = img
        self.__convert_to_opengl(img)
        #self.img.bindImage(self.feed)

    def __convert_to_opengl(self, img):
        tx_img = cv2.flip(img, 0)
        tx_img = Image.fromarray(tx_img)
        ix = tx_img.size[0]
        iy = tx_img.size[1]
        tx_img = tx_img.tobytes('raw', 'BGRX', 0, -1)
        tx_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tx_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, tx_img)
        self.img.bindImage(tx_id)

        


class CamSource():

    def __init__(self, parent, x, y):
        self.window = Window(parent, "Camera source")
        self.window.setPosition((x,y))
        self.window.setLayout(GroupLayout())
        self.input_path = ["item 1", "item 2", "item 3"]
        Label(self.window, "Scene camera", "sans-bold")
        self.scn_combo = ComboBox(self.window, self.input_path)
        Label(self.window, "Left eye camera", "sans-bold")
        self.le_combo  = ComboBox(self.window, self.input_path)
        Label(self.window, "Right eye camera", "sans-bold")
        self.re_combo  = ComboBox(self.window, self.input_path)



class UI(Screen):

    def __init__(self):
        super(UI, self).__init__((1200, 800), "Cadu's Eye Tracker")
        self.scene_window = Camera(self,15,15,800,600, "Scene Camera")
        self.left_eye_window = Camera(self,830,15,355,290, "Left Eye Camera")
        self.right_eye_Window = Camera(self,830,325,355,290, "Right Eye Camera")
        self.source = CamSource(self,15,630)
        self.performLayout()


    def set_cam_feed(self, feed_id, img):
        #img = nanogui.__nanogui_get_image(self.nvgContext(), img)
        if feed_id == 0:
            self.scene_window.set_feed(img)
        elif feed_id == 1:
            self.left_eye_window.set_feed(img)
        elif feed_id == 2:
            self.right_eye_window.set_feed(img)

    
if __name__ == "__main__":
    img = cv2.imread("test.jpg")

    nanogui.init()
    ui = UI()
    ui.set_cam_feed(0, img)
    ui.drawAll()
    ui.setVisible(True)
    nanogui.mainloop()
    del ui
    gc.collect()
nanogui.shutdown()