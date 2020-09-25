import logging
logging.root.handlers = []  # Jupyter messes up logging so needs a reset
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
from smart_open import smart_open
import numpy as np
from numpy import random
import gensim
import nltk
import sklearn
if sklearn.__version__ > '0.18':
    from sklearn.model_selection import train_test_split
else:
    from sklearn.cross_validation import train_test_split

from sklearn import linear_model
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics import accuracy_score, confusion_matrix
import matplotlib.pyplot as plt
from gensim.models import Word2Vec
from sklearn.neighbors import KNeighborsClassifier
from nltk.corpus import stopwords
import pickle
import os

import pdb

from chatapp import db_handler

print("[+] GoogleNews-vectors-negative300 loading...Size: 1.5GB")
wv = gensim.models.KeyedVectors.load_word2vec_format( "model/GoogleNews-vectors-negative300.bin.gz", binary=True)
wv.init_sims(replace=True)

path_knn_model = os.path.join("model", "knn.pickle")
path_logic_reg_model = os.path.join("model", "logistic_regression.pickle")

class Training:
    def mytrain_test_split(self):
        # read data from datbase
        # X is query
        # y is intent
        X, y = db_handler.Intent_Training_Dataset().intent_training_data()
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=42)
        return X_train, X_test, y_train, y_test

    def plot_confusion_matrix(self, cm, title='Confusion matrix', cmap=plt.cm.Blues):
        plt.imshow(cm, interpolation='nearest', cmap=cmap)
        plt.title(title)
        plt.colorbar()
        tick_marks = np.arange(len(my_tags))
        target_names = my_tags
        plt.xticks(tick_marks, target_names, rotation=45)
        plt.yticks(tick_marks, target_names)
        plt.tight_layout()
        plt.ylabel('True label')
        plt.xlabel('Predicted label')
        plt.savefig("confusion_matrix.png")

    def evaluate_prediction(self, predictions, target, title="Confusion matrix"):
        print('accuracy %s' % accuracy_score(target, predictions))
        cm = confusion_matrix(target, predictions)
        print('confusion matrix\n %s' % cm)
        print('(row=expected, col=predicted)')

        cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        # self.plot_confusion_matrix(cm_normalized, title + ' Normalized') 
    
    
    def word_averaging(self, wv, words):
        all_words, mean = set(), []

        for word in words:
            if isinstance(word, np.ndarray):
                mean.append(word)
            elif word in wv.vocab:
                mean.append(wv.syn0norm[wv.vocab[word].index])
                all_words.add(wv.vocab[word].index)

        if not mean:
            logging.warning("[-] cannot compute similarity with no input %s", words)
            # FIXME: remove these examples in pre-processing
            return np.zeros(wv.layer1_size,)

        mean = gensim.matutils.unitvec(np.array(mean).mean(axis=0)).astype(np.float32)
        return mean
    
    def  word_averaging_list(self, wv, text_list):
        return np.vstack([self.word_averaging(wv, review) for review in text_list ])
    
    def w2v_tokenize_text(self, text):
        tokens = []
        for sent in nltk.sent_tokenize(text, language='english'):
            for word in nltk.word_tokenize(sent, language='english'):
                if len(word) < 2:
                    continue
                tokens.append(word)
        return tokens
    def remove_lessfrequent_words(self, input_text):        
        all_ = [x for y in input_text for x in y.split(' ') ]
        a,b = np.unique(all_, return_counts = True)
        to_remove = a[b<2]
        output_text = [' '.join(np.array(y.split(' '))[~np.isin(y.split(' '), to_remove)]) for y in input_text]
        return output_text
    def clean_data(self, X, y=None):        
        if y:
            X = self.remove_lessfrequent_words(X)

        tokenized_list = []
        for text in X:
            tokenized_list.append(self.w2v_tokenize_text(text))
        if y:
            i = 0                        
            for j in range(0, len(tokenized_list)):            
                if len(tokenized_list[i]) == 0:  
                    print(tokenized_list.pop(i))
                    print(y.pop(i))
                else:
                    i += 1
        
        return tokenized_list, y

    def train_knn(self, X_train_word_average, y_train):
        knn_naive_dv = KNeighborsClassifier(n_neighbors=3, n_jobs=1, algorithm='brute', metric='cosine' )
        knn_naive_dv.fit(X_train_word_average, y_train)
        # Save model
        pickle.dump(knn_naive_dv, open(path_knn_model, "wb"))

    def train_logistic_reg(self, X_train_word_average, y_train):
        logreg = linear_model.LogisticRegression(n_jobs=1, C=1e5)
        logreg = logreg.fit(X_train_word_average, y_train)
        # Save model
        pickle.dump(logreg, open(path_logic_reg_model, "wb"))

    def load_knn(self):
        return pickle.load(open(path_knn_model, "rb"))

    def load_logic_reg(self):
        return pickle.load(open(path_logic_reg_model, "rb"))

    def train(self):
        result = {}
        error = []
        
        X_train, X_test, y_train, y_test = self.mytrain_test_split()
        train_tokenized, y_train = self.clean_data(X_train, y_train)
        # test_tokenized, y_test = self.clean_data(X_test, y_test)

        X_train_word_average = self.word_averaging_list(wv,train_tokenized)
        # X_test_word_average = self.word_averaging_list(wv,test_tokenized)

        self.train_logistic_reg(X_train_word_average, y_train)
        self.train_knn(X_train_word_average, y_train)
        predicted = model_knn.predict([X_train_word_average[0]])
        result["train"] = True
        return result, error

obj_training = Training()

if os.path.exists(path_knn_model):
    model_knn = obj_training.load_knn()
    print("[+] <--- Interactive KNN model loaded successfully...--->")

class Prediction:
    # def predict_knn(self):
    #     predicted = knn_naive_dv.predict(X_test_word_average)
    #     print(predicted)
    #     self.evaluate_prediction(predicted, y_test)
    def predict_KNN(self, data):        
        result = {}
        error = []
        test_tokenized, _ = obj_training.clean_data([data["end_user_expression"]])
        
        word_average = obj_training.word_averaging_list(wv,test_tokenized)
        predicted = model_knn.predict(word_average)
        """ At present knn_model is used to predict. Besides, we gave logistic-regression
            to train for the making model. So both logistic_regression and knn are available
            to predict. Choose which gives better prediction.
        """
        intent_id = db_handler.Get_Intent_Handler().get_intent_id(predicted[0])
        result["predicted"] = predicted[0]
        result["intent_id"] = intent_id
        return result, error
