from huellas import obtenerHuellas

DEFAULT_WINDOW_SIZE = 4096
DEFAULT_OVERLAP_RATIO = 0.5
DEFAULT_HIT_MIN = 10
FACTOR_OFFSET = 1

def _recognize( db, fs , *data):
    matches = []
    for d in data:
        matches.extend(find_matches(db, d, fs))
    return align_matches(db, matches , fs)


def find_matches(db, samples, fs):
    hashes = obtenerHuellas(samples, fs)
    return db.return_matches(hashes)


def align_matches(db, matches, fs):
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
        dic = value;
        for key1, value1 in dic.iteritems():
            if value1 > DEFAULT_HIT_MIN:
                aviso = db.obtenerAviso(key1)
                nseconds = round(float(key) / fs *
                                 DEFAULT_WINDOW_SIZE *
                                 DEFAULT_OVERLAP_RATIO *
                                 FACTOR_OFFSET, 5)
                avisoRec = {
                    'avisoId': key1,
                    'nombre': aviso.get('nombre', None),
                    'Inicio': nseconds,
                    'duracion': aviso.get('duracion', None),
                }
                listaAvisoRec.append(avisoRec)
    return listaAvisoRec