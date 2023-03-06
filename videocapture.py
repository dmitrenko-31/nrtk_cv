import cv2
import numpy as np

cam1, cam2 = cv2.VideoCapture(0), cv2.VideoCapture(1)

  
while True:
	ret1, frame1 = cam1.read()
	ret2, frame2 = cam2.read()
	cv2.imshow('frame', cv2.hconcat([frame1, frame2]))
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break

cam1.release()
cam2.release()
cv2.destroyAllWindows()
