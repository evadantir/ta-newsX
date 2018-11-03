# -*- coding: utf-8 -*-
from preprocessing import Preprocess
from nlp_helper import NLPHelper
from feature_extractor import FeatureExtractor
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
from utility_code import Utility
import json
from meta_parser import parse_date
from pprint import pprint


class FiveWExtractor(object):

    def __init__(self):
        self.pre = Preprocess()
        self.nex = NLPHelper()
        self.exf = FeatureExtractor()
        self.ut = Utility()
    
    def extractNerCorefFromTxt(self, text,title):
        
        combine = text + '. ' + title

        ner = self.nex.getNER(text)
        print ("NER extraction completed")
        coref = self.nex.getCoref(text)
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
        model = self.exf.loadPickle(ml)

        # extracting features and convert it to numeric type
        features = self.exf.extractFeaturesDirectFromText(ner_coref)
        features = self.convertToNumeric(features)
        
        # predicting who or where by it's feature, dropping unused column
        predict_candidate = model.predict(features.drop('entity', axis=1))

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
                    list_date.append(self.joinText(date))
                    date = []
                if time != []:
                    list_time.append(self.joinText(time))
                    time = []

        list_date = self.pre.sieveSubstring(list_date)
        list_time = self.pre.sieveSubstring(list_time)
        when_candidates = list_date + list_time

        if when_candidates:
            return when_candidates
        else:
            return None

    def joinText(self,list_text):
        import string

        text = ""
        for t in list_text:
            if not text:
                text = t
            elif t in string.punctuation:
                text += t
            else:
                text += " " + t
        return text

    def extractWhenFromText(self,text,ner):
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
    
        try:
            parsed_candidate = parse(candidate)
            return 1
        except (ValueError,AttributeError) as e:
            return 0

    def isTime(self,candidate):
        # check if when candidate contains date+time, time only, or neither

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

    # extracting what element from text -- LOGIC STILL NEEDED TO BE APPROVED
    def extractWhatFromText(self,who_candidates,title,text):
        what = []
        
        for who in who_candidates:
            anno = []
            # If one of our WHO candidates occurs in the title, we look for the subsequent verb phrase of it
            match = re.findall(r'\b'+re.escape(who.lower()) + r'\b',title.lower())
            if match:
                # print("Match: ",match)
                anno = list(self.nex.getConstituencyParsing(title))
                # returning verb phrase from title
                vp = list(anno[0].subtrees(filter=lambda x: x.label()=='VP'))
                vp_str = [" ".join(v.leaves()) for v in vp]
                print(vp_str[0])
                exit()
                # print("VP",vp)
                # for sub_tree in anno[0].subtrees(lambda t: t.label() == 'VP'):
                #     print(sub_tree.leaves())
                #     what.append(' '.join(sub_tree.leaves()))
                # print("Matched what:",what)
            # If there is no WHO in the headline, we search within the text for the first occurrence of our highest ranked WHO and also take the subsequent verb phrase as WHAT
            else:
                sent_list = sent_tokenize(text)
                for sent in sent_list:
                    # find first occurrence of who in sentence
                    match = re.findall(r'\b'+re.escape(who.lower()) + r'\b',sent.lower())
                    if match:
                        # getting verb phrase
                        anno = list(self.nex.getConstituencyParsing(sent))
                        # print(anno)
                        break
                # returning verb phrase from text
                if anno:
                    for sub_tree in anno[0].subtrees(lambda t: t.label() == 'VP'):
                        what.append(' '.join(sub_tree.leaves()))
        # if what:
        #     return what
        # else:
        #     return None
        return what

    def extractWhyFromText(self,what_candidates,text):
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
                    match = re.findall(r'\b' + what.lower() + r'\b',sent.lower())
                    if match:
                        # check with WHAT(.*)to/TO(.*)/VB rule
                        pos = self.nex.getPOS(sent)
                        for i in range(len(pos)):
                            if pos[i][1] == 'TO':
                                if pos[i+1][1] == 'VB':
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
        who_model = "./model/train_who.pkl"
        where_model = "./model/train_where.pkl"

        # getting NER and Coref of the text
        ner_coref = self.extractNerCorefFromTxt(text,title)

        # extracting 5w
        who = self.extractWhoOrWhere(text,title,who_model,ner_coref)
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

    def prettyPrint5w(self, result):
        print("News Title: ",result['title'])
        print()
        print("WHO is in the news?: ",result['who'])
        print("WHERE does the news take place?: ",result['where'])
        if not result['who']:
            print("WHAT in the news is not detected, because the WHO element in the news is not detected")
            if not result['why']:
                print("WHY in the news is not detected, because the WHAT element in the news is not detected")
            else:
                print("WHY did the news happen: ",result['why'])
        else:
            print("WHAT happened in the news: ",result['what'])
        print("WHEN did the news happen: ",result['when'])
    
    def evaluateGoldenDatasetNews(self, file_range=None):
        # filerange = (0, 10)
        # find feature in one text and save it to excel
        path = "./datasets/"
        filelist = os.listdir(path)
        data = pd.DataFrame()

        if file_range:
            filelist = filelist[file_range[0]:file_range[1]]

        for idx, file in enumerate(filelist):
            print (file)
            #buka file pickle yang isinya data ner, coref, dan pos dari suatu teks berita
            file_temp = self.ut.loadJSON(os.path.join(path, file))
            # ekstraksi 5W dari file JSON
            try:
                temp = self.extract5w(file_temp["text"],file_temp["title"])
                temp["file"] = file
                data = data.append(temp,ignore_index = True)
            except:
                temp = []
                print("It failed huhu")
           
        self.ut.convertToExcel("goldendata_evaluate_089.xlsx",data,'Sheet1')

        print("Evaluating golden data is done!")

    def evaluateLocalNews(self,filename):
        
        data = self.nex.loadCSV(filename,',',"ISO-8859-1")
        data['extracted'] = data.apply(lambda x: self.extract5w(x['text'], x['title']), axis=1)
        # print(data['extracted'].iloc[0])
        temp = pd.DataFrame()
        temp['title'] = data['extracted'].apply(lambda x: x['title'])
        temp['text'] = data['extracted'].apply(lambda x: x['text'])
        temp['who'] = data['extracted'].apply(lambda x: x['who'])
        temp['where'] = data['extracted'].apply(lambda x: x['where'])
        temp['what'] = data['extracted'].apply(lambda x: x['what'])
        temp['when'] = data['extracted'].apply(lambda x: x['when'])
        temp['why'] = data['extracted'].apply(lambda x: x['why'])
        # temp = pd.DataFrame.from_dict(data['extracted'])
        print(temp)
        # exit()
        self.ut.convertToExcel("localnews_evaluate.xlsx",temp,'Sheet1')

        print("Evaluating local news is done!")

