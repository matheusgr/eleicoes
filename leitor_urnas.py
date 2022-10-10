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

brcs = [urna_group.prepare(x) for x in range(2,14)]
sample = None

for fname in os.listdir("urnas"):
    f_urna = "urnas" + os.sep + fname
    i = 0
    with ZipFile(f_urna) as myzip:
        print("....", f_urna)
        for zip_name in myzip.namelist():
            if not zip_name.endswith('rdv'):
                continue
            #if random.randint(0, 10) > 1:  # sample 10% of votes
            #    continue
            logejz_name = zip_name[:-3] + 'logjez'
            try:
                my_file = myzip.open(logejz_name)
            except:
                continue  # dont read RDV without logejz
            with myzip.open(zip_name) as myfile:
                # 13, 22, brancos/nulos, outros
                res_presidentes =  ler_rdv(myfile.read())
            f_log = py7zr.SevenZipFile(my_file)
            file_content = f_log.read('logd.dat')
            # [secao1, secao2, secao3, ...] --> secao1 = [v1, v2, v3, ...]
            resultados = process_log(file_content['logd.dat'], sum(res_presidentes))
            # 5 cargos tempo/erros -> 1, 2, 3, 4, 5, 6, 7, 8, 9, 10
            if not resultados is None:
                logs = resultados
                for brc in brcs:
                    urna_group.partial_fit(brc, logs)
                if sample is None:
                    sample = logs[np.random.choice(logs.shape[0], 1)]
                else:
                    # FIXME get one from sample
                    sample = np.concatenate((sample, logs[np.random.choice(logs.shape[0], 1)]))
                logs = []

for i, brc in enumerate(brcs):
    urna_group.count(brc, sample)
    urna_group.save(brc, 'model-' + str(i))

# 2 0.745
# 3 0.597
# 4 0.526
# 5 0.206
# 6 0.288
# 8  0.246
# 10 0.234
# 12 

# pstats.Stats('prof').sort_stats('tottime').reverse_order().print_stats()
# python -m cProfile -o prof leitor_urnas.py
