from flask import Blueprint, request, jsonify
from app.utils.firebird import connect_to_firebird

respuestas_bp = Blueprint('respuestas', __name__)


@respuestas_bp.route('/guardar_respuestas', methods=['POST'])
def guardar_respuestas():
    try:
        data = request.json
        print("📥 Datos recibidos:", data)

        # Verificamos parámetros de conexión
        dsn = data.get('dsn')
        user = data.get('user')
        password = data.get('password')

        if not all([dsn, user, password]):
            return jsonify({
                'error': 'Faltan parámetros de conexión',
                'detalle': {
                    'dsn': dsn,
                    'user': user,
                    'password': '******' if password else None
                }
            }), 400

        # Intentar conectar a la BD
        conn = connect_to_firebird(dsn, user, password)
        if not conn:
            return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500

        cur = conn.cursor()

        # Obtener el siguiente respuesta_grupo_id
        cur.execute("SELECT MAX(respuesta_grupo_id) FROM respuestas")
        last_group_id = cur.fetchone()[0]
        respuesta_grupo_id = (last_group_id + 1) if last_group_id else 1

        respuestas = data.get('respuestas', [])
        if not respuestas:
            return jsonify({'error': 'No se recibieron respuestas'}), 400

        for i, respuesta in enumerate(respuestas):
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
                return jsonify({
                    'error': f'Faltan campos obligatorios en la respuesta #{i+1}',
                    'detalle': respuesta
                }), 400

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

        # Verificar si existe el procedimiento
        cur.execute("SELECT COUNT(*) FROM rdb$procedures WHERE rdb$procedure_name = 'PROC_GENERA_PEDIDO'")
        existe_proc = cur.fetchone()[0]
        pedido_clave = None

        if existe_proc:
            cur.execute("EXECUTE PROCEDURE PROC_GENERA_PEDIDO(?)", (respuesta_grupo_id,))
            print("✅ Pedido generado")

            cur.execute("SELECT CLAVE FROM PEDIDOS WHERE GRUPO_RESP = ?", (respuesta_grupo_id,))
            pedido_row = cur.fetchone()

            if pedido_row:
                pedido_clave = pedido_row[0]
                print(f"📦 Pedido clave: {pedido_clave}")
            else:
                print("⚠️ No se encontró pedido con ese grupo de respuestas.")
        else:
            print("⚠️ El procedimiento PROC_GENERA_PEDIDO no existe. Se omitió su ejecución.")

        # Guardar descuentos si vienen
        descuentos = data.get('descuentos', [])
        if descuentos and pedido_clave:
            for desc in descuentos:
                id_descuento = desc.get('id_descuento')
                monto = desc.get('monto')

                if id_descuento is not None and monto is not None:
                    cur.execute("SELECT GEN_ID(GEN_PEDIDOS_DESCUENTOS_ID, 1) FROM RDB$DATABASE")
                    nuevo_id = cur.fetchone()[0]


                    cur.execute("""
                        INSERT INTO PEDIDOS_DESCUENTOS (ID, ID_DESCUENTO, ID_PEDIDO, MONTO, CANCELADO)
                        VALUES (?, ?, ?, ?, 0)
                    """, (nuevo_id, id_descuento, pedido_clave, monto))

                    print(f"🟢 Descuento guardado: ID {nuevo_id}, descuento {id_descuento}, monto {monto}")
                else:
                    print("⚠️ Descuento ignorado por falta de datos:", desc)

        conn.commit()
        conn.close()

        return jsonify({
            'message': 'Respuestas guardadas correctamente',
            'respuesta_grupo_id': respuesta_grupo_id,
            'pedido_clave': pedido_clave,
            'procedimiento_ejecutado': bool(existe_proc),
        }), 200

    except Exception as e:
        print("❌ Excepción:", str(e))
        return jsonify({'error': str(e)}), 500