import time
from rec import Rec
from multiprocessing import freeze_support
from rec.util import ObtenerConfiguracion

rec = Rec()
if rec.RESET_BD == 1:
    rec.ResetBD()
if __name__ == '__main__':
    cnf = ObtenerConfiguracion()
    DEMONIO_TIEMPO_AVISOS = cnf["DEMONIO_TIEMPO_AVISOS"]
    freeze_support()
    while True:
        print("Buscando avisos ...")
        rec.ProcesarDirectorio()
        time.sleep(DEMONIO_TIEMPO_AVISOS)