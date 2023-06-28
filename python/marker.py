"""Модуль с основной логикой для обнаружения маркеров"""

from abc import ABC, abstractmethod
from math import hypot
from typing import Optional

import config
import cv2
import imutils
import numpy as np


class Marker(ABC):
    """
    Базовый класс для представления маркера.

    Описывает основные параметры и методы для работы с маркером.

    Параметры:
    ----------
    dead_zone: float
        мертвая зона поворота (проценты/100 [0.0;1.0])
    start_distance: int
        минимальная дистанция до маркера для движения вперед (мм)
    marker_true_size: int
        реальный размер маркера (длина стороны, мм)
    valid_id: int
        id маркера для распознавания
    valid_frame_count: int
        минимальное количество подряд идущих кадров с рапознанным маркером, для защиты от случайных срабатываний
    center: list[int]
        координаты точки цетра маркера на кадре
    points: np.ndarray
        координаты точек углов маркера на кадре
    distance: float
        расстояние до маркера (мм)
    direction: str
        направление движения
    valid: bool
        флаг

    Методы:
    -------
    find_contour(frame): bool
        поиск маркера на кадре, возвращает True если маркер найден
    draw_contour(frame): None
        изображение контура маркера на кадре
    get_direction(frame_width): str
        определение направление движения до маркера
    get_distance(distance_coefficient): int
        определение расстояния до маркера
    check_valid: None
        проверка кадра на условие минимально подряд идущих кадров с маркером
    print_info(frame): None
        изображение ключевой информации на кадре
    """

    def __init__(
        self,
        dead_zone: float = config.DEAD_ZONE,
        start_distance: int = config.START_DISTANCE,
        marker_true_size: int = config.MARKER_TRUE_SIZE,
        valid_id: int = config.CORRECT_ID,
        valid_frame_count: int = config.VALID_FRAME_COUNT,
    ) -> None:
        """
        Устанавливает все необходимые атрибуты для объекта marker.

        Параметры:
        ----------
        dead_zone: float, optional
            мертвая зона поворота (проценты/100 [0.0;1.0]). По умолчанию config.DEAD_ZONE
        start_distance: int, optional
            минимальная дистанция до маркера для движения вперед (мм). По умолчанию config.START_DISTANCE
        marker_true_size: int, optional
            реальный размер маркера (длина стороны, мм). По умолчанию config.MARKER_TRUE_SIZE
        valid_id: int, optional
            id маркера для распознавания. По умолчанию config.CORRECT_ID
        valid_frame_count: int, optional
            минимальное количество подряд идущих кадров с рапознанным маркером. По умолчанию config.VALID_FRAME_COUNT
        """
        self.dead_zone: float = dead_zone
        self.start_distance: int = start_distance
        self.marker_true_size: int = marker_true_size
        self.valid_id: int = valid_id
        self.valid_frame_count = valid_frame_count
        self.last_frames: list[bool] = [False] * valid_frame_count
        self.center: list[int] = None
        self.points: np.ndarray = None
        self.distance: float = 0
        self.direction: str = "S"
        self.valid: bool = False

    @abstractmethod
    def find_contour(self, frame: np.ndarray) -> bool:
        """
        Поиск маркера на кадре.

        Параметры:
        ----------
        frame: np.ndarray
            кадр

        Возвращаемое значение:
        ----------------------
        bool:
            результат поиска маркера
        """
        pass

    @abstractmethod
    def draw_contour(self, frame: np.ndarray) -> None:
        """
        Изображение контура маркера на кадре.

        Параметры:
        ----------
        frame: np.ndarray
            кадр

        """
        pass

    def get_direction(self, frame_width: int) -> str:
        """
        Определение направление движения до маркера.

        Параметры:
        ----------
        frame_width: int
            ширина кадра

        Возвращаемое значение:
        ----------------------
        str:
            направление движения ('S', 'L', 'R', 'F')

        """
        self.direction = "S"
        self.distance = 0
        if self.center is not None:
            eps = (2.0 * self.center[0]) / frame_width - 1.0
            distance = self.get_distance(frame_width / 720)
            if -self.dead_zone <= eps <= self.dead_zone:
                if distance > self.start_distance:
                    self.direction = "F"
            else:
                self.direction = "L" if eps < 0 else "R"
        return self.direction

    def get_distance(self, distance_coefficient: float) -> int:
        """
        Определение расстояния до маркера.

        Параметры:
        ----------
        distance_coefficient: float
            коэффициент расстояния (зависит от разрешения и камеры)

        Возвращаемое значение:
        ----------------------
        int:
            расстояние до маркера (мм)

        """
        self.distance = 0
        if self.points is not None and len(self.points) > 0:
            marker_size = hypot(
                self.points[0][1][0] - self.points[0][0][0],
                self.points[0][1][1] - self.points[0][0][1],
            ) + hypot(
                self.points[0][2][0] - self.points[0][1][0],
                self.points[0][2][1] - self.points[0][1][1],
            )
            # TODO Изменить коэффициент, добавить коэффициент камеры
            self.distance = (
                distance_coefficient * 1000.0 * self.marker_true_size / marker_size
            )
        return self.distance

    def check_valid(self) -> None:
        """Проверка кадра на условие минимально подряд идущих кадров с маркером."""
        if len(self.last_frames) > self.valid_frame_count - 1:
            self.last_frames = self.last_frames[1:]
        self.last_frames.append(bool(self.center))
        self.valid = self.last_frames == [True] * self.valid_frame_count

    def print_info(self, frame: np.ndarray) -> None:
        """
        Изображение ключевой информации на кадре.

        Параметры:
        ----------
        frame: np.ndarray
            кадр

        """
        cv2.putText(
            frame,
            f"distance: {self.distance}",
            (0, 50),
            config.FONT_STYLE,
            config.FONT_SIZE,
            config.FONT_COLOR,
            config.FONT_THICKNESS,
        )
        cv2.putText(
            frame,
            f"direction: {self.direction}",
            (0, 100),
            config.FONT_STYLE,
            config.FONT_SIZE,
            config.FONT_COLOR,
            config.FONT_THICKNESS,
        )


