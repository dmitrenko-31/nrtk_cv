import time

import cv2
import imutils
import numpy as np

from tracked_object import TrackedColorObject, TrackedQRObject
from data_sender import Sender

class Tracking:
    def __init__(self) -> None:
        self.sender = Sender()
        self.sender.open_connect()

        #self.tracked_object = TrackedColorObject()
        self.tracked_object = TrackedQRObject()

    def tracking(self):
        cam = cv2.VideoCapture('./resources/example.mp4')
        fps = 20
        while True:
            ret, frame = cam.read()

            # if we are viewing a video and we did not grab a frame,
            # then we have reached the end of the video
            if not ret or frame is None:
                break

           
            ret = self.tracked_object.findObjectContour(frame)
            if ret:
                self.tracked_object.drawObjectContour(frame)
            
            cv2.imshow('tracking', frame)
            command = self.tracked_object.getDirection(frame.shape[1]) 
            ret = self.sender.send_command(command)
            print(f'Sending command "{command}" ---> {ret}')

            time.sleep(1.0 / fps - 0.005)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

