import time
from rec import Rec
from multiprocessing import freeze_support
from rec.util import ObtenerConfiguracion

rec = Rec()
if __name__ == '__main__':
    cnf = ObtenerConfiguracion()
    DEMONIO_TIEMPO_XMLS = cnf["DEMONIO_TIEMPO_XMLS"]
    freeze_support()
    while True:
        time.sleep(DEMONIO_TIEMPO_XMLS)
        print("Buscando huellas pendientes ...")
        rec.reconocerPendientes()