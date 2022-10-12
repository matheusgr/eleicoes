import collections
import os
from zipfile import ZipFile
import random

import py7zr
import numpy as np

from rdv_resumo import ler_rdv, normaliza_eleicao
from log import process_log

import urna_classifier
import urna_group


def get_logejz(zip_name, myzip):
    if not zip_name.endswith('rdv'):
        return
    if random.random() >= 0.01:
        return
    logejz_name = zip_name[:-3] + 'logjez'
    try:
        return myzip.open(logejz_name)
    except KeyError:
        return  # dont read RDV without logejz


def get_sample(sample, logs):
    if sample is None:
        return logs[np.random.choice(logs.shape[0], 1)]
    else:
        return np.concatenate((sample, logs[np.random.choice(logs.shape[0], 1)]))    


def read_logs(logejz_file, num_votos):
    f_log = py7zr.SevenZipFile(logejz_file)
    file_content = f_log.read('logd.dat')
    return process_log(file_content['logd.dat'], num_votos)


def process_logs(action, sampling=True):
    sample = None
    for fname in os.listdir("urnas"):
        f_urna = "urnas" + os.sep + fname
        with ZipFile(f_urna) as myzip:
            print("....", f_urna)
            for zip_name in myzip.namelist():
                logejz_file = get_logejz(zip_name, myzip)
                if logejz_file is None:
                    continue
                with myzip.open(zip_name) as myfile:
                    # 13, 22, brancos/nulos, outros
                    res_presidentes, num_votos =  ler_rdv(myfile.read())
                logs = read_logs(logejz_file, num_votos)
                if logs is not None:
                    action(logs, res_presidentes)
                    if sampling:
                        sample = get_sample(sample, logs)
    return sample


# PREPARE CLUSTERING
def prepare_clustering():
    brcs = [urna_group.prepare(x) for x in range(6,18)]
    prepare_classifier = lambda logs, _: [urna_group.partial_fit(brc, logs) for brc in brcs]
    sample = process_logs(prepare_classifier)
    for i, brc in enumerate(brcs):
        urna_group.count(brc, sample)
        urna_group.save(brc, 'model-' + str(i))


# TRAIN NEURAL NETWORK
def train_neural(model_name):
    brc = urna_group.load(model_name)
    clf = urna_classifier.prepare()
    test_x = []
    test_y = []
    def prepare_base(logs, rdv):
        res = brc.predict(logs)
        res_c = collections.Counter(res)
        rdv = normaliza_eleicao(rdv)
        i_layer = [res_c.get(x, 0) for x in range(10)]
        if random.randint(0,10) > 8:
            # test
            test_x.append(i_layer),
            test_y.append(rdv[1])
        else:
            urna_classifier.partial_fit(clf, [i_layer], [rdv[0]])
    process_logs(prepare_base, False)
    for x, y in zip(clf.predict(test_x), test_y):
        print(x, y)
    urna_group.save(clf, 'nn')


#prepare_clustering()
train_neural('model-11.joblib')