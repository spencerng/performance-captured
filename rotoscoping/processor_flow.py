
import numpy as np
import cv2 as cv
import json
import argparse
from util import maybeOutput


flow = None
prev_frame_gray = None

arguments = {}


X = None
Y = None

optic_flow = cv.DISOpticalFlow.create(cv.DISOPTICAL_FLOW_PRESET_MEDIUM)
optic_flow.setUseSpatialPropagation(True)

n = 0

def handleFrame(frame):
    global prev_frame_gray, flow, X, Y, n

    frame_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    if (prev_frame_gray is None):
        prev_frame_gray = frame_gray

    if flow is not None:
        flow = optic_flow.calc(prev_frame_gray, frame_gray, warp_flow(flow, flow))
    else:
        flow = optic_flow.calc(prev_frame_gray, frame_gray, None)

    prev_frame_gray = frame_gray

    if (not arguments.hide):
        cv.imshow('flow HSV', draw_hsv(flow))

    maybeOutput("flow", draw_hsv(flow), n)


    u,v = cv.split(flow)
    mu = cv.mean(u)
    mv = cv.mean(v)

    if (X is None):    
        height = frame.shape[0]
        width = frame.shape[1]
        X = np.fromfunction(lambda y,x : x, (height, width))
        Y = np.fromfunction(lambda y,x : y, (height, width))
    
    mag, angle = cv.cartToPolar(u,v)
    mx = (np.sum(mag*X)/np.sum(mag))
    my = (np.sum(mag*Y)/np.sum(mag))
    
    bx = np.sum(frame_gray*X)/np.sum(frame_gray)
    by = np.sum(frame_gray*Y)/np.sum(frame_gray)

    mr,mg,mb = np.mean(frame, axis=(0,1))

    out = dict(frame=n, mean_motion_x=mu[0]/frame.shape[1], mean_motion_y=mv[0]/frame.shape[0], mean_motion_px=mx/frame.shape[1], mean_motion_py=my/frame.shape[0], 
                mean_bright_px=bx, mean_bright_py=by, mean_red=mr, mean_green=mg, mean_blue=mb)

    n += 1
    return out


def warp_flow(img, flow):
    h, w = flow.shape[:2]
    flow = -flow
    flow[:,:,0] += np.arange(w)
    flow[:,:,1] += np.arange(h)[:,np.newaxis]
    res = cv.remap(img, flow, None, cv.INTER_LINEAR)
    return res


def draw_hsv(flow):
    h, w = flow.shape[:2]
    fx, fy = flow[:,:,0], flow[:,:,1]
    ang = np.arctan2(fy, fx) + np.pi
    v = np.sqrt(fx*fx+fy*fy)
    hsv = np.zeros((h, w, 3), np.uint8)
    hsv[...,0] = ang*(180/np.pi/2)
    hsv[...,1] = np.minimum(v*4, 255)
    hsv[...,2] = 255
    bgr = cv.cvtColor(hsv, cv.COLOR_HSV2BGR)
    return bgr