import os
import glob
import ntpath
import cv2

from settings import CUR_DIR


def collect_rotated_images(img_dir):
    image_paths = glob.glob(os.path.join(img_dir, "*.jpg"))
    for i_path in image_paths:
        image_name = ntpath.basename(i_path).replace(".jpg", "")
        image = cv2.imread(i_path)
        clock_image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        counter_clock_image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        horizontal_image = cv2.rotate(image, cv2.ROTATE_180)
        cv2.imwrite(os.path.join(img_dir, f"{image_name}_clocked.jpg"), clock_image)
        cv2.imwrite(os.path.join(img_dir, f"{image_name}_counter_clocked.jpg"), counter_clock_image)
        cv2.imwrite(os.path.join(img_dir, f"{image_name}_180.jpg"), horizontal_image)

    return


def create_training_images(origin_img_dir):
    image_paths = glob.glob(os.path.join(origin_img_dir, "*.*"))
    cnt = 895
    for i_path in image_paths:
        image = cv2.imread(i_path)
        cv2.imwrite(os.path.join(CUR_DIR, 'training_dir', f"image{cnt}.jpg"), image)
        cnt += 1

    return


def creat_front_back_classification_images(img_dir):
    image_paths = glob.glob(os.path.join(img_dir, "*.*"))
    front_cnt = 116
    for i_path in image_paths:
        frame = cv2.imread(i_path)
        init_pos = cv2.selectROI("Front/Back Selection", cv2.resize(frame, None, fx=0.5, fy=0.5), fromCenter=False,
                                 showCrosshair=True)
        if init_pos != (0, 0, 0, 0):
            roi_frame = frame[init_pos[1] * 2:2 * (init_pos[1] + init_pos[3]), 2 * init_pos[0]:2 * (init_pos[0] +
                                                                                                    init_pos[2])]
            cv2.imwrite(os.path.join(CUR_DIR, 'classification_dir', "back", f"image{front_cnt}.jpg"), roi_frame)
            front_cnt += 1
        cv2.destroyWindow("Front/Back Selection")

    return


if __name__ == '__main__':
    creat_front_back_classification_images(img_dir="/media/main/Data/Task/StampDetectorArduino/Pictures_second_project/Single/01. Top")
