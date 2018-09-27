# import re
# import string

# candidate = [u'October', u'29', u',', u'2016']

# text = ""
# for c in candidate:
#     if not text:
#         text = c
#     elif c in string.punctuation:
#         text += c
#     else:
#         text += " " + c

# print text
# exit()

# candidate = "October 29, 2016"

# sent = u"pic.twitter.com/C2VD3DjppE -- Alana Cartwright (@AlanaCartwrigh3) October 29, 2016  @HelenRyles Hi Helen, yes this is just our smaller bar."

# match = re.search(candidate.lower(),sent.lower())
# print match.group()

from stanfordcorenlp import StanfordCoreNLP
from nltk.tokenize import sent_tokenize 
# import json
# to run server: java --add-modules java.se.ee -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000 -timeout 15000
nlp = StanfordCoreNLP('http://localhost', port=9000)
# nlp = StanfordCoreNLP(r'stanford-corenlp-full-2018-02-27',quiet=False)
# props = {'annotators': 'coref', 'pipelineLanguage': 'en', 'outputFormat': 'text'}
# text = ('GOP Sen. Rand Paul was assaulted in his home in Bowling Green, Kentucky, on Friday, '
#         'according to Kentucky State Police. State troopers responded to a call to the senator\'s '
#         'residence at 3:21 p.m. Friday. Police arrested a man named Rene Albert Boucher, who they '
#         'allege "intentionally assaulted" Paul, causing him "minor injury". Boucher, 59, of Bowling '
#         'Green was charged with one count of fourth-degree assault. As of Saturday afternoon, he '
#         'was being held in the Warren County Regional Jail on a $5,000 bond.')
# text = "My sister has a friend called John. Really, tell me more about him? She think he is so funny!"
# hehe =  nlp.coref(text)
text = "A girl named Kendall Jenner praises Manchester's 'incredible resilience' after bombing. Jenner said it because she thinks that they will never going to let anyone forget about those victims"
# print hehe

# sent = sent_tokenize(text)
# print(text)
# for s in sent:
#     print(nlp.ner(s))
data = nlp.coref(text)

print(data[0][0][3])
nlp.close()

# result = json.loads(nlp.annotate(text, properties=props))
# num, mentions = result['corefs'].items()[0]
# for mention in mentions:
#     print(mention)
# print(result)
# nlp.close()


# from pynlp import StanfordCoreNLP

# annotators = 'tokenize, ssplit, pos, lemma, ner, entitymentions, coref, sentiment, quote, openie'
# options = {'openie.resolve_coref': True}

# nlp = StanfordCoreNLP(annotators=annotators, options=options)
# document = nlp(text)

# chain = document.coref_chains[0]
# print(chain)