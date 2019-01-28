from preprocessing import Preprocess
from nlp_helper import NLPHelper
from feature_extractor import FeatureExtractor
from utility_code import Utility 
from model_trainer import ModelTrainer 
import pandas as pd
import os

'''
DO NOT FORGET TO CHANGE NER MODEL AND DESTINATION FOLDERS IN NLP_HELPER!!!!!!!
DO NOT FORGET TO CHANGE CROSS VALIDATION EXCEL!!!!
'''

class CreateClassifier(object):
    def __init__(self):
        self.pre = Preprocess()
        self.nlp = NLPHelper()
        self.fex = FeatureExtractor()
        self.ut = Utility()
        self.mt = ModelTrainer()

    def createClassifier(self):
        # get golden data
        # data = self.nlp.getGoldenDataset()
        # # extract entity and save into pickle
        # self.nlp.extractNews(data)
        # self.nlp.core_nlp.close()

        # find feature in one text and save it to excel
        # scenario 1
        # path = "scenario1_halfidn_pickle/"
        # scenario 2
        # path = "scenario2_fullidn_pickle/"
        # # scenario 3
        # # path = "scenario3_stanford_pickle/"
        # filelist = os.listdir(path)
        # data = pd.DataFrame()

        # for idx, file in enumerate(filelist):

        #     #buka file pickle yang isinya data ner, coref, dan pos dari suatu teks berita
        #     pkl_dict = self.ut.loadPickle(os.path.join(path, file))
        #     # ekstraksi fitur dari file pickle
        #     temp = self.fex.extractFeaturesFromPickle(pkl_dict)
        #     data = data.append(temp)

        # #scenario 1 
        # # self.ut.convertToExcel("scenario1_idnnerhalf_extracted_feature.xlsx",data,'Sheet1')
        # #scenario 2
        # self.ut.convertToExcel("scenario2_idnnerfull_extracted_feature.xlsx",data,'Sheet1')
        # #scenario 3 
        # self.ut.convertToExcel("scenario3_stanford_extracted_feature.xlsx",data,'Sheet1')

        # reading excel that contain features (HARUS DIKASIH KOLOM WHO DAN WHERE DULU, DAN DITENTUKAN YANG MANA WHO DAN WHERE)
        df = pd.read_excel('scenario3_stanford_extracted_feature.xlsx', sheet_name='Sheet1')
        # training model for detecting who and where, input "where" or "who" meaning that column will be dropped (deleted)
        who = self.mt.train(df,'where')
        where = self.mt.train(df,'who')
        self.nlp.core_nlp.close()

cc = CreateClassifier()

cc.createClassifier()