# app/utils/firebird.py
import fdb

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
