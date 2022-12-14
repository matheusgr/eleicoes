import joblib

import numpy as np
from sklearn.cluster import Birch
from sklearn.cluster import MiniBatchKMeans
from sklearn import metrics
from sklearn.datasets import make_blobs
from sklearn.preprocessing import StandardScaler


def prepare(n_clusters):
    brc = MiniBatchKMeans(n_clusters=n_clusters)
    return brc
    
def partial_fit(brc, X):
    brc.partial_fit(X)

def count(brc, X):
    labels = brc.labels_
    
    x_labels, x_counts = np.unique(labels[labels >= 0], return_counts=True)
    print(x_labels[np.argsort(-x_counts)[:3]])
    
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
    print(n_clusters_)
    n_clusters_ = np.unique(labels).size
    n_noise_ = list(labels).count(-1)
    
    print("Estimated number of clusters: %d" % n_clusters_)
    print("Estimated number of noise points: %d" % n_noise_)
    if X.any():
        labels = brc.predict(X)
        print("Silhouette Coefficient: %0.3f" % metrics.silhouette_score(X, labels))
    print("Cluster centers", brc.cluster_centers_)
    

def save(brc, fname='model'):
     joblib.dump(brc, fname + '.joblib') 

def load(fname):
    return joblib.load(fname)
