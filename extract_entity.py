# -*- coding: utf-8 -*-

from tokenization import *

class ExtractEntity(object):

    def extractNewsSentence(self,text):
        return sentence_extraction(text);

ex = ExtractEntity()

text = "We investigated our 100 news articles to find out how the words of Altenberg are indicating a causal link to another event and at the same time are the reason of the event, which answers our question WHY. The outcome is a list of indicators and the number each indicator is located within the sentence describing the reason of the event."

print ex.extractNewsSentence(text)
