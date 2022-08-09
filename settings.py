import os

from utils.folder_file_manager import make_directory_if_not_exists


CUR_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(CUR_DIR, 'utils', 'model')
OUTPUT_DIR = make_directory_if_not_exists(os.path.join(CUR_DIR, 'output'))
TEMP_IMAGE_DIR = make_directory_if_not_exists(os.path.join(CUR_DIR, 'temp'))
TEMP_FINAL_IMAGE_DIR = make_directory_if_not_exists(os.path.join(CUR_DIR, 'temp_final'))

CREDENTIAL_PATH = os.path.join(CUR_DIR, 'utils', 'credential', 'vision_key.txt')
STAMP_MODEL_PATH = os.path.join(MODEL_DIR, 'stamp_detector_v2.pb')
SIDE_MODEL_PATH = os.path.join(MODEL_DIR, 'side_classifier.pkl')
CONFIG_FILE_PATH = os.path.join(CUR_DIR, 'user_config.cfg')
TOP_IMAGE_PATH = os.path.join(CUR_DIR, 'top.jpg')
BOTTOM_IMAGE_PATH = os.path.join(CUR_DIR, 'bottom.jpg')
MAIN_SCREEN_PATH = os.path.join(CUR_DIR, "gui", 'kiv', "main_screen.kv")
BAD_FRAME_PATH = os.path.join(CUR_DIR, 'utils', 'img', 'bad_camera.png')

MAIN_SCREEN = "main_screen"
APP_WIDTH = '1920'
APP_HEIGHT = '1080'
ROTATION_Y_THREAD = 50
CONFIDENCE = 0.6
BAUD_RATE = 115200
STAMP_AREA_THRESH = 0.02
PIXEL_TO_MM = 11.2
PAPER_WIDTH = 210
PAPER_HEIGHT = 290
DETECTION_REGION = [466, 390, 2870, 2325]
FRONT_ROI = []
BACK_ROI = []

COLLECTION_PATH = ""
