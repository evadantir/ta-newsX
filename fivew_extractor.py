# -*- coding: utf-8 -*-
from preprocessing import Preprocess
from nlp_helper import NLPHelper
from feature_extractor import FeatureExtractor
from utility_code import Utility
from nltk.tokenize import sent_tokenize,word_tokenize
from nltk.parse.stanford import StanfordParser
from nltk.tag import StanfordNERTagger
from nltk.tag import StanfordPOSTagger
from nltk.tree import *
from dateutil.parser import parse
import dateutil.parser as parser
import re
import os
import pandas as pd
import json
from meta_parser import parse_date
from pprint import pprint


class FiveWExtractor(object):

    def __init__(self):
        self.pre = Preprocess()
        self.nlp = NLPHelper()
        self.fex = FeatureExtractor()
        self.ut = Utility()
    
    def extractNerCorefFromTxt(self, text,title):

        ner = self.nlp.getNER(text)
        print ("NER extraction completed")
        coref = self.nlp.getCoref(text)
        print ("Coref extraction completed")
        nlp_dict = {
            'title' : title,
            'text' : text,
            'ner' : ner,
            'coref' : coref,
        }
        
        return nlp_dict

    def extractINANerAndCoref(self,text,title):
        ner = self.nlp.getIdnNER(text)
        print ("NER extraction completed")
        coref = self.nlp.getCoref(text)
        print ("Coref extraction completed")
        nlp_dict = {
            'title' : title,
            'text' : text,
            'ner' : ner,
            'coref' : coref,
        }
        
        return nlp_dict 

    def extractWhoOrWhere(self,text,title,ml,ner_coref):

        # load machine learning model
        model = self.ut.loadPickle(ml)

        # extracting features and convert it to numeric type
        features = self.fex.extractFeaturesDirectFromText(ner_coref)
        # print(features)
        features = self.convertToNumeric(features)
        
        # predicting who or where by it's feature, dropping unused column
        predict_candidate = model.predict(features.drop('entity', axis=1))
        print("candidates: ", predict_candidate)
        candidate = []

        for i in range(len(predict_candidate)):
            if predict_candidate[i] == 1:
                # insert candidate to list
                candidate.append(features.iloc[i,1])
        
        return candidate
    
    def convertToNumeric(self,dataset):
        # convert categorical feature to numeric
        dataset['type'] = dataset['type'].map({'PERSON': 1, 'LOCATION': 2, 'ORGANIZATION': 3,'NP': 4,'DATE':5,'TIME':6}).astype(int)
        dataset['occ_title'] = dataset['occ_title'].map({False: 0, True: 1}).astype(int)
        return dataset

    def getWhenCandidatefromNER(self,ner_list):
        print("Getting date and time entities in text with NER...")

        # getting when candidate (date and time) from extracted NER

        list_date = []
        list_time = []
        when_candidates = []

        date = []
        time = []

        for ner in ner_list:
            if ner[1] == 'DATE':
                date.append(ner[0])
            elif ner[1] == 'TIME':
                time.append(ner[0])
            else:
                if date != []:
                    list_date.append(self.pre.joinText(date))
                    date = []
                if time != []:
                    list_time.append(self.pre.joinText(time))
                    time = []

        list_date = self.pre.sieveSubstring(list_date)
        list_time = self.pre.sieveSubstring(list_time)
        when_candidates = list_date + list_time

        if when_candidates:
            return when_candidates
        else:
            return None

    def extractWhenFromText(self,text,ner):
        print()
        print("Extracting WHEN...")
        when_candidates = self.getWhenCandidatefromNER(ner)

        if when_candidates:
            when = None
            when_score = None

            for candidate in when_candidates:
                candidate_score = self.scoreWhenCandidate(candidate,text)
                if not when_score or candidate_score > when_score:
                    when = candidate
                    when_score = candidate_score

            return when
        else:
            return None

    def findPositioninText(self, candidate, sent_list):
        for i in range(len(sent_list)):
            pos = i+1
            
            match = re.search(candidate.lower(),sent_list[i].lower())
            if match:
                return pos
            else:
                return None
                
            
    def scoreWhenCandidate(self, candidate,text): 
        # w0, w1, w2, w3 = weight of value
        # d = the document length measured in sentences
        # pc || p(c) = the position measured in sentences of candidate c within the document
        print("Scoring WHEN candidate: "+ candidate)
        w0 = 10
        w1 = w2 = 1
        w3 = 5

        sent_list = sent_tokenize(text)
        d = len(sent_list)
        pc = self.findPositioninText(candidate,sent_list)

        if pc:
            score = w0 * ((d-pc) / d) + w1 * self.isDate(candidate) + w2 * self.isTime(candidate) + w3 * self.isDateTime(candidate)
        else:
            score = 0
        
        return score

    def isDate(self,candidate):
        # check if candidate is date instance, else return 0
        print("Checking if "+candidate+" can be parsed to a Date object...")
        parser.parser.parse = parse_date
        try:
            parsed_candidate = parser.parser().parse(candidate,None)
            # if contain date
            if parsed_candidate[0].day or parsed_candidate[0].month or parsed_candidate[0].year or parsed_candidate[0].weekday:
                return 1
            # if doesnt contain time and/or date
            else:
                return 0

        except (ValueError,AttributeError) as e:
            return 0

    def isDateTime(self,candidate):
        # check if it's parseable to datetime type
        print("Checking if "+candidate+" can be parsed to a DateTime object...")
        try:
            parsed_candidate = parse(candidate)
            return 1
        except (ValueError,AttributeError) as e:
            return 0

    def isTime(self,candidate):
        # check if when candidate contains date+time, time only, or neither
        print("Checking if "+candidate+" can be parsed to a Time object...")
        parser.parser.parse = parse_date
        try:
            parsed_time = parser.parser().parse(candidate,None)

            # if contain time
            if parsed_time[0].hour or parsed_time[0].minute or parsed_time[0].second or parsed_time[0].microsecond:
                # if contain date too
                if parsed_time[0].day or parsed_time[0].month or parsed_time[0].year or parsed_time[0].weekday:
                    return 0.8
                # if time only
                else:
                    return 1
            # if doesnt contain time and/or date
            else:
                return 0

        except (ValueError,AttributeError) as e:
            return 0

    def extractWhatFromText(self,who_candidates,title,text):
        print()
        print("Extracting WHAT...")
        what = []
        for who in who_candidates:
            # If one of our WHO candidates occurs in the title, we look for the subsequent verb phrase of it
            match = re.findall(r'\b'+re.escape(who.lower()) + r'\b',title.lower())
            if match:
                print("getting subsequent Verb Phrase from title...")
                anno = list(self.nlp.getConstituencyParsing(title))
                # print(anno)
                # returning verb phrase from title
                for sub_tree in anno[0].subtrees(lambda t: t.label() == 'VP'):
                    what.append(' '.join(sub_tree.leaves()))
            # If there is no WHO in the headline, we search within the text for the first occurrence of our highest ranked WHO and also take the subsequent verb phrase as WHAT
            else:
                sent_list = sent_tokenize(text)
                for sent in sent_list:
                    # find first occurrence of who in sentence
                    match = re.findall(r'\b'+re.escape(who.lower()) + r'\b',sent.lower())
                    if match:
                        print("getting subsequent Verb Phrase from sentence...")
                        # getting verb phrase
                        anno = list(self.nlp.getConstituencyParsing(sent))
                        # print(anno)
                        break
                # returning verb phrase from text
                for sub_tree in anno[0].subtrees(lambda t: t.label() == 'VP'):
                    what.append(' '.join(sub_tree.leaves()))

        what = self.pre.sieveSubstring(what)

        return what

    def extractWhyFromText(self,what_candidates,text):
        print()
        print("Extracting WHY...")
        regexWhy = [('since',0.2),('cause',0.3),('because',0.3),('hence',0.2),('therefore',0.3),('why',0.3),('result',0.4),('reason',0.3),('provide',0.1),('s behind',0.1),('Due to',0.2)]

        #for returning reason candidates from inputted text(s)
        why_candidates = []

        #extract sentence from the text
        sentence_list = sent_tokenize(text)

        for sent in sentence_list:
            matched_key = []
            # why = {}
            for reg in regexWhy:
                #check every word in sentence to see if there are same word with the keyword
                match = re.findall(r'\b'+re.escape(reg[0].lower()) + r'\b',sent.lower())
                if match:
                    matched_key.append(reg)

            if what_candidates:
                # check if what is in sentence
                # anggap 1 kalimat hanya punya 1 what
                for what in what_candidates:
                    # match = re.findall(r'\b' + what.lower() + r'\b',sent.lower())
                    # if match:
                    if what.lower() in sent.lower():
                        # check with WHAT(.*)to/TO(.*)/VB rule
                        
                        print("getting Part of Speech tag...")
                        pos = self.nlp.getPOS(sent)
                        for i in range(len(pos)):
                            if pos[i][1] == 'TO':
                                if pos[i+1][1] == 'VB':
                                    print("getting VERB in text...")
                                    rule = ('(WHAT(.*)to/TO(.*)/VB)',0.5)
                                    matched_key.append(rule)
                        # check with (WHAT(.*)will) rule
                        checked = re.findall(r'\b'+re.escape('will') + r'\b',sent.lower())
                        if checked:
                            rule = ('(WHAT(.*)will)',0.5)
                            matched_key.append(rule)
                    
            #store all reason list found from one text in  container
            if matched_key != []:
                why = sent
                # why['sentence'] = sent
                # why['keys'] = list(set(matched_key))
                # why['total_confidence'] = sum([value[1] for value in why['keys']])
                why_candidates.append(why)

        return why_candidates

    def extract5w(self,text,title):

        # getting ML model for classifying who and where 
        # scenario 1:
        who_model = "./model/train_who_idnhalf.pkl"
        where_model = "./model/train_where_idnhalf.pkl"

        # scenario 2:
        who_model = "./model/train_who_idnfull.pkl"
        where_model = "./model/train_where_idnfull.pkl"

                # scenario 3:
        who_model = "./model/train_who.pkl"
        where_model = "./model/train_where.pkl"

        print("Using " + who_model + " as WHO classifier and " + where_model + " as WHERE classifier\n")

        # getting NER and Coref of the text
        ner_coref = self.extractNerCorefFromTxt(text,title)
        # extracting 5w
        print("Extracting WHO...")
        who = self.extractWhoOrWhere(text,title,who_model,ner_coref)
        print("\nExtracting WHERE...")
        where = self.extractWhoOrWhere(text,title,where_model,ner_coref)
        when = self.extractWhenFromText(text,ner_coref['ner'])
        if who:
            what = self.extractWhatFromText(who,title,text)
        else:
            what = None
        why = self.extractWhyFromText(what,text)

        result_dict = {
            'title':title,
            'text': text,
            "who" : who,
            'where' : where,
            'what' : what,
            'when' : when,
            'why' : why
        }
        return result_dict

    # def extract5wLocalNews(self,text,title):


    #     # getting NER and Coref of the text
    #     ner_coref = self.extractINANerAndCoref(text,title)
    #     # extracting 5w
    #     who = self.extractWhoOrWhere(text,title,who_model,ner_coref)
    #     where = self.extractWhoOrWhere(text,title,where_model,ner_coref)
    #     when = self.extractWhenFromText(text,ner_coref['ner'])
    #     if who:
    #         what = self.extractWhatFromText(who,title,text)
    #     else:
    #         what = None
    #     why = self.extractWhyFromText(what,text)

    #     result_dict = {
    #         'title':title,
    #         'text': text,
    #         "who" : who,
    #         'where' : where,
    #         'what' : what,
    #         'when' : when,
    #         'why' : why
    #     }
    #     return result_dict

    def prettyPrint5w(self, result):
        print("\nExtracted 5W from: "+result['title'])
        print()
        if result['who']:
            print("WHO is in the news?: ",result['who'])
        else:
            print("Sorry, can not detect the WHO in the news")

        if result['where']:
            print("WHERE does the news take place?: ",result['where'])
        else:
            print("Sorry, can not detect the WHERE in the news")

        if result['when']:
            print("WHEN did the event in the news happen: ",result['when'])
        else:
            print("Sorry, can not detect the WHEN in the news")

        if not result['who']:
            print("WHAT in the news is not detected, because the WHO element in the news was not detected")
        else:
            print("WHAT is the event that happened in the news: ",result['what'])

        if not result['why']:
            if not result['what']:
                print("WHY in the news is not detected, because the WHAT element in the news was not detected")
            else:
                print("Sorry, can not detect the WHY in the news")
        else:
            print("WHY did the event in the news happen: ",result['why'])

