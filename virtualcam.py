import pyvirtualcam
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont
from threading import Thread
from os import system
import time
from json import dumps
from json import loads
from json_ipc import json_ipc

def cal_row(index, row, data, d, img):
    # For every pixel in the image...
    for x_pos in range(0, 160, 4):
        # find its color
        color = row[x_pos*4]
        d.line((x_pos,0, x_pos+4, 0), fill=(color[2], color[1], color[0]))
    # finally return the output
    data[index] = np.asarray(img, np.uint8)[0]

def asci(image):
    children = {}
    child_number = 0

    data = {}
    img = Image.new('RGB', (160, 1), color = (0, 0, 0))
    d = ImageDraw.Draw(img)

    for ri in range(0, len(image), 4):
        children[child_number] = Thread(target=cal_row, args=(child_number, image[ri], data, d, img))
        children[child_number].start()
        child_number += 1

    while len(data) < 120:
        continue
    mat = [0]*int(len(data)/4)
    for i in range(int(len(data)/4)):
        mat[i] = data[i*4]

    mat = [val for val in mat for _ in range(4)]

    mat = np.array(mat)
    return mat


cap = cv2.VideoCapture(0)

timer = 0
iterations = 0

fps = ".."

start = time.time()

with pyvirtualcam.Camera(width=160, height=120, fps=100) as cam:
    print(f'Using virtual camera: {cam.device}')
    while True:
        iterations += 1
        end = time.time()
        timer = end-start

        if timer > 1:
            fps = iterations
            end = time.time()
            start = time.time()
            timer = 0
            iterations = 0
        ret, frame = cap.read()
        cam.send(np.array(np.asarray(asci(frame)), np.uint8))
        print("\033c", fps)

cap.release()
cv2.destroyAllWindows()
