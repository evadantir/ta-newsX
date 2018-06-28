# -*- coding: utf-8 -*-
from nltk.tokenize import sent_tokenize,word_tokenize
from nltk.parse.stanford import StanfordParser
from nltk.tag import StanfordNERTagger
from nltk.tag import StanfordPOSTagger
from nltk.tree import *
import re
import os
import pandas as pd
import joblib
import en_coref_md

class NewsEntityExtractor(object):
    def __init__(self):
        self.count = 0

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
        nlp = en_coref_md.load()
        doc = nlp(unicode(text,"utf-8"))

        coref_list = []
        for blah in doc._.coref_clusters:
            coref = {
                'main' : str(blah.main),
                'mentions' : [str(i) for i in blah.mentions]
            }
            coref_list.append(coref)

        return coref_list

    def extractNerCoref(self, text, title):
        combine = text + '. ' + title
        ner = self.getNER(text)
        print "NER extraction completed"
        coref = self.getCoref(text)
        print "Coref extraction completed"
        nlp_dict = {
            'title' : title,
            'text' : text,
            'ner' : ner,
            'coref' : coref
        }

        return nlp_dict

    def saveObject(self, nlp_dict, filename):
        self.count += 1
        folder = "nlp_object"
        name = filename + "_" + str(self.count) + ".pkl"
        joblib.dump(nlp_dict, os.path.join(folder, name))
        print "Inserted text from file " + filename + " with index " + str(self.count)

    def extractNews(self,file_open,file_close):
        dataset = se.loadData(file_open)
        dataset.apply(lambda x: se.saveObject(se.extractNerCoref(x['content'], x['title']), file_close), axis=1)

se = NewsEntityExtractor()
file_open = "Java Program/ta eva/cnn.csv"
file_close = 'cnn'
# se.extractNews(file_open,file_close)

