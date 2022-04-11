import cv2
import numpy as np
import glob
import argparse

parser = argparse.ArgumentParser(
    description="Join a folder of video frames into an output video"
)
parser.add_argument("--input", required=True, help="folder of the input frames")
parser.add_argument("--framerate", default=30, type=int, help="output framerate")
parser.add_argument("--output", default="out.mp4", help="output file")

args = parser.parse_args()

img_array = []
for filename in sorted(glob.glob(f"{args.input}/*.jpg")):
    img = cv2.imread(filename)
    height, width, layers = img.shape
    size = (width, height)
    img_array.append(img)


out = cv2.VideoWriter(
    args.output, cv2.VideoWriter_fourcc(*'avc1'), args.framerate, size
)

for i in range(len(img_array)):
    out.write(img_array[i])
out.release()
