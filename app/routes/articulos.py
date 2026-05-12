# app/routes/articulos.py
from flask import Blueprint, request, jsonify
from decimal import Decimal
from app.utils.firebird import get_firebird_connection
from app.utils.logging_utils import log_info, log_warning, log_error

articulos_bp = Blueprint('articulos', __name__)

@articulos_bp.route('/servicios', methods=['POST'])
def obtener_todos_los_articulos():
    try:
        log_info('Inicio obtener_todos_los_articulos')
        data = request.json or {}
        dsn = data.get('dsn')
        user = data.get('user')
        password = data.get('password')

        if not all([dsn, user, password]):
            log_warning('Faltan parametros de conexion en /servicios')
            return jsonify({'error': 'Faltan parametros: dsn, user, password'}), 400

        with get_firebird_connection(dsn, user, password) as conn:
            cur = conn.cursor()
            cur.execute("SELECT clave, nombre, unidad, precio FROM ARTICULOVENTA")
            resultados = cur.fetchall()

            articulos = [
                {
                    'clave': row[0],
                    'nombre': row[1],
                    'unidad': row[2],
                    'precio': float(round(row[3] + (row[3] * Decimal('0.16')), 2))
                }
                for row in resultados
            ]
            log_info(f'Articulos retornados: {len(articulos)}')

            return jsonify(articulos)

    except Exception as e:
        log_error('Error en /servicios', excepcion=e)
        return jsonify({
            'error': 'Error obteniendo servicios',
            'detalle': str(e)
        }), 500
