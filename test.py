from rec import Rec
import time
rec = Rec()
#rec.ResetBD()
#rec.aprenderSpot('audios/spots/spotariel.mp3',None)
#rec.ProcesarDirectorio()
t = time.time()
print rec.reconocerArchivo('audios/programas/programa02.mp3')
t = time.time() - t
print("totalTime : %s", t)