fd = FiveWExtractor()

# text="\"I must say that he surprised me,\" said father, Jos, who competed in Formula One from 1994 to 2003. \"I've seen many races of this, and this was incredible. Although Red Bull didn't have the right strategy and were unlucky with the weather, it was almost worth them having a bad stop to see what he did afterwards. It's good for F1, everyone is enthusiastic. What more do you want?\" Equally enraptured was Niki Lauda, the former world champion and Mercedes' non-executive chairman. Congratulating the Verstappen family, he said: \"Max was outstanding with the passes he performed. He did a job that was impressive. I knew the guy was good, but he has proved again to everybody what he can do.\""
# title="Max Verstappen even stuns his dad by storming home into third place at Brazilian Grand Prix"
# test =  list(fd.nex.getConstituencyParsing(title))
# print (test)
# huhu = (fd.nex.getCP(title))
# print(type(huhu))
# fd.prettyPrint5w(fd.extract5w(text,title))
# fd.evaluateGoldenDatasetNews(file_range=(0,88))
# fd.evaluateLocalNews("beritalokal.csv")

title = "It's official: Prabowo to join 2019 race"
text = "Gerindra Party chairman and chief patron Prabowo Subianto accepted his party's mandate to run for the presidency at its national coordination meeting in Hambalang, West Java, on Wednesday.His decision ended speculation over whether he was considering sitting the election out to endorse another candidate in the 2019 race. It also increased the likelihood that the upcoming election sees a rematch between the former commander of the Army's Special Forces and President Joko \"Jokowi\" Widodo.\"As the party's mandatary, as the holder of your mandate [...] I declare that I have submitted and complied with your decision,\" Prabowo said in a video of the closed-door meeting provided by a Gerindra politician.Earlier in the day, the opposition leader made it clear that he would only contest the election if the party built a strong alliance with other parties.Arriving to the meeting's main stage on horseback, to the strains of a brassy rendition of traditional marching song \"The British Grenadiers\", Prabowo cut an imposing figure in Gerindra's trademark white shirt, khaki pants, and black peci fez. \"With all my energy, body and soul, if Gerindra orders me to run in the upcoming presidential election, I am ready to carry out that task,\" he said, according to a Gerindra politician that was present, to the applause of the party members in attendance, who broke out in chants of \"Prabowo, president!\"Prabowo cut off the chanting, however, and asked for patience.\"I said 'if', 'if the party orders me,'\" he said. \"There is one condition. Even if the party orders me [to run], I need the support of friendly parties.\" Over the past few weeks, Prabowo has seemed hesitant over whether to run against President Jokowi again.Maksimus Ramses Lalongkoe, the executive director of the Institute of Indonesian Political Analysis, said Prabowo's apparent hesitation rested mostly on the lack of a clear coalition backing his candidacy.The 2017 Elections Law specifies that political parties seeking to nominate a presidential candidate are required to secure at least 20 percent of seats at the House of Representatives or 25 percent of the popular vote.Gerindra currently holds only 13 percent of House seats and 11.81 percent of the popular vote, which means it needs to join forces with other parties to be able to nominate Prabowo or any other potential candidate.Four parties with significant vote shares have yet to officially back a candidate: the National Mandate Party (PAN), the Prosperous Justice Party (PKS), the National Awakening Party (PKB) and the Democratic Party (PD).PAN and the PKS have worked together with Gerindra in recent times, most notably during the contentious Jakarta gubernatorial election last year. "

