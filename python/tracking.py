import time

import cv2

from tracked_object import TrackedArucoObject
from data_sender import Sender


class Tracking:
    def __init__(self) -> None:
        self.sender = Sender()
        self.sender.open_connect()

        self.tracked_object = TrackedArucoObject()

    def tracking(self):
        cam = cv2.VideoCapture(0, cv2.CAP_V4L2)

        cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        
        # Set 1080 resolution
        cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)

        while True:
            ret, frame = cam.read()
            
            # if we are viewing a video and we did not grab a frame,
            # then we have reached the end of the video
            # if not ret or frame is None:
            #     break
            ret = self.tracked_object.findObjectContour(frame)
            if ret:
                self.tracked_object.drawObjectContour(frame)

            cv2.imshow('Tracking', frame)
            command = self.tracked_object.getDirection(frame.shape[1])
            #ret = self.sender.send_command(command)
            # print(f'Sending command "{command}" ---> {ret}')

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cam.release()
