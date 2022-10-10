import datetime

import numpy as np

def convertDate(str_date, str_time):
    d, m, y = map(int, str_date.split(b'/'))
    h, mi, s = map(int, str_time.split(b':'))
    return int(datetime.datetime(y, m, d, h, mi, s).timestamp())

vagas = dict(zip([b'[Deputado Federal]', b'[Deputado Estadual]', b'[Senador]', b'[Governador]', b'[Presidente]'], range(5)))

i_time = 0
e_time = 0
c_tecl = 0

def process_log(lines, expected):
    result = np.empty((expected, 10), dtype="ubyte")
    t = 0
    i = 0
    for line in lines:
        fields  = line.strip().split(b'\t', maxsplit=5)
        c_date = fields[0].split()[0]
        c_time = fields[0].split()[1]
        c_type = fields[1]
        c_urna = fields[2]
        c_event = fields[3]
        c_data = fields[4]
        if c_event == b"VOTA":
            if b"Eleitor foi habilitado" in c_data:
                i = 0
                c_tecl = 0
                i_time = c_time
                v_time = c_time
                pass
            if b"O voto do eleitor foi computado" in c_data:
                if i == 10:
                    t += 1
                i = 0
                e_time = c_time
                i_time = 0
                e_time = 0
                pass
            if b"Voto confirmado para " in c_data:
                f_sec = convertDate(c_date, c_time) - convertDate(c_date, v_time)
                result[t][i] = min(255, f_sec)
                i += 1
                result[t][i] = min(255, c_tecl)
                i += 1
                v_time = c_time
                c_tecl = 0
            if b"Tecla indevida pressionada" in c_data:
                c_tecl += 1
    if not t:
        return None
    return result[0:t]
