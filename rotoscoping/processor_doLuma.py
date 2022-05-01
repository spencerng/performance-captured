import numpy as np
import cv2 as cv
import json
import argparse
from util import maybeOutput
from skimage.util import img_as_ubyte


X = None
Y = None

kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (3, 3))

arguments = {}
n = 0


def chunker(seq, size):
    return (seq[pos : pos + size] for pos in range(0, len(seq), size))


def handleFrame(frame):
    global X, Y, n, fgbg

    frame_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    if X is None:
        height = frame.shape[0]
        width = frame.shape[1]
        X = np.fromfunction(lambda y, x: x, (height, width))
        Y = np.fromfunction(lambda y, x: y, (height, width))

    fgmask = frame_gray < arguments.luma_threshold
    # fgmask = cv.morphologyEx(fgmask, cv.MORPH_OPEN, kernel)

    backx = np.sum(fgmask * X) / np.sum(fgmask)
    backy = np.sum(fgmask * Y) / np.sum(fgmask)
    if not arguments.hide:
        cv.imshow("fgbg", fgmask * 1.0)

    maybeOutput("bg", fgmask, n)

    out = dict(
        frame=n,
        mean_background_px=backx,
        mean_background_py=backy,
        mean_background=np.mean(fgmask),
    )

    if arguments.compute_contours:
        dst = cv.Canny(fgmask, 50, 200)
        maybeOutput("bg_contours", dst, n)

        # im2, contours  = cv.findContours(img_as_ubyte(dst),cv.RETR_LIST,cv.CHAIN_APPROX_SIMPLE)
        im2, contours = cv.findContours(
            img_as_ubyte(fgmask), cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE
        )

        data = [
            [
                [x / frame.shape[1], y / frame.shape[0]]
                for x, y in chunker(np.concatenate(q).ravel().tolist(), 2)
            ]
            for q in im2
            if cv.contourArea(q) > arguments.area_threshold
        ]
        out["contours"] = data

        if not arguments.hide:
            cv.imshow("bg-contours", dst)

    n += 1
    return out
