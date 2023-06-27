import requests


class gopro:
    def __init__(self, serial=tuple('322')) -> None:
        self.ip = f"http://172.2{serial[0]}.1{serial[1]}{serial[2]}.51:8080".format(serial)

    def stream_start(self):
        return requests.get(self.ip + "/gopro/camera/stream/start")

    def stream_stop(self):
        return requests.get(self.ip + "/gopro/camera/stream/stop")

    def stream_exit(self):
        return requests.get(self.ip + "/gopro/camera/stream/start")
    
if __name__ == '__main__':
    go = gopro()
    go.stream_start()
