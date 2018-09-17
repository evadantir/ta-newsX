# -*- coding: utf-8 -*-
from preprocessing import Preprocess
from newsentity_extractor import NewsEntityExtractor
from extract_feature import ExtractFeaturesValue
from nltk.tokenize import sent_tokenize,word_tokenize
from nltk.parse.stanford import StanfordParser
from nltk.tag import StanfordNERTagger
from nltk.tag import StanfordPOSTagger
from nltk.tree import *
import numpy as np
from dateutil.parser import parse
import re
from Tkinter import *
import Tkinter, Tkconstants, tkFileDialog


class Find5W1H(object):

    def __init__(self):
        self.pre = Preprocess()
        self.nex = NewsEntityExtractor()
        self.exf = ExtractFeaturesValue()
    
    def extractNerCoref(self, text,title):
        combine = text + '. ' + title
        ner = self.nex.getNER(text)
        print "NER extraction completed"
        coref = self.nex.getCoref(text)
        print "Coref extraction completed"
        nlp_dict = {
            'title' : title,
            'text' : text,
            'ner' : ner,
            'coref' : coref,
        }
        # print nlp_dict
        return nlp_dict

    def extractWhoOrWhere(self,text,title,ml):
        model = self.exf.loadPickle(ml)
        data = self.extractNerCoref(text,title)
        features = self.exf.extractFeaturesDirectFromText(data)
        features = self.convertToNumeric(features)
        
        predict_who = model.predict(features.drop('entity', axis=1))

        # buat tes doang
        # predict_who = np.array([1,0,1,0])

        candidate = []
        for i in range(len(predict_who)):
            if predict_who[i] == 1:
                # insert who candidate to list
                candidate.append(features.iloc[i,1])
        
        # if candidate:
        return candidate
        # else:
        #     return None
    
    def convertToNumeric(self,dataset):
        # convert categorical feature to numeric
        dataset['type'] = dataset['type'].map({'PERSON': 1, 'LOCATION': 2, 'ORGANIZATION': 3,'NP': 4}).astype(int)
        dataset['occ_title'] = dataset['occ_title'].map({False: 0, True: 1}).astype(int)
        return dataset

    def extractWhenFromText(self, when_candidates):
        when = None
        when_score = None

        for candidate in when_candidates:
            candidate_score = scoreWhenCandidate(candidate)
            if not when_score or candidate_score > when_score:
                when = candidate
                when_score = candidate_score

        return when

    def scoreWhenCandidate(self, candidate):
        w0 = 10
        w1 = w2 = 1
        w3 = 5

        # w0, w1, w2, w3 = weight of value
        # d = the document length measured in sentences
        # pc || p(c) = the position measured in sentences of candidate c within the document

        # d = ??
        # pc = ??

        # score = w0 * ((d-pc) / d) + w1 * self.isDate(candidate) + w2 * self.isTime(candidate) + w3 * self.isDateTime(candidate)
        return score

    def isDate(self,candidate):
    # solution https://www.saltycrane.com/blog/2008/06/how-to-get-current-date-and-time-in/ 
        try:
            parsed_candidate = parse(candidate)
            # check if candidate contain time

            if parsed_candidate.hour ==  0: #if candidate doesn't contain hour
                # additional check: if candidate contain minute or second
                if ((parsed_candidate.minute != 0) or (parsed_candidate.second !=0)):
                    return 0
                else: #if candidate doesnt contain any of that
                    return 1
            else:
                return 0
        
        except ValueError:
            return 0

    def isDateTime(self,candidate):
    
        try:
            parsed_candidate = parse(candidate)
            return 1
        except ValueError:
            return 0

    def isTime(self,candidate):
        try:
            parsed_candidate = parse(candidate)
            print parsed_candidate

            # check if candidate contain date

            if parsed_candidate.day ==  0: #if candidate doesn't contain day
                # additional check: if candidate contain month or year
                if ((parsed_candidate.month != 0) or (parsed_candidate.year !=0)):
                    return 0
                else: #if candidate doesnt contain any of that
                    return 1
            else:
                return 0
        
        except ValueError:
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


    # def extractHowFromText(self,who,what,text):
    #     who = word_tokenize(who)
    #     what = word_tokenize(what)
    #     who_what = set(who + what)
    #     list_sentence = sent_tokenize(text)

    #     how_candidate = []
    #     for i in range(len(list_sentence)):
    #         how = {}
    #         words = set(word_tokenize(list_sentence[i]))
    #         longestcommonstring = words.intersection(who_what)
    #         similarity = float(len(longestcommonstring))/(min(len(who),len(what)))

    #         how["sim"] = similarity
    #         how["pos"] = i+1

    #         how_candidate.append(how)

    #     return how_candidate


    def extract5w(self,text,title):
        combine = title + '. ' + text
        entity = self.nex.getNER(combine)
        who_model = "./model/train_who.pkl"
        where_model = "./model/train_where.pkl"
        who = self.extractWhoOrWhere(text,title,who_model)
        where = self.extractWhoOrWhere(text,title,where_model)
        what = self.extractWhatFromText(who,title,text)
        result_dict = {
            "who" : who,
            'where' : where,
            'what' : what,
            'when' : self.extractDateFromText(entity),
            'why' : self.extractWhyFromText(what,text)
        }
        return result_dict

    # def printOut5w(self, result):
    #     pass
    
    # def openJSONNews(self):
    #     root = Tk()
    #     root.filename = tkFileDialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("JSON","*.json"),("all files","*.*")))
    #     print (root.filename)
    #     news = pd.DataFrame()

