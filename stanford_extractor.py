# Simple usage
from stanfordcorenlp import StanfordCoreNLP
from tokenization import *
import pandas as pd
import joblib


class StanfordExtractor(object):
    def __init__(self):
        self.nlp = StanfordCoreNLP(r'./stanford-corenlp-full-2018-02-27',quiet=False)
        self.index = 0

    def loadData(self, filename):
        dataset = pd.read_csv(filename, sep=";")
        return dataset

    def extractNerCoref(self, text):
        ner = self.nlp.ner(text)
        print "NER extraction completed"
        coref = self.nlp.coref(text)
        print "Coref extraction completed"
        exit()
        nlp_dict = {
            'text' : text,
            'ner' : ner,
            'coref' : coref
        }
        return nlp_dict

    def saveObject(self, nlp_dict, filename):
        self.index += 1
        folder = "nlp_object"
        name = filename + "_" + index
        joblib.dump(nlp_dict, os.path.join(folder, name))
        print "Inserted text from file " + filename + " with index " + index


se = StanfordExtractor()
filename = "cnn_edit1.csv"
dataset = se.loadData(filename)
dataset['content'].apply(lambda x: se.saveObject(se.extractNerCoref(x), filename))
self.nlp.close()