# TODO: Закончить документацию, комментарии
class ColorMarker(Marker):
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

    def find_contour(self, frame: np.ndarray) -> bool:
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
            ((_, _), self.radius) = cv2.minEnclosingCircle(largest_counter)
            moment = cv2.moments(largest_counter)
            self.center = [
                int(moment["m10"] / moment["m00"]),
                int(moment["m01"] / moment["m00"]),
            ]
            return True
        return False

    def draw_contour(self, frame: np.ndarray) -> None:
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

    def get_direction(self, frame_width):
        return super().get_direction(frame_width)

    def print_info(self, frame) -> None:
        return super().print_info(frame)


class QRMarker(Marker):
    """
    Класс для представления маркера QR кода.

    Описывает основные параметры и методы для работы с QR маркером.

    Параметры:
    ----------
    dead_zone: float
        мертвая зона поворота (проценты/100 [0.0;1.0])
    start_distance: int
        минимальная дистанция до маркера для движения вперед (мм)
    marker_true_size: int
        реальный размер маркера (длина стороны, мм)
    valid_id: int
        id маркера для распознавания
    valid_frame_count: int
        минимальное количество подряд идущих кадров с рапознанным маркером, для защиты от случайных срабатываний
    center: list[int]
        координаты точки цетра маркера на кадре
    points: np.ndarray
        координаты точек углов маркера на кадре
    distance: float
        расстояние до маркера (мм)
    direction: str
        направление движения
    valid: bool
        флаг
    detector: cv2.QRCodeDetector
        объект класса cv2.QRCodeDetector, детектор QR кода

    Методы:
    -------
    find_contour(frame): bool
        поиск маркера на кадре, возвращает True если маркер найден
    draw_contour(frame): None
        изображение контура маркера на кадре
    get_direction(frame_width): str
        определение направление движения до маркера
    get_distance(distance_coefficient): int
        определение расстояния до маркера
    check_valid: None
        проверка кадра на условие минимально подряд идущих кадров с маркером
    print_info(frame): None
        изображение ключевой информации на кадре

    """

    def __init__(
        self,
        dead_zone: float = config.DEAD_ZONE,
        start_distance: int = config.START_DISTANCE,
        marker_true_size: int = config.MARKER_TRUE_SIZE,
        valid_id: int = config.CORRECT_ID,
        valid_frame_count: int = config.VALID_FRAME_COUNT,
    ) -> None:
        super().__init__(
            dead_zone, start_distance, marker_true_size, valid_id, valid_frame_count
        )
        self.detector = cv2.QRCodeDetector()

    def find_contour(self, frame: np.ndarray) -> bool:
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

    def draw_contour(self, frame: np.ndarray) -> None:
        if not self.valid:
            return
        frame = cv2.polylines(
            frame, self.points.astype(int), True, config.CONTOUR_COLOR, 3
        )
        cv2.circle(frame, self.center, 5, config.CONTOUR_COLOR, -1)

    def get_direction(self, frame_width: int) -> str:
        return super().get_direction(frame_width)

    def get_distance(self, distance_coefficient: float) -> int:
        return super().get_distance(distance_coefficient)

    def check_valid(self) -> None:
        return super().check_valid()

    def print_info(self, frame: np.ndarray) -> None:
        return super().print_info(frame)


