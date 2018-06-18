import json
import pandas as pd
from pprint import pprint

#load json file
with open('nlp.json') as file:
    data = json.load(file)

# get coref and ner data from JSON file
cf_coref = data["Coref"]
ner = data["NER"]

#--count entity's occurences in text

# cari yang mentionsnya (kata ganti) tidak kosong
cf_morethanone = [{"entity" : x["head"], "count" : len(x["mentions"])+1} for x in cf_coref if x["mentions"]]
#cari entity yang unique
cf_unique = [{"entity" : x["head"], "count" : 1} for x in cf_coref if not x["mentions"]]

# -- find out entity's type
# extract people entities from text
list_person = []

for ne in ner:
    person = []
    for sent in ne:
        if sent["ner"] == 'PERSON':  
            person.append(sent["word"]) 
        else:
            if person != []:
                list_person.append(' '.join(person))
                person = []


temp = pd.DataFrame()
temp = cf_morethanone+cf_unique+ list_person
print temp