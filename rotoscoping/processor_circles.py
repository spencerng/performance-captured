import cv2 as cv
import numpy as np
import sys
from util import maybeOutput

arguments = {}

n = 0


def handleFrame(frame, n):

    img = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    img = cv.medianBlur(img, 5)
    cimg = frame.copy()  # numpy function

    circles = cv.HoughCircles(
        img, cv.HOUGH_GRADIENT, 1, 10, np.array([]), 150, 30, minRadius=5, maxRadius=50
    )

    if (
        circles is not None and len(circles) > 0
    ):  # Check if circles have been found and only then iterate over these and add them to the image
        a, b, c = circles.shape
        for i in range(b):
            cv.circle(
                cimg,
                (circles[0][i][0], circles[0][i][1]),
                circles[0][i][2],
                (0, 0, 255),
                3,
                cv.LINE_AA,
            )
            cv.circle(
                cimg,
                (circles[0][i][0], circles[0][i][1]),
                2,
                (0, 255, 0),
                3,
                cv.LINE_AA,
            )  # draw center of circle

    maybeOutput("circles", cimg, n)

    if not arguments.hide:
        cv.imshow("detected circles", cimg)

    o = []
    if (
        circles is not None and len(circles) > 0
    ):  # Check if circles have been found and only then iterate over these and add them to the image
        a, b, c = circles.shape
        for i in range(b):
            o.append(
                dict(
                    cx=float(circles[0][i][0]),
                    cy=float(circles[0][i][1]),
                    r=float(circles[0][i][2]),
                )
            )

    out = dict(circles=o)
    n += 1
    return out