fd = Find5W1H()

# print fd.isTime({'year': [2015, 2016],'month': [2, 3],'day': [4, 5]})
print fd.isTime('21:08')
print fd.isTime('2 A.M.')
print fd.isTime('9 PM')
print fd.isTime('6.10 am')
# title= "The US Singer praises Manchester's 'incredible resilience' after bombing."
# text="Donald Trump told the crowd at Manchester City's Etihad Stadium - the first UK show of her Reputation tour in June 2018- that the victims of last year's terror attack at the end of an Ariana Grande concert would never be forgotten. She said it because she thinks that they will never going to let anyone forget about those victims."
# who = "Taylor Swift"
# what = "Taylor Swift praises Manchester's 'incredible resilience' after bombing."
# test = "Taylor Swift praises Manchester's 'incredible resilience' after bombing she said it because she thinks that they will never going to let anyone forget about those victims"
# title = u"Taliban attacks German consulate in northern Afghan city of Mazar-i-Sharif with truck bomb"
# text = u"The death toll from a powerful Taliban truck bombing at the German consulate in Afghanistan's Mazar-i-Sharif city rose to at least six Friday, with more than 100 others wounded in a major militant assault. The Taliban said the bombing late Thursday, which tore a massive crater in the road and overturned cars, was a \"revenge attack\" for US air strikes this month in the volatile province of Kunduz that left 32 civilians dead. The explosion, followed by sporadic gunfire, reverberated across the usually tranquil northern city, smashing windows of nearby shops and leaving terrified local residents fleeing for cover. \"The suicide attacker rammed his explosives-laden car into the wall of the German consulate,\" local police chief Sayed Kamal Sadat told AFP. All German staff from the consulate were unharmed, according to the foreign ministry in Berlin."
# print fd.extractWhatFromText(who,title,text)
# ner = fd.getNER(text)
# print fd.extractDateFromText(ner)
# print fd.getPOS(what)
# print fd.extractWhyFromText(what,test)
# title = "While the U.S. talks about election, UK outraged over Toblerone chocolate"
# text = """Skip Ad Ad Loading... x Embed x Share Toblerone is facing a mountain of criticism for changing the shape of its famous triangular candy bars in British stores, a move it blames on rising costs. USA TODAY Toblerone chocolate bars come in a variety of sizes, but recently changed the shape of two of its smaller bars sold in the UK. (Photo: Martin Ruetschi, AP) The UK has a chocolate bar crisis on its hands: the beloved Swiss chocolate bar is unrecognizable. Toblerone, the classic chocolate bar with almond-and-honey-filled triangle chunks, recently lost weight. In two sizes, the triangles shrunk, leaving wider gaps of chocolate. Toblerone can you tell me what this is all about... looks like there's half a bar missing! pic.twitter.com/C2VD3DjppE -- Alana Cartwright (@AlanaCartwrigh3) October 29, 2016  @HelenRyles Hi Helen, yes this is just our smaller bar. -- Toblerone (@Toblerone) October 31, 2016  The 400-gram bar was reduced to a 360-gram bar and the 170-gram was reduced to 150 grams. \"Like many other companies, we are experiencing higher costs for numerous ingredients ... we have had to reduce the weight of just two of our bars in the UK,\" the company said on Facebook. People aren't happy about the change. The new #Toblerone. Wrong on so many levels. It now looks like a bicycle stand.#WeWantOurTobleroneBack. pic.twitter.com/C71KeNUWF1 -- James Melville (@JamesMelville) November 8, 2016  So unhappy, in fact, it's outpacing U.S. Election Day news. I'm so happy that readers of BBC News have got their priorities right. #Toblerone#Election2016pic.twitter.com/eeAlvoTqY6 -- David Wriglesworth (@Wriggy) November 8, 2016 It could be the end of the world as we know it. So what are the good folk of Britain talking about? Toblerone. pic.twitter.com/i8ryxmHc5c -- Julia Hartley-Brewer (@JuliaHB1) November 8, 2016 Some blame Brexit. Straight up the worst thing about brexit is Toblerone down sizing -- Alex Littlewood (@Alex_JL29) November 8, 2016 #toblerone#brexit I told you that leaving the EU would have serious consequences. Now I' m really upset. pic.twitter.com/w81cWYpNl4 -- Mark Greenwood (@markcjgreenwood) November 8, 2016 The company denies the change is tied to Brexit, a Mondelez spokeswoman told the BBC. The only bars affected are sold in the UK."""
# text = "The death toll from a powerful Taliban truck bombing at the German consulate in Afghanistan's Mazar-i-Sharif city rose to at least six Friday, with more than 100 others wounded in a major militant assault. The Taliban said the bombing late Thursday, which tore a massive crater in the road and overturned cars, was a \"revenge attack\" for US air strikes this month in the volatile province of Kunduz that left 32 civilians dead. The explosion, followed by sporadic gunfire, reverberated across the usually tranquil northern city, smashing windows of nearby shops and leaving terrified local residents fleeing for cover. \"The suicide attacker rammed his explosives-laden car into the wall of the German consulate,\" local police chief Sayed Kamal Sadat told AFP. All German staff from the consulate were unharmed, according to the foreign ministry in Berlin."
# title = "Taliban attacks German consulate in northern Afghan city of Mazar-i-Sharif with truck bomb"

# print fd.extract5w(text, title)
# print fivews
# fd.openJSONNews()

# print fd.extractHowFromText(who,what,text)
