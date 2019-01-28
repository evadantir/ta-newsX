import os
import pandas as pd
from utility_code import Utility
from fivew_extractor import FiveWExtractor
from feature_extractor import FeatureExtractor
from nlp_helper import NLPHelper

class EvaluateNews(object):

    def __init__(self):
        self.ut = Utility()
        self.fwe = FiveWExtractor()
        self.fex = FeatureExtractor()
        self.nlp = NLPHelper()

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

    def evaluateLocalNews(self,filename):
        
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

        self.ut.convertToExcel("eksperimen3_default_localnews_evaluate.xlsx",temp,'Sheet1')

        print("Evaluating local news is done!")

    def evaluateWhoWhereLocalNews(self,filename):
        data = self.ut.loadCSV(filename,',',"ISO-8859-1")

        data['ner'] = data['text'].apply(lambda x: self.nlp.getNER(x))
        data['coref'] = data['text'].apply(lambda x: self.nlp.getCoref(x))

        feature = pd.DataFrame()
        for i in range(data.shape[0]):
            feature = feature.append(self.fex.extractFeaturesDirectFromText(data.iloc[i]), ignore_index=True)

        #     print(entities)
        self.ut.convertToExcel("3default_local_feature.xlsx",feature,'Sheet1')

ev = EvaluateNews()


# ev.evaluateGoldenDatasetNews(file_range=(0,88))
# ev.evaluateLocalNews("beritalokal.csv")
ev.evaluateWhoWhereLocalNews("beritalokal.csv")
