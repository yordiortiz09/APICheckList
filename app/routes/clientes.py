# app/routes/clientes.py
from flask import Blueprint, request, jsonify
from app.utils.firebird import get_firebird_connection

clientes_bp = Blueprint('clientes', __name__)

@clientes_bp.route('/clientes', methods=['POST'])
def obtener_clientes():
    try:
        data = request.json
        dsn = data.get('dsn')
        user = data.get('user')
        password = data.get('password')

        if not all([dsn, user, password]):
            return jsonify({'error': 'Faltan parámetros'}), 400

        with get_firebird_connection(dsn, user, password) as conn:
            cur = conn.cursor()
            query = """
                SELECT sc_cliente.sc_clave, cat_sujcolectivos.sc_nombre
                FROM sc_cliente, cat_sujcolectivos, tipocliente
                WHERE sc_cliente.sc_clave = cat_sujcolectivos.sc_clave
                  AND sc_cliente.scc_tipo = tipocliente.clave
                  AND sc_cliente.SCC_ACTIVO = 1
            """
            cur.execute(query)
            resultados = cur.fetchall()

            clientes = [{'clave': row[0], 'nombre': row[1]} for row in resultados]

            return jsonify(clientes)

    except Exception as e:
        print(f"Error en /clientes: {str(e)}")
        return jsonify({'error': str(e)}), 500
