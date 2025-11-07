# app/utils/firebird.py
import fdb
from contextlib import contextmanager

def connect_to_firebird(dsn, user, password):
    try:
        connection = fdb.connect(
            dsn=dsn,
            user=user,
            password=password
        )
        print("Conexión establecida con Firebird")
        return connection
    except Exception as e:
        print(f"Error conectando a Firebird: {str(e)}")
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
            # La conexión se cierra automáticamente al salir del bloque
    """
    conn = None
    try:
        conn = fdb.connect(
            dsn=dsn,
            user=user,
            password=password
        )
        print("Conexión establecida con Firebird")
        yield conn
    except Exception as e:
        print(f"Error en conexión Firebird: {str(e)}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            try:
                conn.close()
                print("Conexión cerrada correctamente")
            except Exception as e:
                print(f"Error cerrando conexión: {str(e)}")
