from rec import Rec, reconocerArchivo, util
import multiprocessing
from multiprocessing import freeze_support

import time
rec = Rec()

#rec.ResetBD()
#rec.aprenderAviso('audios/avisos/avisoarie0.mp3',None)
#rec.ProcesarDirectorio()



#t = time.time()
#print reconocerArchivo('audios/horas/programa01.mp3')
#t = time.time() - t
#print("totalTime : %s", t)

#
# def longProcess(rutaArchivo):
#     print 'Start : {0}, {1}'.format(rutaArchivo, time.ctime())
#     time.sleep(10)
#     print 'End : {0}, {1}'.format(rutaArchivo, time.ctime())
# #
#if __name__ == '__main__':
 #   freeze_support()
#     print rec.reconocerArchivo('audios/horas/hora01.mp3')
#    rec.reconocerDirectorio('audios/horas')
    # rutaAvisos = []
    # for rutaArchivo, ext in rec.LeerDirectorio('audios/horas'):
    #     rutaAvisos.append(rutaArchivo)
    # nprocesses=None
    # try:
    #     nprocesses = nprocesses or multiprocessing.cpu_count()
    # except NotImplementedError:
    #     nprocesses = 1
    # else:
    #     nprocesses = 1 if nprocesses <= 0 else nprocesses
    # pool = multiprocessing.Pool(nprocesses)
   # worker_input = zip(rutaAvisos)
   # rec.reconocerArchivo(rutaAvisos[0])
   # iterator = pool.imap_unordered(longProcess,
    #                               rutaAvisos)
    #iterator.next()
#     while True:
#         try:
#             iterator.next()
#         except multiprocessing.TimeoutError:
#             continue
#         except StopIteration:
#             break
#         except:
#             print("Failed fingerprinting")
#         else:
#             print("Exitos")
#     pool.close()
#     pool.join()


#rec = Rec()
#if __name__ == '__main__':
    #freeze_support()
    #datos = {}
    #GrabarXML('baseconocimiento/','archivo',datos)
    #rec.reconocerDirectorio('audios/horas')

#import time
#t = time.time()
#t = time.time() - t
#print("time to obtenerhuellas : %s", t)

#from rec import Rec
#rec = Rec()
#rec.ResetBD()
#rec.ProcesarDirectorio()
#if __name__ == '__main__':
#    freeze_support()
#    rec.reconocerDirectorio('audios/horas')


#import time
#rec = Rec()
#if __name__ == '__main__':
#    freeze_support()
#    while True:
#        time.sleep(5)
#        rec.reconocerDirectorio('audios/horas')

#def do_main_program():
#    freeze_support()
#    time.sleep(5)
#    print("searching...")
#    rec.reconocerDirectorio('audios/horas')

#while True:
#    time.sleep( 1 )
#    try:
#        do_main_program()
#    except:
#        pass


#import os
#import fnmatch
#ruta="audios/avisos/"
#avisos = []
#extension = "mp3"
#for rutadir, nombredir, archivos in os.walk(ruta):
#    print(nombredir)
#    print(archivos)
#    for f in fnmatch.filter(archivos, "*.%s" % extension):
#        p = os.path.join(rutadir, f)
#        avisos.append((p, extension))



#print rec.db.obtenerHoras('programa01', '20161218', '20161218')

#import datetime
#string_date = '2016-12-18 00:00:00'
#print datetime.datetime.strptime(string_date, "%Y-%m-%d %H:%M:%S")

#from rec.util import AbrirArchivo
#AbrirArchivo("")


nombre = '2016-11-21_08-00-00_AQP_MELODIA-FM_FM'
metadato = nombre.split('_')
hora_fecha = metadato[0]
hora_hora = metadato[1]
hora_ciudad = metadato[2]
hora_medio = metadato[3]
hora_tipo = metadato[4]
print (metadato)

