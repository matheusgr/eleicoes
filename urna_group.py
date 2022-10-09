import numpy as np


from sklearn.cluster import Birch
from sklearn.cluster import MiniBatchKMeans
from sklearn import metrics
from sklearn.datasets import make_blobs
from sklearn.preprocessing import StandardScaler

def prepare():
    brc = MiniBatchKMeans(n_clusters=40)
    #brc = Birch()
    return brc
    
def partial_fit(brc, X):
    brc.partial_fit(X)

def count(brc, clusters, X):
    #brc.set_params(n_clusters=clusters)
    #brc.partial_fit()
    labels = brc.labels_
    
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
    
