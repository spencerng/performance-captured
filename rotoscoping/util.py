
import os, sys
from pathlib import PurePath
import cv2 as cv

arguments = {}

def maybeOutput(processName, frame, n):
    if (not arguments.output_directory): return
    if (not os.path.exists(str(PurePath(arguments.output_directory) / processName))):
        os.makedirs(str(PurePath(arguments.output_directory) / processName))
    
    p = str(PurePath(arguments.output_directory) / processName / ("out_%06i.jpg" % n))
    print("saving to %s" % p, file=sys.stderr)
    cv.imwrite(p, frame)
