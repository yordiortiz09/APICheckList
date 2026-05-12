# app/routes/clientes.py
from flask import Blueprint, request, jsonify
from app.utils.firebird import get_firebird_connection
from app.utils.logging_utils import log_info, log_warning, log_error

clientes_bp = Blueprint('clientes', __name__)

@clientes_bp.route('/clientes', methods=['POST'])
def obtener_clientes():
    try:
        log_info('Inicio obtener_clientes')
        data = request.json or {}
        dsn = data.get('dsn')
        user = data.get('user')
        password = data.get('password')

        if not all([dsn, user, password]):
            log_warning('Faltan parametros de conexion en /clientes')
            return jsonify({'error': 'Faltan parametros'}), 400

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
            log_info(f'Clientes retornados: {len(clientes)}')

            return jsonify(clientes)

    except Exception as e:
        log_error('Error en /clientes', excepcion=e)
        return jsonify({
            'error': 'Error obteniendo clientes',
            'detalle': str(e)
        }), 500
