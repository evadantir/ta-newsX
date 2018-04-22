# -*- coding: utf-8 -*-

import pandas as pd
import json,os
from preprocessing import Preprocess

class CombineNews(object):
    def __init__(self):
        self.pre = Preprocess()

    def cleansingText(self,text):
        return text.apply(lambda x: self.pre.normalizePunctuation(x))

    def combineToCsv(self):
        path_to_json = "news_crawler/page_contents_extracted/"

        data = pd.DataFrame()

        for filename in os.listdir(path_to_json):
            if filename.endswith('.json'):
                with open(os.path.join(path_to_json ,filename)) as json_data:
                    json_result = json.load(json_data)
                    temp = pd.DataFrame()
                    temp = data.append(json_result, ignore_index=True)
                    temp['body'] = self.cleansingText(temp['body'])
                    temp['title'] = self.cleansingText(temp['title'])
                    data = temp

        data.to_csv('combined.csv',sep=';', encoding='utf-8')

c = CombineNews()

c.combineToCsv()
