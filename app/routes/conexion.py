from flask import Blueprint, request, jsonify
from app.utils.firebird import connect_to_firebird

conexion_bp = Blueprint('conexion', __name__)

@conexion_bp.route('/test_connection', methods=['POST'])
def test_connection():
    """
    Endpoint para probar la conexión a Firebird con parámetros enviados en la solicitud.
    """
    try:
        data = request.json
        dsn = data.get('dsn')
        user = data.get('user')
        password = data.get('password')

        if not all([dsn, user, password]):
            return jsonify({'success': False, 'message': 'Faltan parámetros: dsn, user, password'}), 400

        conn = connect_to_firebird(dsn, user, password)
        if conn:
            conn.close()
            return jsonify({'success': True, 'message': 'Conexión exitosa a Firebird'}), 200
        else:
            return jsonify({'success': False, 'message': 'No se pudo conectar a la base de datos'}), 500

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500
    
