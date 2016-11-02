import MySQLdb as mysql
from itertools import izip_longest
import Queue
from MySQLdb.cursors import DictCursor
class Database(object):
    def __init__(self, **options):
        self.cursor = cursor_factory(**options)
    DROP_HUELLAS = "DROP TABLE IF EXISTS huellas;"
    DROP_SPOTS = "DROP TABLE IF EXISTS spots;"
    CREATE_HUELLAS = """
            CREATE TABLE IF NOT EXISTS `huellas` (
                 `hash` binary(10) not null,
                 `spotId` mediumint unsigned not null,
                 `offset` int unsigned not null,
             INDEX (hash),
             UNIQUE KEY `unique_constraint` (hash, spotId, offset),
             FOREIGN KEY (spotId) REFERENCES spots(spotId) ON DELETE CASCADE
        ) ENGINE=INNODB;"""
    CREATE_SPOTS = """
            CREATE TABLE IF NOT EXISTS `spots` (
                `spotId` mediumint unsigned not null auto_increment,
                `nombre` varchar(250) not null,
                `procesado` tinyint default 0,
                `sha1` binary(20) not null,
                `duracion` mediumint unsigned not null,
            PRIMARY KEY (`spotId`),
            UNIQUE KEY `spotId` (`spotId`)
        ) ENGINE=INNODB;"""

    INSERT_HUELLAS = "INSERT IGNORE INTO Huellas (hash, spotId, offset) values (UNHEX(%s), %s, %s);"
    INSERT_SPOTS = "INSERT INTO spots (nombre, sha1, duracion) values (%s, UNHEX(%s), %s);"
    DELETE_HUELLAS_NOPROCESADAS = "DELETE FROM spots WHERE procesado = 0;"
    UPDATE_SPOT_PROCESADO = "UPDATE spots SET procesado = 1 WHERE spotId = %s;"
    SELECT_SPOTS = "SELECT spotId, nombre, HEX(sha1) as sha1 FROM spots WHERE procesado = 1;"
    SELECT_MULTIPLE = "SELECT HEX(hash), spotId, offset FROM huellas WHERE hash IN (%s);"
    SELECT_SPOT = "SELECT nombre, HEX(sha1) as sha1, duracion FROM spots WHERE spotId = %s;"

    def inicializar(self):
        with self.cursor() as cur:
            cur.execute(self.CREATE_SPOTS)
            cur.execute(self.CREATE_HUELLAS)
            cur.execute(self.DELETE_HUELLAS_NOPROCESADAS)

    def limpiar(self):
        with self.cursor() as cur:
            cur.execute(self.DROP_HUELLAS)
            cur.execute(self.DROP_SPOTS)
        self.inicializar()
        print "Limpieza de tablas completa"

    def insert_spot(self, nombreSpot, hashArchivo, duracion):
        with self.cursor() as cur:
            cur.execute(self.INSERT_SPOTS, (nombreSpot, hashArchivo, duracion))
            return cur.lastrowid

    def insert_hashes(self, spotId, hashes):
        values = []
        for hash, offset in hashes:
            values.append((hash, spotId, offset))
        with self.cursor() as cur:
            for split_values in grouper(values, 1000):
                cur.executemany(self.INSERT_HUELLAS, split_values)

    def marcar_spot_procesado(self, spotId):
        with self.cursor() as cur:
            cur.execute(self.UPDATE_SPOT_PROCESADO, (spotId,))

    def get_spots(self):
        with self.cursor(cursor_type=DictCursor) as cur:
            cur.execute(self.SELECT_SPOTS)
            for row in cur:
                yield row

    def return_matches(self, hashes):
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
                    spots = [item for item in map1 if item[0] == hash.lower()]
                    for spot in spots:
                        yield (sid,  spot[1] - offset)

    def obtenerSpot(self, spotId):
        with self.cursor(cursor_type=DictCursor) as cur:
            cur.execute(self.SELECT_SPOT, (spotId,))
            return cur.fetchone()
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
            # Ping the connection before using it from the cache.
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
        # if we had a MySQL related error we try to rollback the cursor.
        if extype is mysql.MySQLError:
            self.cursor.rollback()

        self.cursor.close()
        self.conn.commit()

        # Put it back on the queue
        try:
            self._cache.put_nowait(self.conn)
        except Queue.Full:
            self.conn.close()