fd.extractWhatFromText('Prabowo Subianto',title,text)
# A Gerindra official has said that Prabowo might declare his candidacy in Banyumas, Central Java, should the party secure the support of PAN and the PKS. However, PAN seems reluctant about unequivocally endorsing Prabowo, with its chairman Zulkifli Hasan, who attended the Gerindra meeting, saying that the party had yet to make a decision. \"If the PDI-P [Jokowi's Indonesian Democratic Party of Struggle] invited us, we would also come and speak,\" he said as quoted by Antara.Gerindra and the PKS have enough seats at the House to nominate Prabowo, but it is likely that Prabowo is seeking more support to match a much bigger political alliance behind Jokowi, who has the backing of five parties.Maksimus said Indonesia's dynamic political landscape meant that parties were still looking to see what moves might give them the edge. \"They're still doing a lot of maneuvering, trying to see if one of their own members has a chance at running,\" he said. Prabowo has struggled to match Jokowi's electability, which is at 45 to 55 percent, but Maksimus said that such a challenge was unlikely to be the cause of his indecision. \"Electability can change very quickly, Jokowi's electability can be high now, but who knows what it will be like on election day.\" He added that Prabowo had no other choice but to run as other potential candidates, such as former Indonesian Military chief Gatot Nurmantyo and Jakarta Governor Anies Baswedan, would not motivate the party machine in the same way that Prabowo would.Nevertheless, he did not dismiss out of hand the possibility of Prabowo pairing up with erstwhile adversary Jokowi, once again citing the fast-moving nature of Indonesian politics.\"If Prabowo is backed into a corner, then he might well decide to join forces with Jokowi, rather than leave empty-handed.\"