from flask import Blueprint, request, jsonify
from app.utils.firebird import connect_to_firebird

respuestas_bp = Blueprint('respuestas', __name__)

@respuestas_bp.route('/guardar_respuestas', methods=['POST'])
def guardar_respuestas():
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

        cur.execute("SELECT MAX(respuesta_grupo_id) FROM respuestas")
        last_group_id = cur.fetchone()[0]
        respuesta_grupo_id = (last_group_id + 1) if last_group_id else 1

        for respuesta in data['respuestas']:
            formulario_id = respuesta.get('formulario_id')
            seccion_id = respuesta.get('seccion_id')
            pregunta_id = respuesta.get('pregunta_id')
            columna_id = respuesta.get('columna_id')
            texto_respuesta = respuesta.get('texto_respuesta')
            numero_respuesta = respuesta.get('numero_respuesta')
            sc_clave = respuesta.get('sc_clave')
            firma_base64 = respuesta.get('firma')
            cantidad = respuesta.get('cantidad')
            precio_unitario = respuesta.get('precio_unitario')
            importe_total = respuesta.get('importe_total')
            articulo_clave = respuesta.get('articulo_clave')

            if not all([formulario_id, seccion_id, pregunta_id, sc_clave]):
                return jsonify({'error': 'Faltan datos en una de las respuestas'}), 400

            firma_binaria = None
            if firma_base64:
                import base64
                firma_binaria = base64.b64decode(firma_base64)

            cur.execute("""
                INSERT INTO respuestas (
                    formulario_id, seccion_id, pregunta_id, columna_id,
                    texto_respuesta, numero_respuesta, sc_clave, firma,
                    cantidad, precio_unitario, importe_total, articulo_clave,
                    respuesta_grupo_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                formulario_id, seccion_id, pregunta_id, columna_id,
                texto_respuesta, numero_respuesta, sc_clave, firma_binaria,
                cantidad, precio_unitario, importe_total, articulo_clave,
                respuesta_grupo_id 
            ))

        cur.execute("SELECT COUNT(*) FROM rdb$procedures WHERE rdb$procedure_name = 'PROC_GENERA_PEDIDO'")
        existe_proc = cur.fetchone()[0]

        if existe_proc:
            print(respuesta_grupo_id)
            cur.execute("EXECUTE PROCEDURE PROC_GENERA_PEDIDO(?)", (respuesta_grupo_id,))
            print("PEDIDO GENERADO")
        else:
            print("⚠️ El procedimiento PROC_GENERA_PEDIDO no existe. Se omitió su ejecución.")

        conn.commit()
        conn.close()

        return jsonify({
            'message': 'Respuestas guardadas correctamente',
            'respuesta_grupo_id': respuesta_grupo_id,
            'procedimiento_ejecutado': bool(existe_proc)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
