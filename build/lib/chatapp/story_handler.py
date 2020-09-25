import csv
import pandas as pd
import nltk
import sklearn
if sklearn.__version__ > '0.18':
    from sklearn.model_selection import train_test_split
else:
    from sklearn.cross_validation import train_test_split

from sklearn.metrics import accuracy_score, confusion_matrix
import matplotlib.pyplot as plt
import gensim
from gensim.models import Word2Vec
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier

import pickle
import os
import pdb
from chatapp import db_handler

path_knn_model = os.path.join("model", "story_knn.pickle")
path_rf_model = os.path.join("model", "story_rf.pickle")
class Story_Feature_Vector:
    def story_feature_vector_Create(self, data):
        return db_handler.Story().add_features(data)

class Story:
    def load_knn(self):
        return pickle.load(open(path_knn_model, "rb"))
    def load_rf(self):
        return pickle.load(open(path_rf_model, "rb"))
    def Prediction(self, data, model = "random_forest"):
        result = {}
        error = []
        
        feature_vector = data["feature_vec"]        
        feature = [int(x) for x in feature_vector.split(", ")]
        
        if model == "random_forest":
            model = self.load_rf()
        elif model == "knn":
            model = self.load_knn()
        predicted = model.predict([feature])
        result["predicted"] = int(predicted[0])
        return result, error
    def train_knn(self, X_train, y_train):
        knn_naive_dv = KNeighborsClassifier(n_neighbors=3, n_jobs=1, algorithm='brute', metric='cosine' )
        knn_naive_dv.fit(X_train, y_train)
        # Save model
        
        pickle.dump(knn_naive_dv, open(path_knn_model, "wb"))
    def train_randomForest(self, X_train, y_train):        
        random_forest = RandomForestClassifier(max_depth=4, random_state=0)
        random_forest.fit(X_train, y_train)
        # Save model
        
        pickle.dump(random_forest, open(path_rf_model, "wb"))

class  Story_Trainer:
    def story_feature_vector_training(self):
        result = {}
        error = []
        
        # retrieving X
        X, y = db_handler.Story().get_dataset()
        # retrieving y
        pdb.set_trace()
        # X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=42)
        Story().train_randomForest(X, y)
        result["Is_Trained"] = True
        return result, error