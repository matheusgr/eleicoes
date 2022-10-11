import datetime

import numpy as np

def convertDate(str_date, str_time):
    return (int(str_time[0:2]) * 3600) + (int(str_time[3:5]) * 60) + int(str_time[6:8])


vagas = dict(zip([b'[Deputado Federal]', b'[Deputado Estadual]', b'[Senador]', b'[Governador]', b'[Presidente]'], range(5)))

i_time = 0
e_time = 0
c_tecl = 0

LEN_SIZE = 11

def process_log(lines, expected):
    result = np.empty((expected * 5, LEN_SIZE), dtype="ubyte")
    t = 0
    i = 0
    for line in lines:
        fields  = line.split(b'\t', maxsplit=5)
        c_date = fields[0][0:9]
        c_time = fields[0][11:20]
        c_type = fields[1]
        c_urna = fields[2]
        c_event = fields[3]
        c_data = fields[4]
        if c_event == b"VOTA":
            if b"Voto confirmado para " in c_data:
                f_sec = convertDate(c_date, c_time) - convertDate(c_date, v_time)
                if i == LEN_SIZE:
                    continue  # Conselheiro digital para algumas urnas
                result[t][i] = min(30, f_sec)/30.0
                i += 1
                result[t][i] = min(5, c_tecl)/5.0
                i += 1
                v_time = c_time
                c_tecl = 0
            elif b"Eleitor foi habilitado" in c_data:
                i = 0
                result[t][i] = max(0, min(10, (int(c_time[0:2]) - 8)))/10.0  # tempo
                i += 1
                c_tecl = 0
                i_time = c_time
                v_time = c_time
                pass
            elif b"O voto do eleitor foi computado" in c_data:
                if i == LEN_SIZE:
                    t += 1
                i = 0
                e_time = c_time
                i_time = 0
                e_time = 0
                pass
            elif b"Tecla indevida pressionada" in c_data:
                c_tecl += 1
    if not t:
        return None
    return result[0:t]
