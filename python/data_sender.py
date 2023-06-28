"""
Модуль для работы с Arduino
    Классы:
        Sender
        
"""
from serial import Serial
import config


class Sender:
    """
    Класс для работы с Arduino.

    Атрибуты:
    ----------
    boudrate: int
        скороть передачи данных
    usb_port: str
        порт usb (директория)
    timeout: int
        задержка(мс)

    Методы:
    ----------
    open_connect():
        Создает объект класса Serial, открывает соединение с Arduino.
    send_command(command):
        Отправляет комманду command на Arduino.
    """

    def __init__(
        self,
        bd_rate: int = config.SERIAL_BOUD_RATE,
        usb_port: str | None = config.SERIAL_PORT,
        timeout: int = config.SERIAL_TIMEOUT,
    ) -> None:
        """
        Устанавливает все необходимые атрибуты для объекта sender.

        Параметры:
        ----------
        bd_rate: int, optional
            скорость передачи данных. По умолчанию config.SERIAL_BOUD_RATE.
        usb_port: str | None, optional
            порт usb. По умолчанию config.SERIAL_PORT.
        timeout: int, optional
            задержка (мс). По умолчанию config.SERIAL_TIMEOUT.
        """

        self.boud_rate = bd_rate
        self.usb_port = usb_port
        self.timeout = timeout

    def open_connect(self) -> None:
        """Создает объект класса Serial, открывает соединение с Arduino."""
        try:
            self.arduino = Serial(
                port=self.usb_port, boudrate=self.boud_rate, timeout=self.timeout
            )
        except:
            print("ERROR - Could not open USB serial port.")

    def send_command(self, command: str) -> bool:
        """
        Отправляет команду на Arduino

        Возращает True при успешной отправке, иначе False

        Параметры:
        ----------
        command: str
            команда

        Возвращаемое значение:
        ----------------------
        bool:
            результат отправки
        """
        try:
            self.arduino.write(command.encode(encoding="UTF-8"))
            return True
        except:
            return False


if __name__ == "__main__":
    sender = Sender()
    sender.open_connect()
