from serial import Serial
import config


class Sender:
    def __init__(
        self,
        bd_rate=config.SERIAL_BOUD_RATE,
        usb_port=config.SERIAL_PORT,
        timeout=config.SERIAL_TIMEOUT,
    ) -> None:
        self.boud_rate = bd_rate
        self.usb_port = usb_port
        self.timeout = timeout

    def open_connect(self) -> None:
        try:
            self.arduino = Serial(
                port=self.usb_port, boudrate=self.boud_rate, timeout=self.timeout
            )
        except:
            print("ERROR - Could not open USB serial port.")

    def send_command(self, command: str) -> bool:
        try:
            self.arduino.write(command.encode(encoding="UTF-8"))
            return True
        except:
            return False


if __name__ == "__main__":
    sender = Sender()
    sender.open_connect()
