# -*- coding: utf-8 -*-

import pandas as pd
import json,os
from preprocessing import Preprocess
from pprint import pprint

class CombineNews(object):
    def __init__(self):
        self.pre = Preprocess()

    def cleansingText(self, text):
        text = self.pre.eliminatePunctuation(text)
        return self.pre.normalizePunctuation(text)

    def combineToCsvFromFolder(self):
        path_to_json = "datasets/"

        data = pd.DataFrame()

        for filename in os.listdir(path_to_json):
            if filename.endswith('.json'):
                with open(os.path.join(path_to_json ,filename)) as json_data:
                    json_result = json.load(json_data)
                    for key, value in json_result['fiveWoneH'].iteritems():
                        json_result[key] = value
                    del json_result['fiveWoneH']
                    data = data.append(json_result, ignore_index=True)
        data['text'] = data['text'].apply(lambda x: self.cleansingText(x))
        data['title'] = data['title'].apply(lambda x: self.cleansingText(x))
        data = data.dropna(axis=1, how="any")
        data.to_csv('golden_data.csv',sep=';', index=False, encoding='utf-8')

    def combineToCsvFromFile(self):
        filename = "news_crawler/page_contents.json"

        data = pd.DataFrame()

        with open(filename) as json_data:
            json_result = json.load(json_data)
            temp = pd.DataFrame()
            temp = data.append(json_result, ignore_index=True)
            temp['body'] = temp['body'].apply(lambda x: self.cleansingText(x))
            temp['title'] = temp['title'].apply(lambda x: self.cleansingText(x))
            temp = temp.dropna(axis=0,how="any")
            data = temp

        data.to_csv('test.csv',sep=';', index=False, encoding='utf-8')


c = CombineNews()

c.combineToCsvFromFolder()
# c.combineToCsvFromFile()
