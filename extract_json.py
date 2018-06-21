import json
import pandas as pd
from pprint import pprint
from nltk.tokenize import sent_tokenize
import re

class ExtractFeaturesValue(object):

    #load json file
    def loadJSON(self,filename):
        with open(filename) as file:
            data = json.load(file)

        return data

    # -- find out entity's type then extract it
    def extractEntityFromJSON(self,data):
        # list of extracted people,loc, organization entities from text
        list_person = []
        list_loc = []
        list_org = []

        for ner in data:
            # temporary array for person/org/loc composed from >1 word
            person = []
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
                    
                    #empty dictionary
                    tempdict = {}

        list_loc = self.removeDuplicateListDict(list_loc)
        list_person = self.removeDuplicateListDict(list_person)
        list_org = self.removeDuplicateListDict(list_org)

        entities = list_loc + list_person + list_org

        return entities

    # remove duplicate value in list of entities
    def removeDuplicateListDict(self,listdict):
        seen = set()
        new_list = []
        for dictionary in listdict:
            t = tuple(dictionary.items())
            if t not in seen:
                seen.add(t)
                new_list.append(dictionary)

        return new_list

    # count entity's occurences from text manually
    def countOccurencesInText(self,text,list_entity):
        sent_list = sent_tokenize(text)

        for i in range(len(entities)):
            count = 0
            for sent in sent_list:
                match = re.findall(r'\b'+re.escape(entities[i]["entity"].lower()) + r'\b',sent.lower())
                if match:
                    count += len(match)
                entities[i]["occ_text"] = count

        return entities
    
    # find entity's occurence in text's title
    def findOuccurencesInTitle(self,title,list_entity):

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

e = ExtractFeaturesValue()

# find feature in one text
data = e.loadJSON("nlp1.json")

entities = e.extractEntityFromJSON(data["NER"])
entities = e.countOccurencesInText(data["Text"],entities)
entities = e.findOuccurencesInTitle(data["Title"],entities)
entities = e.findDistribution(data["Text"],entities)

feature = pd.DataFrame(entities)

# convert to excel
excel = pd.ExcelWriter('test.xlsx',engine='xlsxwriter')
feature.to_excel(excel,sheet_name='Sheet1',index=False)
excel.save()
