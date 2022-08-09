import os
import pandas as pd
import joblib
import numpy as np

from ast import literal_eval
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from settings import CUR_DIR, MODEL_DIR


class ClassifierTrainer:
    def __init__(self):
        self.x_data = []
        self.y_data = []

        self.model_names = ["Nearest Neighbors", "Linear SVM", "RBF SVM", "Gaussian Process",
                            "Decision Tree", "Random Forest", "Neural Net", "AdaBoost",
                            "Naive Bayes", "QDA"]
        self.classifiers = [
            KNeighborsClassifier(3),
            SVC(kernel="linear", C=2, degree=3, gamma='auto', coef0=0.0, shrinking=True, probability=True,
                tol=0.001, cache_size=200, class_weight='balanced', verbose=False, max_iter=-1,
                decision_function_shape='ovr', random_state=None),
            SVC(gamma=2, C=1, probability=True),
            GaussianProcessClassifier(1.0 * RBF(1.0)),
            DecisionTreeClassifier(max_depth=5),
            RandomForestClassifier(max_depth=5, n_estimators=10, max_features=1),
            MLPClassifier(alpha=1, max_iter=1000),
            AdaBoostClassifier(),
            GaussianNB(),
            QuadraticDiscriminantAnalysis()]

    @staticmethod
    def convert_str_array(array_str):
        list_str = array_str.replace("  ", " ").replace(" ", ",")
        last_comma = list_str.rfind(",")
        f_list_str = list_str[:last_comma] + list_str[last_comma + 1:]
        converted_array = np.array(literal_eval(f_list_str))

        return converted_array

    def train_best_model(self, model_path):
        x_train, x_test, y_train, y_test = \
            train_test_split(self.x_data, self.y_data, test_size=.3, random_state=42)

        scores = []
        for name, clf in zip(self.model_names, self.classifiers):
            clf.fit(x_train, y_train)
            score = clf.score(x_test, y_test)
            scores.append(score)
            print(f"[INFO] model:{name}, score:{score}")

        print(f"[INFO] The best model: {self.model_names[scores.index(max(scores))]}, {max(scores)}")
        best_clf = self.classifiers[scores.index(max(scores))]
        best_clf.fit(self.x_data, self.y_data)
        score = best_clf.score(x_test, y_test)
        print(f"[INFO] The accuracy of the best model: {self.model_names[scores.index(max(scores))]}, {score}")
        joblib.dump(best_clf, model_path)
        print(f"[INFO] Successfully saved in {model_path}")

        return

    def train(self):
        train_df = pd.read_csv(os.path.join(CUR_DIR, 'classification_dir', 'side_features.csv'))
        self.y_data = train_df["Label"].values.tolist()
        for x_d_f in train_df["Feature"].values.tolist():
            self.x_data.append(literal_eval(x_d_f))

        self.train_best_model(model_path=os.path.join(MODEL_DIR, "side_classifier.pkl"))

        return


if __name__ == '__main__':
    ClassifierTrainer().train()
