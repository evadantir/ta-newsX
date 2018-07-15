import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib

class Trainer(object):
    def convertToNumeric(self,dataset):
        # convert categorical feature to numeric
        dataset['type'] = dataset['type'].map({'PERSON': 1, 'LOCATION': 2, 'ORGANIZATION': 3,'NP': 4}).astype(int)
        dataset['occ_title'] = dataset['occ_title'].map({False: 0, True: 1}).astype(int)
        return dataset

    def train(self,dataset,news_element):
        #classifier algorithm
        clf = RandomForestClassifier()

        # extract feature needed, drop entity
        dataset = dataset.drop(['entity',news_element], axis=1)
        # print dataset
        # exit()

        dataset = self.convertToNumeric(dataset)

        # determine wich column is feature or label
        X = dataset.iloc[:,:-1]
        y = dataset.iloc[:,-1]
        print X
        print y
        exit()

        if news_element == 'who':    
            # training and save into pickle
            joblib.dump(clf.fit(X, y),'model/train_who.pkl')
            print "Model for WHERE has been saved"
        elif news_element == 'where':
            # training and save into pickle
            joblib.dump(clf.fit(X, y),'model/train_where.pkl')
            print "Model for WHO has been saved"

tr = Trainer()

df = pd.read_excel('test123.xlsx', sheet_name='Sheet1')

# training model for detecting who and where
tr.train(df,'where')

# tr.train(df,'who')
