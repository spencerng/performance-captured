import cv2
import numpy as np


import cv2

import pykinect_azure as pykinect

MIN_DIST = 1
MAX_DIST = 300 * 6


class KinectCam:
    def __init__(self):
        pykinect.initialize_libraries(
            track_body=True, module_k4abt_path="/usr/lib/x86_64-linux-gnu/libk4a.so.1.3"
        )

        # Modify camera configuration
        device_config = pykinect.default_configuration
        device_config.color_resolution = pykinect.K4A_COLOR_RESOLUTION_OFF
        device_config.depth_mode = pykinect.K4A_DEPTH_MODE_WFOV_2X2BINNED

        # Start device
        self.cam = pykinect.start_device(config=device_config)
        self.tracker = pykinect.start_body_tracker(
            model_type=pykinect.K4ABT_DEFAULT_MODEL
        )

    def get_frame(self):
        capture = self.cam.update()
        body_frame = self.tracker.update()

        for body in body_frame.get_bodies():
            print(body)

        ret, img = capture.get_transformed_depth_image()

        if not ret:
            return None, None, None

        print(body_frame.joints)

        # Based in mm of depth camera
        mask = cv2.inRange(img, MIN_DIST, MAX_DIST)

        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.erode(mask, kernel)

        # masked_img = cv2.bitwise_and(color_img, color_img, mask=mask)

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

        return mask_img, centroids, max_contour

    def close(self):
        self.cam.stop()


if __name__ == "__main__":
    main()
