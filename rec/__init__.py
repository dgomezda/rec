import os
from rec.util import GrabarXML, LeerDirectorio, ExtraerNombreArchivo, ObtenerHashArchivo, GrabarXML, ObtenerConfiguracion, EliminarArchivo
from rec.huellas import obtenerHuellas
from rec.reconocimiento import reconocer
import warnings
import multiprocessing
warnings.filterwarnings("ignore")
import time
from pydub import AudioSegment
import numpy as np

from rec.database import Database


class Rec(object):
    AVISO = 1
    HORA = 2
    DEFAULT_WINDOW_SIZE = 4096
    DEFAULT_OVERLAP_RATIO = 0.5
    DEFAULT_HIT_MIN  = 10
    FACTOR_OFFSET = 1

    #FROM CONFIG
    BD_HOST = ""
    BD_USER = ""
    BD_PASSWD = ""
    BD_ID = ""
    BD_PORT = 0
    DIR_AVISO = ""
    DIR_HORA = ""
    DIR_AVISO_PROCESADOS = ""

    def __init__(self):
        cnf = util.ObtenerConfiguracion()
        self.BD_HOST = cnf["BD_HOST"]
        self.BD_USER = cnf["BD_USER"]
        self.BD_PASSWD = cnf["BD_PASSWD"]
        self.BD_ID = cnf["BD_ID"]
        self.BD_PORT = cnf["BD_PORT"]
        self.DIR_AVISO = cnf["DIR_AVISO"]
        self.DIR_HORA = cnf["DIR_HORA"]
        self.DIR_AVISO_PROCESADOS = cnf["DIR_AVISO_PROCESADOS"]
        self.db = Database(user=self.BD_USER, passwd=self.BD_PASSWD, host = self.BD_HOST, db = self.BD_ID, port = self.BD_PORT  )
        #print "Inicializando..."

    def ResetBD(self):
        self.db.limpiar()

    def ProcesarDirectorio(self):
        avisos = LeerDirectorio(self.DIR_AVISO)
        contadorAviso = 1
        for aviso in avisos:
            print "%d.- aprendiendo aviso : %s" % (contadorAviso, aviso[0])
            self.aprenderAviso(aviso[0])
            contadorAviso += 1
            EliminarArchivo(aviso[0])

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
            hashes = obtenerHuellas(channel, Fs=Fs, 
                                    wsize=self.DEFAULT_WINDOW_SIZE,
                                    wratio=self.DEFAULT_OVERLAP_RATIO)
            result |= set(hashes)
        return nombre, result, hashArchivo, duracion

    def obtenerAvisosAprendidos(self):
        self.avisos = self.db.get_avisos()
        self.avisos_set = set()
        for aviso in self.avisos:
            hashArchivo = aviso['sha1']
            self.avisos_set.add(hashArchivo)

    def reconocerDirectorio(self, ruta):
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

        #print reconocerArchivo(self, rutaAvisos[0])
        pool = multiprocessing.Pool(nprocesses)

        iterator = pool.imap_unordered(reconocerArchivo,
                                      rutaAvisos)
        #print iterator.next()

        while True:
            try:
                print iterator.next()
            except multiprocessing.TimeoutError:
                continue
            except StopIteration:
                break
            except:
                print("Failed fingerprinting")
            else:
                pass
                #print("Completo.")

        pool.close()
        pool.join()



def reconocerArchivo(filename):
    rec = Rec()
    nombre = ExtraerNombreArchivo(filename)
    frames, fs, hashArchivo, duracion = rec.LeerArchivo(filename)
    t = time.time()
    print "reconociendo hora = : %s ..." % (nombre)
    matches = reconocer(rec.db, fs, rec.DEFAULT_WINDOW_SIZE, rec.DEFAULT_OVERLAP_RATIO, rec.DEFAULT_HIT_MIN, rec.FACTOR_OFFSET  , *frames)
    t = time.time() - t
    print("time to reconize : %s", t)
    GrabarXML(rec.DIR_AVISO_PROCESADOS,nombre,matches)
    EliminarArchivo(filename);
    return matches

