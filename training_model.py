import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score
import joblib

class Trainer(object):
    def convertToNumeric(self,dataset):
        # convert categorical feature to numeric
        dataset['type'] = dataset['type'].map({'PERSON': 1, 'LOCATION': 2, 'ORGANIZATION': 3,'NP': 4}).astype(int)
        dataset['occ_title'] = dataset['occ_title'].map({False: 0, True: 1}).astype(int)
        return dataset

    def train(self,dataset,drop_element):
        #classifier algorithm
        clf = RandomForestClassifier(n_estimators=10, random_state=42)

        # extract feature needed, drop entity
        dataset = dataset.drop(['entity','id_text',drop_element], axis=1)
        # print dataset
        # exit()

        dataset = self.convertToNumeric(dataset)

        # determine wich column is feature or label
        X = dataset.iloc[:, :-1]
        y = dataset.iloc[:, -1]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        clf = clf.fit(X_train, y_train)

        y_pred = clf.predict(X_test)
        print("Accuracy: ", (accuracy_score(y_test, y_pred) * 100).round(4))
        print("Precision: ", (precision_score(y_test, y_pred) * 100).round(4))
        print("Recall: ", (recall_score(y_test, y_pred) * 100).round(4))
        print("F-measure: ", (f1_score(y_test, y_pred) * 100).round(4))

        if drop_element == 'who':
            # training and save into pickle
            joblib.dump(clf,'model/train_where.pkl')
            print ("Model for WHERE has been saved")
        elif drop_element == 'where':
            # training and save into pickle
            joblib.dump(clf,'model/train_who.pkl')
            print ("Model for WHO has been saved")

tr = Trainer()

# reading excel that contain features (HARUS DIKASIH KOLOM WHO DAN WHERE DULU, DAN DITENTUKAN YANG MANA WHO DAN WHERE)
df = pd.read_excel('goldendata_extracted_feature.xlsx', sheet_name='Sheet1')
# training model for detecting who and where, input "where" or "who" meaning that column will be dropped (deleted)
tr.train(df,'where')
tr.train(df,'who')
