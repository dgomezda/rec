import os
import dicttoxml
import fnmatch
from hashlib import sha1

def grabarXML(rutaDirectorio, nombre, *data):
    xml = dicttoxml.dicttoxml(data, custom_root='avisos', attr_type=False)
    rutaArchivo = rutaDirectorio + nombre + '.xml'
    f = open(rutaArchivo, 'w+')
    f.write(xml)
    f.close()


def LeerDirectorio(ruta=None):
    avisos = []
    extension = "mp3"
    for rutadir, nombredir, archivos in os.walk(ruta):
        for f in fnmatch.filter(archivos, "*.%s" % extension):
            p = os.path.join(rutadir, f)
            avisos.append((p, extension))
    return avisos


def ExtraerNombreArchivo(rutaArchivo):
    return os.path.splitext(os.path.basename(rutaArchivo))[0]


def ObtenerHashArchivo( rutaArchivo, blocksize=2 ** 20):
    s = sha1()
    with open(rutaArchivo, "rb") as f:
        while True:
            buf = f.read(blocksize)
            if not buf:
                break
            s.update(buf)
    return s.hexdigest().upper()