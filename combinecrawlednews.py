# -*- coding: utf-8 -*-

import pandas as pd
import json,os
from pprint import pprint

path_to_json = "news_crawler/page_contents_extracted/"

data = pd.DataFrame()

for filename in os.listdir(path_to_json):
    if filename.endswith('.json'):
        with open(os.path.join(path_to_json ,filename)) as json_data:
            json_result = json.load(json_data)

            data = data.append(json_result, ignore_index=True)

data.to_csv('combined.csv',sep=';', encoding='utf-8')


def cleanWeirdPunctuation(self, text):
    pass