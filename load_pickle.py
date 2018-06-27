from pprint import pprint
import joblib

blah = joblib.load('nlp_object/cnn_1.pkl')
# pprint(blah)
print blah['coref']
for cf in blah['coref']:
    print cf['main']