fw = FiveWExtractor()

# title = "It's official: Prabowo to join 2019 race"
# text = "Gerindra Party chairman and chief patron Prabowo Subianto accepted his party's mandate to run for the presidency at its national coordination meeting in Hambalang, West Java, on Wednesday.His decision ended speculation over whether he was considering sitting the election out to endorse another candidate in the 2019 race. It also increased the likelihood that the upcoming election sees a rematch between the former commander of the Army's Special Forces and President Joko \"Jokowi\" Widodo.\"As the party's mandatary, as the holder of your mandate [...] I declare that I have submitted and complied with your decision,\" Prabowo said in a video of the closed-door meeting provided by a Gerindra politician.Earlier in the day, the opposition leader made it clear that he would only contest the election if the party built a strong alliance with other parties.Arriving to the meeting's main stage on horseback, to the strains of a brassy rendition of traditional marching song \"The British Grenadiers\", Prabowo cut an imposing figure in Gerindra's trademark white shirt, khaki pants, and black peci fez. \"With all my energy, body and soul, if Gerindra orders me to run in the upcoming presidential election, I am ready to carry out that task,\" he said, according to a Gerindra politician that was present, to the applause of the party members in attendance, who broke out in chants of \"Prabowo, president!\"Prabowo cut off the chanting, however, and asked for patience.\"I said 'if', 'if the party orders me,'\" he said. \"There is one condition. Even if the party orders me [to run], I need the support of friendly parties.\" Over the past few weeks, Prabowo has seemed hesitant over whether to run against President Jokowi again.Maksimus Ramses Lalongkoe, the executive director of the Institute of Indonesian Political Analysis, said Prabowo's apparent hesitation rested mostly on the lack of a clear coalition backing his candidacy.The 2017 Elections Law specifies that political parties seeking to nominate a presidential candidate are required to secure at least 20 percent of seats at the House of Representatives or 25 percent of the popular vote.Gerindra currently holds only 13 percent of House seats and 11.81 percent of the popular vote, which means it needs to join forces with other parties to be able to nominate Prabowo or any other potential candidate.Four parties with significant vote shares have yet to officially back a candidate: the National Mandate Party (PAN), the Prosperous Justice Party (PKS), the National Awakening Party (PKB) and the Democratic Party (PD).PAN and the PKS have worked together with Gerindra in recent times, most notably during the contentious Jakarta gubernatorial election last year. "


