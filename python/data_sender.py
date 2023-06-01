from serial import Serial


class Sender:

    def __init__(self, bd_rate: int = 9600, usb_port: str = '/dev/ttyACM0', timeout: int = 1) -> None:
        self.boud_rate = bd_rate
        self.usb_port = usb_port
        self.timeout = timeout

    def open_connect(self) -> None:
        try:
            self.arduino = Serial(self.usb_port, self.boud_rate, self.timeout)
        except:
            print("ERROR - Could not open USB serial port.")

    def send_command(self, command: str) -> bool:
        try:
            self.arduino.write(command.encode(encoding='UTF-8'))
            return True
        except:
            return False

