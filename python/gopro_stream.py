import requests


class gopro:
    def __init__(self, serial=tuple(3, 2, 2)) -> None:
        self.ip = "http://172.2{}.1{}{}.51:8080".format(serial)

    def stream_start(self):
        return requests.get(self.ip + "/gopro/camera/stream/start")

    def stream_stop(self):
        return requests.get(self.ip + "/gopro/camera/stream/stop")

    def stream_exit(self):
        return requests.get(self.ip + "/gopro/camera/stream/start")
