import os
import fnmatch
import dicttoxml
import warnings
warnings.filterwarnings("ignore")

import time

#ObtenerHash
from hashlib import sha1

#leerArchivo
from pydub import AudioSegment
import numpy as np

#obtenerHuellas
import matplotlib.mlab as mlab

#2d
from scipy.ndimage.filters import maximum_filter
from scipy.ndimage.morphology import (generate_binary_structure,
                                      iterate_structure, binary_erosion)
#generatehashes
import hashlib
from operator import itemgetter

from rec.database import Database

#import json

class Rec(object):
    SPOT = 1
    PROGRAMA = 2
    DIR_SPOT = "audios/spots/"
    DIR_PROGRAMA = "audios/programas/"
    DIR_SPOT_PROCESADOS = "baseconocimiento/"

    DEFAULT_FS = 32000
    DEFAULT_WINDOW_SIZE = 4096
    DEFAULT_OVERLAP_RATIO = 0.5
    DEFAULT_FAN_VALUE = 15
    DEFAULT_AMP_MIN = 10
    PEAK_NEIGHBORHOOD_SIZE = 20

    #generatehash
    PEAK_SORT = True
    IDX_FREQ_I = 0
    IDX_TIME_J = 1

    MIN_HASH_TIME_DELTA = 0
    MAX_HASH_TIME_DELTA = 200
    FINGERPRINT_REDUCTION = 20

    #BD
    BD_HOST = "127.0.0.1"
    BD_USER = "root"
    BD_PASSWD = "toor"
    BD_ID = "ironrec"
    BD_PORT = 3306
	#3311

    def __init__(self):
        self.db = Database(user=self.BD_USER, passwd=self.BD_PASSWD, host = self.BD_HOST, db = self.BD_ID, port = self.BD_PORT  )
        #self.obtenerSpotsAprendidos()
        print "Inicializando..."

    def ResetBD(self):
        self.db.limpiar()
    def ProcesarDirectorio(self):
        spots = self.LeerDirectorio()
        contadorSpot = 1
        for spot in spots:
            print "%d.- aprendiendo spot : %s" % (contadorSpot, spot[0])
            self.aprenderSpot(spot[0])
            contadorSpot += 1
    def LeerDirectorio(self):
        """Toma los archivos en TODO"""
        spots = []
        extension = "mp3"
        ruta = self.DIR_SPOT
        for rutadir, nombredir, archivos in os.walk(ruta):
            for f in fnmatch.filter(archivos, "*.%s" % extension):
                p = os.path.join(rutadir, f)
                spots.append((p, extension))
        return spots

    def ObtenerHash(self, rutaArchivo, blocksize=2 ** 20):
        s = sha1()
        with open(rutaArchivo, "rb") as f:
            while True:
                buf = f.read(blocksize)
                if not buf:
                    break
                s.update(buf)
        return s.hexdigest().upper()

    def LeerArchivo(self, rutaArchivo):
        contenido = AudioSegment.from_file(rutaArchivo)
        data = np.fromstring(contenido._data, np.int16)
        channels = []
        for chn in xrange(contenido.channels):
            channels.append(data[chn::contenido.channels])
        fs = contenido.frame_rate
        return channels, contenido.frame_rate, self.ObtenerHash(rutaArchivo), contenido.duration_seconds

    def generate_hashes(self, peaks, fan_value=DEFAULT_FAN_VALUE):
        if self.PEAK_SORT:
            peaks.sort(key=itemgetter(1))

        for i in range(len(peaks)):
            for j in range(1, fan_value):
                if (i + j) < len(peaks):

                    freq1 = peaks[i][self.IDX_FREQ_I]
                    freq2 = peaks[i + j][self.IDX_FREQ_I]
                    t1 = peaks[i][self.IDX_TIME_J]
                    t2 = peaks[i + j][self.IDX_TIME_J]
                    t_delta = t2 - t1

                    if t_delta >= self.MIN_HASH_TIME_DELTA and t_delta <= self.MAX_HASH_TIME_DELTA:
                        h = hashlib.sha1(
                            "%s|%s|%s" % (str(freq1), str(freq2), str(t_delta)))
                        yield (h.hexdigest()[0:self.FINGERPRINT_REDUCTION], t1)

    def get_2D_peaks(self, arr2D,  amp_min):
        struct = generate_binary_structure(2, 1)
        neighborhood = iterate_structure(struct, self.PEAK_NEIGHBORHOOD_SIZE)

        # find local maxima using our fliter shape
        local_max = maximum_filter(arr2D, footprint=neighborhood) == arr2D
        background = (arr2D == 0)
        eroded_background = binary_erosion(background, structure=neighborhood,
                                           border_value=1)

        # Boolean mask of arr2D with True at peaks
        detected_peaks = local_max - eroded_background

        # extract peaks
        amps = arr2D[detected_peaks]
        j, i = np.where(detected_peaks)

        # filter peaks
        amps = amps.flatten()
        peaks = zip(i, j, amps)
        peaks_filtered = [x for x in peaks if x[2] > amp_min]  # freq, time, amp

        # get indices for frequency and time
        frequency_idx = [x[1] for x in peaks_filtered]
        time_idx = [x[0] for x in peaks_filtered]

        return zip(frequency_idx, time_idx)

    # fingerprint
    def obtenerHuellas(self, channel_samples, Fs=DEFAULT_FS,
                    wsize=DEFAULT_WINDOW_SIZE,
                    wratio=DEFAULT_OVERLAP_RATIO,
                    fan_value=DEFAULT_FAN_VALUE,
                    amp_min=DEFAULT_AMP_MIN):
        arr2D = mlab.specgram(
            channel_samples,
            NFFT=wsize,
            Fs=Fs,
            window=mlab.window_hanning,
            noverlap=int(wsize * wratio))[0]
        arr2D = 10 * np.log10(arr2D)
        arr2D[arr2D == -np.inf] = 0  # replace infs with zeros
        local_maxima = self.get_2D_peaks(arr2D, amp_min)
        return self.generate_hashes(local_maxima, fan_value=fan_value)

    def ExtraerNombreArchivo(self, rutaArchivo):
        return os.path.splitext(os.path.basename(rutaArchivo))[0]

    def aprenderSpot(self, rutaSpot, nombreSpot=None): #fingerprint_file
        nombre = self.ExtraerNombreArchivo(rutaSpot)
        #hashArchivo = self.ObtenerHash(rutaSpot)
        nombre = nombreSpot or nombre
        #if hashArchivo in self.spots_set:
        #    print "ya se aprendio el spot: %s" % nombre
        #else:
        nombre, hashes, hashArchivo, duracion = self.ProcesarHuellas(
            rutaSpot,
            nombre
        )
        spotId = self.db.insert_spot(nombre, hashArchivo, duracion)

        self.db.insert_hashes(spotId, hashes)
        self.db.marcar_spot_procesado(spotId)
        #self.obtenerSpotsAprendidos()

    def ProcesarHuellas(self, archivo, nombreSpot=None): #_fingerprint_worker

        nombre, extension = os.path.splitext(os.path.basename(archivo))
        nombre = nombreSpot or nombre
        channels, Fs, hashArchivo, duracion = self.LeerArchivo(archivo)
        result = set()
        channel_amount = len(channels)

        for channeln, channel in enumerate(channels):
            hashes = self.obtenerHuellas(channel, Fs=Fs)
            result |= set(hashes)
        return nombre, result, hashArchivo, duracion

    def obtenerSpotsAprendidos(self):
        # get songs previously indexed
        self.spots = self.db.get_spots()
        self.spots_set = set()
        for spot in self.spots:
            hashArchivo = spot['sha1']
            self.spots_set.add(hashArchivo)

    def reconocerArchivo(self, filename):
        nombre = self.ExtraerNombreArchivo(filename);
        frames, fs, hashArchivo, duracion  = self.LeerArchivo(filename)
        print "reconociendo programa = : %s ..." % (nombre)
        matches = self._recognize(fs, *frames)
        self.grabarXML(nombre, matches)
        return matches

    def grabarXML(self,nombre, *data):
        xml = dicttoxml.dicttoxml(data, custom_root='spots', attr_type=False)
        filepath = self.DIR_SPOT_PROCESADOS +  nombre + '.xml'
        f = open(filepath, 'w+')
        f.write(xml)  # python will convert \n to os.linesep
        f.close()

    def _recognize(self, fs,  *data):
        matches = []
        for d in data:
            matches.extend(self.find_matches(d, fs))
        return self.align_matches(matches, fs)

    def find_matches(self, samples, fs):
        hashes = self.obtenerHuellas(samples, fs)
        return self.db.return_matches(hashes)

    def align_matches(self, matches, fs):
        diff_counter = {}
        listaSpotRec = []
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
                if value1 > 10:
                    spot = self.db.obtenerSpot(key1)
                    nseconds = round(float(key) / fs *
                    self.DEFAULT_WINDOW_SIZE *
                    self.DEFAULT_OVERLAP_RATIO, 5)
                    spotRec = {
                        'spotId': key1,
                        'nombre': spot.get('nombre', None),
                        'Inicio': nseconds,
                        'duracion': spot.get('duracion',None),
                    }
                    listaSpotRec.append(spotRec)
        return listaSpotRec

                    # extract idenfication
        #song = self.db.obtenerSpot(song_id)
        #if song:
        #    # TODO: Clarify what `get_song_by_id` should return.
        #    songname = song.get('nombre', None)
        #else:
        #    return None
        #return song

       # nseconds = round(float(largest) / fs *
       #                  fingerprint.DEFAULT_WINDOW_SIZE *
       #                  fingerprint.DEFAULT_OVERLAP_RATIO, 5)
       # song = {
       #     Ironrec.SONG_ID: song_id,
       #     Ironrec.SONG_NAME: songname,
       #     Ironrec.CONFIDENCE: largest_count,
       #     Ironrec.OFFSET: int(largest),
       #     Ironrec.OFFSET_SECS: nseconds,
       #     Database.FIELD_FILE_SHA1: song.get(Database.FIELD_FILE_SHA1, None), }
       # return song

    def GrabarArchivoProcesado(self):
        """Graba las huellas de memoria a archivos fisico"""
        pass
    def LeerSpotProcesados(self):
        """Lee archivos procesados de memoria y los coloca en memoria"""
        pass
    def Reconocer(self):
        """Compara las huellas de los archivos de"""
        pass
    def GenerarXml(self):
        pass
