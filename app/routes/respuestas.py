from flask import Blueprint, request, jsonify
from app.utils.firebird import get_firebird_connection

respuestas_bp = Blueprint('respuestas', __name__)


@respuestas_bp.route('/guardar_respuestas', methods=['POST'])
def guardar_respuestas():
    try:
        data = request.json
        print("📥 Guardando respuestas...")

        dsn = data.get('dsn')
        user = data.get('user')
        password = data.get('password')

        if not all([dsn, user, password]):
            return jsonify({'error': 'Faltan parámetros de conexión'}), 400

        with get_firebird_connection(dsn, user, password) as conn:
            cur = conn.cursor()

            # Obtener el siguiente respuesta_grupo_id
            cur.execute("SELECT MAX(respuesta_grupo_id) FROM respuestas")
            last_group_id = cur.fetchone()[0]
            respuesta_grupo_id = (last_group_id + 1) if last_group_id else 1

            respuestas = data.get('respuestas', [])
            if not respuestas:
                return jsonify({'error': 'No se recibieron respuestas'}), 400

            respuesta_ids = {}

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
                    return jsonify({'error': f'Faltan campos en respuesta #{i+1}'}), 400

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

                # Obtener respuesta_id
                cur.execute("SELECT MAX(ID) FROM respuestas WHERE respuesta_grupo_id = ? AND pregunta_id = ?", 
                           (respuesta_grupo_id, pregunta_id))
                respuesta_id = cur.fetchone()[0]
                
                if respuesta_id:
                    respuesta_ids[pregunta_id] = respuesta_id

            # Procedimiento y descuentos (código existente)...
            cur.execute("SELECT COUNT(*) FROM rdb$procedures WHERE rdb$procedure_name = 'PROC_GENERA_PEDIDO'")
            existe_proc = cur.fetchone()[0]
            pedido_clave = None

            if existe_proc:
                cur.execute("EXECUTE PROCEDURE PROC_GENERA_PEDIDO(?)", (respuesta_grupo_id,))
                cur.execute("SELECT CLAVE FROM PEDIDOS WHERE GRUPO_RESP = ?", (respuesta_grupo_id,))
                pedido_row = cur.fetchone()
                if pedido_row:
                    pedido_clave = pedido_row[0]

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

            conn.commit()

            return jsonify({
                'message': 'Respuestas guardadas correctamente',
                'respuesta_grupo_id': respuesta_grupo_id,  
                'respuesta_ids': respuesta_ids,
                'pedido_clave': pedido_clave,
                'procedimiento_ejecutado': bool(existe_proc),
            }), 200

    except Exception as e:
        print("❌ Excepción:", str(e))
        return jsonify({'error': str(e)}), 500
    
@respuestas_bp.route('/guardar_fotos', methods=['POST'])
def guardar_fotos():
    """
    Guarda las fotos asociadas a las respuestas
    Body esperado:
    {
        "dsn": "...",
        "user": "...",
        "password": "...",
        "fotos": [
            {
                "respuesta_id": 123,
                "respuesta_grupo_id": 456,  // ✅ NUEVO
                "pregunta_id": 45,
                "url_s3": "https://...",
                "nombre_archivo": "abc123.jpg",
                "tamanio_bytes": 2048576,
                "tipo_contenido": "image/jpeg",
                "orden": 1
            }
        ]
    }
    """
    try:
        data = request.json
        print("📸 Guardando fotos...")

        dsn = data.get('dsn')
        user = data.get('user')
        password = data.get('password')

        if not all([dsn, user, password]):
            return jsonify({'error': 'Faltan parámetros de conexión'}), 400

        with get_firebird_connection(dsn, user, password) as conn:
            cur = conn.cursor()
            fotos = data.get('fotos', [])
            
            if not fotos:
                return jsonify({'error': 'No se recibieron fotos'}), 400

            fotos_guardadas = 0

            for foto in fotos:
                respuesta_id = foto.get('respuesta_id')
                respuesta_grupo_id = foto.get('respuesta_grupo_id') 
                pregunta_id = foto.get('pregunta_id')
                url_s3 = foto.get('url_s3')
                nombre_archivo = foto.get('nombre_archivo')
                tamanio_bytes = foto.get('tamanio_bytes')
                tipo_contenido = foto.get('tipo_contenido')
                orden = foto.get('orden', 1)

                if not all([respuesta_id, respuesta_grupo_id, pregunta_id, url_s3]):
                    print(f"⚠️ Foto ignorada por falta de datos: {foto}")
                    continue

                try:
                    cur.execute("""
                        INSERT INTO FOTOS_RESPUESTAS (
                            RESPUESTA_ID,
                            RESPUESTA_GRUPO_ID,
                            PREGUNTA_ID,
                            URL_S3,
                            NOMBRE_ARCHIVO,
                            TAMANIO_BYTES,
                            TIPO_CONTENIDO,
                            ORDEN
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        respuesta_id,
                        respuesta_grupo_id,  # ✅ NUEVO
                        pregunta_id,
                        url_s3,
                        nombre_archivo,
                        tamanio_bytes,
                        tipo_contenido,
                        orden
                    ))
                    
                    fotos_guardadas += 1
                    print(f"✅ Foto guardada: {nombre_archivo} (Grupo {respuesta_grupo_id})")

                except Exception as e:
                    print(f"❌ Error guardando foto: {e}")
                    continue

            conn.commit()

            return jsonify({
                'message': 'Fotos guardadas correctamente',
                'fotos_guardadas': fotos_guardadas,
                'fotos_recibidas': len(fotos)
            }), 200

    except Exception as e:
        print("❌ Excepción:", str(e))
        return jsonify({'error': str(e)}), 500