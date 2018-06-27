import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

def train(dataset,news_element,test):
    #classifier algorithm
    clf = RandomForestClassifier()

    # extract feature needed
    dataset = dataset.drop(['entity',news_element], axis=1)

    # convert categorical feature to numeric
    dataset['type'] = dataset['type'].map({'PERSON': 1, 'LOCATION': 2, 'ORGANIZATION': 3}).astype(int)
    dataset['occ_title'] = dataset['occ_title'].map({False: 0, True: 1}).astype(int)

    # determine wich column is feature or label
    X = dataset.iloc[:,:-1]
    y = dataset.iloc[:,-1]

    # training
    clf.fit(X, y)

    result = clf.predict([test])

    return result


df = pd.read_excel('test.xlsx', sheet_name='Sheet1')

# testing predicted value
test = np.array([1, 1, 1, 1])
who = train(df,'where',test)
where = train(df,'who',test)

print who
