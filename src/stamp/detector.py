import tensorflow as tf
import cv2
import numpy as np
import time

from settings import STAMP_MODEL_PATH, CONFIDENCE, CUR_DIR, DETECTION_REGION

class StampDetector:

    def __init__(self):
        detection_graph = tf.Graph()
        with detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(STAMP_MODEL_PATH, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')

            self.sess = tf.Session(graph=detection_graph)

        self.image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
        self.boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
        self.scores = detection_graph.get_tensor_by_name('detection_scores:0')
        self.classes = detection_graph.get_tensor_by_name('detection_classes:0')
        self.num_detections = detection_graph.get_tensor_by_name('num_detections:0')

    def detect_objects(self, image_np):
        # Expand dimensions since the models expects images to have shape: [1, None, None, 3]
        image_np_expanded = np.expand_dims(image_np, axis=0)

        # Actual detection.
        return self.sess.run([self.boxes, self.scores, self.classes, self.num_detections],
                             feed_dict={self.image_tensor: image_np_expanded})

    def detect_from_images(self, frame, stamp_top_ret=False):

        if stamp_top_ret:
            frame = frame[DETECTION_REGION[1]:DETECTION_REGION[3], DETECTION_REGION[0]:DETECTION_REGION[2]]
        [frm_height, frm_width] = frame.shape[:2]
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        st_time = time.time()

        (boxes, scores, classes, _) = self.detect_objects(frame_rgb)
        print(f"detection time: {time.time() - st_time}")
        print(scores[0][:3])
        detected_rect_list = []
        detected_scores = []

        for i in range(len(scores[0])):
            if scores[0][i] >= CONFIDENCE:
                left, top = int(boxes[0][i][1] * frm_width), int(boxes[0][i][0] * frm_height)
                right, bottom = int(boxes[0][i][3] * frm_width), int(boxes[0][i][2] * frm_height)
                if stamp_top_ret:
                    detected_rect_list.append([left + DETECTION_REGION[0], top + DETECTION_REGION[1],
                                               right + DETECTION_REGION[0], bottom + DETECTION_REGION[1]])
                else:
                    detected_rect_list.append([left, top, right, bottom])
                detected_scores.append(scores[0][i])
                # cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 1)
        # cv2.imshow("Stamps", cv2.resize(frame, None, fx=0.5, fy=0.5))
        # cv2.waitKey()
        # max_detected_stamp_rect = detected_rect_list[detected_scores.index(max(detected_scores))]

        return detected_rect_list, detected_scores

if __name__ == '__main__':
    import glob
    import os

    stamp_detector = StampDetector()
    # rect_len = stamp_detector.detect_from_images(frame=cv2.imread("))
    img_files = glob.glob(os.path.join(CUR_DIR, 'new model', 'Bottom', "*.png"))

    for i_file in img_files:
        rect_len, _ = stamp_detector.detect_from_images(frame=cv2.imread(i_file))
        if len(rect_len) >= 2:
            print(f"[WARN] {i_file}: {rect_len}")
