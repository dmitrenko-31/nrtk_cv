"""Модуль реализующий основную логику работы системы"""
import time

import config
import cv2
from data_sender import Sender
from marker import ArucoMarker
from video_capture import GoProVideoCapture, UsbVideoCapture


class Tracking:
    """
    Класс реализующий основную логику работы системы

    Параметры:
    ----------
    sender: Sender
        объект класса Sender, реализующий отправку команд
    marker: Marker
        объкт класса Marker, реализующий основную логику работы с маркером

    Методы:
    -------
    tracking:
        основной алгоритм работы системы
    """

    def __init__(self) -> None:
        self.sender = Sender()
        self.sender.open_connect()
        self.marker = ArucoMarker()

    def tracking(self):
        cam = UsbVideoCapture()
        # cam = GoProVideoCapture()
        while True:
            ret, frame = cam.read()
            if ret:
                find_ret = self.marker.find_contour(frame)
                command = self.marker.get_direction(frame.shape[1])
                if find_ret:
                    self.marker.draw_contour(frame)
                self.marker.print_info(frame)
                cv2.imshow("Tracking", frame)
                # ret = self.sender.send_command(command + '\n')
                # print(f'Sending command "{command}" ---> {ret}')

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        cam.release()
