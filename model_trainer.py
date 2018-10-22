import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import KFold
from sklearn.model_selection import StratifiedKFold
import joblib
from utility_code import Utility

class ModelTrainer(object):

    def __init__(self):
        self.ut = Utility()

    def convertToNumeric(self,dataset):
        # convert categorical feature to numeric
        dataset['type'] = dataset['type'].map({'PERSON': 1, 'LOCATION': 2, 'ORGANIZATION': 3,'NP': 4}).astype(int)
        dataset['occ_title'] = dataset['occ_title'].map({False: 0, True: 1}).astype(int)
        return dataset

    def train(self,dataset,drop_element):
        #classifier algorithm, n_estimator = jumlah tree, random_state= angka apapun, sengaja didefine biar hasilnya tetap sama
        clf = RandomForestClassifier(n_estimators=10, random_state=42)

        # extract feature needed, drop entity
        dataset = dataset.drop(['entity','id_text',drop_element], axis=1)

        dataset = self.convertToNumeric(dataset)

        # determine wich column is feature or label
        # X itu fitur
        X = dataset.iloc[:, :-1] # [x = take  entire row, y = take all column except last column]
        # y itu label
        y = dataset.iloc[:, -1]  # [x = take entire row, y = last column only]

        # get training score with train test split (cara biasa)
        # self.getTrainingScore(X, y, clf)

        # get training score using cross validation
        result = self.nFoldCrossValidation(X, y, clf, nfold=10)
        
        if drop_element == 'who':
            # training and save into pickle
            joblib.dump(clf,'model/train_where.pkl')
            print ("Model for WHERE has been saved")
            ut.convertToExcel("WHERE_result.xlsx",result,"Sheet1")
        elif drop_element == 'where':
            # training and save into pickle
            joblib.dump(clf,'model/train_who.pkl')
            print ("Model for WHO has been saved")
            ut.convertToExcel("WHO_result.xlsx",result,"Sheet1")

    # classic method
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

    # cross validation
    def nFoldCrossValidation(self, X, y, model, nfold):
        # ngitung jumlah class
        class_count = y.groupby(y).count().shape[0]
        # shuffle biar ngacak di awal, random_state biar dirunning berkali kali tetap sama
        k_fold = StratifiedKFold(n_splits=nfold, shuffle=True, random_state=7)
        # initiate score lists
        precision_list = []
        recall_list = []
        fscore_list = []
        train_score = []
        test_score = []

        # counter fold, dimulai dari 1
        fold_count = 1
        print ("Confusion matrix of " + model.__class__.__name__ + ":\n")

        # train_indices and test_indices returns an array of indices which indicate train and test data  (indices = index)
        for train_indices, test_indices in k_fold.split(X, y):  #split per n fold
            # memisahkan data training dan data testing
            X_train, X_test = X.iloc[train_indices], X.iloc[test_indices] #iloc = locate data by index
            y_train, y_test = y.iloc[train_indices], y.iloc[test_indices]

            # fit = buat training
            model.fit(X_train, y_train)

            # prediksi data training
            predictions = model.predict(X_train)
            # mendapatkan nilai akurasi dengan cara ngebandingin hasil prediksi dengan nilai aslinya (y_train / data training) satu persatu
            train_score.append(accuracy_score(y_train, predictions).round(4)) #diround 4 biar hasilnya dibulatkan jadi 4 angka di belakang koma

            # prediksi data testing
            predictions = model.predict(X_test)
            # mendapatkan nilai akurasi dengan cara ngebandingin hasil prediksi dengan nilai aslinya (y_test / data testing)
            test_score.append(accuracy_score(y_test, predictions).round(4))

            # mencari nilai precision, recall dan f_score dengan membandingkan nilai asli (y_testing) dengan hasil prediksi
            precision_list.append(precision_score(y_test, predictions).round(4))
            recall_list.append(recall_score(y_test, predictions).round(4))
            fscore_list.append(f1_score(y_test, predictions).round(4))

            # menunjukkan fold ke berapa, dan confusion matrixnya seperti apa
            print ("Fold " + str(fold_count) + ":")
            # urutan confusion matrix, pokoknya baris bawah, sebelah kanan itu True Positive nya kirinya False Positive, atas True Negative dan False Negative
            print (confusion_matrix(y_test, predictions))
            print () 
            fold_count += 1
        
        # hitung rata - rata nilai akurasi, precision, recall, dan f_score
        acc_train = (sum(train_score)/len(train_score)).round(4)
        acc_test = (sum(test_score)/len(test_score)).round(4)
        precision = (sum(precision_list)/len(precision_list)).round(4)
        recall = (sum(recall_list)/len(recall_list)).round(4)
        f_score = (sum(fscore_list)/len(fscore_list)).round(4)

        print ("Evaluation using " + model.__class__.__name__ + ":\n")

        # simpan data hasil perhitungan akurasi precision recall f_score ke dataframe
        fold_index = [str(i+1) for i in range(nfold)] #create fold index
        fold_data = [fold_index, train_score, test_score, precision_list, recall_list, fscore_list]
        fold_column = ['fold', 'acc_train', 'acc_test', 'precision', 'recall', 'f_score'] #create column name
        df_fold = pd.DataFrame(np.column_stack(fold_data), columns=fold_column) #bikin DataFrame
        df_fold = df_fold.set_index('fold') #set data fold as index

        #PRINT  hasil
        print (df_fold)
        print ("=" * 50 + "\n")

        print ('Total data classified:', len(X))
        # perlu dibandingkan nilai akurasi di training dan di testing, siapa tau ada overfitting, kalau misalnya ga beda jauh, berarti kemungkinan modelnya benar
        print ('Accuracy on Train:', acc_train)
        print ('Accuracy on Test:', acc_test)
        print ('Precision:', precision)
        print ('Recall:', recall)
        print ('F-Score:', f_score)

        return df_fold

tr = ModelTrainer()
ut = Utility()

# reading excel that contain features (HARUS DIKASIH KOLOM WHO DAN WHERE DULU, DAN DITENTUKAN YANG MANA WHO DAN WHERE)
df = pd.read_excel('goldendata_extracted_feature.xlsx', sheet_name='Sheet1')
# training model for detecting who and where, input "where" or "who" meaning that column will be dropped (deleted)
who = tr.train(df,'where')
where = tr.train(df,'who')
