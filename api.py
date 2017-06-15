from flask import Flask,  request, json, jsonify, make_response
from flask_restful import Api
from rec import Rec
from rec.util import ObtenerConfiguracion, ListarResumenes,ExtraerNombreArchivo
import os
import datetime

rec = Rec()
DIR_AVISO = ''
DIR_HORA = ''
DIR_BASECONOCIMIENTO = ''
ALLOWED_EXTENSIONS = set(['mp3'])

app = Flask(__name__)
api = Api(app)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def upload_file(request, directorio):
    if 'file' not in request.files:
        return 10002
    file = request.files['file']
    if file.filename == '':
        return 10003
    if file and allowed_file(file.filename):
        file.save(os.path.join(directorio, file.filename))
        return 0
    else:
        return 10004


def ValidarFechas(fechai, fechaf):
    try:
        datetime.datetime.strptime(fechai, "%Y-%m-%d %H:%M:%S")
        datetime.datetime.strptime(fechaf, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return False
    return True


def GetError(errorCode):
    if errorCode == 10001:
        return 'Error en base de datos'
    if errorCode == 10002:
        return 'No se ha encontrado seccion de archivo en la solicitud'
    if errorCode == 10003:
        return 'No se ha encontrado archivo adjunto a la solicitud'
    if errorCode == 10004:
        return 'Archivo no permitido'
    if errorCode == 10005:
        return 'Las fechas ingresadas no son validas'
    return  None

def getResponse(errorCode=0, obj=None):
    statusCode = 200
    if errorCode > 0:
        statusCode = 500
    return jsonify({
        "result": obj,
        "errorCode": errorCode,
        "errorMessage": GetError(errorCode),
        "status": statusCode
    })

@app.route('/')
def api_root():
    return  'API de Reconocimiento'

#Implementacion de recurso horas
@app.route('/horas', methods = ['GET'])
def api_horas():
    return 'Recurso Horas'

@app.route('/horas/cargar', methods = ['POST'])
def api_horas_cargar():
    errorCode = upload_file(request, DIR_HORA)
    if (errorCode == 0):
        nombreHora = ExtraerNombreArchivo(request.files['file'].filename)
        horaId = rec.db.insert_hora(nombreHora)
    return getResponse(errorCode, horaId)

@app.route('/horas/consultar', methods = ['GET'])
def api_horas_consultar():
    parametros = request.args
    try:
        nombre = parametros.get('nombre')
        fechai = parametros.get('fechai')
        fechaf = parametros.get('fechaf')
        procesado = parametros.get('procesado')
        if procesado is None:
            procesado = -1
        if(ValidarFechas(fechai, fechaf) == False):
            return getResponse(10005, None)
        result = rec.db.obtenerHoras(nombre, fechai, fechaf, procesado)
    except (RuntimeError):
        return jsonify(GetError(1001))
    return getResponse(0,result)

@app.route('/horas/consultarProcesados', methods = ['GET'])
def api_horas_consultarProcesados():
    parametros = request.args
    try:
        result = ListarResumenes(DIR_BASECONOCIMIENTO)
    except (RuntimeError):
        return jsonify(GetError(1001))
    return getResponse(0,result)

@app.route('/horas/reprocesarxml', methods = ['POST'])
def api_horas_reprocesarxml():
    parametros = json.loads(request.data)
    try:
        nombre = parametros.get('nombre')
        result = rec.db.reprocesar_hora(nombre)
    except (RuntimeError):
        return jsonify(GetError(1001))
    return getResponse(0,result)
#Fin implementacion del recurso horas

#Implementacion del recurso avisos
@app.route('/avisos', methods = ['GET'])
def api_avisos():
    return 'Recurso avisos'

@app.route('/avisos/cargar', methods = ['POST'])
def api_avisos_cargar():
    resultado = upload_file(request, DIR_AVISO)
    return jsonify({ "resultado" : resultado})

@app.route('/avisos/consultar', methods = ['GET'])
def api_avisos_consultar():
    parametros = request.args
    try:
        nombre = parametros.get('nombre')
        result = rec.db.obtenerAvisos(nombre)
    except (RuntimeError):
        return jsonify(GetError(1001))
    return getResponse(0,result)
#Fin de implementacion del recurso avisos.


@app.route('/apagar', methods=['GET'])
def shutdown():
    shutdown_server()
    return 'Apagando servicio...'

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.route('/limpiar', methods=['GET'])
def cleanDataFiles():
    rec.ResetBD()
    rec.ResetDirectorios()
    return 'Success'
#Fin implementacion del recurso parametros

if __name__ == '__main__':
    cnf = ObtenerConfiguracion()
    API_HOST = cnf["API_HOST"]
    API_PORT = cnf["API_PORT"]
    DIR_AVISO = cnf["DIR_AVISO"]
    DIR_HORA = cnf["DIR_HORA"]
    DIR_BASECONOCIMIENTO = cnf["DIR_BASECONOCIMIENTO"]
    app.run(host=API_HOST, port=API_PORT)