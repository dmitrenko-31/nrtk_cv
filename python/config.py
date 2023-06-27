from cv2 import aruco, VideoWriter_fourcc, CAP_V4L2

START_DISTANCE = 1000  # Расстояние, с которого начинается движение вперед
MARKER_TRUE_SIZE = 150  # Размер маркера в мм
DEAD_ZONE = 0.1 # мертвая зона поворота - 10%
CORRECT_ID = 1

# Разрешение камеры
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720



# Font 
FONT_COLOR = (0, 255, 0)
FONT_SIZE = 2
FONT_THICKNESS = 2
FONT_SCALE = 2

CONTOUR_COLOR = (0, 255, 0)

VALID_FRAME_COUNT = 3
ARUCO_TYPE = aruco.DICT_4X4_250

VIDEO_CODEC = VideoWriter_fourcc(*'MJPG')
PREF_API = CAP_V4L2
CAMERA_INDEX = 0