class ArucoMarker(Marker):
    """
    Класс для представления Aruco маркера.

    Описывает основные параметры и методы для работы с QR маркером.

    Параметры:
    ----------
    dead_zone: float
        мертвая зона поворота (проценты/100 [0.0;1.0])
    start_distance: int
        минимальная дистанция до маркера для движения вперед (мм)
    marker_true_size: int
        реальный размер маркера (длина стороны, мм)
    valid_id: int
        id маркера для распознавания
    valid_frame_count: int
        минимальное количество подряд идущих кадров с рапознанным маркером, для защиты от случайных срабатываний
    center: list[int]
        координаты точки цетра маркера на кадре
    points: np.ndarray
        координаты точек углов маркера на кадре
    distance: float
        расстояние до маркера (мм)
    direction: str
        направление движения
    valid: bool
        флаг
    detector: cv2.aruco.ArucoDetector
        объект класса cv2.aruco.ArucoDetector, детектор Aruco маркера
    id 

    Методы:
    -------
    find_contour(frame): bool
        поиск маркера на кадре, возвращает True если маркер найден
    draw_contour(frame): None
        изображение контура маркера на кадре
    get_direction(frame_width): str
        определение направление движения до маркера
    get_distance(distance_coefficient): int
        определение расстояния до маркера
    check_valid: None
        проверка кадра на условие минимально подряд идущих кадров с маркером
    print_info(frame): None
        изображение ключевой информации на кадре

    """

    def __init__(
        self,
        dead_zone: float = config.DEAD_ZONE,
        start_distance: int = config.START_DISTANCE,
        marker_true_size: int = config.MARKER_TRUE_SIZE,
        valid_id: int = config.CORRECT_ID,
        valid_frame_count: int = config.VALID_FRAME_COUNT,
    ) -> None:
        super().__init__(
            dead_zone, start_distance, marker_true_size, valid_id, valid_frame_count
        )
        dictionary = cv2.aruco.getPredefinedDictionary(config.ARUCO_TYPE)
        parameters = cv2.aruco.DetectorParameters()
        self.detector = cv2.aruco.ArucoDetector(dictionary, parameters)

    def find_contour(self, frame: np.ndarray) -> bool:
        self.points = None
        try:
            detected_points, detected_ids, _ = self.detector.detectMarkers(frame)
            if detected_points is not None and detected_ids is not None:
                for points, id in zip(detected_points, detected_ids):
                    if id == self.valid_id:
                        self.points = points
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

    def draw_contour(self, frame: np.ndarray) -> None:
        if not self.valid:
            return
        frame = cv2.aruco.drawDetectedMarkers(frame, [self.points], np.ndarray(self.valid_id))
        cv2.circle(frame, self.center, 2, config.CONTOUR_COLOR, -1) # TODO вынести в параметры метода

    def get_direction(self, frame_width: int) -> str:
        return super().get_direction(frame_width)

    def get_distance(self, distance_coefficient: float) -> int:
        return super().get_distance(distance_coefficient)

    def check_valid(self) -> None:
        return super().check_valid()

    def print_info(self, frame: np.ndarray) -> None:
        return super().print_info(frame)
