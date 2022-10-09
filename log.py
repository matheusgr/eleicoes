import datetime

def convertDate(str_date, str_time):
    d, m, y = map(int, str_date.split(b'/'))
    h, mi, s = map(int, str_time.split(b':'))
    return int(datetime.datetime(y, m, d, h, mi, s).timestamp())

vagas = dict(zip([b'[Deputado Federal]', b'[Deputado Estadual]', b'[Senador]', b'[Governador]', b'[Presidente]'], range(5)))

i_time = 0
e_time = 0
c_tecl = 0

def process_log(lines):
    results = [[]]
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
                if len(results[-1]) != 10:
                    results.pop()
                results.append([])
                c_tecl = 0
                i_time = c_time
                v_time = c_time
                pass
            if b"O voto do eleitor foi computado" in c_data:
                if len(results[-1]) != 10:
                    results.pop()
                results.append([])
                e_time = c_time
                i_time = 0
                e_time = 0
                pass
            if b"Voto confirmado para " in c_data:
                #print(vagas[c_data.split(maxsplit=3)[3]], convertDate(c_date, c_time) - convertDate(c_date, v_time), ';', end='')
                f_sec = convertDate(c_date, c_time) - convertDate(c_date, v_time)
                results[-1].append(255 if f_sec > 255 else f_sec)
                results[-1].append(c_tecl)
                v_time = c_time
                c_tecl = 0
            if b"Tecla indevida pressionada" in c_data:
                c_tecl += 1
    if len(results[-1]) != 10:
        results.pop()
    return results
