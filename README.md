# IronRec
IronRec Project is an script for audio recognition using FFT.


Agregar el app.config el tiempo para demonios Done!
mover audios procesados de avisos y horas ?
grabar el archivo extraido en archivos separados (BD).
EL demonio de las horas solo procesa, y actualiza la bd.
Desde api lanzar el reconocmiento de las horas seleccionadas.
agregar avisos_procesados, horas_procesados

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
with open("log.txt") as infile:
    for line in infile:
        do_something_with(line)

with open('datafile') as fin:
    data = fin.read(chunksize)
    process(data)
    while len(data) == chunksize
        data = fin.read(chunksize)
        process(data)

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^		
x = y = z = np.arange(0.0,5.0,1.0)
np.savetxt('test.out', x, delimiter=',')   # X is an array
np.savetxt('test.out', (x,y,z))   # x,y,z equal sized 1D arrays
np.savetxt('test.out', x, fmt='%1.4e')   # use exponential notation


a = numpy.array([1,2,3])
b = numpy.array([4,5,6])
numpy.savetxt(filename, (a,b), fmt="%d")

# gives:
# 1 2 3
# 4 5 6

