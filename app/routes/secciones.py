from flask import Blueprint, request, jsonify
from app.utils.firebird import connect_to_firebird

secciones_bp = Blueprint('secciones', __name__)

@secciones_bp.route('/secciones/<int:seccion_id>', methods=['DELETE'])
def eliminar_seccion(seccion_id):
    try:
        data = request.json
        dsn = data.get('dsn')
        user = data.get('user')
        password = data.get('password')

        if not all([dsn, user, password]):
            return jsonify({'error': 'Faltan parámetros: dsn, user, password'}), 400

        conn = connect_to_firebird(dsn, user, password)
        if not conn:
            return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500

        cur = conn.cursor() 
        cur.execute("DELETE FROM secciones WHERE id = ?", (seccion_id,))
        conn.commit()

        if cur.rowcount == 0:
                return jsonify({'error': 'No se encontró la sección con el ID proporcionado'}), 404

        return jsonify({'message': 'Sección eliminada correctamente'}), 200

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@secciones_bp.route('/secciones', methods=['POST'])
def insertar_seccion():
    try:
        data = request.json
        dsn = data.get('dsn')
        user = data.get('user')
        password = data.get('password')
        formulario_id = data.get('formulario_id')
        nombre = data.get('nombre')

        if not all([dsn, user, password, formulario_id, nombre]):
            return jsonify({'error': 'Faltan parámetros: dsn, user, password, formulario_id, nombre'}), 400

        conn = connect_to_firebird(dsn, user, password)
        if not conn:
            return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500

        cur = conn.cursor()
        cur.execute(
            "INSERT INTO secciones (formulario_id, nombre) VALUES (?, ?) RETURNING id",
            (formulario_id, nombre)
        )
        seccion_id = cur.fetchone()[0]
        conn.commit()

        return jsonify({'id': seccion_id, 'message': 'Sección insertada correctamente'}), 200

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500
    

@secciones_bp.route('/secciones/<int:seccion_id>', methods=['PUT'])
def actualizar_seccion(seccion_id):
    try:
        data = request.json
        dsn = data.get('dsn')
        user = data.get('user')
        password = data.get('password')
        nombre = data.get('nombre')

        if not all([dsn, user, password, nombre]):
            return jsonify({'error': 'Faltan parámetros: dsn, user, password, nombre'}), 400

        conn = connect_to_firebird(dsn, user, password)
        if not conn:
            return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500

        cur = conn.cursor() 
        cur.execute(
            "UPDATE secciones SET nombre = ? WHERE id = ?",
            (nombre, seccion_id)
        )
        conn.commit()

        return jsonify({'id': seccion_id, 'message': 'Sección actualizada correctamente'}), 200

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500


