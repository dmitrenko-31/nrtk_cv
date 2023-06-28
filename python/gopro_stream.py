""" Модуль для работы с камерой GoPro"""
import requests
import config


class gopro:
    """
    Класс для предоставления камеры GoPro.

    Атрибуты:
    ---------
    ip: str
        ip адрес камеры
    protocol: str
        протокол для отправки команд

    """

    def __init__(
        self, serial: str = config.GOPRO_SERIAL, protocol: str = "http"
    ) -> None:
        """
        Устанавливает все необходимые атрибуты для объекта gopro.

        Параметры:
        ----------
        serial: str, optional
            3 последних цифры серийного номера камеры GoPro. По умолчанию config.GOPRO_SERIAL.
        protocol: str, optional
            используемый протокол для отправки команд. По умолчанию "http".
        """
        self.ip = "172.2{0}.1{1}{2}.51".format(*serial)
        self.protocol = protocol

    def stream_start(self) -> requests.Response:
        """
        Отправляет команду старта потока.

        Возвращаемое значение:
        ----------------------
        requests.Response:
            ответ сервера на запрос
        """
        return requests.get(
            self.protocol + "://" + self.ip + "/gopro/camera/stream/start"
        )

    def stream_stop(self) -> requests.Response:
        """
        Отправляет команду остановки потока.

        Возвращаемое значение:
        ----------------------
        requests.Response:
            ответ сервера на запрос
        """
        return requests.get(
            self.protocol + "://" + self.ip + "/gopro/camera/stream/stop"
        )

    def stream_exit(self) -> requests.Response:
        """
        Отправляет команду выхода из режима потоковой передачи видео.

        Возвращаемое значение:
        ----------------------
        requests.Response:
            ответ сервера на запрос
        """
        return requests.get(
            self.protocol + "://" + self.ip + "/gopro/camera/stream/start"
        )


if __name__ == "__main__":
    gopro = gopro()
    gopro.stream_start()
