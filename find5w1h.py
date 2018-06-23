# -*- coding: utf-8 -*-
from stanfordcorenlp import StanfordCoreNLP
from preprocessing import Preprocess
from nltk.tokenize import sent_tokenize,word_tokenize
from nltk.parse.stanford import StanfordParser
from nltk.tag import StanfordNERTagger
from nltk.tag import StanfordPOSTagger
from nltk.tree import *
import re

class Find5W1H(object):

    def __init__(self):
        self.pre = Preprocess()
        # self.nlp = StanfordCoreNLP(r'./stanford-corenlp-full-2018-02-27',memory='5g')
        # self.annotate = self.getConstituencyParsing()

    # parsing for getting verb phrase
    def getConstituencyParsing(self,text):
        scp = StanfordParser('./stanford/stanford-parser.jar','./stanford/stanford-parser-3.9.1-models.jar',encoding='utf8')
        return scp.raw_parse(text)

    def getNER(self,text):

        list_sentence = sent_tokenize(text)
        ner_tagger = StanfordNERTagger('./stanford/english.muc.7class.distsim.crf.ser.gz','./stanford/stanford-ner.jar', encoding='utf8')
        ner = []
        for sent in list_sentence:
            words = word_tokenize(sent)
            ner.append(ner_tagger.tag(words))

        return ner

    def getPOS(self,text):
        pos_tagger = StanfordPOSTagger('./stanford/english-bidirectional-distsim.tagger','./stanford/stanford-postagger.jar',encoding='utf8')
        words = word_tokenize(text)
        pos = pos_tagger.tag(words)

        return pos

    def extractDateFromText(self,data):

        list_date = []

        date = []
        for sent in data:
            for ner in sent:
                if ner[1] == 'DATE':
                    date.append(ner[0])
                else:
                    if date != []:
                        list_date.append(' '.join(date))
                        date = []

        list_date = self.pre.sieveSubstring(list_date)

        return list_date

    # extracting what element from text -- LOGIC STILL NEEDED TO BE APPROVED
    def extractWhatFromText(self,who,title,text):
        # If one of our WHO candidates occurs in the title, we look for the subsequent verb phrase of it
        match = re.findall(r'\b'+re.escape(who.lower()) + r'\b',title.lower())
        if match:
            anno = list(self.getConstituencyParsing(title))
            # returning verb phrase from title
            for sub_tree in anno[0].subtrees(lambda t: t.label() == 'VP'):
                return ' '.join(sub_tree.leaves())
        # If there is no WHO in the headline, we search within the text for the first occurrence of our highest ranked WHO and also take the subsequent verb phrase as WHAT
        else:
            sent_list = sent_tokenize(text)
            for sent in sent_list:
                # find first occurrence of who in sentence
                match = re.findall(r'\b'+re.escape(who.lower()) + r'\b',sent.lower())
                if match:
                    # getting verb phrase
                    anno = list(self.getConstituencyParsing(sent))
                    break
            # returning verb phrase from text
            for sub_tree in anno[0].subtrees(lambda t: t.label() == 'VP'):
                return ' '.join(sub_tree.leaves())

    def extractWhyFromText(self,what,text):
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
            match = re.findall(r'\b'+re.escape(what.lower()) + r'\b',sent.lower())
            if match:
                # check with WHAT(.*)to/TO(.*)/VB rule
                pos = self.getPOS(sent)
                for i in range(len(pos)):
                    if pos[i][1] == 'TO':
                        if pos[i+1][1] == 'VB':
                            rule = ('(WHAT(.*)to/TO(.*)/VB)',0.5)
                            matched_key.append(rule)
                # check with (WHAT(.*)will) rule
                checked = re.findall('will',sent.lower())
                if checked:
                    rule = ('(WHAT(.*)will)',0.5)
                    matched_key.append(rule)
            
            #store all reason list found from one text in  container
            if matched_key != []:
                why['sentence'] = list(set(sent))
                why['keys'] = list(set(matched_key))
                why['total_confidence'] = sum([value[1] for value in why['keys']])
                why_candidates.append(why)

        if why_candidates:
            return why_candidates

    def extractHowFromText(self,who,what,text):
        who = word_tokenize(who)
        what = word_tokenize(what)
        who_what = set(who + what)
        list_sentence = sent_tokenize(text)

        how_candidate = []
        for i in range(len(list_sentence)):
            how = {}
            words = set(word_tokenize(list_sentence[i]))
            longestcommonstring = words.intersection(who_what)
            similarity = float(len(longestcommonstring))/(min(len(who),len(what)))

            how["sim"] = similarity
            how["pos"] = i+1

            how_candidate.append(how)

        return how_candidate

fd = Find5W1H()

title= "The US Singer praises Manchester's 'incredible resilience' after bombing."
text="Taylor Swift told the crowd at Manchester City's Etihad Stadium - the first UK show of her Reputation tour - that the victims of last year's terror attack at the end of an Ariana Grande concert would never be forgotten. She said it because she thinks that they will never going to let anyone forget about those victims."
who = "Taylor Swift"
what = "praises Manchester's 'incredible resilience' after bombing."
test = "She said it because she thinks that they will never going to let anyone forget about those victims"
# text = "At least 39 people were killed and at least 69 wounded in an attack in a nightclub early Sunday as they were celebrating the new year, Turkey's Interior Minister said."
# print fd.extractWhatFromText(who,title,text)
# ner = fd.getNER(text)
# print fd.extractDateFromText(ner)
# print fd.getPOS(what)
print fd.extractWhyFromText(what,text)
# print fd.extractHowFromText(who,what,text)
