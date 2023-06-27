from abc import ABC, abstractmethod

import config
import cv2
import numpy as np


class VideoCapture:
    def __init__(self) -> None:
        pass

    @abstractmethod
    def read():
        pass

    @abstractmethod
    def release():
        pass


class UsbVideoCapture(VideoCapture):
    def __init__(
        self,
        camera_index=config.CAMERA_INDEX,
        api=config.PREF_API,
        video_codec=config.VIDEO_CODEC,
        resolution=(config.FRAME_HEIGHT, config.FRAME_WIDTH),
    ) -> None:
        self.cap = cv2.VideoCapture(camera_index, api)
        self.cap.set(cv2.CAP_PROP_FOURCC, video_codec)

        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[0])
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[1])

    def read(self):
        return self.cap.read()

    def release(self):
        self.cap.release()


class RealSenseVideoCapture(VideoCapture):
    def __init__(self) -> None:
        pass

    def read():
        pass

    def release():
        pass
