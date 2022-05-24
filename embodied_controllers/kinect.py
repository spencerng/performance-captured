import cv2
import numpy as np

import pyk4a

from pyk4a import Config, PyK4A

MIN_DIST = 1
MAX_DIST = 300 * 9

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
                color_resolution=pyk4a.ColorResolution.OFF,
                camera_fps=pyk4a.FPS.FPS_30,
                depth_mode=pyk4a.DepthMode.WFOV_UNBINNED,
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
        mask = cv2.inRange(capture.transformed_depth, MIN_DIST, MAX_DIST)

        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.erode(mask, kernel)

        masked_img = cv2.bitwise_and(color_img, color_img, mask=mask)

        # n_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
        #     mask, 12, cv2.CV_32S
        # )

        contours, _ = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        centroids = []
        max_contour = None

        if len(contours) != 0:
            max_area = cv2.contourArea(contours[0])
            max_contour = contours[0]
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > max_area:
                    max_area = area
                    max_contour = contour

            # Extrapolate center of contour
            m = cv2.moments(max_contour)
            centroids = [(int(m["m10"] / m["m00"]), int(m["m01"] / m["m00"]))]

            if max_area < 20000:
                centroids = []
                max_contour = None

        mask_img = cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB)

        if max_contour is not None:
            max_contour = np.vstack(max_contour).squeeze()

        return masked_img[:, :, :3], centroids, max_contour

    def close(self):
        self.cam.stop()


if __name__ == "__main__":
    main()
