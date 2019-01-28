import json
import joblib
import pandas as pd
from nltk.tokenize import sent_tokenize
import re
import numpy as np
import os
import string
from preprocessing import Preprocess
from nlp_helper import NLPHelper
import openpyxl
from pprint import pprint
from utility_code import Utility

class FeatureExtractor(object):

    def __init__(self):
        self.pre = Preprocess()
        self.nlp = NLPHelper()

    # -- find out entity's type then extract it
    def extractEntity(self,data):
        # list of extracted people,loc, organization entities from text
        list_person = []
        list_loc = []
        list_org = []
        dont_remove_punct = ".,'_"

        # temporary variable for each people org and loc
        per = []
        org = []
        loc = []
        # print(data)
        # looping in array of NER data
        for i in range(len(data)):
            
            tempdict = {}
            if data[i][1] == 'PERSON':
                per.append(data[i][0])
            elif data[i][1] == 'ORGANIZATION':
                org.append(data[i][0])
            elif (data[i][1] == 'LOCATION') or (data[i][1] == 'COUNTRY') or (data[i][1] == 'CITY'):
                loc.append(data[i][0])
            else: 
                if per:
                    # print(per)
                    join_entity = ' '.join(per)
                    filter_punctuation = re.sub(r"(?<=\W) ",r"",join_entity)
                    # filter_punctuation = re.sub(r"(?<=\.\(\') ",r"",join_entity)
                    tempdict["entity"] = filter_punctuation
                    tempdict["type"] = "PERSON"
                    list_person.append(tempdict)
                    #empty temp array
                    per = []
                elif org:
                    # print(org)
                    join_entity = ' '.join(org)
                    # filter_punctuation = re.sub(r"(?<=\.\(\') ",r"",join_entity)
                    filter_punctuation = re.sub(r"(?<=\W) ",r"",join_entity)
                    tempdict["entity"] = filter_punctuation
                    tempdict["type"] = "ORGANIZATION"
                    list_org.append(tempdict)
                    #empty temp array
                    org = []
                elif loc:
                    # print(loc)
                    join_entity = ' '.join(loc)
                    filter_punctuation = re.sub(r"(?<=\W) ",r"",join_entity)
                    tempdict["entity"] = filter_punctuation
                    tempdict["type"] = "LOCATION"
                    list_loc.append(tempdict)
                    #empty temp array
                    loc = []

        # remove duplicate item in list
        list_loc = self.pre.removeDuplicateListDict(list_loc)
        list_person = self.pre.removeDuplicateListDict(list_person)
        list_org = self.pre.removeDuplicateListDict(list_org)

        entities = list_loc + list_person + list_org
        # print(entities)
        # exit()
        return entities

    def findNounPhraseFromTitle(self,title,entities):
        print("Find Noun Phrase in title...")
        anno = list(self.nlp.getConstituencyParsing(title))

        # returning verb phrase from title
        temp = {}
        for sub_tree in anno[0].subtrees(lambda t: t.label() == 'NP'):
            temp['entity'] = (' '.join(sub_tree.leaves()))
            temp['type'] = 'NP'
            entities.append(temp)
        
        return entities

    def countCfOccurencesInText(self,entities,coref,title):

        # if "main" entity in coref extraction is the same with named entities from ner process, then unite it
        for i in range(len(entities)):
            # print(entities[i])
            # jumlah default kemunculan suatu entity,minimal 1 kali muncul
            count = 1
            if coref:
                for cf in coref:
                    # hasil coref: {'main': entity, 'mentions': [...,..,...]}
                    # jika ternyata dari hasil coref (coref['main']) ada entity yang sama dengan entity dari ner, maka jumlah kemunculan entity ditambahkan dengan jumlah entity dari coref (coref['mention'])  
                    if cf['main'] in entities[i]['entity']:
                        if cf['mentions']:
                            count = 0
                            count += len(cf['mentions'])
                            entities[i]['occ_text'] = count
                        else:
                            count=1
                    else:
                        # jika tidak ada, maka jumlah kemunculan entity itu sesuai dengan jumlah defaultnya
                        entities[i]['occ_text'] = count
            else:
                entities[i]['occ_text'] = count

        return entities

    # find entity's occurence in text's title
    def findOccurencesInTitle(self,title,entities):

        for i in range(len(entities)):
            occ_title = False

            match = re.findall(r'\b'+re.escape(entities[i]["entity"].lower()) + r'\b',title.lower())
            if match:
                occ_title = True
            entities[i]["occ_title"] = occ_title

        return entities

    # find entities distribution in one text
    def findDistribution(self, data, entities):
        
        sent_list = sent_tokenize(data)

        #for every entities
        for i in range(len(entities)):
            dist = []
            # dist = 0
            #for every sentences
            for j in range(len(sent_list)):
                #find how many times entities found in each sentence
                # match = re.findall(r'\b'+re.escape(entities[i]["entity"].lower()) + r'\b',sent_list[j].lower())
                # if match:
                if entities[i]["entity"] in sent_list[j]:
                    # print("Entity:\t",entities[i]["entity"])
                    # print("Sentences:\t",sent_list[j])
                    # n of entity in sentence * index of sentences
                    # dist  = dist + (len(match)*(j+1))
                    # print("pos:",i)
                    dist.append(i+1)
            
            if dist == 0:
                print("zero dist: ",entities[i])
                print()

            # find disribution of entity with (n of entity in sentence * index of sentences)/frequency of entity in text
            # print("List dist:",dist)
            temp = np.sum(dist)
            # print(temp)
            # print()
            # entities[i]["dist"] = float(dist / entities[i]["occ_text"])
            entities[i]["dist"] = float(temp / entities[i]["occ_text"])
        
        return entities

    # combine all the module so we can extract features from pickle object
    def extractFeaturesFromPickle(self,data):
        print("Extracting features...")
        # extract entity yang ada berdasarkan data ner dari variable data
        print()
        print("Extracting feature: entity types")
        entities = self.extractEntity(data["ner"])
        # ambil noun phrase dari judul, lalu masukkan ke data entities, jika ternyata ada yang sama, hapus
        entities = self.pre.removeDuplicateListDict(self.findNounPhraseFromTitle(data["title"],entities))
        # bandingkan entity dari coref dengan entity yang dari ner, jika ada yang sama, maka tambahkan jumlah kemunculannya dan simpan
        print("Extracting feature: occurences in text ")
        entities = self.countCfOccurencesInText(entities,data["coref"],data["title"])
        # cari kemunculan enity di judul
        print("Extracting feature: occurences in title ")
        entities = self.findOccurencesInTitle(data["title"],entities)
        # cari nilai distribusid dari entity dalam teks
        print("Extracting feature: distribution ")
        entities = self.findDistribution(data["text"],entities)

        # append text index
        for entity in entities:
            entity['id_text'] = data["filename"]

        feature = pd.DataFrame(entities)
        return feature

    def extractFeaturesDirectFromText(self,data):
        print("Extracting features from text...")
        print("Extracting feature: entity types")
        entities = self.extractEntity(data["ner"])
        entities = self.pre.removeDuplicateListDict(self.findNounPhraseFromTitle(data["title"],entities))
        print("Extracting feature: occurences in text ")
        entities = self.countCfOccurencesInText(entities,data["coref"],data["title"])
        print("Extracting feature: occurences in title ")
        entities = self.findOccurencesInTitle(data["title"],entities)
        print("Extracting feature: distribution ")
        entities = self.findDistribution(data["text"],entities)

        feature = pd.DataFrame(entities)
        return feature

e = FeatureExtractor()
ut = Utility()

