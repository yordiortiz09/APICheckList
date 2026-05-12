# app/utils/firebird.py
import fdb
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)


def connect_to_firebird(dsn, user, password):
    try:
        connection = fdb.connect(
            dsn=dsn,
            user=user,
            password=password
        )
        logger.info('Conexion establecida con Firebird')
        return connection
    except Exception as e:
        logger.error(f'Error conectando a Firebird: {str(e)}', exc_info=True)
        return None


@contextmanager
def get_firebird_connection(dsn, user, password):
    """
    Context manager para manejar conexiones de Firebird de forma segura.
    Asegura que las conexiones siempre se cierren, incluso si hay errores.

    Uso:
        with get_firebird_connection(dsn, user, password) as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM tabla")
    """
    conn = None
    try:
        conn = fdb.connect(
            dsn=dsn,
            user=user,
            password=password
        )
        logger.info('Conexion establecida con Firebird')
        yield conn
    except Exception as e:
        logger.error(f'Error en conexion Firebird: {str(e)}', exc_info=True)
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
        raise
    finally:
        if conn:
            try:
                conn.close()
                logger.info('Conexion cerrada correctamente')
            except Exception as e:
                logger.error(f'Error cerrando conexion: {str(e)}', exc_info=True)
