import requests
import config

class gopro:
    def __init__(self) -> None:
        self.ip = "http://172.2{0}.1{1}{2}.51".format(*config.GOPRO_SERIAL)

    def stream_start(self):
        return requests.get(self.ip + "/gopro/camera/stream/start")

    def stream_stop(self):
        return requests.get(self.ip + "/gopro/camera/stream/stop")

    def stream_exit(self):
        return requests.get(self.ip + "/gopro/camera/stream/start")
    
if __name__ == '__main__':
    gopro = gopro()
    gopro.stream_start()