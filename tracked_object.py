from abc import ABC, abstractmethod

import cv2
import imutils
import numpy as np


class TrackedObject(ABC):

    def __init__(self) -> None:
        self.x = None
        self.y = None
        self.center = None

        self.depth_zone = 0.1  # (+-10%) - depth_zone

    @abstractmethod
    def findObjectContour(self, frame: np.ndarray) -> bool:
        pass

    @abstractmethod
    def drawObjectContour(self, frame: np.ndarray) -> None:
        pass

    @abstractmethod
    def getObjectPosition(self) -> list[int, int]:
        return self.center

    @abstractmethod
    def getDirection(self, frame_width) -> float:
        if self.center is None:
            return 404.0
        eps = (2.0 * self.center[0]) / frame_width - 1.0
        return 0 if -self.depth_zone <= eps <= self.depth_zone else eps   # -1.0..1.0


class TrackedColorObject(TrackedObject):
    def __init__(self, color_rgb=(124, 10, 33)) -> None:
        super().__init__()
        self.color_rgb = color_rgb
        self.color_bgr = np.uint8([[color_rgb[::-1]]])
        self.color_hsv = cv2.cvtColor(self.color_bgr, cv2.COLOR_BGR2HSV)
        self.color_lowerb = np.array(
            [self.color_hsv[0][0][0] - 10, 100, 100], dtype=np.uint8)
        self.color_upperb = np.array(
            [self.color_hsv[0][0][0] + 10, 255, 255], dtype=np.uint8)

    def findObjectContour(self, frame: np.ndarray) -> bool:
        # blur the frame and convert it to the HSV
        frame_blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        frame_hsv = cv2.cvtColor(frame_blurred, cv2.COLOR_BGR2HSV)

        # construct a mask for the defined color, then perform
        # a series of dilations and erosions to remove any small
        # blobs left in the mask
        frame_mask = cv2.inRange(
            frame_hsv, self.color_lowerb, self.color_upperb)
        frame_mask = cv2.erode(frame_mask, None, iterations=2)
        frame_mask = cv2.dilate(frame_mask, None, iterations=2)

        # find contours in the mask and initialize the current
        # (x, y) center of the ball
        contours = cv2.findContours(
            frame_mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = imutils.grab_contours(contours)

        # only proceed if at least one contour was found
        if len(contours) > 0:
            # find the largest contour in the mask, then use
            # it to compute the minimum enclosing circle and centroid
            largest_counter = max(contours, key=cv2.contourArea)
            ((self.x, self.y), self.radius) = cv2.minEnclosingCircle(largest_counter)
            moment = cv2.moments(largest_counter)
            self.center = [int(moment["m10"] / moment["m00"]),
                           int(moment["m01"] / moment["m00"])]
            return True
        return False

    def drawObjectContour(self, frame: np.ndarray) -> None:
        if self.center is None:
            return
        # only proceed if the radius meets a minimum size
        if self.radius > 10:
            # draw the circle and centroid on the frame,
            cv2.circle(frame, self.center, int(self.radius), tuple(255 -
                       item for item in self.color_rgb[::-1]), 2)
            cv2.circle(frame, self.center, 5, tuple(255 -
                       item for item in self.color_rgb[::-1]), -1)

    def getObjectPosition(self) -> list[int, int]:
        return super().getObjectPosition()

    def getDirection(self, frame_width):
        return super().getDirection(frame_width)


class TrackedQRObject(TrackedObject):

    def __init__(self) -> None:
        super().__init__()
        self.points = None
        self.three_last = [False] * 3

    def findObjectContour(self, frame: np.ndarray) -> bool:
        detector = cv2.QRCodeDetector()
        ret, self.points = detector.detect(frame)
        if ret:
            pass
        return ret

    def drawObjectContour(self, frame: np.ndarray) -> None:
        if self.points is None:
            return
        frame = cv2.polylines(
            frame, self.points.astype(int), True, (0, 255, 0), 3)

    def getObjectPosition(self) -> list[int, int]:
        return super().getObjectPosition()

    def getDirection(self, frame_width):
        return super().getDirection(frame_width)

    # def check_valid(self) -> None:
    #     if len(self.three_last) > 2:
    #         self.three_last = self.three_last[-2:]
    #     self.three_last.append(bool(self.center))
    #     return self.three_last == [True, True, True]
