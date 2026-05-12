from flask import Blueprint, request, jsonify
from app.utils.firebird import connect_to_firebird
from app.utils.logging_utils import log_info, log_warning, log_error, limpiar_texto_error

conexion_bp = Blueprint('conexion', __name__)

@conexion_bp.route('/test_connection', methods=['POST'])
def test_connection():
    """
    Endpoint para probar la conexion a Firebird con parametros enviados en la solicitud.
    """
    try:
        log_info('Inicio test_connection')
        data = request.json or {}
        dsn = data.get('dsn')
        user = data.get('user')
        password = data.get('password')

        if not all([dsn, user, password]):
            log_warning('Faltan parametros en test_connection')
            return jsonify({
                'success': False,
                'message': 'Faltan parametros: dsn, user, password'
            }), 400

        conn = connect_to_firebird(dsn, user, password)
        if conn:
            conn.close()
            log_info('Conexion a Firebird exitosa')
            return jsonify({
                'success': True,
                'message': 'Conexion exitosa a Firebird'
            }), 200
        else:
            log_warning('No se pudo conectar a Firebird (None retornado)')
            return jsonify({
                'success': False,
                'message': 'No se pudo conectar a la base de datos'
            }), 503

    except Exception as e:
        log_error('Error en test_connection', excepcion=e)
        return jsonify({
            'success': False,
            'message': f'Error al intentar conectar: {limpiar_texto_error(str(e))}'
        }), 500
