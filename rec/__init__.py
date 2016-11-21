import os
from rec.util import grabarXML, LeerDirectorio, ExtraerNombreArchivo, ObtenerHashArchivo
from rec.huellas import obtenerHuellas
from rec.reconocimiento import _recognize

import warnings
import multiprocessing
warnings.filterwarnings("ignore")
from rec.util import grabarXML

#leerArchivo
from pydub import AudioSegment
import numpy as np


from rec.database import Database


class Rec(object):
    AVISO = 1
    HORA = 2
    DIR_AVISO = "audios/avisos/"
    DIR_HORA = "audios/horas/"
    DIR_AVISO_PROCESADOS = "baseconocimiento/"

    DEFAULT_WINDOW_SIZE = 4096
    DEFAULT_OVERLAP_RATIO = 0.5
    DEFAULT_HIT_MIN  = 10

    FACTOR_OFFSET = 1

    #BD
    BD_HOST = "127.0.0.1"
    BD_USER = "root"
    BD_PASSWD = "toor"
    BD_ID = "ironrec"
    BD_PORT = 3311

    def __init__(self):
        self.db = Database(user=self.BD_USER, passwd=self.BD_PASSWD, host = self.BD_HOST, db = self.BD_ID, port = self.BD_PORT  )
        print "Inicializando..."

    def ResetBD(self):
        self.db.limpiar()

    def ProcesarDirectorio(self):
        avisos = LeerDirectorio(self.DIR_AVISO)
        contadorAviso = 1
        for aviso in avisos:
            print "%d.- aprendiendo aviso : %s" % (contadorAviso, aviso[0])
            self.aprenderAviso(aviso[0])
            contadorAviso += 1

    def LeerArchivo(self, rutaArchivo):
        contenido = AudioSegment.from_file(rutaArchivo)
        data = np.fromstring(contenido._data, np.int16)
        channels = []
        for chn in xrange(contenido.channels):
            channels.append(data[chn::contenido.channels])
        fs = contenido.frame_rate
        return channels, contenido.frame_rate, ObtenerHashArchivo(rutaArchivo), contenido.duration_seconds

    def aprenderAviso(self, rutaAviso, nombreAviso=None): #fingerprint_file
        nombre = ExtraerNombreArchivo(rutaAviso)
        nombre = nombreAviso or nombre
        nombre, hashes, hashArchivo, duracion = self.ProcesarHuellas(
            rutaAviso,
            nombre
        )
        avisoId = self.db.insert_aviso(nombre, hashArchivo, duracion)

        self.db.insert_hashes(avisoId, hashes)
        self.db.marcar_aviso_procesado(avisoId)

    def ProcesarHuellas(self, archivo, nombreAviso=None): #_fingerprint_worker

        nombre, extension = os.path.splitext(os.path.basename(archivo))
        nombre = nombreAviso or nombre
        channels, Fs, hashArchivo, duracion = self.LeerArchivo(archivo)
        result = set()
        channel_amount = len(channels)

        for channeln, channel in enumerate(channels):
            hashes = obtenerHuellas(channel, Fs=Fs)
            result |= set(hashes)
        return nombre, result, hashArchivo, duracion

    def obtenerAvisosAprendidos(self):
        # get songs previously indexed
        self.avisos = self.db.get_avisos()
        self.avisos_set = set()
        for aviso in self.avisos:
            hashArchivo = aviso['sha1']
            self.avisos_set.add(hashArchivo)

    def reconocerDirectorio(self, ruta):
        rec = Rec()
        rutaAvisos = []
        for rutaArchivo, ext in LeerDirectorio(ruta):
            rutaAvisos.append(rutaArchivo)
        nprocesses = None
        try:
            nprocesses = nprocesses or multiprocessing.cpu_count()
        except NotImplementedError:
            nprocesses = 1
        else:
            nprocesses = 1 if nprocesses <= 0 else nprocesses

        pool = multiprocessing.Pool(nprocesses)
        #print reconocerArchivo(rutaAvisos[0])
        iterator = pool.imap_unordered(reconocerArchivo,
                                      rutaAvisos)
        #iterator.next()

        while True:
            try:
                iterator.next()
            except multiprocessing.TimeoutError:
                continue
            except StopIteration:
                break
            except:
                print("Failed fingerprinting")
            else:
                print("Exitos")
        pool.close()
        pool.join()



def reconocerArchivo(filename):
    rec = Rec()
    nombre = ExtraerNombreArchivo(filename)
    horaId = rec.obtenerHoraId(filename)
    frames, fs, hashArchivo, duracion = rec.LeerArchivo(filename)
    print "reconociendo hora = : %s ..." % (nombre)
    matches = _recognize(rec.db, fs , *frames)
    #print matches
    resultado = '{resultado}'
    rec.db.marcar_hora_procesado(horaId, resultado)
    #grabarXML(rec.DIR_AVISO_PROCESADOS, nombre, matches)
    return matches


