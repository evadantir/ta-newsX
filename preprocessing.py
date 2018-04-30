# -*- coding: utf-8 -*-
#credits to: ElSolrBeam
import string, re
import nltk
from nltk.collocations import *
from nltk import ngrams

class Preprocess():
	"""docstring for Preprocess"""
	def __init__(self):
		# self.stopword = map(str.strip, open("library/stopword.txt","r").readlines())
		pass

	# def eliminateStopword(self, string):
	# 	splitString = string.split()
	# 	result = []
	# 	for word in splitString:
	# 		if word not in self.stopword:
	# 			result.append(word)
	# 	return ' '.join(result)

	# def eliminatePunctuation(self, inputString, is_name=False):
		
	# 	if is_name == True:
	# 		punctuation = string.punctuation.replace("-","").replace("\'","")
	# 	else:
	# 		punctuation = string.punctuation.replace("-","")

	# 	for char in punctuation:
	# 		inputString = inputString.replace(char,"").replace("  "," ") # temporary spacing change

	# 	return inputString
		# return inputString.translate(None, string.punctuation.replace("-",""))

	# def tokenizeString(self, rawString):
	# 	return nltk.word_tokenize(self.eliminatePunctuation(rawString.lower()))
		# return nltk.word_tokenize(rawString)

	def customizeSub(self, matchObj):
		matchString = matchObj.group(0)
		if matchString == '.':
			return '. '
		elif matchString == '?':
			return '? '
		elif matchString == '!':
			return '! '
		elif matchString == '\"':
			return ' \"'

	def normalizePunctuation(self, text, is_entity=False):
		# normalize irregular apostrophe (regex should be splitted to prevent matching fails)
		text = re.sub(r'\“', '\"', text)
		text = re.sub(r'\”', '\"', text)
		text = re.sub(r'\’', '\'', text)

		# remove fckin unwanted characters
		text = re.sub(r'[^\x00-\x7f]',r'', text)

		if not is_entity:
			# give space to space one sentence with another
			text = re.sub(r'[\.?!\"](?=[A-Z0-9])', self.customizeSub, text)
			text = re.sub(r'\"(?=[a-z0-9])', '\" ', text)

			# swap the '.' and '"' to any direct sentences so that the sentence could be splitted easily
			text = re.sub(r'(?<=\w)\.\"', '".', text)

		return text

# p = Preprocess()
# # print p.eliminatePunctuation(p.eliminateStopword("Sebuah foto suasana copilot salah satu maskapai Indonesia, Sarah Widyanti Kusuma menjadi viral di media sosial. Dalam foto ini ditampilkan kopilot sedang melakukan ibadah shalat di dalam kokpit pesawat. Foto yang diunggah oleh kapten pilot melalui akun facebooknya menuai banyak pujian."))

# raw = "Sebuah foto suasana copilot salah satu maskapai Indonesia, Sarah Widyanti Kusuma menjadi viral di media sosial. Dalam foto ini ditampilkan kopilot sedang melakukan ibadah shalat di dalam kokpit pesawat. Foto yang diunggah oleh kapten pilot melalui akun facebooknya menuai banyak pujian."

# tokens = p.tokenizeString(raw)

# # Create your bigrams
# bgs = nltk.bigrams(tokens)

# # Create your trigrams
# tgs = nltk.trigrams(tokens)

# #compute frequency distribution for all the bigrams in the text
# fdist = nltk.FreqDist(bgs)
# ngram = list(fdist.items())
# ngram.sort(key=lambda item: item[-1], reverse=True)

# for k,v in ngram:
# 	print k,v