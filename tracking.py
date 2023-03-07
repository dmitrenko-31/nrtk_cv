import time

import cv2
import imutils
import numpy as np

from trackedObject import TrackedObject


class Tracking:
    def __init__(self) -> None:

        self.tracked_object = TrackedObject()

    def createMask(self, frame: np.ndarray) -> np.ndarray:

        # blur the frame and convert it to the HSV
        frame_blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        frame_hsv = cv2.cvtColor(frame_blurred, cv2.COLOR_BGR2HSV)

        # construct a mask for the defined color, then perform
        # a series of dilations and erosions to remove any small
        # blobs left in the mask
        frame_mask = cv2.inRange(
            frame_hsv, self.tracked_object.color_lowerb, self.tracked_object.color_upperb)
        frame_mask = cv2.erode(frame_mask, None, iterations=2)
        frame_mask = cv2.dilate(frame_mask, None, iterations=2)
        return frame_mask

    def getObjectContour(self, frame_mask: np.ndarray) -> tuple:

        # find contours in the mask and initialize the current
        # (x, y) center of the ball
        contours = cv2.findContours(
            frame_mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = imutils.grab_contours(contours)
        center = None

        # only proceed if at least one contour was found
        if len(contours) > 0:
            # find the largest contour in the mask, then use
            # it to compute the minimum enclosing circle and centroid
            largest_counter = max(contours, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(largest_counter)
            moment = cv2.moments(largest_counter)
            center = (int(moment["m10"] / moment["m00"]),
                      int(moment["m01"] / moment["m00"]))

            return int(x), int(y), int(radius), center

    def showContour(self, frame: np.ndarray, x: int, y: int, radius: int, center: tuple) -> None:
        # only proceed if the radius meets a minimum size
        if radius > 10:
            # draw the circle and centroid on the frame,
            cv2.circle(frame, (x, y), radius, tuple(255 -
                       item for item in self.tracked_object.color_rgb[::-1]), 2)
            cv2.circle(frame, center, 5, tuple(255 -
                       item for item in self.tracked_object.color_rgb[::-1]), -1)

    def getDirection(self, frame_width: int, center: tuple):

        return 'right' if center[0] > frame_width // 2 else 'left'

    def main(self):

        cam = cv2.VideoCapture('./resources/example.mp4')
        fps = 20
        while True:
            ret, frame = cam.read()

            # if we are viewing a video and we did not grab a frame,
            # then we have reached the end of the video
            if not ret or frame is None:
                break

            mask = self.createMask(frame)
            attr = self.getObjectContour(mask)
            self.showContour(frame, *attr)
            cv2.imshow('tracking', frame)
            print(self.getDirection(frame.shape[1], attr[3]))

            time.sleep(1.0 / fps - 0.005)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break


if __name__ == '__main__':

    tracker = Tracking()
    tracker.main()
