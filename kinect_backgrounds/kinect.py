import cv2
import numpy as np

import pyk4a

from pyk4a import Config, PyK4A


def colorize(
    image: np.ndarray,
    clipping_range = (None, None),
    colormap: int = cv2.COLORMAP_AUTUMN,
) -> np.ndarray:
    if clipping_range[0] or clipping_range[1]:
        img = image.clip(clipping_range[0], clipping_range[1])
    else:
        img = image.copy()
    img = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    img = cv2.applyColorMap(img, colormap)
    return img

class KinectCam:
    def __init__(self):
        k4a = PyK4A(
        Config(
            color_resolution=pyk4a.ColorResolution.RES_1080P,
            camera_fps=pyk4a.FPS.FPS_30,
            depth_mode=pyk4a.DepthMode.NFOV_UNBINNED,
            synchronized_images_only=False,
            )
        )
        k4a.start()
        k4a.whitebalance = 4510
        self.cam = k4a
        self.file = open("output.txt", "w")

    def get_frame(self):
        capture = self.cam.get_capture()
        
                    
        if capture.color is None:
            return None
        
        color_img = capture.color
        
        color_img[:, :, 3] = capture.transformed_depth[:, :]
        ret, mask = cv2.threshold(color_img[:, :, 3], 1, 255, cv2.THRESH_BINARY)
        # cv2.imshow("image", mask)
        # for i in range(color_img.shape[0]):
        #     for j in range(color_img.shape[1]):
        #       if capture.transformed_depth[i][j] == 0:
        #             color_img[i][j] = [0, 0, 0, 0]
        return colorize(capture.transformed_depth)
            # return colorize(capture.depth, (None, 5000), cv2.COLORMAP_HSV)


        
    def close(self):
        self.cam.stop()
        self.file.close()


if __name__ == "__main__":
    main()