import sys
import cv2 as cv
from pylsd.lsd import lsd

from util import maybeOutput

arguments = {}

n = 0


def handleFrame(frame):
    global n
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    lines = lsd(gray)
    # lines = lsd.detect(gray, 2, 1)

    for i in range(lines.shape[0]):
        pt1 = (int(lines[i, 0]), int(lines[i, 1]))
        pt2 = (int(lines[i, 2]), int(lines[i, 3]))
        width = int(lines[i, 4])
        cv.line(gray, pt1, pt2, [255, 0, 0], max(1, min(width, 10)))
        # for kl in lines:
        # # cv.line only accepts integer coordinate
        # pt1 = (int(kl.startPointX), int(kl.startPointY))
        # pt2 = (int(kl.endPointX), int(kl.endPointY))
        # cv.line(gray, pt1, pt2, [255, 0, 0], 2)

    if not arguments.hide:
        cv.imshow("lsd_lines", gray)

    maybeOutput("lines", gray, n)

    # out = dict(lines=[[kl.startPointX,kl.startPointY,kl.endPointX,kl.endPointY] for kl in lines if kl.octave == 0])
    out = dict(
        lines=[
            [
                [lines[i, 0] / frame.shape[1], lines[i, 1] / frame.shape[0]],
                [lines[i, 2] / frame.shape[1], lines[i, 3] / frame.shape[0]],
            ]
            for i in range(lines.shape[0])
        ]
    )
    n += 1

    return out
