# -*- coding: utf-8 -*-
#credits to: ElSolrBeam
import string, re
import nltk
from tokenization import *

class Preprocess():

    def removeWhitespaces(self,text):
        temp = text.strip()
        return " ".join(temp.split())

    def eliminatePunctuation(self, inputString, is_name=False):
        
        if is_name == True:
            punctuation = string.punctuation.replace("-","").replace("\'","")
        else:
            punctuation = string.punctuation.replace("-","")

        for char in punctuation:
            inputString = inputString.replace(char,"").replace("  "," ") # temporary spacing change

        return inputString
        return inputString.translate(None, string.punctuation.replace("-",""))

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
        text = self.removeWhitespaces(text)

        if not is_entity:
            # give space to space one sentence with another
            text = re.sub(r'[\.?!\"](?=[A-Z0-9])', self.customizeSub, text)
            text = re.sub(r'\"(?=[a-z0-9])', '\" ', text)

            # swap the '.' and '"' to any direct sentences so that the sentence could be splitted easily
            text = re.sub(r'(?<=\w)\.\"', '".', text)

        return text

    # Remove element which is a substring to other element, e.g. [Novanto, Setya Novanto, Prabowo]
    def sieveSubstring(self, string_list):
        string_list.sort(key=lambda s: len(s), reverse=True)
        out = []
        for s in string_list:
            if not any([s in o for o in out]):
                out.append(s)
        return out

    # remove duplicate value in list of entities
    def removeDuplicateListDict(self,listdict):
        seen = set()
        new_list = []
        for dictionary in listdict:
            t = tuple(dictionary.items())
            if t not in seen:
                seen.add(t)
                new_list.append(dictionary)

        return new_list

    def joinText(self,list_text):
        import string

        text = ""
        for t in list_text:
            if not text:
                text = t
            elif t in string.punctuation:
                text += t
            else:
                text += " " + t
        return text

p = Preprocess()