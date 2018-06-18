# -*- coding: utf-8 -*-
from stanfordcorenlp import StanfordCoreNLP
from tokenization import *

class ExtractEntity(object):

    def extractNewsSentence(self,text):
        return sentence_extraction(text);

    def coreNLP(self,text):
        if(ner):
            return nlp.ner(sentence)
        else:
            return nlp.


    def orgPhraseChunking(self,ner):
	ent_list = []
	temp = []

	for entity in ner:
		if(entity[1] == 'ORGANIZATION'):
			temp.append(entity[0])
		else:
			if len(temp) > 0:
				ent_list.append(" ".join(temp))
				temp = []

	return ent_list

    def calculateFeature(self,text):
        feature = {}
        num_occur_text 
        num_occur_head
        ent_pos
        ent_type

    # def extractLoc(self,text):
        # sentence = self.extractNewsSentence(text)
        # ne_lists = {'LOCATION': [], 'DATE': [], 'TIME': [], 'TIME+DATE': []}

        # for sent in sentence:
        #     if 

ex = ExtractEntity()

text = "We investigated our 100 news articles to find out how the words of Altenberg are indicating a causal link to another event and at the same time are the reason of the event, which answers our question WHY. The outcome is a list of indicators and the number each indicator is located within the sentence describing the reason of the event."

print ex.extractNewsSentence(text)
