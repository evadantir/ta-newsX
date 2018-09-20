import re
import string

candidate = [u'October', u'29', u',', u'2016']

text = ""
for c in candidate:
    if not text:
        text = c
    elif c in string.punctuation:
        text += c
    else:
        text += " " + c

print text
exit()

candidate = "October 29, 2016"

sent = u"pic.twitter.com/C2VD3DjppE -- Alana Cartwright (@AlanaCartwrigh3) October 29, 2016  @HelenRyles Hi Helen, yes this is just our smaller bar."

match = re.search(candidate.lower(),sent.lower())
print match.group()