# print("Input the title of the news:")
# title = input()
# print("Input the text of the news:")
# text = input()
# print(fw.extract5wLocalNews(text,title))

# print(fw.extractWhoOrWhere(text,title,))

title = "Actress Titi Qadarsih passes away after battle with colon cancer"
text = """Veteran actress Titi Qadarsih passed away on Monday after battling colon cancer. She was 73 years old."Mama has been sick since the fasting month, when the doctor diagnosed her with stage fourcolon cancer," said Indra Q, the late actress's son on Monday, as quoted by kompas.com.Indra said that Titi had been undergoing intensive treatment for the past couple of months, since the diagnosis was made during the fasting month that began in mid-May."We started the treatment around two months ago. The last two weeks were intensive at Fatmawati Hospital," said Indra, who is a BIP band member and Slank's former keyboardist.He said her death came unexpectedly. "Eating has been a bit difficult. But mama was always agile. We never knew, and she finally passed away like this," Indra said.Titi is expected to be buried at Tanah Kusir Cemetery in Kebayoran Lama, South Jakarta. Throughout her life, Titi was known for her diverse skills in the entertainment world, ranging from acting in movies, singing, dancing to modeling.Titi made her debut on the big screen in the 1996 movie Hancurnya Petualang(Destroyed Adventurers). She also joined the stage through Teater Koma and sang a duet with Gombloh. (liz/kes)"""
fw.prettyPrint5w(fw.extract5w(text,title))

# print(fw.nlp.getIdnNER(text))
