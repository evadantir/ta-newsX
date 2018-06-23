# -*- coding: utf-8 -*-
from stanfordcorenlp import StanfordCoreNLP
from preprocessing import Preprocess
from nltk.tokenize import sent_tokenize,word_tokenize
from nltk.parse.stanford import StanfordParser
from nltk.tag import StanfordNERTagger
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
                return who + ' ' + ' '.join(sub_tree.leaves())
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
                return who + ' ' + ' '.join(sub_tree.leaves())

fd = Find5W1H()

title= "The US Singer praises Manchester's 'incredible resilience' after bombing."
# text="Taylor Swift told the crowd at Manchester City's Etihad Stadium - the first UK show of her Reputation tour - that the victims of last year's terror attack at the end of an Ariana Grande concert would never be forgotten. She said: \"You've shown that you're never going to let anyone forget about those victims.\""
who = "Taylor Swift"
text = "At least 39 people were killed and at least 69 wounded in an attack in a nightclub early Sunday as they were celebrating the new year, Turkey's Interior Minister said."
# print fd.extractWhatFromText(who,title,text)
ner = fd.getNER(text)
print fd.extractDateFromText(ner)
