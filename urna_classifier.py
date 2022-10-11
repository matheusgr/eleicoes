from sklearn.neural_network import MLPClassifier

def prepare():
    clf = MLPClassifier(solver='adam', alpha=1e-5, random_state=1)
    return clf
    
def partial_fit(clf, X, y):
    #print(X, y, list(range(0,101)))
    clf.partial_fit(X, y, classes=list(range(0,101)))

def test(clf, X, y):
    return clf.score(X, y)
