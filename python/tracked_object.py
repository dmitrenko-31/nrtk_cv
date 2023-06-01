from abc import ABC, abstractmethod
from math import hypot
from typing import Optional

import cv2
import imutils
import numpy as np


class TrackedObject(ABC):
    def __init__(
        self, dead_zone=0.1, start_distance=2000, marker_true_size=150
    ) -> None:
        self.x = None
        self.y = None
        self.center = None
        self.points = None

        self.dead_zone = dead_zone
        self.start_distance = start_distance
        self.marker_true_size = marker_true_size

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
    def getDirection(self, frame_width) -> str:
        if self.center is None:
            return "S"
        eps = (2.0 * self.center[0]) / frame_width - 1.0

        if -self.dead_zone <= eps <= self.dead_zone:
            distance = self.get_distance(self.points[0], frame_width / 720)
            if distance is not None and distance > self.start_distance:
                return "F"
            else:
                return "S"
        else:
            return "L" if eps < 0 else "R"

    @abstractmethod
    def get_distance(self, points, distance_coefficient) -> int:
        if points is not None and len(points) > 0:
            marker_size = hypot(
                points[0][1][0] - points[0][0][0],
                points[0][1][1] - points[0][0][1],
            ) + hypot(
                points[0][2][0] - points[0][1][0],
                points[0][2][1] - points[0][1][1],
            )

            return distance_coefficient * 1000.0 * self.marker_true_size / marker_size

        else:
            return 0


class TrackedColorObject(TrackedObject):
    def __init__(self, color_rgb=(124, 10, 33)) -> None:
        super().__init__()
        self.color_rgb = color_rgb
        self.color_bgr = np.uint8([[color_rgb[::-1]]])
        self.color_hsv = cv2.cvtColor(self.color_bgr, cv2.COLOR_BGR2HSV)
        self.color_lowerb = np.array(
            [self.color_hsv[0][0][0] - 10, 100, 100], dtype=np.uint8
        )
        self.color_upperb = np.array(
            [self.color_hsv[0][0][0] + 10, 255, 255], dtype=np.uint8
        )

    def findObjectContour(self, frame: np.ndarray) -> bool:
        # blur the frame and convert it to the HSV
        frame_blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        frame_hsv = cv2.cvtColor(frame_blurred, cv2.COLOR_BGR2HSV)

        # construct a mask for the defined color, then perform
        # a series of dilations and erosions to remove any small
        # blobs left in the mask
        frame_mask = cv2.inRange(frame_hsv, self.color_lowerb, self.color_upperb)
        frame_mask = cv2.erode(frame_mask, None, iterations=2)
        frame_mask = cv2.dilate(frame_mask, None, iterations=2)

        # find contours in the mask and initialize the current
        # (x, y) center of the ball
        contours = cv2.findContours(
            frame_mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        contours = imutils.grab_contours(contours)

        # only proceed if at least one contour was found
        if len(contours) > 0:
            # find the largest contour in the mask, then use
            # it to compute the minimum enclosing circle and centroid
            largest_counter = max(contours, key=cv2.contourArea)
            ((self.x, self.y), self.radius) = cv2.minEnclosingCircle(largest_counter)
            moment = cv2.moments(largest_counter)
            self.center = [
                int(moment["m10"] / moment["m00"]),
                int(moment["m01"] / moment["m00"]),
            ]
            return True
        return False

    def drawObjectContour(self, frame: np.ndarray) -> None:
        if self.center is None:
            return
        # only proceed if the radius meets a minimum size
        if self.radius > 10:
            # draw the circle and centroid on the frame,
            cv2.circle(
                frame,
                self.center,
                int(self.radius),
                tuple(255 - item for item in self.color_rgb[::-1]),
                2,
            )
            cv2.circle(
                frame,
                self.center,
                5,
                tuple(255 - item for item in self.color_rgb[::-1]),
                -1,
            )

    def getObjectPosition(self) -> list[int, int]:
        return super().getObjectPosition()

    def getDirection(self, frame_width):
        return super().getDirection(frame_width)


class TrackedQRObject(TrackedObject):
    def __init__(self) -> None:
        super().__init__()
        self.points = None
        self.valid = False
        self.three_last = [False] * 3
        self.detector = cv2.QRCodeDetector()

    def findObjectContour(self, frame: np.ndarray) -> bool:
        try:
            self.true_size, self.points, _ = self.detector.detectAndDecode(frame)
        except:
            print("ERROR - QR detect error")

        self.center = None
        if self.points is not None and len(self.points) > 0:
            self.center = [
                (int(self.points[0][0][0] + self.points[0][2][0])) // 2,
                (int(self.points[0][0][1] + self.points[0][2][1])) // 2,
            ]
        self.check_valid()
        return self.points is not None

    def get_pixels_size(self) -> Optional[list[float]]:
        if not self.valid:
            return None

        return [
            hypot(
                self.points[0][1][0] - self.points[0][0][0],
                self.points[0][1][1] - self.points[0][0][1],
            ),
            hypot(
                self.points[0][2][0] - self.points[0][1][0],
                self.points[0][2][1] - self.points[0][1][1],
            ),
        ]

    def drawObjectContour(self, frame: np.ndarray) -> None:
        if not self.valid:
            return
        frame = cv2.polylines(frame, self.points.astype(int), True, (0, 255, 0), 3)
        cv2.circle(frame, self.center, 5, (0, 255, 0), -1)

    def getObjectPosition(self) -> list[int, int]:
        return super().getObjectPosition()

    def getDirection(self, frame_width) -> str:
        return super().getDirection(frame_width)

    def check_valid(self) -> None:
        if len(self.three_last) > 2:
            self.three_last = self.three_last[1:]
        self.three_last.append(bool(self.center))
        self.valid = self.three_last == [True] * 3


class TrackedArucoObject(TrackedObject):
    def __init__(self) -> None:
        super().__init__()
        self.points = None
        self.valid = False
        self.three_last = [False] * 3

        dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)
        parameters = cv2.aruco.DetectorParameters()
        self.detector = cv2.aruco.ArucoDetector(dictionary, parameters)

    def findObjectContour(self, frame: np.ndarray) -> bool:
        try:
            self.points, self.ids, _ = self.detector.detectMarkers(frame)
        except:
            print("ERROR - Aruco detect error")

        self.center = None
        if self.points is not None and len(self.points) > 0:
            self.center = [
                (int(self.points[0][0][0][0] + self.points[0][0][2][0])) // 2,
                (int(self.points[0][0][0][1] + self.points[0][0][2][1])) // 2,
            ]
        self.check_valid()
        return self.points is not None

    def drawObjectContour(self, frame: np.ndarray) -> None:
        if not self.valid:
            return

        frame = cv2.aruco.drawDetectedMarkers(frame, self.points, self.ids)
        cv2.circle(frame, self.center, 2, (0, 255, 0), -1)

    def getDirection(self, frame_width) -> str:
        return super().getDirection(frame_width)

    def getObjectPosition(self) -> list[int]:
        return super().getObjectPosition()

    def check_valid(self) -> None:
        if len(self.three_last) > 2:
            self.three_last = self.three_last[1:]
        self.three_last.append(bool(self.center))
        self.valid = self.three_last == [True] * 3

    def get_distance(self, points, distance_coefficient) -> int:
        return super().get_distance(points, distance_coefficient)
