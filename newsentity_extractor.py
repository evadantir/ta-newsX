# -*- coding: utf-8 -*-
from nltk.tokenize import sent_tokenize,word_tokenize
from nltk.parse.stanford import StanfordParser
from nltk.tag import StanfordNERTagger
from nltk.tag import StanfordPOSTagger
from nltk.tree import *
from preprocessing import Preprocess
import re
import os
import json
import pandas as pd
import joblib
import en_coref_md
from stanfordcorenlp import StanfordCoreNLP 

class NewsEntityExtractor(object):
    def __init__(self):
        self.count = 0
        self.pre = Preprocess()
        self.stanford = StanfordCoreNLP('http://localhost', port=9000)

    # reading CSV 
    def loadData(self, filename):
        dataset = pd.read_csv(filename, sep=";")
        return dataset

    # parsing for getting verb phrase
    def getConstituencyParsing(self,text):
        scp = StanfordParser('./stanford/stanford-parser.jar','./stanford/stanford-parser-3.9.1-models.jar',encoding='utf8')
        return scp.raw_parse(text)

    def getNER(self,text):

        list_sentence = sent_tokenize(text)
        ner_tagger = StanfordNERTagger('./stanford/english.muc.7class.distsim.crf.ser.gz','./stanford/stanford-ner.jar', encoding='utf8')
        ner = []
        for sent in list_sentence:
            words = word_tokenize(sent)
            ner.append(ner_tagger.tag(words))

        return ner

    def getPOS(self,text):
        pos_tagger = StanfordPOSTagger('./stanford/english-bidirectional-distsim.tagger','./stanford/stanford-postagger.jar',encoding='utf8')
        words = word_tokenize(text)
        pos = pos_tagger.tag(words)

        return pos

    def getCoref(self,text):
        coref = self.stanford.coref(text)
        return coref

    def extractNerCoref(self, filename, text, title, fiveWoneH):
        combine = text + '. ' + title
        ner = self.getNER(text)
        print "NER extraction completed"
        coref = self.getCoref(text)
        print "Coref extraction completed"
        nlp_dict = {
            'filename' : filename,
            'title' : title,
            'text' : text,
            'ner' : ner,
            'coref' : coref,
            'fiveWoneH' : fiveWoneH
        }

        return nlp_dict

    # saving extracted NER and COREF from news text into a pickle 
    def saveObject(self, nlp_dict):
        # self.count += 1
        folder = "nlp_object"
        name = nlp_dict['filename'] + ".pkl"
        joblib.dump(nlp_dict, os.path.join(folder, name))
        print "Inserted text from file " + nlp_dict['filename']

    def extractNews(self, dataset, prefix):
        # dataset = se.loadData(file_open)
        dataset.apply(lambda x: se.saveObject(se.extractNerCoref(x['filename'], x['text'], x['title'], x['fiveWoneH'])), axis=1)

    def cleansingText(self, text):
        text = self.pre.eliminatePunctuation(text)
        return self.pre.normalizePunctuation(text)

    def getGoldenDataset(self):
        path_to_json = "datasets/"

        data = pd.DataFrame()

        for filename in os.listdir(path_to_json):
            if filename.endswith('.json'):
                with open(os.path.join(path_to_json ,filename)) as json_data:
                    json_result = json.load(json_data)
                    json_result['filename'] = filename
                    data = data.append(json_result, ignore_index=True)
        data['text'] = data['text'].apply(lambda x: self.cleansingText(x))
        data['title'] = data['title'].apply(lambda x: self.cleansingText(x))
        data = data.dropna(axis=1, how="any")

        return data

se = NewsEntityExtractor()

# data = se.getGoldenDataset()
# prefix = 'golden_data'
# se.extractNews(data, prefix)




# se.extractNews(file_open,file_close)

# file_open = "news/test_news.csv" #file yang akan dibaca
# file_close = 'test' #prefix dari nama file hasil
# se.extractNews(file_open,file_close)
