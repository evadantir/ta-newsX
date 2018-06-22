# Simple usage
from stanfordcorenlp import StanfordCoreNLP
import logging

nlp = StanfordCoreNLP(r'./stanford-corenlp-full-2018-02-27',memory='5g')
# text = 'My sister has a friend called John. Really, tell me more about him? She think he is so funny!'
# text = "Microsoft is a company built by Bill Gates. It has a lot of branch all over the world"
# text_blah = []

sentence = 'Guangdong University of Foreign Studies is located in Guangzhou.'
print 'Constituency Parsing:', nlp.parse(sentence)

# text_blah = {
# 				'text' : text,
# 				'ner': ner,
# 				'coref': coref
# 			}

# joblib.dump(text_blah, 'text_blah.pkl')	

nlp.close() # Do not forget to close! The backend server will consume a lot memory.
