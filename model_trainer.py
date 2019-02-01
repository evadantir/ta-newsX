import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import KFold
from sklearn.model_selection import StratifiedKFold
import joblib
from utility_code import Utility
from sklearn.preprocessing import OneHotEncoder

class ModelTrainer(object):

    def __init__(self):
        self.ut = Utility()

    def train(self,dataset,drop_element):
        #classifier algorithm, n_estimator = jumlah tree, random_state= angka apapun, sengaja didefine biar hasilnya tetap sama
        clf = RandomForestClassifier(n_estimators=10, random_state=2) #coba utak atik
        
        # extract feature needed, drop entity
        dataset = dataset.drop(['entity','id_text',drop_element], axis=1)
        # convert type to numeric
        dataset = self.convertToNumeric(dataset)
        dataset = self.ut.oneHotEncoding(dataset)

        # determine wich column is feature or label
        # X itu fitur
        X = dataset.iloc[:, :-1] # [x = take  entire row, y = take all column except last column]
        # y itu label
        y = dataset.iloc[:, -1]  # [x = take entire row, y = last column only]

        # get training score using cross validation
        result = self.nFoldCrossValidation(X, y, clf, nfold=10)
        
        if drop_element == 'who':

            # training and save into pickle
            # scenario 1
            # joblib.dump(clf,'model/scen1_train_where_halfidn.pkl')
            # # scenario 2
            # joblib.dump(clf,'model/scen2_train_where_fullidn.pkl')
            # # scenario 3
            # joblib.dump(clf,'model/scen3_train_where_default.pkl')
            # testing
            joblib.dump(clf,'model/s2_testing_where.pkl')
            print ("Model for WHERE has been saved")

            # scenario 1
            # self.ut.convertToExcel("./result/scenario1_halfidn_WHERE_10fold.xlsx",result,"Sheet1")
            # scenario 2
            # self.ut.convertToExcel("./result/scenario2_fullidn_WHERE_10fold.xlsx",result,"Sheet1")
            # scenario 3
            # self.ut.convertToExcel("./result/scenario3_default_WHERE_10fold.xlsx",result,"Sheet1")
             # scenario testing
            self.ut.convertToExcel("./result/s2_testing_WHERE_10fold.xlsx",result,"Sheet1")           
            print("Cross Validation for WHERE model has been saved to excel file!")

        elif drop_element == 'where':
            # training and save into pickle
            # scenario 1
            # joblib.dump(clf,'model/scen1_train_who_halfidn.pkl')
            # # scenario 2
            # joblib.dump(clf,'model/scen2_train_who_fullidn.pkl')
            # # scenario 3
            # joblib.dump(clf,'model/scen3_train_who_default.pkl')
            # testing
            # joblib.dump(clf,'model/s2_testing_who.pkl')
            # print ("Model for WHO has been saved")

            # scenario 1
            # self.ut.convertToExcel("./result/scenario1_halfidn_WHO_10fold.xlsx",result,"Sheet1")
            # scenario 2
            # self.ut.convertToExcel("./result/scenario2_fullidn_WHO_10fold.xlsx",result,"Sheet1")
            # # scenario 3
            # self.ut.convertToExcel("./result/scenario3_default_WHO_10fold.xlsx",result,"Sheet1")
            # scenario testing
            self.ut.convertToExcel("./result/s2_testing_WHO_10fold.xlsx",result,"Sheet1")  
            print("Cross Validation for WHO model has been saved to excel file!")

    # classic method
    def getEvaluationScore(self, X_test, y_test, model):
        y_pred = model.predict(X_test)
        print(y_pred)
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


