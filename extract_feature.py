import json
import joblib
import pandas as pd
from nltk.tokenize import sent_tokenize
import re
import os
from preprocessing import Preprocess
from newsentity_extractor import NewsEntityExtractor

class ExtractFeaturesValue(object):

    def __init__(self):
        self.pre = Preprocess()
        self.nex = NewsEntityExtractor()

    #load json file
    def loadJSON(self, filename):
        with open(filename) as file:
            data = json.load(file)

        return data

    def loadPickle(self,filename):
        pkl = joblib.load(filename)
        return pkl

    # -- find out entity's type then extract it
    def extractEntityFromJSON(self,data):
        # list of extracted people,loc, organization entities from text
        list_person = []
        list_loc = []
        list_org = []
        list_misc = []

        for ner in data:
            # temporary array for person/org/loc composed from >1 word
            person = []
            misc = []
            tempdict = {}
            org = []
            loc = []
            # looping for in each of sentences
            for sent in ner:
                # check if entity is person/loc/org. if found save it in temp array
                if sent["ner"] == 'PERSON':  
                    person.append(sent["word"])
                elif sent["ner"] == 'ORGANIZATION':
                    org.append(sent["word"])
                elif (sent["ner"] == 'LOCATION') or (sent["ner"] == 'COUNTRY') or (sent["ner"] == 'CITY'):
                    loc.append(sent["word"])
                elif sent["ner"] == 'MISC':
                    misc.append(sent["word"])
                #if it's not one of them...
                else:
                    #check if there's temp array that's not emptied yet 
                    if person != []:
                        tempdict["entity"] = ' '.join(person)
                        tempdict["type"] = "PERSON"
                        list_person.append(tempdict)
                        #empty temp array
                        person = []
                    # if 
                    if org != []:
                        tempdict["entity"] = ' '.join(org)
                        tempdict["type"] = "ORGANIZATION"
                        list_org.append(tempdict)
                        #empty temp array
                        org = []
                    # if
                    if loc != []:
                        tempdict["entity"] = ' '.join(loc)
                        tempdict["type"] = "LOCATION"
                        list_loc.append(tempdict)
                        #empty temp array
                        loc = []
                    if misc != []:
                        tempdict["entity"] = ' '.join(misc)
                        tempdict["type"] = "MISC"
                        list_misc.append(tempdict)
                        #empty temp array
                        misc = []
                    #empty dictionary
                    tempdict = {}

        list_loc = self.pre.removeDuplicateListDict(list_loc)
        list_person = self.pre.removeDuplicateListDict(list_person)
        list_org = self.pre.removeDuplicateListDict(list_org)
        list_misc = self.pre.removeDuplicateListDict(list_misc)

        entities = list_loc + list_person + list_org + list_misc

        return entities

    # -- find out entity's type then extract it
    def extractEntityFromPickle(self,data):
        # list of extracted people,loc, organization entities from text
        list_person = []
        list_loc = []
        list_org = []
        list_misc = []

        for ner in data:
            # temporary array for person/org/loc composed from >1 word
            person = []
            misc = []
            tempdict = {}
            org = []
            loc = []
            # looping for in each of sentences
            for sent in ner:
                # check if entity is person/loc/org. if found save it in temp array
                if sent[1] == 'PERSON':  
                    person.append(sent[0])
                elif sent[1] == 'ORGANIZATION':
                    org.append(sent[0])
                elif (sent[1] == 'LOCATION') or (sent[1] == 'COUNTRY') or (sent[1] == 'CITY'):
                    loc.append(sent[0])
                elif sent[1] == 'MISC':
                    misc.append(sent[0])
                #if it's not one of them...
                else:
                    #check if there's temp array that's not emptied yet 
                    if person != []:
                        tempdict["entity"] = ' '.join(person)
                        tempdict["type"] = "PERSON"
                        list_person.append(tempdict)
                        #empty temp array
                        person = []
                    # if 
                    if org != []:
                        tempdict["entity"] = ' '.join(org)
                        tempdict["type"] = "ORGANIZATION"
                        list_org.append(tempdict)
                        #empty temp array
                        org = []
                    # if
                    if loc != []:
                        tempdict["entity"] = ' '.join(loc)
                        tempdict["type"] = "LOCATION"
                        list_loc.append(tempdict)
                        #empty temp array
                        loc = []
                    if misc != []:
                        tempdict["entity"] = ' '.join(misc)
                        tempdict["type"] = "MISC"
                        list_misc.append(tempdict)
                        #empty temp array
                        misc = []
                    #empty dictionary
                    tempdict = {}

        list_loc = self.pre.removeDuplicateListDict(list_loc)
        list_person = self.pre.removeDuplicateListDict(list_person)
        list_org = self.pre.removeDuplicateListDict(list_org)
        list_misc = self.pre.removeDuplicateListDict(list_misc)

        entities = list_loc + list_person + list_org + list_misc

        return entities

    # count entity's occurences from text manually
    def countManOccurencesInText(self,text,entities):
        sent_list = sent_tokenize(text)

        for i in range(len(entities)):
            count = 0
            for sent in sent_list:
                match = re.findall(r'\b'+re.escape(entities[i]["entity"].lower()) + r'\b',sent.lower())
                if match:
                    count += len(match)
                entities[i]["occ_text"] = count

        return entities

    def findNounPhraseFromTitle(self,title,entities):
        anno = list(self.nex.getConstituencyParsing(title))

        # returning verb phrase from title
        temp = {}
        for sub_tree in anno[0].subtrees(lambda t: t.label() == 'NP'):
            temp['entity'] = (' '.join(sub_tree.leaves()))
            temp['type'] = 'NP'
            entities.append(temp)
        
        return entities

    def countCfOccurencesInText(self,entities,coref):
        # if "main" entity in coref extraction is the same with named entities from ner process, then unite it
        for i in range(len(entities)):
            count = 1
            for cf in coref:
                if cf['main'] in entities[i]['entity']:
                    count = 0
                    count += len(cf['mentions'])
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

    #--count entity's occurences in text from coref -- NOT USED
    def extractCoRef(self,data):

        # cari yang mentionsnya (kata ganti) tidak kosong
        cf_morethanone = [{"entity" : x["head"], "count" : len(x["mentions"])+1} for x in data if x["mentions"]]
        #cari entity yang unique
        cf_unique = [{"entity" : x["head"], "count" : 1} for x in data if not x["mentions"]]

        temp = cf_morethanone + cf_unique
        temp = pd.DataFrame(temp)

    # find entities distribution in one text
    def findDistribution(self,data,entities):
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
            
            # find disribution of entity with (n of entity in sentence * index of sentences)/frequency of entity in text
            entities[i]["dist"] = float(dist / entities[i]["occ_text"])

        return entities

    def extractFeaturesFromJSON(self,filename):

        data = self.loadJSON(filename)

        entities = self.extractEntityFromJSON(data["NER"])
        entities = self.countManOccurencesInText(data["Text"],entities)
        entities = self.findOccurencesInTitle(data["Title"],entities)
        entities = self.findDistribution(data["Text"],entities)

        feature = pd.DataFrame(entities)

        return feature

    # combine all the module so we can extract features from pickle object
    def extractFeaturesFromPickle(self,filename):

        data = self.loadPickle(filename)
        entities = self.extractEntityFromPickle(data["ner"])
        entities = self.pre.removeDuplicateListDict(self.findNounPhraseFromTitle(data["title"],entities))
        entities = self.countCfOccurencesInText(entities,data["coref"])
        entities = self.findOccurencesInTitle(data["title"],entities)
        entities = self.findDistribution(data["text"],entities)

        feature = pd.DataFrame(entities)

        return feature

    def convertToExcel(self,filename,data):
        import xlsxwriter
        # convert to excel
        excel = pd.ExcelWriter(filename,engine='xlsxwriter')
        data.to_excel(excel,sheet_name='Sheet1',index=False)
        excel.save()

        print filename + " successfully saved as Excel file!"

e = ExtractFeaturesValue()

# find feature in one text and save it to excel
path = "./nlp_object/"
filelist = os.listdir(path)

for file in filelist:
    data = e.extractFeaturesFromPickle(os.path.join(path, file))
    e.convertToExcel("test123.xlsx",data)

