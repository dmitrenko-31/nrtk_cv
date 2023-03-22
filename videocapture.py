import cv2
import time

cam = cv2.VideoCapture('./resources/example.mp4')
fps = 20

while True:
	ret, frame = cam.read()
	cv2.imshow('frame', frame)
	time.sleep(1.0 / fps - 0.005)
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break

cam.release()
cv2.destroyAllWindows()
