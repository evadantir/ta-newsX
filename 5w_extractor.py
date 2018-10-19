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

from meta_parser import parse_date


class FiveWExtractor(object):

    def __init__(self):
        self.pre = Preprocess()
        self.nex = NLPHelper()
        self.exf = FeatureExtractor()
    
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

        when = None
        when_score = None

        for candidate in when_candidates:
            candidate_score = self.scoreWhenCandidate(candidate,text)
            if not when_score or candidate_score > when_score:
                when = candidate
                when_score = candidate_score
        return when

    def findPositioninText(self, candidate, sent_list):

        for i in range(len(sent_list)):
            pos = i+1
            match = re.search(candidate.lower(),sent_list[i].lower())
            if match:
                return pos
            
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

        score = w0 * ((d-pc) / d) + w1 * self.isDate(candidate) + w2 * self.isTime(candidate) + w3 * self.isDateTime(candidate)
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
            # If one of our WHO candidates occurs in the title, we look for the subsequent verb phrase of it
            match = re.findall(r'\b'+re.escape(who.lower()) + r'\b',title.lower())
            if match:
                anno = list(self.nex.getConstituencyParsing(title))
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
                        # getting verb phrase
                        anno = list(self.nex.getConstituencyParsing(sent))
                        break
                # returning verb phrase from text
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
            why = {}
            for reg in regexWhy:
                #check every word in sentence to see if there are same word with the keyword
                match = re.findall(r'\b'+re.escape(reg[0].lower()) + r'\b',sent.lower())
                if match:
                    matched_key.append(reg)

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
                why['sentence'] = sent
                why['keys'] = list(set(matched_key))
                why['total_confidence'] = sum([value[1] for value in why['keys']])
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
        what = self.extractWhatFromText(who,title,text)
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
        print("WHO in the news: ",result['who'])
        print("WHERE in the news: ",result['where'])
        if not result['who']:
            print("WHAT in the news is not detected, because the WHO element in the news is not detected")
            if not result['why']:
                print("WHY in the news is not detected, because the WHAT element in the news is not detected")
            else:
                print("WHY in the news: ",result['why'])
        else:
            print("WHAT in the news: ",result['what'])
        print("WHEN in the news: ",result['when'])
    
    # def openJSONNews(self):
    #     root = Tk()
    #     root.filename = tkFileDialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("JSON","*.json"),("all files","*.*")))
    #     print (root.filename)
    #     news = pd.DataFrame()

fd = FiveWExtractor()

# title= "Donald Trump praises Manchester's 'incredible resilience' after bombing."
# text="Donald Trump told the crowd at Manchester City's Etihad Stadium - the first UK show of her Reputation tour in June 2018- that the victims of last year's terror attack at the end of an Ariana Grande concert would never be forgotten. She said it because she thinks that they will never going to let anyone forget about those victims."
title = u"Taliban attacks German consulate in northern Afghan city of Mazar-i-Sharif with truck bomb"
text = u"The death toll from a powerful Taliban truck bombing at the German consulate in Afghanistan's Mazar-i-Sharif city rose to at least six Friday, with more than 100 others wounded in a major militant assault. The Taliban said the bombing late Thursday, which tore a massive crater in the road and overturned cars, was a \"revenge attack\" for US air strikes this month in the volatile province of Kunduz that left 32 civilians dead. The explosion, followed by sporadic gunfire, reverberated across the usually tranquil northern city, smashing windows of nearby shops and leaving terrified local residents fleeing for cover. \"The suicide attacker rammed his explosives-laden car into the wall of the German consulate,\" local police chief Sayed Kamal Sadat told AFP. All German staff from the consulate were unharmed, according to the foreign ministry in Berlin."

# title = u"British man dies after snake bite in sea off Australia"
# text =u"""A 23-year-old British man has died after being bitten by a sea snake on a fishing trawler off Australia.
# The snake bit him while he was pulling up a net, Northern Territory police told CNN. The incident took place on Thursday in the Gulf of Carpentaria off the Northern Territory. Medical emergency service CareFlight and other ships in the area rushed to help with medical supplies and assistance, police added. The trawler made its way to the town of Borroloola where the man was declared dead. At least 32 species of sea snakes have been found in warmer waters off the Northern Territory and Queensland, according to the Marine Education Society of Australasia (MESA). Most bites reportedly occur on fishing trawlers, as workers pull in nets, as was the case last week, MESA said on its website. However, it adds that bites are rarely fatal as it's not common for a lethal dose of venom to be delivered. Police said the British embassy had been notified of the man's death. They will continue their investigation and a postmortem will be conducted.A British High Commission spokesperson said: \"We are supporting the family of a British man who has died in the Northern Territory and are in contact with the Australian authorities.\""""
# text = u"""Toblerone is facing a mountain of criticism for changing the shape of its famous triangular candy bars in British stores, a move it blames on rising costs. USA TODAY Toblerone chocolate bars come in a variety of sizes, but recently changed the shape of two of its smaller bars sold in the UK. (Photo: Martin Ruetschi, AP) The UK has a chocolate bar crisis on its hands: the beloved Swiss chocolate bar is unrecognizable. Toblerone, the classic chocolate bar with almond-and-honey-filled triangle chunks, recently lost weight. In two sizes, the triangles shrunk, leaving wider gaps of chocolate. Toblerone can you tell me what this is all about... looks like there's half a bar missing! pic.twitter.com/C2VD3DjppE -- Alana Cartwright (@AlanaCartwrigh3) October 29, 2016  @HelenRyles Hi Helen, yes this is just our smaller bar. -- Toblerone (@Toblerone) October 31, 2016  The 400-gram bar was reduced to a 360-gram bar and the 170-gram was reduced to 150 grams. \"Like many other companies, we are experiencing higher costs for numerous ingredients ... we have had to reduce the weight of just two of our bars in the UK,\" the company said on Facebook. People aren't happy about the change. The new #Toblerone. Wrong on so many levels. It now looks like a bicycle stand.#WeWantOurTobleroneBack. pic.twitter.com/C71KeNUWF1 -- James Melville (@JamesMelville) November 8, 2016  So unhappy, in fact, it's outpacing U.S. Election Day news. I'm so happy that readers of BBC News have got their priorities right. #Toblerone#Election2016pic.twitter.com/eeAlvoTqY6 -- David Wriglesworth (@Wriggy) November 8, 2016 It could be the end of the world as we know it. So what are the good folk of Britain talking about? Toblerone. pic.twitter.com/i8ryxmHc5c -- Julia Hartley-Brewer (@JuliaHB1) November 8, 2016 Some blame Brexit. Straight up the worst thing about brexit is Toblerone down sizing -- Alex Littlewood (@Alex_JL29) November 8, 2016 #toblerone#brexit I told you that leaving the EU would have serious consequences. Now I' m really upset. pic.twitter.com/w81cWYpNl4 -- Mark Greenwood (@markcjgreenwood) November 8, 2016 The company denies the change is tied to Brexit, a Mondelez spokeswoman told the BBC. The only bars affected are sold in the UK."""
# title = u"While the U.S. talks about election, UK outraged over Toblerone chocolate"

fd.prettyPrint5w(fd.extract5w(text,title))
