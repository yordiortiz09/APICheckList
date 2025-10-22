from flask import Blueprint, request, jsonify
from app.utils.firebird import connect_to_firebird

preguntas_bp = Blueprint('preguntas', __name__)

@preguntas_bp.route('/preguntas', methods=['POST'])
def insertar_pregunta():
    try:
        data = request.json
        dsn = data.get('dsn')
        user = data.get('user')
        password = data.get('password')       
        seccion_id = data.get('seccion_id')
        pregunta_padre_id = data.get('pregunta_padre_id')
        pregunta_padre_opcion_id = data.get('pregunta_padre_opcion_id')
        texto = data.get('texto')
        tipo = data.get('tipo')
        con_filas = data.get('con_filas', False)
        con_foto = data.get('con_foto', False)

        if not all([dsn, user, password, texto, tipo]):
            return jsonify({'error': 'Faltan parámetros obligatorios'}), 400

        conn = connect_to_firebird(dsn, user, password)
        if not conn:
            return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500

        cur = conn.cursor()

        # 🔹 Validar que la pregunta tenga un padre o una sección
        if seccion_id is None and pregunta_padre_id is None and pregunta_padre_opcion_id is None:
            return jsonify({'error': 'Error: Una pregunta debe pertenecer a una sección o tener un padre'}), 400

        cur.execute("""
            INSERT INTO preguntas (seccion_id, pregunta_padre_id, pregunta_padre_opcion_id, texto, tipo, con_filas, con_foto)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            RETURNING id
        """, (seccion_id, pregunta_padre_id, pregunta_padre_opcion_id, texto, tipo, con_filas, con_foto))

        pregunta_id = cur.fetchone()[0]
        conn.commit()
        print(f'🟢 Pregunta insertada en BD: ID {pregunta_id}, Sección: {seccion_id}, PadrePregunta: {pregunta_padre_id}, PadreOpción: {pregunta_padre_opcion_id}')
        return jsonify({'id': pregunta_id, 'message': 'Pregunta insertada correctamente'}), 200

    except Exception as e:
        print(f"🔴 Error al insertar pregunta: {str(e)}")
        return jsonify({'error': str(e)}), 500

@preguntas_bp.route('/preguntas/<int:pregunta_id>', methods=['PUT'])
def actualizar_pregunta(pregunta_id):
    try:
        data = request.json
        dsn = data.get('dsn')
        user = data.get('user')
        password = data.get('password')
        texto = data.get('texto')
        tipo = data.get('tipo')
        con_filas = data.get('con_filas', False)
        con_foto = data.get('con_foto', False)
        pregunta_padre_id = data.get('pregunta_padre_id')
        pregunta_padre_opcion_id = data.get('pregunta_padre_opcion_id')
        seccion_id = data.get('seccion_id')

        if not all([dsn, user, password, texto, tipo]):
            return jsonify({'error': 'Faltan parámetros'}), 400

        conn = connect_to_firebird(dsn, user, password)
        if not conn:
            return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500

        cur = conn.cursor()

        # 🔹 Verificar si la pregunta existe antes de actualizar
        cur.execute("SELECT seccion_id FROM preguntas WHERE id = ?", (pregunta_id,))
        pregunta_existente = cur.fetchone()
        if not pregunta_existente:
            return jsonify({'error': 'La pregunta no existe'}), 404

        seccion_id_actual = pregunta_existente[0]

        # 🔹 Validación: Si no tiene sección, debe tener un padre
        if seccion_id is None and pregunta_padre_id is None and pregunta_padre_opcion_id is None:
            return jsonify({'error': 'Error: Una pregunta debe tener una sección o un padre'}), 400

        # 🔹 Construcción dinámica de la actualización
        campos_a_actualizar = []
        valores = []

        if texto:
            campos_a_actualizar.append("texto = ?")
            valores.append(texto)
        if tipo:
            campos_a_actualizar.append("tipo = ?")
            valores.append(tipo)
        if isinstance(con_filas, bool):
            campos_a_actualizar.append("con_filas = ?")
            valores.append(int(con_filas))
        if isinstance(con_foto, bool):
            campos_a_actualizar.append("con_foto = ?")
            valores.append(int(con_foto))
        if pregunta_padre_id is not None:
            campos_a_actualizar.append("pregunta_padre_id = ?")
            valores.append(pregunta_padre_id)
        if pregunta_padre_opcion_id is not None:
            campos_a_actualizar.append("pregunta_padre_opcion_id = ?")
            valores.append(pregunta_padre_opcion_id)
        if seccion_id is not None:
            campos_a_actualizar.append("seccion_id = ?")
            valores.append(seccion_id)

        if not campos_a_actualizar:
            return jsonify({'message': 'No hay cambios para actualizar'}), 200

        sql_update = f"UPDATE preguntas SET {', '.join(campos_a_actualizar)} WHERE id = ?"
        valores.append(pregunta_id)

        cur.execute(sql_update, valores)
        conn.commit()

        return jsonify({'id': pregunta_id, 'message': 'Pregunta actualizada correctamente'}), 200

    except Exception as e:
        print(f"🔴 Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

@preguntas_bp.route('/preguntas/<int:pregunta_id>', methods=['DELETE'])
def eliminar_pregunta(pregunta_id):
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
        cur.execute("DELETE FROM preguntas WHERE id = ?", (pregunta_id,))
        conn.commit()
        if cur.rowcount == 0:
            return jsonify({'error': 'No se encontró la pregunta con el ID proporcionado'}), 404

        return jsonify({'message': f'Pregunta con ID {pregunta_id} eliminada correctamente'}), 200

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
