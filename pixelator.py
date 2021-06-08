"""
PIXELATOR

This simple script takes an input from a standard webcam and pixelates it.
Then, the pixelated form is outputted to the virtual webcam.
Max FPS is usually around 17

options:
    -h or --help:    Display this help.
    -u or --update:  Update this script with the latest version from github.

    default:         Begin streaming pixelated video.
"""

from sys import argv
from threading import Thread

import cv2
import numpy as np
from PIL import Image, ImageDraw

import pyvirtualcam

 

def cal_row(index, row, data, canvas, img):
    """Calculate a row in the image."""
    # For every fourth pixel in the row...
    for x_pos in range(0, 160, 4):
        # find its color
        color = row[x_pos * 4]
        # Add a pixel
        canvas.line((x_pos, 0, x_pos + 4, 0), fill=(color[2], color[1], color[0]))
    # finally return the output
    data[index] = np.asarray(img, np.uint8)[0]


def pixel(image):
    """
    Take an image.

    split it into 160 rows.

    send each row to a thread.

    and squash the resulting rows together.
    """
    # initialize
    children = {}
    child_number = 0

    data = {}
    img = Image.new("RGB", (160, 1), color=(0, 0, 0))
    canvas = ImageDraw.Draw(img)

    # for row_index in the length of the image, step 4
    for ri in range(0, len(image), 4):
        # start a thread for each row
        children[child_number] = Thread(
            target=cal_row, args=(child_number, image[ri], data, canvas, img)
        )
        children[child_number].start()
        child_number += 1

    # When the threads finish...
    while len(data) < 120:
        continue

    # Make the outputs from the threads one image again
    mat = [0] * int(len(data) / 4)
    for i in range(int(len(data) / 4)):
        mat[i] = data[i * 4]

    mat = [val for val in mat for _ in range(4)]

    # make the image an array
    mat = np.array(mat)
    return mat


def update():
    pass


def main():
    """Wrapper to eliminate global varibles."""
    # Get the camara input
    cap = cv2.VideoCapture(0)

    # open a virtual webcam (fps set to 100 as max, not actual)
    with pyvirtualcam.Camera(width=160, height=120, fps=100) as cam:
        # print the name of the camara so that the user can find it.
        print(f"Using virtual camera: {cam.device}")

        # continually send a pixelated frame to the camara
        while True:
            _, frame = cap.read()
            cam.send(np.array(np.asarray(pixel(frame)), np.uint8))
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    if len(argv) == 2:
        arg = argv[1]
        if arg == "--help" or arg == "-h":
            print(__doc__)
            exit()
        elif arg == "--update" or arg == "-u":
            update()
            exit()
    main()
