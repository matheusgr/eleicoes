import io
import os
from zipfile import ZipFile
import random

import asn1crypto.core as asn1
import py7zr
import numpy as np

from rdv_resumo import EntidadeResultadoRDV
from log import process_log
import urna_group
import random

def simplifica_eleicao(resultados):
    final = [resultados["13"], resultados["22"], resultados["branco"], resultados["nulo"]]
    final.append(sum(resultados.values()) - sum(final))  # outros
    return final
    

def ler_rdv(encoded_rdv):
    resultado_rdv = EntidadeResultadoRDV.load(encoded_rdv)
    rdv = resultado_rdv["rdv"]
    eleicoes = rdv["eleicoes"].chosen
    resultados = {"13": 0, "22": 0, "branco": 0, "nulo" : 0}
    for eleicao in eleicoes:
        votos_cargos = eleicao["votosCargos"]
        for votos_cargo in votos_cargos:
            qtd = 0
            if ("Presidente" != votos_cargo['idCargo'].chosen.native):
                break
            votos = votos_cargo["votos"]
            for voto in votos:
                qtd += 1
                digitacao = voto["digitacao"]
                tipo = voto["tipoVoto"]  # nominal, branco, nulo
                if digitacao == asn1.VOID:
                    resultados["branco"] = resultados.get("branco", 0) + 1
                else:
                    if str(tipo.native) == 'nulo':
                        resultados["nulo"] = resultados.get('nulo', 0) + 1
                    else:
                        resultados[str(digitacao)] = resultados.get(str(digitacao), 0) + 1
    return simplifica_eleicao(resultados)



logs = []

brc = urna_group.prepare()
sample = None
    
sec = 0

for fname in os.listdir("urnas"):
    f_urna = "urnas" + os.sep + fname
    i = 0
    with ZipFile(f_urna) as myzip:
        print("....", f_urna)
        for zip_name in myzip.namelist():
            if not zip_name.endswith('rdv'):
                continue
            if random.randint(0, 1000) > 1:  # sample 1% of votes
                continue
            with myzip.open(zip_name) as myfile:
                # 13, 22, brancos/nulos, outros
                res_presidentes =  ler_rdv(myfile.read())
            logejz_name = zip_name.split('.')[0] + '.logjez'
            if logejz_name not in myzip.namelist():
                continue
            with py7zr.SevenZipFile(myzip.open(logejz_name)) as f_log:
                print(sec)
                sec += 1
                file_content = f_log.read('logd.dat')
                # [secao1, secao2, secao3, ...] --> secao1 = [v1, v2, v3, ...]
                resultados = process_log(file_content['logd.dat'])
                if resultados:
                    logs.append(resultados)
                # 5 cargos tempo/erros -> 1, 2, 3, 4, 5, 6, 7, 8, 9, 10
                if logs:
                    logs = np.concatenate([np.array(i) for i in logs])
                    urna_group.partial_fit(brc, logs)
                    if sample is None:
                        sample = logs[np.random.choice(logs.shape[0], 1)]
                    else:
                        # FIXME get one from sample
                        sample = np.concatenate((sample, logs[np.random.choice(logs.shape[0], 1)]))
                    logs = []

urna_group.count(brc, 20, sample)

# pstats.Stats('prof').sort_stats('tottime').reverse_order().print_stats()
