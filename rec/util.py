import os
import dicttoxml
import fnmatch
from hashlib import sha1
import json
import sys
RUTA_CONFIG = "app.config"


def GrabarXML(rutaDirectorio, nombre, *data):
    if len(data)>0:
        xml = dicttoxml.dicttoxml(data[0], custom_root='Huellas', attr_type=False)
        xml = xml.replace('item>','DataHuella>')
        rutaArchivo = rutaDirectorio + nombre + '.xml'
        f = open(rutaArchivo, 'w+')
        f.write(xml)
        f.close()

def GrabarArchivoHuella(rutaArchivo, iter):
    try:
        esPrimerElemento = True
        with open(rutaArchivo, 'w') as f:
            for x in iter:
                if esPrimerElemento:
                    esPrimerElemento = False
                else:
                    f.write(",")
                f.write(str(x))
    except ValueError:
        print("Ocurrio un error Grabando el archivo de huellas: %s. " % (str(ValueError)))
        return False
    return True


def LeerArchivoAFP(rutaArchivo):
    completo = False
    huellas = []
    try:
        with open(rutaArchivo, 'rb') as f:
            huellas = eval(f.read())
            completo = True
    except:
        print("Archivo de huellas no valido")
    return completo, huellas

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

def ExtraerTipoArchivo(rutaArchivo):
    return os.path.splitext(os.path.basename(rutaArchivo))[1]

def EliminarArchivo(rutaArchivo):
    os.remove(rutaArchivo);

def MoverArchivo(rutaArchivo, Directorio):
    resultFileName = Directorio + ExtraerNombreArchivo(rutaArchivo) + ExtraerTipoArchivo(rutaArchivo)
    try:
        os.remove(resultFileName)
    except OSError:
        pass
    os.rename(rutaArchivo, resultFileName)


def ObtenerHashArchivo( rutaArchivo, blocksize=2 ** 20):
    s = sha1()
    with open(rutaArchivo, "rb") as f:
        while True:
            buf = f.read(blocksize)
            if not buf:
                break
            s.update(buf)
    return s.hexdigest().upper()

def ObtenerConfiguracion():
    configpath = RUTA_CONFIG
    try:
        with open(configpath) as f:
            config = json.load(f)
    except IOError as err:
        print("Ocurrio un error leyendo el archivo de configuracion: %s. La ejecucion del programa ha concluido." % (str(err)))
        sys.exit(1)
    return config

def ObtenerMetaDatosdeArchivoHora(nombre):
    dict = {}
    completo = False
    try:
        metadato = nombre.split('_')
        dict['RegFecha'] = metadato[0].replace('-', '')
        dict['RegHora'] = metadato[1].replace('-', ':')
        dict['CiuCod'] = metadato[2]
        dict['MedCod'] = metadato[3]
        dict['TipMedCod'] = metadato[4]
        completo = True
    except :
        print("El archivo no tiene el nombre con el formato esperado, %s " % (str(nombre)))
        dict['RegFecha'] = ''
        dict['RegHora'] = ''
        dict['CiuCod'] = ''
        dict['MedCod'] = ''
        dict['TipMedCod'] = ''
    return completo, dict