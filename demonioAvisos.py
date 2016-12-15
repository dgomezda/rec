import time
from rec import Rec
from multiprocessing import freeze_support
rec = Rec()
rec.ResetBD()
if __name__ == '__main__':
    freeze_support()
    while True:
        time.sleep(10)
        print("Buscando avisos ...")
        rec.ProcesarDirectorio()