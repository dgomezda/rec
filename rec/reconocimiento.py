from huellas import obtenerHuellas
import datetime

def reconocer( db, fs,  windowSize, overlap, hitMin, factorOffset, metadatoHora , *hashes):
    coincidencias = []
    coincidencias.extend(db.return_matches(hashes[0]))
    return alinear_horario(db, coincidencias , fs, windowSize, overlap, hitMin, factorOffset, metadatoHora)


def alinear_horario(db, matches, fs, windowSize, overlap, hitMin, factorOffset, metadatoHora):
    CodOrd = 0
    diff_counter = {}
    listaAvisoRec = []
    for tup in matches:
        sid, diff = tup
        if diff not in diff_counter:
            diff_counter[diff] = {}
        if sid not in diff_counter[diff]:
            diff_counter[diff][sid] = 0
        diff_counter[diff][sid] += 1
    for key, value in diff_counter.iteritems():
        dic = value
        for key1, value1 in dic.iteritems():
            if value1 > hitMin:
                aviso = db.obtenerAviso(key1)
                nseconds = round(float(key) / fs *
                                 windowSize *
                                 overlap *
                                 factorOffset, 5)
                varFecha = metadatoHora.get('RegFecha', '19000101')
                varhora = metadatoHora.get('RegHora', '000000')
                varduracion = aviso.get('duracion', 0)
                CodOrd = CodOrd + 1
                regHoraIni = datetime.datetime.strptime(varFecha + varhora, '%Y%m%d%H:%M:%S') + datetime.timedelta(seconds=nseconds)
                regHoraFin = regHoraIni + datetime.timedelta(seconds=varduracion)
                avisoRec = {
                    'CodOrd': CodOrd,
                    'nombre': aviso.get('nombre', None),
                    'CiuCod': metadatoHora.get('CiuCod', None),
                    'MedCod': metadatoHora.get('MedCod', None),
                    'RegHoraIni': regHoraIni.strftime("%d/%m/%y %H:%M:%S"),
                    'RegHoraFin': regHoraFin.strftime("%d/%m/%y %H:%M:%S"),
                    'RegDuracion': varduracion,
                    'RegFecha': metadatoHora.get('RegFecha', None),
                    'TipoMedCod': metadatoHora.get('MedCod', None),
                }
                listaAvisoRec.append(avisoRec)
    return listaAvisoRec