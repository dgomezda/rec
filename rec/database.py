import MySQLdb as mysql
from itertools import izip_longest
import Queue
from MySQLdb.cursors import DictCursor
import time
class Database(object):
    def __init__(self, **options):
        self.cursor = cursor_factory(**options)
    DROP_HUELLAS = "DROP TABLE IF EXISTS huellas;"
    DROP_AVISOS = "DROP TABLE IF EXISTS avisos;"
    DROP_HORAS = "DROP TABLE IF EXISTS horas;"
    CREATE_HUELLAS = """
            CREATE TABLE IF NOT EXISTS `huellas` (
                 `hash` binary(10) not null,
                 `avisoId` mediumint unsigned not null,
                 `offset` int unsigned not null,
             INDEX (hash),
             UNIQUE KEY `unique_constraint` (hash, avisoId, offset),
             FOREIGN KEY (avisoId) REFERENCES avisos(avisoId) ON DELETE CASCADE
        ) ENGINE=INNODB;"""
    CREATE_AVISOS = """
            CREATE TABLE IF NOT EXISTS `avisos` (
                `avisoId` mediumint unsigned not null auto_increment,
                `nombre` varchar(250) not null,
                `procesado` tinyint default 0,
                `sha1` binary(20) not null,
                `duracion` mediumint unsigned not null,
            PRIMARY KEY (`avisoId`),
            UNIQUE KEY `avisoId` (`avisoId`)
        ) ENGINE=INNODB;"""

    CREATE_HORAS = """
                CREATE TABLE IF NOT EXISTS `horas` (
                    `horaId` mediumint unsigned not null auto_increment,
                    `nombre` varchar(250) not null,
                    `procesado` tinyint default 0,
                    `resultado` varchar(4000) null,
                    `fechaCreacion`  datetime default null,
                    `fechaProcesado` datetime default null,
                PRIMARY KEY (`horaId`),
                UNIQUE KEY `horaId` (`horaId`)
            ) ENGINE=INNODB;"""
    INSERT_HUELLAS = "INSERT IGNORE INTO huellas (hash, avisoId, offset) values (UNHEX(%s), %s, %s);"
    INSERT_AVISOS = "INSERT INTO avisos (nombre, sha1, duracion) values (%s, UNHEX(%s), %s);"
    INSERT_HORAS = "INSERT INTO horas (nombre, fechacreacion) values ( %s , CURRENT_TIMESTAMP);"
    DELETE_HUELLAS_NOPROCESADAS = "DELETE FROM avisos WHERE procesado = 0;"
    UPDATE_AVISO_PROCESADO = "UPDATE avisos SET procesado = 1 WHERE avisoId = %s;"
    UPDATE_HORA_PROCESADO = "UPDATE horas SET procesado = 1, resultado = %s, fechaprocesado = CURRENT_TIMESTAMP WHERE horaId = %s ;"

    SELECT_AVISOS = "SELECT avisoId, nombre, HEX(sha1) as sha1 FROM avisos WHERE procesado = 1;"
    SELECT_MULTIPLE = "SELECT HEX(hash), avisoId, offset FROM huellas WHERE hash IN (%s);"
    SELECT_AVISO = "SELECT nombre, HEX(sha1) as sha1, duracion FROM avisos WHERE avisoId = %s;"
    #SELECT_HORA_NOMBRE = "SELECT horaId FROM horas WHERE nombre = %s;"
    SELECT_HORA_HORAID = "SELECT horaId, nombre, procesado, resultado, fechacreacion, fechaprocesado FROM horas WHERE horaId = %s;"
    SELECT_HORAS_LIKENOMBRE ="SELECT horaId, nombre, procesado, resultado, fechacreacion, fechaprocesado FROM horas " \
                  "where INSTR(nombre, %s) > 0"
    SELECT_HORAS = "SELECT horaId, nombre, procesado, resultado, fechacreacion, fechaprocesado FROM horas " \
                  "WHERE horaId = %s " \
                  "union " \
                  "SELECT horaId, nombre, procesado, resultado, fechacreacion, fechaprocesado FROM horas " \
                  "where fechacreacion > %s and fechacreacion < %s " \
                  ""
    SELECT_ULTIMA_HORA = "SELECT horaId FROM horas  order by horaId desc limit 1;"
    SELECT_AVISOS_LIKENOMBRE = "SELECT avisoId, nombre, procesado, sha1, duracion FROM avisos " \
                              "where INSTR(nombre, %s) > 0"

    def inicializar(self):
        with self.cursor() as cur:
            cur.execute(self.CREATE_AVISOS)
            cur.execute(self.CREATE_HUELLAS)
            cur.execute(self.DELETE_HUELLAS_NOPROCESADAS)
            cur.execute(self.CREATE_HORAS)
    def limpiar(self):
        with self.cursor() as cur:
            cur.execute(self.DROP_HUELLAS)
            cur.execute(self.DROP_AVISOS)
            cur.execute(self.DROP_HORAS)
        self.inicializar()
        print "Limpieza de tablas completa"

    def insert_aviso(self, nombreAviso, hashArchivo, duracion):
        with self.cursor() as cur:
            cur.execute(self.INSERT_AVISOS, (nombreAviso, hashArchivo, duracion))
            return cur.lastrowid
    def insert_hora(self, nombreHora):
        with self.cursor() as cur:
            cur.execute(self.INSERT_HORAS, (nombreHora,))
            return cur.lastrowid
    def insert_hashes(self, avisoId, hashes):
        values = []
        for hash, offset in hashes:
            values.append((hash, avisoId, offset))
        with self.cursor() as cur:
            for split_values in grouper(values, 1000):
                cur.executemany(self.INSERT_HUELLAS, split_values)

    def marcar_hora_procesado(self, horaId, resultado):
        with self.cursor() as cur:
            cur.execute(self.UPDATE_HORA_PROCESADO, ('', horaId,))

    def marcar_aviso_procesado(self,  avisoId):
        with self.cursor() as cur:
            cur.execute(self.UPDATE_AVISO_PROCESADO, (avisoId,))

    def get_avisos(self):
        with self.cursor(cursor_type=DictCursor) as cur:
            cur.execute(self.SELECT_AVISOS)
            for row in cur:
                yield row
    #@profile
    def return_matches(self, hashes):
        mapper = dict((x.upper(), y) for x, y in hashes)
        values = mapper.keys()
        with self.cursor() as cur:
            for split_values in grouper(values, 1000):
                query = self.SELECT_MULTIPLE
                query = query % ', '.join(['UNHEX(%s)'] * len(split_values))
                cur.execute(query, split_values)
                for hash, sid, offset in cur:
                    songOffset = mapper[hash]
                    yield (sid,  songOffset - offset)

    def return_matcheslarge(self, hashes):
        mapper = {}
        map1 = tuple(hashes)
        #for hash, offset in hashes:
        for hash, offset in map1:
            mapper[hash.upper()] = offset
        values = mapper.keys()
        with self.cursor() as cur:
            for split_values in grouper(values, 1000):
                query = self.SELECT_MULTIPLE
                query = query % ', '.join(['UNHEX(%s)'] * len(split_values))
                cur.execute(query, split_values)
                for hash, sid, offset in cur:
                    avisos = [item for item in map1 if item[0] == hash.lower()]
                    for aviso in avisos:
                        yield (sid,  aviso[1] - offset)

    def obtenerAviso(self, avisoId):
        with self.cursor(cursor_type=DictCursor) as cur:
            cur.execute(self.SELECT_AVISO, (avisoId,))
            return cur.fetchone()

    def obtenerHora_horaId(self, horaId):
        with self.cursor(cursor_type=DictCursor) as cur:
            cur.execute(self.SELECT_HORA_HORAID, (horaId,))
            return cur.fetchone()


    def obtenerUltimaHora(self, nombre):
        with self.cursor(cursor_type=DictCursor) as cur:
            cur.execute(self.SELECT_ULTIMA_HORA)
            return cur.fetchone()

    def obtenerHoras(self, nombre, fecha):
        #TODO: Implementar filtro por fecha
        lista = []
        query = self.SELECT_HORAS_LIKENOMBRE
        #query = self.SELECT_HORAS.join(query)
        with self.cursor(cursor_type=DictCursor) as cur:
            cur.execute(query, (nombre,))
            lista = [row for row in cur]
        return lista

    def obtenerAvisos(self, nombre, fecha):
        # TODO: Implementar filtro por fecha
        lista = []
        query = self.SELECT_AVISOS_LIKENOMBRE
        with self.cursor(cursor_type=DictCursor) as cur:
            cur.execute(query, (nombre,))
            lista = [row for row in cur]
        return lista

def cursor_factory(**factory_options):
    def cursor(**options):
        options.update(factory_options)
        return Cursor(**options)
    return cursor

def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return (filter(None, values) for values
            in izip_longest(fillvalue=fillvalue, *args))

class Cursor(object):
    _cache = Queue.Queue(maxsize=5)
    def __init__(self, cursor_type=mysql.cursors.Cursor, **options):
        super(Cursor, self).__init__()

        try:
            conn = self._cache.get_nowait()
        except Queue.Empty:
            conn = mysql.connect(**options)
        else:
            conn.ping(True)

        self.conn = conn
        self.conn.autocommit(False)
        self.cursor_type = cursor_type

    @classmethod
    def clear_cache(cls):
        cls._cache = Queue.Queue(maxsize=5)

    def __enter__(self):
        self.cursor = self.conn.cursor(self.cursor_type)
        return self.cursor

    def __exit__(self, extype, exvalue, traceback):
        if extype is mysql.MySQLError:
            self.cursor.rollback()
        self.cursor.close()
        self.conn.commit()
        try:
            self._cache.put_nowait(self.conn)
        except Queue.Full:
            self.conn.close()
