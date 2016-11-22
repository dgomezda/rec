from rec import Rec
from multiprocessing import freeze_support

rec = Rec()
if __name__ == '__main__':
    freeze_support()
    rec.reconocerDirectorio('audios/horas')