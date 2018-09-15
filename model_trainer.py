import os
import json
import pandas as pd
from pprint import pprint
from sklearn.naive_bayes import MultinomialNB


class ModelTrainer(object):
    def __init__(self):
        pass

    def readGoldenDataset(self):
        path = "./datasets/"
        filelist = os.listdir(path)
        if filelist:
            dataframe = pd.DataFrame()
            for idx, file in enumerate(filelist):
                json_data=open(os.path.join(path, file)).read()
                data = json.loads(json_data)
                dataframe = dataframe.append(data, ignore_index=True)

        return dataframe

    # combine all the module so we can extract features from pickle object
    def extractFeatures(data):
        # extract entity yang ada berdasarkan data ner dari variable data
        entities = self.extractEntity(data["ner"])
        # ambil noun phrase dari judul, lalu masukkan ke data entities, jika ternyata ada yang sama, hapus
        entities = self.pre.removeDuplicateListDict(self.findNounPhraseFromTitle(data["title"],entities))
        # bandingkan entity dari coref dengan entity yang dari ner, jika ada yang sama, maka tambahkan jumlah kemunculannya dan simpan
        entities = self.countCfOccurencesInText(entities,data["coref"])
        # cari kemunculan enity di judul
        entities = self.findOccurencesInTitle(data["title"],entities)
        # cari nilai distribusid dari entity dalam teks
        entities = self.findDistribution(data["text"],entities)

    def trainWHOModel(self, data, classifier):
        data = data[['title', 'text', 'fiveWoneH']]
        print data

mt = ModelTrainer()

data = mt.readGoldenDataset()
clf = MultinomialNB()

mt.trainWHOModel(data, clf)