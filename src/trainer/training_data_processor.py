import os
import pandas as pd

from src.feature.extractor import ImageFeature
from settings import CUR_DIR


class TrainDataProcessor:
    def __init__(self):
        self.feature_extractor = ImageFeature()
        self.training_data = os.path.join(CUR_DIR, 'classification_dir')

    def create_training_data(self):
        image_features = []
        image_labels = []
        side_file_path = os.path.join(self.training_data, 'side_features.csv')
        for path, sub_dirs, files in os.walk(self.training_data):
            if files:
                current_category = path.replace(self.training_data, "").split("/")[1]
                for file in files:
                    try:
                        image_features.append(
                            self.feature_extractor.get_feature_from_file(img_path=os.path.join(path, file)).tolist())
                        image_labels.append(current_category)
                    except Exception as e:
                        print(e)
                        print(path, file)

        pd.DataFrame(list(zip(image_features, image_labels)),
                     columns=["Feature", "Label"]).to_csv(side_file_path, index=False,
                                                          header=True,
                                                          mode="w")

        print(f"[INFO] Successfully saved data into {side_file_path}")

        return


if __name__ == '__main__':
    TrainDataProcessor().create_training_data()
