from pprint import pprint
import joblib

blah = joblib.load('text_blah.pkl')
pprint(blah)
# for bh in blah['ner']:
#     if bh[0] == 'Really':
#         print bh