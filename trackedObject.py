import cv2
import numpy as np


class TrackedObject:
    def __init__(self, color_rgb=(124, 10, 33)) -> None:
        
        self.color_rgb=color_rgb
        self.color_bgr = np.uint8([[color_rgb[::-1]]])
        self.color_hsv = cv2.cvtColor(self.color_bgr, cv2.COLOR_BGR2HSV)
        self.color_lowerb = np.array(
            [self.color_hsv[0][0][0] - 10, 100, 100], dtype=np.uint8)
        self.color_upperb = np.array(
            [self.color_hsv[0][0][0] + 10, 255, 255], dtype=np.uint8)


# if __name__ == '__main__':
#     redball = TrackedObject()
#     print(redball.color_hsv, redball.color_lowerb, redball.color_upperb)
