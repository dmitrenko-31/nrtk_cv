import queue
from abc import ABC, abstractmethod
from threading import Thread

import config
import cv2
import gopro_stream
import numpy as np
import requests


class VideoCapture:
    def __init__(self) -> None:
        pass

    @abstractmethod
    def read(self):
        pass

    @abstractmethod
    def release(self):
        pass


class UsbVideoCapture(VideoCapture):
    def __init__(
        self,
        camera_index=config.CAMERA_INDEX,
        api=config.USB_PREF_API,
        video_codec=config.USB_VIDEO_CODEC,
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


class BufferlessVideoCapture(Thread):

    def __init__(self, source, api, video_codec) -> None:
        self.cap = cv2.VideoCapture(source, api)
        self.cap.set(cv2.CAP_PROP_FOURCC, video_codec)
        self.q = queue.Queue()
        super().__init__(daemon=True)

    def run(self) -> None:
        """Read frames as soon as they are available, keeping only most recent one"""
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            if not self.q.empty():
                try:
                    self.q.get_nowait()  # discard previous (unprocessed) frame
                except queue.Empty:
                    pass

            self.q.put(frame)

    def get_frame(self):
        return self.q.get()


class GoProVideoCapture(VideoCapture):
    def __init__(
        self,
        serial=config.GOPRO_SERIAL,
        api=config.GOPRO_PREF_API,
        video_codec=config.GOPRO_VIDEO_CODEC,
    ) -> None:
        self.gopro = gopro_stream.gopro()
        self.gopro.stream_stop()
        self.gopro.stream_start()
        cv2.setUseOptimized(onoff=True)
        self.buff = BufferlessVideoCapture('udp://@172.2{0}.1{1}{2}.51:8554'.format(*serial), api, video_codec)
        self.buff.start()

    def read(self):
        try:
            return True, self.buff.get_frame()
        except:
            return False, None

    def release(self):
        self.buff.cap.release()
        self.gopro.stream_stop()
