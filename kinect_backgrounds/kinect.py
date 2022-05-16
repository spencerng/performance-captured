import cv2
import numpy as np

import pyk4a

from pyk4a import Config, PyK4A


def colorize(
    image: np.ndarray,
    clipping_range=(None, None),
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

    def get_frame(self):
        capture = self.cam.get_capture()

        if capture.color is None or capture.transformed_depth is None:
            return None

        color_img = capture.color

        # Based in mm of depth camera
        mask = cv2.inRange(capture.transformed_depth, 1, 1000)

        n_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
            mask, 12, cv2.CV_32S
        )
        # mask_inv = mask
        # mask_inv[mask_inv == 255] = 10
        # mask_inv[mask_inv == 0] = 255
        # mask_inv[mask_inv == 10] = 0
        masked_img = cv2.bitwise_and(color_img, color_img, mask=mask)

        return masked_img[:, :, :3], centroids
        # return colorize(capture.depth, (None, 5000), cv2.COLORMAP_HSV)

    def close(self):
        self.cam.stop()


if __name__ == "__main__":
    main()
