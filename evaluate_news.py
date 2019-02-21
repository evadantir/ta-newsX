import os
import pandas as pd
from utility_code import Utility
from fivew_extractor import FiveWExtractor
from feature_extractor import FeatureExtractor
from nlp_helper import NLPHelper
from model_trainer import ModelTrainer
import joblib

class EvaluateNews(object):

    def __init__(self):
        self.ut = Utility()
        self.fwe = FiveWExtractor()
        self.fex = FeatureExtractor()
        self.nlp = NLPHelper()
        self.tr = ModelTrainer()

    def evaluateGoldenDatasetNews(self, file_range=None):
        # filerange = (0, 10)
        # find feature in one text and save it to excel
        path = "./datasets/"
        filelist = os.listdir(path)
        data = pd.DataFrame()

        if file_range:
            filelist = filelist[file_range[0]:file_range[1]]

        for idx, file in enumerate(filelist):
            print (file)
            #buka file pickle yang isinya data ner, coref, dan pos dari suatu teks berita
            file_temp = self.ut.loadJSON(os.path.join(path, file))
            # ekstraksi 5W dari file JSON
            try:
                temp = self.fwe.extract5w(file_temp["text"],file_temp["title"])
                temp["file"] = file
                data = data.append(temp,ignore_index = True)
            except:
                temp = []
                print("It failed huhu")
           
        self.ut.convertToExcel("idnhalf_goldendata_evaluate_089.xlsx",data,'Sheet1')

        print("Evaluating golden data is done!")

    def extract5wLocalNewsForEval(self,filename):
        
        data = self.ut.loadCSV(filename,',',"ISO-8859-1")

        data['extracted'] = data.apply(lambda x: self.fwe.extract5wLocalNews(x['text'], x['title']), axis=1)
        temp = pd.DataFrame()
        temp['title'] = data['extracted'].apply(lambda x: x['title'])
        temp['text'] = data['extracted'].apply(lambda x: x['text'])
        temp['who'] = data['extracted'].apply(lambda x: x['who'])
        temp['where'] = data['extracted'].apply(lambda x: x['where'])
        temp['what'] = data['extracted'].apply(lambda x: x['what'])
        temp['when'] = data['extracted'].apply(lambda x: x['when'])
        temp['why'] = data['extracted'].apply(lambda x: x['why'])

        # scenario 1
        # self.ut.convertToExcel("3_scen1_halfidn_evallocalnews.xlsx",temp,'Sheet1')
        # self.ut.convertToExcel("HO_scen1_halfidn_evallocalnews.xlsx",temp,'Sheet1')
        # scenario 2
        # self.ut.convertToExcel("3_scen2_fullidn_evallocalnews.xlsx",temp,'Sheet1')
        # self.ut.convertToExcel("HO_scen2_fullidn_evallocalnews.xlsx",temp,'Sheet1')
        # scenario 3
        self.ut.convertToExcel("3_scen3_default_evallocalnews.xlsx",temp,'Sheet1')
        # self.ut.convertToExcel("HO_scen3_default_evallocalnews.xlsx",temp,'Sheet1')

        print("Evaluating local news is done!")

    def extractFeatureFromLocalNews(self,filename):
        data = self.ut.loadCSV(filename,',',"ISO-8859-1")

        data['ner'] = data['text'].apply(lambda x: self.nlp.getNER(x))
        data['coref'] = data['text'].apply(lambda x: self.nlp.getCoref(x))

        feature = pd.DataFrame()
        for i in range(data.shape[0]):
            feature = feature.append(self.fex.extractFeaturesDirectFromText(data.iloc[i]), ignore_index=True)

        # scenario 1
        # self.ut.convertToExcel("scen1_halfidn_localfeature.xlsx",feature,'Sheet1')
        # scenario 2
        # self.ut.convertToExcel("scen2_fullidn_localfeature.xlsx",feature,'Sheet1')
        # scenario 3
        # self.ut.convertToExcel("scen3_default_localfeature.xlsx",feature,'Sheet1')

    def evaluateLocalWhoWhere(self,drop_element):

        # # scenario 1
        # dataset = pd.read_excel('scen1_halfidn_localfeature.xlsx', sheet_name='Sheet1')
        # model_where = joblib.load('model/3_scen1_train_where_halfidn.pkl')
        # model_who = joblib.load('model/3_scen1_train_who_halfidn.pkl')

        # scenario 2
        # dataset = pd.read_excel('scen2_fullidn_localfeature.xlsx', sheet_name='Sheet1')
        # model_where = joblib.load('model/3_scen2_train_where_fullidn.pkl')
        # model_who = joblib.load('model/3_scen2_train_who_fullidn.pkl')

        # # scenario 3
        dataset = pd.read_excel('scen3_default_localfeature.xlsx', sheet_name='Sheet1')
        model_where = joblib.load('model/3_scen3_train_where_default.pkl')
        model_who = joblib.load('model/3_scen3_train_who_default.pkl')

        # scenario HO -------------------------------
        # # # scenario 1
        # dataset = pd.read_excel('scen1_halfidn_localfeature.xlsx', sheet_name='Sheet1')
        # model_where = joblib.load('model/HO2_scen1_train_where_halfidn.pkl')
        # model_who = joblib.load('model/HO2_scen1_train_who_halfidn.pkl')

        # scenario 2
        # dataset = pd.read_excel('scen2_fullidn_localfeature.xlsx', sheet_name='Sheet1')
        # model_where = joblib.load('model/HO2_scen2_train_where_fullidn.pkl')
        # model_who = joblib.load('model/HO2_scen2_train_who_fullidn.pkl')

        # # # scenario 3
        # dataset = pd.read_excel('scen3_default_localfeature.xlsx', sheet_name='Sheet1')
        # model_where = joblib.load('model/HO2_scen3_train_where_default.pkl')
        # model_who = joblib.load('model/HO2_scen3_train_who_default.pkl')

        # scenario test
        # dataset = pd.read_excel('scen1_halfidn_localfeature.xlsx', sheet_name='Sheet1')
        # model_where = joblib.load('model/s2_testing_where.pkl')
        # model_who = joblib.load('model/s2_testing_who.pkl')

        if drop_element == 'who':
            self.evaluateModelLocal(dataset,'who',model_where)
            print("Evaluation for WHERE's local classifier is done!")
        elif drop_element == 'where':
            self.evaluateModelLocal(dataset,'where',model_who)
            print("Evaluation for WHO's local classifier is done!")

    def evaluateModelLocal(self,dataset,drop_element,model):
        dataset = self.ut.convertToNumeric(dataset)
        
        dataset = dataset.drop(['entity',drop_element], axis=1)
        # !!! FOR ONE HOT ENCODING !!!
        # dataset = self.ut.oneHotEncoding(dataset)

        # determine wich column is feature or label
        # X itu fitur
        X = dataset.iloc[:, :-1] # [x = take  entire row, y = take all column except last column]
        # y itu label
        y = dataset.iloc[:, -1]  # [x = take entire row, y = last column only]

        # get training score using cross validation
        # result = self.nFoldCrossValidation(X, y, clf, nfold=10)
        result = self.tr.getEvaluationScore(X,y,model)


ev = EvaluateNews()

# ev.extractFeatureFromLocalNews('beritalokal.csv')
# ev.extract5wLocalNewsForEval("beritalokal.csv")
ev.evaluateLocalWhoWhere('where')
ev.evaluateLocalWhoWhere('who')
