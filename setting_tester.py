import cv2

from src.image_processing.utils import ImageUtils
from settings import COLLECTION_PATH

image_utils = ImageUtils()
image = cv2.imread(COLLECTION_PATH)
processed_image = image_utils.run(frame=image)
cv2.imshow("Processed Image", cv2.resize(processed_image, None, fx=0.4, fy=0.4))
cv2.waitKey()
