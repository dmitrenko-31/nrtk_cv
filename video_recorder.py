import cv2
import time

cam = cv2.VideoCapture(0)
fps = 20

out = cv2.VideoWriter(f'./resources/video{time.time()}.mp4',
                      cv2.VideoWriter_fourcc(*'mp4v'), fps, (640,  480))

while True:
	ret, frame = cam.read()
	out.write(frame)
	cv2.imshow('frame', frame)
	if cv2.waitKey(1) & 0xFF == ord('q'):
	    break

cam.release()
cv2.destroyAllWindows()
