import json
import joblib
import pandas as pd
from nltk.tokenize import sent_tokenize
import re
import os
from preprocessing import Preprocess
from nlp_helper import NLPHelper
import openpyxl
from pprint import pprint
from utility_code import Utility

class FeatureExtractor(object):

    def __init__(self):
        self.pre = Preprocess()
        self.nlp = NLPHelper()

    #load json file
    def loadJSON(self, filename):
        with open(filename) as file:
            data = json.load(file)

        return data

    def loadPickle(self,filename):
        pkl = joblib.load(filename)
        return pkl

    # -- find out entity's type then extract it
    def extractEntity(self,data):
        # list of extracted people,loc, organization entities from text
        list_person = []
        list_loc = []
        list_org = []

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
                    tempdict["entity"] = ' '.join(per)
                    tempdict["type"] = "PERSON"
                    list_person.append(tempdict)
                    #empty temp array
                    per = []
                elif org:
                    tempdict["entity"] = ' '.join(org)
                    tempdict["type"] = "ORGANIZATION"
                    list_org.append(tempdict)
                    #empty temp array
                    org = []
                elif loc:
                    tempdict["entity"] = ' '.join(loc)
                    tempdict["type"] = "LOCATION"
                    list_loc.append(tempdict)
                    #empty temp array
                    loc = []

        # remove duplicate item in list
        list_loc = self.pre.removeDuplicateListDict(list_loc)
        list_person = self.pre.removeDuplicateListDict(list_person)
        list_org = self.pre.removeDuplicateListDict(list_org)

        entities = list_loc + list_person + list_org

        return entities

    def findNounPhraseFromTitle(self,title,entities):
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
            dist = 0
            #for every sentences
            for j in range(len(sent_list)):
                #find how many times entities found in each sentence
                match = re.findall(r'\b'+re.escape(entities[i]["entity"].lower()) + r'\b',sent_list[j].lower())
                if match:
                    # n of entity in sentence * index of sentences
                    dist  = dist + (len(match)*(j+1))
            
            # if dist == 0:
            #     print(entities[i])

            # find disribution of entity with (n of entity in sentence * index of sentences)/frequency of entity in text

            entities[i]["dist"] = float(dist / entities[i]["occ_text"])
        
        return entities

    # combine all the module so we can extract features from pickle object
    def extractFeaturesFromPickle(self,data):

        # extract entity yang ada berdasarkan data ner dari variable data
        entities = self.extractEntity(data["ner"])
        # ambil noun phrase dari judul, lalu masukkan ke data entities, jika ternyata ada yang sama, hapus
        entities = self.pre.removeDuplicateListDict(self.findNounPhraseFromTitle(data["title"],entities))
        # bandingkan entity dari coref dengan entity yang dari ner, jika ada yang sama, maka tambahkan jumlah kemunculannya dan simpan
        entities = self.countCfOccurencesInText(entities,data["coref"],data["title"])
        # cari kemunculan enity di judul
        entities = self.findOccurencesInTitle(data["title"],entities)
        # cari nilai distribusid dari entity dalam teks
        entities = self.findDistribution(data["text"],entities)

        # append text index
        for entity in entities:
            entity['id_text'] = data["filename"]

        feature = pd.DataFrame(entities)
        return feature

    def extractFeaturesDirectFromText(self,data):
        
        entities = self.extractEntity(data["ner"])
        entities = self.pre.removeDuplicateListDict(self.findNounPhraseFromTitle(data["title"],entities))
        entities = self.countCfOccurencesInText(entities,data["coref"],data["title"])
        entities = self.findOccurencesInTitle(data["title"],entities)
        entities = self.findDistribution(data["text"],entities)

        feature = pd.DataFrame(entities)
        return feature

e = FeatureExtractor()
ut = Utility()

# data = e.loadPickle('./nlp_object/0e7ab2ce71c1bce03040ec2388dd45ab069d5432b364495b9cfcfdf5.json.pkl')

# # find feature in one text and save it to excel
# path = "./nlp_object/"
# filelist = os.listdir(path)
# data = pd.DataFrame()

# for idx, file in enumerate(filelist):

#     #buka file pickle yang isinya data ner, coref, dan pos dari suatu teks berita
#     pkl_dict = e.loadPickle(os.path.join(path, file))
#     # ekstraksi fitur dari file pickle
#     temp = e.extractFeaturesFromPickle(pkl_dict)
#     data = data.append(temp)
    
# ut.convertToExcel("cleaned_goldendata_extracted_feature.xlsx",data,'Sheet1')

