import os
import tensorflow as tf
import sys
import numpy as np
import cv2

from src.feature.download import download_and_extract_model
from settings import MODEL_DIR


class ImageFeature:
    def __init__(self):
        self.model_dir = MODEL_DIR

        self.__create_graph()
        config = tf.ConfigProto()
        config.gpu_options.allow_growth = True
        self.sess = tf.Session(config=config)
        self.softmax_tensor = self.sess.graph.get_tensor_by_name('pool_3:0')

        sys.stdout.write("...init mxnet model.\n")
        test_img = np.ones((20, 20, 3), dtype=np.uint8)
        test_data = cv2.imencode('.jpg', test_img)[1].tostring()
        prediction = self.sess.run(self.softmax_tensor, {'DecodeJpeg/contents:0': test_data})
        prediction = np.squeeze(prediction)
        sys.stdout.write(
            "...length of feature {}    {}.\n".format(len(prediction), "success" * (len(prediction) == 2048)))

    def __create_graph(self):
        # Creates a graph from saved GraphDef file and returns a saver.
        # Creates graph from saved graph_def.pb.
        if not os.path.exists(os.path.join(self.model_dir, 'classify_image_graph_def.pb')):
            data_url = 'http://download.tensorflow.org/models/image/imagenet/inception-2015-12-05.tgz'
            download_and_extract_model(data_url=data_url, save_dir=self.model_dir)
        with tf.gfile.FastGFile(os.path.join(
                self.model_dir, 'classify_image_graph_def.pb'), 'rb') as f:
            graph_def = tf.GraphDef()
            graph_def.ParseFromString(f.read())
            _ = tf.import_graph_def(graph_def, name='')

    def get_feature_from_file(self, img_path):
        """Runs extract the feature from the image.
            Args: img_path: Image file name.

        Returns:  predictions: 2048 * 1 feature vector
        """

        if not tf.gfile.Exists(img_path):
            tf.logging.fatal('File does not exist %s', img_path)
        image_data = tf.gfile.FastGFile(img_path, 'rb').read()

        prediction = self.sess.run(self.softmax_tensor, {'DecodeJpeg/contents:0': image_data})
        prediction = np.squeeze(prediction)
        return prediction

    def get_feature_from_cvimg(self, cvimg):
        image_data = cv2.imencode('.jpg', cvimg)[1].tostring()
        prediction = self.sess.run(self.softmax_tensor, {'DecodeJpeg/contents:0': image_data})
        prediction = np.squeeze(prediction)
        return prediction


if __name__ == '__main__':
    _img_path = "sample.jpg"
    print(_img_path)
    feature = ImageFeature().get_feature_from_file(img_path=_img_path)
    print(len(feature))
