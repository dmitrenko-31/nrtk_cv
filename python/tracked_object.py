from abc import ABC, abstractmethod
from math import hypot
from typing import Optional

import cv2
import imutils
import numpy as np

import config


class TrackedObject(ABC):
    def __init__(
        self,
        dead_zone=config.DEAD_ZONE,
        start_distance=config.START_DISTANCE,
        marker_true_size=config.MARKER_TRUE_SIZE,
    ) -> None:
        self.x = None
        self.y = None
        self.center = None
        self.points = None
        self.distance = None
        self.direction = None

        self.valid_id = config.CORRECT_ID

        self.valid = False
        self.last_frames = [False] * config.VALID_FRAME_COUNT

        self.dead_zone = dead_zone
        self.start_distance = start_distance
        self.marker_true_size = marker_true_size

    @abstractmethod
    def findObjectContour(self, frame: np.ndarray) -> bool:
        pass

    @abstractmethod
    def drawObjectContour(self, frame: np.ndarray) -> None:
        pass

    def getObjectPosition(self) -> list[int, int]:
        return self.center

    def getDirection(self, frame_width) -> str:
        self.direction = "S"
        if self.center is None:
            self.direction = "S"
            self.distance = 0
        else:
            eps = (2.0 * self.center[0]) / frame_width - 1.0
            distance = self.get_distance(self.points, frame_width / 720) # TODO Изменить коэффициент, добавить коэффициент камеры
            if -self.dead_zone <= eps <= self.dead_zone:
                if self.distance is not None and self.distance > self.start_distance:
                    self.direction = "F"
            else:
                self.direction = "L" if eps < 0 else "R"
        return self.direction

    def get_distance(self, points, distance_coefficient) -> int:
        self.distance = 0
        if points is not None and len(points) > 0:
            marker_size = hypot(
                points[0][1][0] - points[0][0][0],
                points[0][1][1] - points[0][0][1],
            ) + hypot(
                points[0][2][0] - points[0][1][0],
                points[0][2][1] - points[0][1][1],
            )
            self.distance = (
                distance_coefficient * 1000.0 * self.marker_true_size / marker_size
            )
        return self.distance

    def check_valid(self) -> None:
        if len(self.last_frames) > config.VALID_FRAME_COUNT - 1:
            self.last_frames = self.last_frames[1:]
        self.last_frames.append(bool(self.center))
        self.valid = self.last_frames == [True] * config.VALID_FRAME_COUNT

    def print_info(self, frame) -> None:
        cv2.putText(
            frame,
            f"distance: {self.distance}",
            (0, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            config.FONT_SIZE,
            config.FONT_COLOR,
            config.FONT_THICKNESS,
        )
        cv2.putText(
            frame,
            f"direction: {self.direction}",
            (0, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            config.FONT_SIZE,
            config.FONT_COLOR,
            config.FONT_THICKNESS,
        )


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

    def print_info(self, frame) -> None:
        return super().print_info(frame)


class TrackedQRObject(TrackedObject):
    def __init__(self) -> None:
        super().__init__()
        self.detector = cv2.QRCodeDetector()

    def findObjectContour(self, frame: np.ndarray) -> bool:
        try:
            id, self.points, _ = self.detector.detectAndDecode(frame)
            if id != self.valid_id:
                self.points = None
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

    def get_distance(self, points, distance_coefficient) -> int:
        return super().get_distance(points, distance_coefficient)

    def drawObjectContour(self, frame: np.ndarray) -> None:
        if not self.valid:
            return
        frame = cv2.polylines(
            frame, self.points.astype(int), True, config.CONTOUR_COLOR, 3
        )
        cv2.circle(frame, self.center, 5, config.CONTOUR_COLOR, -1)

    def getObjectPosition(self) -> list[int, int]:
        return super().getObjectPosition()

    def getDirection(self, frame_width) -> str:
        return super().getDirection(frame_width)

    def check_valid(self) -> None:
        return super().check_valid()

    def print_info(self, frame) -> None:
        return super().print_info(frame)


class TrackedArucoObject(TrackedObject):
    def __init__(self) -> None:
        super().__init__()
        dictionary = cv2.aruco.getPredefinedDictionary(config.ARUCO_TYPE)
        parameters = cv2.aruco.DetectorParameters()
        self.detector = cv2.aruco.ArucoDetector(dictionary, parameters)

    def findObjectContour(self, frame: np.ndarray) -> bool:
        try:
            self.points, self.id = None, None
            detected_points, detected_ids, _ = self.detector.detectMarkers(frame)
            if detected_points is not None and detected_ids is not None:
                for points, id in zip(detected_points, detected_ids):
                    if id == self.valid_id:
                        self.points = points
                        self.id = id
                        break
        except:
            print("ERROR - Aruco detect error")

        self.center = None
        if self.points is not None and len(self.points) > 0:
            self.center = [
                (int(self.points[0][0][0] + self.points[0][2][0])) // 2,
                (int(self.points[0][0][1] + self.points[0][2][1])) // 2,
            ]
        self.check_valid()
        return self.points is not None

    def drawObjectContour(self, frame: np.ndarray) -> None:
        if not self.valid:
            return

        frame = cv2.aruco.drawDetectedMarkers(frame, [self.points], np.ndarray(self.id))
        cv2.circle(frame, self.center, 2, config.CONTOUR_COLOR, -1)

    def getDirection(self, frame_width) -> str:
        return super().getDirection(frame_width)

    def getObjectPosition(self) -> list[int]:
        return super().getObjectPosition()

    def check_valid(self) -> None:
        return super().check_valid()

    def get_distance(self, points, distance_coefficient) -> int:
        return super().get_distance(points, distance_coefficient)

    def print_info(self, frame) -> None:
        return super().print_info(frame)
