# -*- coding: utf-8 -*-
from stanfordcorenlp import StanfordCoreNLP
from preprocessing import Preprocess

class Find5W1H(object):
    
    def __init__(self):
        self.pre = Preprocess()
    def extractDateFromText(self,data):
        list_date = []

        for ner in data:
            date = []
            for sent in ner:
                if sent["ner"] == 'DATE':
                    date.append(sent["word"])
                else:
                    if date != []:
                        list_date.append(' '.join(date))
                        date = []

        list_date = self.sieveSubstring(list_date)
        return list_date

fd = Find5W1H()

text = "We investigated our 100 news articles to find out how the words of Altenberg are indicating a causal link to another event and at the same time are the reason of the event, which answers our question WHY. The outcome is a list of indicators and the number each indicator is located within the sentence describing the reason of the event."


