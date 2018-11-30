# -*- coding: utf-8 -*-
from nltk.tokenize import sent_tokenize,word_tokenize
from nltk.parse.stanford import StanfordParser
from nltk.tag import StanfordNERTagger
from nltk.tag import StanfordPOSTagger
from nltk.tree import *
import nltk
from nltk.internals import find_jars_within_path
from preprocessing import Preprocess
import re
import os
import json
import pandas as pd
import joblib
from stanfordcorenlp import StanfordCoreNLP
from combotagger import NERComboTagger

class NLPHelper(object):
    def __init__(self):
        
        classifier_path1 = "stanford/english.muc.7class.distsim.crf.ser.gz"
        # classifier_path2 = "stanford/id-ner-model-id.ser.gz"
        # classifier_path2 = "stanford/id-ner-model-2.ser.gz"
        classifier_path2 = "stanford/id-ner-model-half.ser.gz"
        ner_jar_path = "stanford/stanford-ner.jar"

        # for handling error nltk internals
        nltk.internals.config_java(options='-xmx5g')

        self.pre = Preprocess()
        self.scp = StanfordParser('./stanford/stanford-parser.jar','./stanford/stanford-parser-3.9.1-models.jar',encoding='utf8')
        self.ner_tagger = StanfordNERTagger(classifier_path1,ner_jar_path, encoding='utf8')
        self.pos_tagger = StanfordPOSTagger('./stanford/english-bidirectional-distsim.tagger','./stanford/stanford-postagger.jar',encoding='utf8')
        # combining classifier from Stanford with custom classifier
        self.com_tagger = NERComboTagger(classifier_path1,ner_jar_path,stanford_ner_models=classifier_path1+","+classifier_path2)
        self.core_nlp = StanfordCoreNLP('http://localhost', port=9000)

    # parsing for getting verb phrase
    def getConstituencyParsing(self, text):
        # props = {'parse.maxlen':'50'}
        return self.scp.raw_parse(text)

    # get named entity in text with Stanford English NER tagger
    def getNER(self, text):
        words = word_tokenize(text)
        ner = self.ner_tagger.tag(words)
        return ner

    # get named entity in text with Stanford English NER tagger + Indonesian tagger
    def getIdnNER(self,text):
        words = word_tokenize(text)
        ner = self.com_tagger.tag(words)
        return ner

    # get Constituency parsing from text
    def getCP(self,text):
        return self.core_nlp.parse(text)

    # get Part of Speech in text
    def getPOS(self,text):
        words = word_tokenize(text)
        pos = self.pos_tagger.tag(words)
        return pos

    # get coref of entities in text
    def getCoref(self,text):
        # property for annotating coref
        props = {'annotators': 'coref', 'pipelineLanguage': 'en'}
        # load annotation as json
        data = json.loads(self.core_nlp.annotate(text,props))


        coref_file = []
        for idx,mentions in data['corefs'].items():
            coref = {}
            temp = []
            comain = None
            for m in mentions:
                if m['isRepresentativeMention']:
                    # if text is MAIN representative
                    comain = m['text']
                else:
                    # if FALSE
                    if comain:
                        # if not, add as mention representative
                        temp.append(m['text'])
                coref['main'] = comain
                coref['mentions'] = temp

            coref_file.append(coref)
        return coref_file

    # extracting Named Entity and coreference resolution in the text
    def extractNerCoref(self, filename, text, title, fiveWoneH):
        combine = title + '. ' + text
        # for default Stanford NER
        # ner = self.getNER(combine)
        # for custom NER (Stanford + IDN)
        ner = self.getIdnNER(combine)
        print("NER extraction completed on ", filename)
        try:
            coref = self.getCoref(text)
            print("Coref extraction completed on ", filename)

        except json.decoder.JSONDecodeError:
            coref = []
            print("Coref extraction unfortunately failed on ", filename)

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
        # folder = "nlp_object"
        folder = "idn_pickle_half"
        name = nlp_dict['filename'] + ".pkl"
        joblib.dump(nlp_dict, os.path.join(folder, name))
        print("Inserted text from file " + nlp_dict['filename'])

    # extracting NER and coref in each news
    def extractNews(self, dataset):
        dataset.apply(lambda x: self.saveObject(self.extractNerCoref(x['filename'], x['text'], x['title'], x['fiveWoneH'])), axis=1)

    # normalizing puncutation in text
    def cleansingText(self, text):
        return self.pre.normalizePunctuation(text)

    # get golden dataset's entity
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

nlp = NLPHelper()

# get golden data
# data = nlp.getGoldenDataset()
# # extract entity and save into pickle
# nlp.extractNews(data)
# nlp.core_nlp.close()
