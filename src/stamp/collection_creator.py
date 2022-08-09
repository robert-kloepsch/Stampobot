import os
import glob
import numpy as np
import cv2

from settings import PAPER_HEIGHT, PAPER_WIDTH, PIXEL_TO_MM, OUTPUT_DIR


def create_main_collection_image(collection_num):
    main_collection_pic_path = os.path.join(OUTPUT_DIR, f"collection{collection_num}",
                                            f"Collection{collection_num}.jpg")
    pic_width = int(PAPER_WIDTH * PIXEL_TO_MM)
    pic_height = int(PAPER_HEIGHT * PIXEL_TO_MM)
    pictures = []
    for init_pic in glob.glob(os.path.join(OUTPUT_DIR, f"collection{collection_num}", "*.jpg")):
        if "Picture" in init_pic:
            pictures.append(init_pic)
    cols = len(pictures) // 2
    if cols < 2:
        collection_image = np.ones([pic_height, pic_width * 2, 3], dtype=np.uint8) * 255
    else:
        collection_image = np.ones([pic_height * 2, pic_width * cols, 3], dtype=np.uint8) * 255
    for pic_idx, pic in enumerate(pictures):
        pic_image = cv2.imread(pic)
        if pic_idx < 2:
            collection_image[:pic_height, pic_width * pic_idx:pic_width * (pic_idx + 1)] = pic_image
        else:
            if pic_idx < cols:
                collection_image[:pic_height, pic_width * pic_idx:pic_width * (pic_idx + 1)] = pic_image
            else:
                collection_image[pic_height:pic_height * 2, pic_width * (pic_idx - cols):pic_width * (
                        pic_idx - cols + 1)] = pic_image

    cv2.imwrite(main_collection_pic_path, cv2.resize(collection_image, None, fx=0.7, fy=0.7))
    # print(f"[INFO] Successfully saved collection image into {main_collection_pic_path}")

    return


if __name__ == '__main__':
    create_main_collection_image(collection_num=0)
