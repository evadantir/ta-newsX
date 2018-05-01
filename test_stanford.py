# Simple usage
import logging
from stanfordcorenlp import StanfordCoreNLP

nlp = StanfordCoreNLP(r'./stanford-corenlp-full-2018-02-27', quiet=False, logging_level=logging.DEBUG)

sentence = 'Guangdong University of Foreign Studies is located in Guangzhou.'
print 'Tokenize:', nlp.word_tokenize(sentence)
print 'Part of Speech:', nlp.pos_tag(sentence)
print 'Named Entities:', nlp.ner(sentence)
print 'Constituency Parsing:', nlp.parse(sentence)
print 'Dependency Parsing:', nlp.dependency_parse(sentence)

nlp.close() # Do not forget to close! The backend server will consume a lot memery.

def extractNormalizedSentenceList(self, text):
    new_sent_list = []

    text = self.pre.normalizePunctuation(text)
    sent_list = sentence_extraction(text)
    sent_list = self.normalizeQuoteTokenization(sent_list)
    return sent_list