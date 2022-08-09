import os
import glob
import threading
import ntpath
import shutil
import time
import joblib
import configparser
import cv2

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock, mainthread
from src.stamp.detector import StampDetector
from src.arduino.communicator import ArduinoCom
from src.feature.extractor import ImageFeature
from src.stamp.aligner import StampAligner
from src.stamp.orientator import StampOrientation
from src.stamp.rotator import rotate_stamp
from src.image_processing.utils import ImageUtils
from src.stamp.collection_creator import create_main_collection_image
# from utils.folder_file_manager import log_print
from settings import MAIN_SCREEN_PATH, SIDE_MODEL_PATH, TOP_IMAGE_PATH, BOTTOM_IMAGE_PATH, CONFIG_FILE_PATH, \
    OUTPUT_DIR, TEMP_IMAGE_DIR, TEMP_FINAL_IMAGE_DIR, FRONT_ROI, BACK_ROI

Builder.load_file(MAIN_SCREEN_PATH)


class MainScreen(Screen):

    def __init__(self, **kwargs):

        super(MainScreen, self).__init__(**kwargs)
        params = configparser.ConfigParser()
        params.read(CONFIG_FILE_PATH)
        self.top_cam_num = int(params.get('DEFAULT', 'top_cam'))
        self.bottom_cam = int(params.get('DEFAULT', 'bottom_cam'))
        self.stamp_detector_cam_num = int(params.get('DEFAULT', 'stamp_detector_cam'))
        self.stamp_detector = StampDetector()
        self.ard_com = ArduinoCom()
        self.stamp_aligner = StampAligner()
        self.stamp_orientation = StampOrientation()
        self.image_utils = ImageUtils()
        self.side_model = joblib.load(SIDE_MODEL_PATH)
        self.image_feature = ImageFeature()
        self.ard_threading = None
        self.run_time_threading = None
        self.main_threading = None
        self.start_ret = False
        self.front_init_pos = FRONT_ROI
        self.back_init_pos = BACK_ROI
        self.collection_num = 1
        self.picture_num = 1
        self.stamp_num = 0
        self.processing_time = 0
        self.finished_collection = 0
        self.__initialize_collection_dir()

    @staticmethod
    def check_roi(roi, rect):
        if roi[1] < rect[0][1] - 20 < roi[1] + roi[3] and roi[1] < rect[0][3] + 20 < roi[1] + roi[3] and \
                roi[0] < rect[0][0] - 20 < roi[0] + roi[2] and roi[0] < rect[0][2] + 20 < roi[0] + roi[2]:
            return True
        else:
            return False

    def __initialize_collection_dir(self):
        collection_dirs = glob.glob(os.path.join(OUTPUT_DIR, "*.*"))
        output_indices = []
        for c_dir in collection_dirs:
            c_index = int(ntpath.basename(c_dir).replace("collection", ""))
            output_indices.append(c_index)
        if output_indices:
            self.collection_num = max(output_indices) + 1
        else:
            self.collection_num = 1

        return

    def on_enter(self, *args):
        self.ids.stamp_cam.start(port_num=self.stamp_detector_cam_num)
        self.ids.top_cam.start(port_num=self.top_cam_num)
        self.ids.bottom_cam.start(port_num=self.bottom_cam)

    def on_leave(self, *args):
        self.ids.stamp_cam.stop()
        self.ids.top_cam.stop()
        self.ids.bottom_cam.stop()
        self.start_ret = False
        self.ard_com.receive_ret = False
        self.ard_threading.join()
        self.run_time_threading.join()
        self.main_threading.join()
        super(MainScreen, self).on_leave(*args)

    def get_stamp_side(self, frame_path):
        frame_feature = self.image_feature.get_feature_from_file(img_path=frame_path)
        stamp_side_proba = max(self.side_model.predict_proba([frame_feature])[0])
        stamp_side = self.side_model.predict([frame_feature])[0]

        return stamp_side, stamp_side_proba

    def start_process(self):
        self.start_ret = True
        self.ard_com.receive_ret = True
        self.ard_com.send_command_arduino(command=f"1000, 1000")
        self.ard_threading = threading.Thread(target=self.ard_com.receive_command_arduino)
        self.ard_threading.start()
        self.run_time_threading = threading.Thread(target=self.display_processing_time)
        self.run_time_threading.start()
        self.main_threading = threading.Thread(target=self.run_main_process)
        self.main_threading.start()

        return

    def run_main_process(self):
        pic_per_collection = int(self.ids.pic_per_collection.text)
        if pic_per_collection not in [2, 4, 6, 8, 10]:
            self.start_ret = False
            print("[WARNING] Please input number of picture per collection among 2, 4, 6, 8 and 10")
        while self.start_ret:
            frame = self.ids.stamp_cam.get_frame()
            if frame is None:
                break
            if self.ard_com.ard_res == "d":
                detected_stamp_rect, detected_stamp_scores = self.stamp_detector.detect_from_images(frame=frame,
                                                                                                    stamp_top_ret=True)
                if detected_stamp_scores:
                    detected_stamp = detected_stamp_rect[detected_stamp_scores.index(max(detected_stamp_scores))]
                    stamp_x = int((detected_stamp[0] + detected_stamp[2]) / 2)
                    stamp_y = int((detected_stamp[1] + detected_stamp[3]) / 2)
                    print(f"[INFO] Pick Stamp at {stamp_x}, {stamp_y}")
                    ard_x = (stamp_y - 996) * 0.09368 + 190
                    ard_y = (stamp_x - 1249) * 0.09368 - 20
                    print(f"[INFO] Pick Stamp at {ard_x}, {ard_y} as Robot Arm Pos")
                    self.ard_com.send_command_arduino(command=f"{ard_x},{ard_y}")
                    self.ard_com.ard_res = None
                else:
                    self.ard_com.send_command_arduino(command="150,0")
                    self.ard_com.ard_res = None
            if self.ard_com.ard_res == "m":
                top_frame = self.ids.top_cam.get_frame()
                bottom_frame = self.ids.bottom_cam.get_frame()
                if top_frame is None or bottom_frame is None:
                    break
                cv2.imwrite(os.path.join(TEMP_IMAGE_DIR, f"top_frame_{time.time()}.jpg"), top_frame)
                cv2.imwrite(os.path.join(TEMP_IMAGE_DIR, f"bottom_frame_{time.time()}.jpg"), bottom_frame)
                top_height, top_width = top_frame.shape[:2]
                bottom_height, bottom_width = bottom_frame.shape[:2]
                top_stamps_rect, _ = self.stamp_detector.detect_from_images(frame=top_frame)
                bottom_stamps_rect, _ = self.stamp_detector.detect_from_images(frame=bottom_frame)
                if len(top_stamps_rect) == 1 and len(bottom_stamps_rect) == 1:
                    if self.check_roi(roi=self.front_init_pos, rect=top_stamps_rect) and \
                            self.check_roi(roi=self.back_init_pos, rect=bottom_stamps_rect):
                        print("[INFO] Single Detected!")
                        self.ard_com.send_command_arduino(command="single")
                        top_stamp_roi = top_frame[max(top_stamps_rect[0][1] - 20, 0):min(top_stamps_rect[0][3] + 20,
                                                                                         top_height),
                                                  max(top_stamps_rect[0][0] - 20, 0):min(top_stamps_rect[0][2] + 20,
                                                                                         top_width)]
                        cv2.imwrite(TOP_IMAGE_PATH, top_stamp_roi)
                        bottom_stamp_roi = \
                            bottom_frame[max(bottom_stamps_rect[0][1] - 20, 0):min(bottom_stamps_rect[0][3] + 20,
                                                                                   bottom_height),
                                         max(bottom_stamps_rect[0][0] - 20, 0):min(bottom_stamps_rect[0][2] + 20,
                                                                                   bottom_width)]
                        cv2.imwrite(BOTTOM_IMAGE_PATH, bottom_stamp_roi)
                        top_side, top_proba = self.get_stamp_side(frame_path=TOP_IMAGE_PATH)
                        bottom_side, bottom_proba = self.get_stamp_side(frame_path=BOTTOM_IMAGE_PATH)
                        if top_side == "front" and bottom_side == "front":
                            if top_proba > bottom_proba:
                                front_stamp_image = top_stamp_roi
                            else:
                                front_stamp_image = bottom_stamp_roi
                        else:
                            if top_side == "front":
                                front_stamp_image = top_stamp_roi
                            else:
                                if bottom_side == "front":
                                    front_stamp_image = bottom_stamp_roi
                                else:
                                    self.ard_com.send_command_arduino(command="retry")
                                    self.ard_com.ard_res = None
                                    continue
                        processed_image = front_stamp_image
                        # processed_image = self.image_utils.run(frame=front_stamp_image)
                        rotated_image_path, rotated_image = rotate_stamp(frame=processed_image)
                        orientation = self.stamp_orientation.estimate_rotate_angle(frame_path=rotated_image_path)
                        if orientation == "normal":
                            final_stamp_image = rotated_image
                        elif orientation == "clock":
                            final_stamp_image = cv2.rotate(rotated_image, cv2.ROTATE_90_CLOCKWISE)
                        elif orientation == "counter_clock":
                            final_stamp_image = cv2.rotate(rotated_image, cv2.ROTATE_90_COUNTERCLOCKWISE)
                        else:
                            final_stamp_image = cv2.rotate(rotated_image, cv2.ROTATE_180)
                        cv2.imwrite(os.path.join(TEMP_FINAL_IMAGE_DIR, f"{self.picture_num}_{self.stamp_num}.jpg"),
                                    final_stamp_image)
                        res, align_image_path = self.stamp_aligner.pack_stamps(stamp_frame=final_stamp_image,
                                                                               collection_num=self.collection_num,
                                                                               picture_num=self.picture_num)
                        self.stamp_num += 1
                        ard_cmd = "retry"
                        if res:
                            self.picture_num += 1
                        if self.picture_num > pic_per_collection:
                            ard_cmd = "complete"
                        Clock.schedule_once(lambda dt: self.insert_image(rotated_image_path, align_image_path))
                        self.ard_com.send_command_arduino(command=ard_cmd)
                        if self.picture_num > pic_per_collection:
                            create_main_collection_image(collection_num=self.collection_num)
                            self.picture_num = 1
                            self.collection_num += 1
                            self.stamp_num = 0
                            self.finished_collection += 1
                    else:
                        print("[INFO] Multi or None Detected")
                        self.ard_com.send_command_arduino(command="none")
                else:
                    print("[INFO] Multi or None Detected")
                    self.ard_com.send_command_arduino(command="none")
                self.ard_com.ard_res = None

        return

    @mainthread
    def insert_image(self, rotate_img_path, align_img_path):
        self.ids.rotated_image.source = rotate_img_path
        self.ids.align_image.source = align_img_path
        self.ids.rotated_image.reload()
        self.ids.align_image.reload()
        self.ids.finished_collection.text = str(self.finished_collection)
        self.ids.no_stamps.text = str(self.stamp_num)
        # print(self.rotated_image_path)
        # print(self.align_image_path)

    def display_processing_time(self):
        start_time = time.time()
        while self.start_ret:
            time.sleep(0.03)
            run_time = time.time() - start_time + self.processing_time
            p_sec = int(run_time % 60)
            p_min = int(run_time // 60)
            p_hour = int(run_time // 3600)
            self.ids.run_time.text = f"{p_hour}:{p_min}:{p_sec}"
        self.processing_time += time.time() - start_time

        return

    def stop_process(self):
        pic_per_collection = int(self.ids.pic_per_collection.text)
        self.start_ret = False
        if self.run_time_threading is not None:
            self.run_time_threading.join()
        if self.main_threading is not None:
            self.main_threading.join()
        self.ard_com.receive_ret = False
        if self.ard_threading is not None:
            self.ard_threading.join()
        self.processing_time = 0
        self.stamp_num = 0
        self.picture_num = 1
        self.finished_collection = 0
        self.ids.finished_collection.text = "00"
        self.ids.no_stamps.text = "00"
        self.ids.run_time.text = "00:00:00"
        # self.ard_com.send_command_arduino(command="stop")
        if self.picture_num <= pic_per_collection:
            if os.path.exists(os.path.join(OUTPUT_DIR, f"collection{self.collection_num}")):
                shutil.rmtree(os.path.join(OUTPUT_DIR, f"collection{self.collection_num}"))
        else:
            self.collection_num += 1

        return

    def pause_process(self):
        self.start_ret = False
        self.ard_com.receive_ret = False
        self.run_time_threading.join()
        self.ard_threading.join()
        self.main_threading.join()

    def close_window(self):
        self.start_ret = False
        self.ard_com.receive_ret = False
        self.run_time_threading.join()
        self.ard_threading.join()
        self.main_threading.join()
        App.get_running_app().stop()

    def on_close(self):
        pass
