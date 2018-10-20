from sklearn.model_selection import StratifiedKFold

FOLD = 10

def stratifiedKFold(data,X,y):
    iteration = 0
    fold_list = []
    f1_list = []
    
    stratified_kfold = StratifiedKFold(n_splits = FOLD)
    for train, test in stratified_kfold.split(X,y):
        print("%s %s" % (train, test))