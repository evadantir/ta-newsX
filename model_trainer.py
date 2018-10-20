import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import KFold
from sklearn.model_selection import StratifiedKFold
import joblib


class ModelTrainer(object):
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
        # X itu fitur
        X = dataset.iloc[:, :-1] # [x = take  entire row, y = take all column except last column]
        # y itu label
        y = dataset.iloc[:, -1]  # [x = take entire row, y = last column only]

        # get training score with train test split
        self.getTrainingScore(X, y, clf)

        # get training score using cross validation
        # self.nFoldCrossValidation(X, y, clf, nfold=5)

        if drop_element == 'who':
            # training and save into pickle
            joblib.dump(clf,'model/train_where.pkl')
            print ("Model for WHERE has been saved")
        elif drop_element == 'where':
            # training and save into pickle
            joblib.dump(clf,'model/train_who.pkl')
            print ("Model for WHO has been saved")

    def getTrainingScore(self, X, y, model):
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        # otak atik aja datanya, gimana biar nilainya jadi ga 0 lagi, undersampling oversampling ?
        print("Accuracy: ", (accuracy_score(y_test, y_pred) * 100).round(4))
        print("Precision: ", (precision_score(y_test, y_pred) * 100).round(4))
        print("Recall: ", (recall_score(y_test, y_pred) * 100).round(4))
        print("F-measure: ", (f1_score(y_test, y_pred) * 100).round(4))
        print("Confusion matrix:")
        print (confusion_matrix(y_test, y_pred))

    def nFoldCrossValidation(self, X, y, model, nfold):
        class_count = y.groupby(y).count().shape[0]
        k_fold = StratifiedKFold(n_splits=nfold, shuffle=True, random_state=7)
        # initiate score lists
        precision_list = []
        recall_list = []
        fscore_list = []
        train_score = []
        test_score = []

        fold_count = 1
        print ("Confusion matrix of " + model.__class__.__name__ + ":\n")

        # train_indices and test_indices returns an array of indices which indicate train and test data 
        for train_indices, test_indices in k_fold.split(X, y):
            X_train, X_test = X.iloc[train_indices], X.iloc[test_indices]
            y_train, y_test = y.iloc[train_indices], y.iloc[test_indices]

            model.fit(X_train, y_train)

            predictions = model.predict(X_train)
            train_score.append(accuracy_score(y_train, predictions).round(4))

            predictions = model.predict(X_test)
            test_score.append(accuracy_score(y_test, predictions).round(4))

            precision_list.append(precision_score(y_test, predictions, average='macro').round(4))
            recall_list.append(recall_score(y_test, predictions, average='macro').round(4))
            fscore_list.append(f1_score(y_test, predictions, average='macro').round(4))

            print ("Fold " + str(fold_count) + ":")
            print (confusion_matrix(y_test, predictions))
            print () 
            fold_count += 1

        acc_train = (sum(train_score)/len(train_score)).round(4)
        acc_test = (sum(test_score)/len(test_score)).round(4)
        precision = (sum(precision_list)/len(precision_list)).round(4)
        recall = (sum(recall_list)/len(recall_list)).round(4)
        f_score = (sum(fscore_list)/len(fscore_list)).round(4)

        print ("Evaluation using " + model.__class__.__name__ + ":\n")

        fold_index = [str(i+1) for i in range(nfold)]
        fold_data = [fold_index, train_score, test_score, precision_list, recall_list, fscore_list]
        fold_column = ['fold', 'acc_train', 'acc_test', 'precision', 'recall', 'f_score']
        df_fold = pd.DataFrame(np.column_stack(fold_data), columns=fold_column)
        df_fold = df_fold.set_index('fold')

        print (df_fold)
        print ("=" * 50 + "\n")

        print ('Total data classified:', len(X))
        print ('Accuracy on Train:', acc_train)
        print ('Accuracy on Test:', acc_test)
        print ('Precision:', precision)
        print ('Recall:', recall)
        print ('F-Score:', f_score)

tr = ModelTrainer()

# reading excel that contain features (HARUS DIKASIH KOLOM WHO DAN WHERE DULU, DAN DITENTUKAN YANG MANA WHO DAN WHERE)
df = pd.read_excel('goldendata_extracted_feature.xlsx', sheet_name='Sheet1')
# training model for detecting who and where, input "where" or "who" meaning that column will be dropped (deleted)
tr.train(df,'where')
tr.train(df,'who')
