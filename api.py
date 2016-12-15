from flask import Flask,  request, json, jsonify, make_response
from flask_restful import Api
from rec import Rec, reconocerArchivo
from rec.util import ObtenerConfiguracion
rec = Rec()

import os
DIR_AVISOS = 'audios/avisos/'
DIR_HORAS = 'audios/horas/'
ALLOWED_EXTENSIONS = set(['mp3', 'wav'])

app = Flask(__name__)
api = Api(app)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def upload_file(request, directorio ):
    if 'file' not in request.files:
        return 1201
    file = request.files['file']
    if file.filename == '':
        return 1202
    if file and allowed_file(file.filename):
        file.save(os.path.join(directorio, file.filename))
        return 0
    else:
        return 1203

@app.route('/')
def api_root():
    response = {"status" : 200}
    return jsonify(response)

#INICIO DE IMPLEMENTACION DEL RECURSO HORAS
@app.route('/horas', methods = ['GET'])
def api_horas():
    return 'Recurso Horas'

@app.route('/horas/cargar', methods = ['POST'])
def api_horas_cargar():
    errorCode = upload_file(request, DIR_HORAS)
    if (errorCode == 0):
        horaId = rec.db.insert_hora(request.files['file'].filename)

    return getResponse(errorCode, horaId)

@app.route('/horas/procesar', methods = ['POST'])
def api_horas_procesar():
    parametros = json.loads(request.data)
    try:
        horaId = parametros.get('horaId')
        hora = rec.db.obtenerHora_horaId(horaId)
        rutaArchivo = os.path.join(DIR_HORAS, hora['nombre'])
        resultado = reconocerArchivo(rutaArchivo)
        response = json.dumps(resultado)
        rec.db.marcar_hora_procesado(horaId, resultado)
    except (RuntimeError):
        return getResponse(1001, None)
    return getResponse(0, response)


@app.route('/horas/consultar', methods = ['GET'])
def api_horas_consultar():
    parametros = request.args
    try:
        nombre = parametros.get('nombre')
        fecha = parametros.get('fecha')
        result = rec.db.obtenerHoras(nombre, fecha)
    except (RuntimeError):
        return jsonify(getError(1001))
    return getResponse(0,result)

@app.route('/horas/obtenerxml', methods = ['GET'])
def api_horas_obtenerxml():
    parametros = request.args
    try:
        horaid = parametros.get('horaid')
    except (RuntimeError):
        return jsonify(getError(1001))
    return jsonify(parametros)
#FIN HORAS

#INICIO DE LA IMPLEMEMENTACION DEL RECURSO AVISOS
@app.route('/avisos', methods = ['GET'])
def api_avisos():
    return 'Recurso avisos'

@app.route('/avisos/cargar', methods = ['POST'])
def api_avisos_cargar():
    resultado = upload_file(request, DIR_AVISOS)
    return jsonify({ "resultado" : resultado})

@app.route('/avisos/consultar', methods = ['GET'])
def api_avisos_consultar():
    parametros = request.args
    try:
        nombre = parametros.get('nombre')
        fecha = parametros.get('fecha')
        result = rec.db.obtenerAvisos(nombre,fecha)
    except (RuntimeError):
        return jsonify(getError(1001))
    return getResponse(0,result)
#FIN AVISOS

#INICIO DE LA IMPLEMEMENTACION DEL RECURSO PARAMETROS
@app.route('/parametros', methods = ['GET'])
def api_parametros():
    return 'Recurso parametros'

@app.route('/parametros/consultarnombrehora', methods = ['GET'])
def api_avisos_consultarnombrehora():
    parametros = request.args
    try:
        pass
    except (RuntimeError):
        return jsonify(getError(1001))
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
        return jsonify(getError(1001))
    return jsonify(parametros)

@app.route('/parametros/creartablas', methods = ['POST'])
def api_parametros_creartablas():
    try:
        rec.ResetBD()
    except (RuntimeError):
        return getResponse(1001)
    return getResponse(0)

@app.route('/apagar', methods=['GET'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
#FIN CONFIGURACION

#begin common
def getError(errorCode):
    if errorCode == 1001:
        return 'Internal Error'
    if errorCode == 1201:
        return 'No file part'
    if errorCode == 1202:
        return 'No selected file'
    if errorCode == 1203:
        return 'file not allowed'


def getResponse(errorCode=0, obj=None):
    return jsonify({
        "result": obj,
        "errorCode": errorCode,
        "errorMessage": getError(errorCode)
    })

if __name__ == '__main__':
    cnf = ObtenerConfiguracion()
    API_HOST = cnf["API_HOST"]
    API_PORT = cnf["API_PORT"]
    app.run(host=API_HOST, port=API_PORT)