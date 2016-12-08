from huellas import obtenerHuellas

def reconocer( db, fs,  windowSize, overlap, hitMin, factorOffset , *data):
    coincidencias = []
    for d in data:
        coincidencias.extend(buscar_coincidencia(db, d, fs, windowSize, overlap))
    return alinear_horario(db, coincidencias , fs, windowSize, overlap, hitMin, factorOffset)

def buscar_coincidencia(db, samples, fs,  windowSize, overlap):
    hashes = obtenerHuellas(samples, fs,  windowSize, overlap)
    return db.return_matches(hashes)

def alinear_horario(db, matches, fs, windowSize, overlap, hitMin, factorOffset):
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
                avisoRec = {
                    'avisoId': key1,
                    'nombre': aviso.get('nombre', None),
                    'Inicio': nseconds,
                    'duracion': aviso.get('duracion', None),
                }
                listaAvisoRec.append(avisoRec)
    return listaAvisoRec