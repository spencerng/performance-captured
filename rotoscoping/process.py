import numpy as np
import cv2 as cv
import json
import argparse
import util
from util import maybeOutput

parser = argparse.ArgumentParser(description='Process a video or a webcam input and extract motion and foreground statistics')
parser.add_argument('--video', dest="video", default=0, help='the name of the video file, if this is missing then we\'ll try to open a webcam instead')
parser.add_argument('--do_flow', dest="do_flow", help='compute optic flow?', action="store_true")
parser.add_argument('--do_background', dest="do_background", help='do background subtract?', action="store_true")
parser.add_argument('--do_lines', dest="do_lines", help='do LSD line detector', action="store_true")
parser.add_argument('--do_circles', dest="do_circles", help='do Hough circle detector', action="store_true")
parser.add_argument('--do_tracks', dest="do_tracks", help='do LK point tracker', action="store_true")

parser.add_argument('--output_directory', dest="output_directory", help='if you set this then we\'ll write intermediate files to a directory')
parser.add_argument('--hide', dest="hide", help='if you set this then we won\'t open windows to show you how the video is playing', action="store_true")
parser.add_argument('--compute_contours', dest="compute_contours", help='if --do_background then, additionally, trace the outline of foreground areas', action="store_true")
parser.add_argument('--shrink', type=float, dest="shrink", default=0.5, help='scale the camera by this much')

args = parser.parse_args()


c = args.video
try:
    c = int(c)
except: 
    pass

cam = cv.VideoCapture(c)    

util.arguments = args

if (args.do_flow):
    import processor_flow
    processor_flow.arguments = args

if (args.do_background):
    import processor_bg
    processor_bg.arguments = args

if (args.do_lines):
    import processor_lines
    processor_lines.arguments = args

if (args.do_circles):
    import processor_circles
    processor_circles.arguments = args

if (args.do_tracks):
    import processor_lk
    processor_lk.arguments = args


n = 0
try:
    while True:
        ret, frame = cam.read()

        if (not (frame is None)):
            frame = cv.resize(src=frame, dsize=None, fx=args.shrink, fy=args.shrink, interpolation=cv.INTER_AREA)
            maybeOutput("input", frame, n)

            out = {}
            if (args.do_flow):
                out.update(processor_flow.handleFrame(frame))
            if (args.do_background):
                out.update(processor_bg.handleFrame(frame))
            if (args.do_lines):
                out.update(processor_lines.handleFrame(frame))
            if (args.do_circles):
                out.update(processor_circles.handleFrame(frame))
            if (args.do_tracks):
                out.update(processor_lk.handleFrame(frame))

            out.update(dict(frame=n, width=frame.shape[1], height=frame.shape[0]))       

            cv.waitKey(1)
            
            print(json.dumps(out).replace("NaN", "0.0"),flush=True)
            
            n+=1

        if (not ret):
            break
except KeyboardInterrupt:
    pass
