import time
from rec import Rec
from multiprocessing import freeze_support
rec = Rec()
if __name__ == '__main__':
    freeze_support()
    while True:
        time.sleep(10)
        print("Buscando horas ...")
        rec.reconocerDirectorio('audios/horas')