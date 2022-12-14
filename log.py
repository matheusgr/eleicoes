import datetime

import numpy as np

def convert_date(str_time):
    return (int(str_time[0:2]) * 3600) + (int(str_time[3:5]) * 60) + int(str_time[6:8])


vagas = dict(zip([b'[Deputado Federal]', b'[Deputado Estadual]', b'[Senador]', b'[Governador]', b'[Presidente]'], range(5)))

i_time = 0
e_time = 0
c_tecl = 0

LEN_SIZE = 10

def process_log(lines, expected):
    result = np.empty((expected * 5, LEN_SIZE), dtype="float")
    t = 0
    i = 0
    for line in lines:
        fields  = line.split(b'\t', maxsplit=5)
        c_time = fields[0][11:20]
        c_event = fields[3]
        c_data = fields[4]
        if c_event == b"VOTA":
            if b"Voto confirmado para " in c_data:
                if i == LEN_SIZE:
                    continue  # Conselheiro distrital ou outros cargos para algumas urnas
                f_sec = convert_date(c_time) - convert_date(v_time)
                result[t][i] = min(60, f_sec)/60.0
                result[t][i + 1] = min(5, c_tecl)/5.0
                i += 2
                v_time = c_time
                c_tecl = 0
            elif b"Eleitor foi habilitado" in c_data:
                i = 0
                c_tecl = 0
                v_time = c_time
            elif b"O voto do eleitor foi computado" in c_data:
                if i == LEN_SIZE:
                    t += 1
                i = 0
            elif b"Tecla indevida pressionada" in c_data:
                c_tecl += 1
    if not t:
        return None
    return result[0:t]
