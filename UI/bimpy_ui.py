import bimpy
import cv2
from PIL import Image

#img = cv2.imread("test.jpg")
img = Image.open("test.jpg")
ctx = bimpy.Context()
ctx.init(800,800, "testing")
while not ctx.should_close():
    with ctx:
        bimpy.text("Mostrando aqui esta linda imagem")
        im = bimpy.Image(img)
        bimpy.image(im)