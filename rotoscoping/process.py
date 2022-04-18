import numpy as np
import cv2 as cv
from cv2 import VideoCapture
import json
import argparse
import os
import util
from util import maybeOutput
import gc

parser = argparse.ArgumentParser(
    description="Process a video or a webcam input and extract motion and foreground statistics"
)
parser.add_argument(
    "--video",
    dest="video",
    default=0,
    help="the name of the video file, if this is missing then we'll try to open a webcam instead",
)
parser.add_argument(
    "--do_flow", dest="do_flow", help="compute optic flow?", action="store_true"
)
parser.add_argument(
    "--do_background",
    dest="do_background",
    help="do background subtract?",
    action="store_true",
)
parser.add_argument(
    "--do_lines", dest="do_lines", help="do LSD line detector", action="store_true"
)
parser.add_argument(
    "--do_circles",
    dest="do_circles",
    help="do Hough circle detector",
    action="store_true",
)
parser.add_argument(
    "--do_tracks", dest="do_tracks", help="do LK point tracker", action="store_true"
)

parser.add_argument(
    "--output_directory",
    dest="output_directory",
    help="if you set this then we'll write intermediate files to a directory",
)
parser.add_argument(
    "--hide",
    dest="hide",
    help="if you set this then we won't open windows to show you how the video is playing",
    action="store_true",
)
parser.add_argument(
    "--compute_contours",
    dest="compute_contours",
    help="if --do_background then, additionally, trace the outline of foreground areas",
    action="store_true",
)
parser.add_argument(
    "--start_frame",
    dest="start_frame",
    help="frame to start on",
    default=0,
    type=int
)
parser.add_argument(
    "--shrink",
    type=float,
    dest="shrink",
    default=0.5,
    help="scale the camera by this much",
)

args = parser.parse_args()


c = args.video
try:
    c = int(c)
except:
    pass

cam = VideoCapture(c)

util.arguments = args

if args.do_flow:
    import processor_flow

    processor_flow.arguments = args

if args.do_background:
    import processor_bg

    processor_bg.arguments = args

if args.do_lines:
    import processor_lines

    processor_lines.arguments = args

if args.do_circles:
    import processor_circles

    processor_circles.arguments = args

if args.do_tracks:
    import processor_lk

    processor_lk.arguments = args


n = args.start_frame
for _ in range(args.start_frame):
    cam.read()

file_num = args.start_frame // 500

outputs = list()
while True:
    ret, frame = cam.read()

    if not (frame is None):
        frame = cv.resize(
            src=frame,
            dsize=None,
            fx=args.shrink,
            fy=args.shrink,
            interpolation=cv.INTER_AREA,
        )
        maybeOutput("input", frame, n)

        out = {}
        if args.do_flow:
            out.update(processor_flow.handleFrame(frame, n))
        if args.do_background:
            out.update(processor_bg.handleFrame(frame, n))
        if args.do_lines:
            out.update(processor_lines.handleFrame(frame, n))
        if args.do_circles:
            out.update(processor_circles.handleFrame(frame, n))
        if args.do_tracks:
            out.update(processor_lk.handleFrame(frame, n))

        out.update(dict(frame=n, width=frame.shape[1], height=frame.shape[0]))

        cv.waitKey(1)

        outputs.append(out)

        n += 1

        if n != 0 and n % 500 == 0:

            with open(f"{args.output_directory}/data-no-lines-{file_num}.json", "w+") as out_file:
                out_file.write(json.dumps(outputs).replace("NaN", "0.0"))
            file_num += 1
            gc.collect()
            outputs.clear()

    if not ret:
        break
with open(f"{args.output_directory}/data-no-lines-{file_num}.json", "w+") as out_file:
    out_file.write(json.dumps(outputs).replace("NaN", "0.0"))

