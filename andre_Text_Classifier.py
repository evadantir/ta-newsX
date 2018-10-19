from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics import f1_score
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import StratifiedKFold
from sklearn.feature_extraction import stop_words
from nltk.corpus import stopwords

import re, sys, pickle
import numpy as np
import pandas as pd

FOLD = 10
random_state = 2
stopwords_list = None
max_df_treshold = 1.0
min_df_treshold = 1

def main():
    mode = None

    if len(sys.argv) == 2:
        mode = sys.argv[1]
    else:
        print "Dataset name and random state must be entered!"
        exit(1)
    
    # Load preprocessed data from csv file
    documents, labels = load_dataset('dataset.csv')

    global stopwords_list
    global max_df_treshold
    global min_df_treshold

    # Configure stopword removal procedure
    if mode == 'tf-high':
        print 'Load tf-high stopword list'
        stopwords_list = load_stop_list('./stoplist/tf_stoplist_26.txt')
    elif mode == 'tf-1':
        print 'Load tf-high stopword list'
        stopwords_list = load_stop_list('./stoplist/tf1_stoplist.txt')
    elif mode == 'idf-low':
        print 'Load idf-low stopword list'
        stopwords_list = load_stop_list('./stoplist/idf_stoplist_300.txt')
        # max_df_treshold = 0.2
    elif mode == 'df-1':
        min_df_treshold = 2
    elif mode == 'mi-low':
        print 'Load mi-low stopword list'
        stopwords_list = load_stop_list('./stoplist/mi_stoplist.txt')
    elif mode == 'classic':
        print 'Load classic stopword list'
        stopwords_list = [word for word in stop_words.ENGLISH_STOP_WORDS]
        # stopwords_list = stopwords.words('english')
        # stopwords_list = load_stop_list('./stoplist/klasik_stoplist_vr.txt')

    if stopwords_list != None:
        print "Stopword number: ", len(stopwords_list)
    
    kfold_cross_validation(documents, labels, mode)

# Load dataset from a file and convert it to array. The dataset must be in csv file format
def load_dataset(file_name):
    data = pd.read_csv(file_name, encoding = 'utf8')
    contents = np.array(data['news'].tolist())
    labels = np.array(data['type'].tolist())
    return (contents, labels)

# Load stop words list from a file and convert it to array. The stop word list must be ini txt file format
def load_stop_list(file_name):
    with open(file_name) as buffer:
        data = [line.rstrip('\n') for line in buffer]
        return data

def kfold_cross_validation(data, label, mode):
    iteration = 0
    fold_list = []
    f1_list = []
    dimension_list = []
    memory_used = []
    
    stratified_kfold = StratifiedKFold(n_splits=FOLD, shuffle=True, random_state=random_state)
    for train_index, test_index in stratified_kfold.split(data, label):
        data_train, data_test = data[train_index], data[test_index]
        label_train, label_test = label[train_index], label[test_index]
        
        iteration += 1
        print "\nIteration: ", iteration

        # Train model using data training
        model =  train_classifier(data_train, label_train, stopwords_list, max_df_treshold, min_df_treshold)
        
        # Test model using data test
        prediction = model.predict(data_test)
        
        # Evaluate model
        f1 = f1_score(label_test, prediction, average='micro')
        dimension = get_dimension_size(model.named_steps['vectorizer'])
        memory_size = get_memory_usage(data_train)

        print "F1-measure (micro-average): {:.8f}".format(f1)
        print "Number of document and feature: ", dimension
        print "Memory used by term-document matrix: {} byte(s)".format(memory_size)

        fold_list.append(iteration)
        f1_list.append(f1)
        dimension_list.append(dimension)
        memory_used.append(memory_size)
    
    # Save measurement result to excel file (.xlsx file)
    data_to_save = {'fold': fold_list, 'f-measure': f1_list, 'dimension': dimension_list, "memory usage": memory_used}
    file_name = './result/' + mode + '.xlsx'
    save_to_xlsx_file(file_name, data_to_save)

def train_classifier(data_training, label_training, stopwords_list, max_df_treshold, min_df_treshold):
    from sklearn.pipeline import Pipeline
    # vectorizer will create feature vector from list of filtered token (term)
    # transformer will calculate weight for each term based on term frequency and inverse document frequency
    # lowercase, remove punctuation, remove stop words, tokenization, tf-idf weighting
    model = Pipeline([('vectorizer', TfidfVectorizer(norm=None, token_pattern=r"(?u)\b[\w\-\'\.\/\\\:]+\w\b", stop_words=stopwords_list,
    max_df=max_df_treshold, min_df=min_df_treshold)), ('classifier', MultinomialNB())])

    model.fit(data_training, label_training)

    return model

# Get size of dimension of data train
def get_dimension_size(vectorizer):
    return len(vectorizer.get_feature_names())

# Get size of used memory (term document matrix)
def get_memory_usage(data):
    vectorizer = TfidfVectorizer(norm=None, token_pattern=r"(?u)\b[\w\-\'\.\/\\\:]+\w\b", stop_words=stopwords_list,
    max_df=max_df_treshold, min_df=min_df_treshold)
    tdm = vectorizer.fit_transform(data)

    return tdm.data.nbytes + tdm.indptr.nbytes + tdm.indices.nbytes

# Get size of model
def get_model_size(model):
    p = pickle.dumps(model)
    return sys.getsizeof(p)

# Save file to xlsx format type
def save_to_xlsx_file(file_name, data_to_save):
    writer = pd.ExcelWriter(file_name)
    data_frame = pd.DataFrame(data_to_save)
    data_frame.to_excel(writer,'Measurement Result', 
    columns=['fold', 'f-measure', 'dimension', 'memory usage'], index=False)
    print "save result to file ", file_name
    writer.save()

main()