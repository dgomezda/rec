from flask import Flask,  request, json, jsonify, make_response
from flask_restful import Api
from rec import Rec, reconocerArchivo
from rec.util import ObtenerConfiguracion
import os
import datetime

rec = Rec()
DIR_AVISO = ''
DIR_HORA = ''
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
        horaId = rec.db.insert_hora(request.files['file'].filename)
    return getResponse(errorCode, horaId)

@app.route('/horas/procesar', methods = ['POST'])
def api_horas_procesar():
    parametros = json.loads(request.data)
    try:
        horaId = parametros.get('horaId')
        hora = rec.db.obtenerHora_horaId(horaId)
        rutaArchivo = os.path.join(DIR_HORA, hora['nombre'])
        resultado = reconocerArchivo(rutaArchivo)
        response = json.dumps(resultado)
        rec.db.marcar_hora_procesado(horaId, response)
    except (RuntimeError):
        return getResponse(1001, None)
    return getResponse(0, response)

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

@app.route('/horas/obtenerxml', methods = ['GET'])
def api_horas_obtenerxml():
    parametros = request.args
    try:
        horaid = parametros.get('horaid')
    except (RuntimeError):
        return jsonify(GetError(1001))
    return jsonify(parametros)
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

#Implementacion del recurso parametros
@app.route('/parametros', methods = ['GET'])
def api_parametros():
    return 'Recurso parametros'

@app.route('/parametros/consultarnombrehora', methods = ['GET'])
def api_avisos_consultarnombrehora():
    parametros = request.args
    try:
        pass
    except (RuntimeError):
        return jsonify(GetError(1001))
    return jsonify(parametros)

@app.route('/parametros/grabarnombrehora', methods = ['POST'])
def api_avisos_grabarnombrehora():
    parametros = json.loads(request.data)
    try:
        CiuCod = parametros.get('CiuCod')
        MedCod = parametros.get('MedCod')
        TipMedCod = parametros.get('TipMedCod')
        MotCod = parametros.get('MotCod')
    except (RuntimeError):
        return jsonify(GetError(1001))
    return jsonify(parametros)

@app.route('/parametros/creartablas', methods = ['POST'])
def api_parametros_creartablas():
    try:
        rec.ResetBD()
    except (RuntimeError):
        return getResponse(10001)
    return getResponse(0)

@app.route('/apagar', methods=['GET'])
def shutdown():
    shutdown_server()
    return 'Apagando servicio...'

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
#Fin implementacion del recurso parametros

if __name__ == '__main__':
    cnf = ObtenerConfiguracion()
    API_HOST = cnf["API_HOST"]
    API_PORT = cnf["API_PORT"]
    DIR_AVISO = cnf["DIR_AVISO"]
    DIR_HORA = cnf["DIR_HORA"]
    app.run(host=API_HOST, port=API_PORT)