import numpy as np
import cv2 as cv
import json
import argparse
from util import maybeOutput

lk_params = dict(
    winSize=(15, 15),
    maxLevel=2,
    criteria=(cv.TERM_CRITERIA_EPS | cv.TERM_CRITERIA_COUNT, 10, 0.03),
)

feature_params = dict(maxCorners=5000, qualityLevel=0.1, minDistance=7, blockSize=7)


flow = None
prev_frame_gray = None

arguments = {}
tracks = []

detect_interval = 1
track_len = 20

frame_idx = 0
n = 0

ID = 0


def handleFrame(frame, n):
    global prev_frame_gray, flow, X, Y, frame_idx, tracks, ID

    frame_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    if prev_frame_gray is None:
        prev_frame_gray = frame_gray.copy()

    vis = frame.copy()

    if len(tracks) > 0:
        img0, img1 = prev_frame_gray, frame_gray
        p0 = np.float32([tr[-1] for tr in tracks]).reshape(-1, 1, 2)
        p1, _st, _err = cv.calcOpticalFlowPyrLK(img0, img1, p0, None, **lk_params)
        p0r, _st, _err = cv.calcOpticalFlowPyrLK(img1, img0, p1, None, **lk_params)
        d = abs(p0 - p0r).reshape(-1, 2).max(-1)
        good = d < 1
        new_tracks = []
        for tr, (x, y), good_flag in zip(tracks, p1.reshape(-1, 2), good):
            if not good_flag:
                continue
            tr.append((x.item(), y.item()))
            if len(tr) > track_len:
                del tr[0]
            new_tracks.append(tr)
            cv.circle(vis, (int(x), int(y)), 2, (0, 255, 0), -1)
        tracks = new_tracks
        cv.polylines(vis, [np.int32(tr) for tr in tracks], False, (0, 255, 0))

    if frame_idx % detect_interval == 0 and len(tracks) < 100:
        mask = np.zeros_like(frame_gray)
        mask[:] = 255
        for x, y in [np.int32(tr[-1]) for tr in tracks]:
            cv.circle(mask, (int(x), int(y)), 5, 0, -1)
        p = cv.goodFeaturesToTrack(frame_gray, mask=mask, **feature_params)
        if p is not None:
            for x, y in np.float32(p).reshape(-1, 2):
                tracks.append([(x.item(), y.item())])

    frame_idx += 1
    prev_frame_gray = frame_gray
    if not arguments.hide:
        cv.imshow("lk_track", vis)

    maybeOutput("lk_track", vis, frame_idx)

    t2 = [[[z[0] / frame.shape[1], z[1] / frame.shape[0]] for z in y] for y in tracks]
    out = dict(frame=n, tracks=t2)
    # print(tracks)

    n += 1
    return out
