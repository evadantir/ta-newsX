# Simple usage
# import logging
from stanfordcorenlp import StanfordCoreNLP

def phraseChunking(ner):
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

nlp = StanfordCoreNLP(r'./stanford-corenlp-full-2018-02-27')
text = "Ethiopian Airlines is expectingto kick off its inaugural direct flight connecting Jakarta and Addis Ababanext month. Foreign Minister Retno LP Marsudi met with Ethiopian AirlinesCEOTewolde Gebremariam on the sidelines of the Indonesia-Africa Forum in Nusa Dua, Bali, on Wednesday. We talked about connectivity because it matters in supporting economic, tradeand people-to-people cooperation, said Retno after the meeting. Hence, the agreement on the direct flight is a breakthrough for Indonesia-Africa economic ties,she added. Retno further said a lack of connectivity had been an issue that hindered Indonesia and Africa from boostingtrade and investment cooperation. In the meeting, I also expressed our interest to designateAddis Ababa as the hub of Indonesias visa services for other African countries, the minister said. Retno also suggestedEthiopian Airlinescooperate with national flag carrier Garuda Indonesia for maintenance services. Separately, Indonesian Ambassador to Ethiopia Imam Santosa said the Jakarta-Addis Ababa direct flight would likely kick off within a month or two, depending on the progress of technical preparations. It depends on technical readiness, like offices, partnerships for catering services and airport facilities, he said. Once they are ready, the flights can start. Ethiopian Airlines plans to provide the direct flightthree times a week via Bangkok. (ebf)"
sentence = 'Monas is located in Jakarta.'
# print 'Tokenize:', nlp.word_tokenize(sentence)
# print 'Part of Speech:', nlp.pos_tag(sentence)
ner = nlp.ner(text)
print ner
print phraseChunking(ner)
# print 'Constituency Parsing:', nlp.parse(sentence)
# print 'Dependency Parsing:', nlp.dependency_parse(sentence)
# print 'Coreference:',nlp.coref(sentence)

nlp.close() # Do not forget to close! The backend server will consume a lot memory.
