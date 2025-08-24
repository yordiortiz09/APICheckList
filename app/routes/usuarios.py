from flask import Blueprint, request, jsonify
from app.utils.firebird import connect_to_firebird
from app.utils.queries_pedidos import CAMPOS_PEDIDO
import traceback



usuarios_bp = Blueprint('usuarios', __name__)

@usuarios_bp.route('/sync_users', methods=['POST'])
def sync_users():
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
        cur.execute("""
            SELECT
                users.SC_CLAVE AS id,
                users.TIPORIGHT AS role,
                catj.SC_NOMBRE AS name,
                'grupostr@grupostr.com' AS email
            FROM
                USERS users
            JOIN CAT_SUJCOLECTIVOS catj ON users.SC_CLAVE = catj.SC_CLAVE;
        """)
        rows = cur.fetchall()

        users = [
            {
                'id': row[0],
                'role': row[1],
                'name': row[2],
                'email': row[3]
            } for row in rows
        ]

        return jsonify({'success': True, 'users': users}), 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
@usuarios_bp.route('/verify_user', methods=['POST'])
def verify_user():
    """Verifica si el usuario y la contraseña son correctos."""
    try:
        data = request.json
        user_id = data.get('user_id')  
        password = data.get('password')  
        
        dsn = data.get('dsn')
        user = data.get('user')
        db_password = data.get('db_password')  

        if not all([user_id, password, dsn, user, db_password]):
            return jsonify({'error': 'Faltan parámetros: user_id, password, dsn, user, db_password'}), 400

        conn = connect_to_firebird(dsn, user, db_password)
        if not conn:
            return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500

        cur = conn.cursor()
       

        cur.execute("SELECT PASS, ROL FROM USERS_APP WHERE SC_CLAVE = ?", (user_id,))
        row = cur.fetchone()

        if row and row[0] == password:
            user_role = row[1] 
            return jsonify({
                'success': True,
                'message': 'Usuario verificado correctamente',
                'role': user_role
            }), 200


    except Exception as e:
        return jsonify({'error': str(e)}), 500


@usuarios_bp.route('/get_users', methods=['POST'])
def get_users():
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
        cur.execute("""
            SELECT 
                u.ID, 
                u.SC_CLAVE, 
                c.SC_NOMBRE, 
                u.ROL
            FROM 
                USERS_APP u
            JOIN 
                CAT_SUJCOLECTIVOS c ON u.SC_CLAVE = c.SC_CLAVE
        """)
        rows = cur.fetchall()

        usuarios = []
        for row in rows:
            usuarios.append({
                'id': row[0],
                'sc_clave': row[1],
                'sc_nombre': row[2],
                'rol': row[3]
            })

        conn.close()

        return jsonify({'usuarios': usuarios}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@usuarios_bp.route('/get_pedidos', methods=['POST'])
def get_pedidos():
    try:
        data = request.json
        sc_clave = data.get('sc_clave')
        dsn = data.get('dsn')
        user = data.get('user')
        password = data.get('password')
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')

        if not all([sc_clave, dsn, user, password, fecha_inicio, fecha_fin]):
            return jsonify({'error': 'Faltan parámetros: sc_clave, dsn, user, password, fecha_inicio, fecha_fin'}), 400

        conn = connect_to_firebird(dsn, user, password)
        if not conn:
            return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500

        cur = conn.cursor()
        cur.execute("""
            SELECT 
          P.CLAVE, 
          P.FECHA, 
          P.TOTAL, 
          P.ESTADO, 
          P.CANCELADO,
          (
            SELECT PC.PC_VALOR
            FROM PEDIDOSCAMPOS PC
            WHERE PC.PC_CLAVEVENTA = P.CLAVE AND PC.CC_CLAVECAMPO = 13
            FETCH FIRST 1 ROWS ONLY
          ) AS MASCOTA,
          (
            SELECT PC.PC_VALOR
            FROM PEDIDOSCAMPOS PC
            WHERE PC.PC_CLAVEVENTA = P.CLAVE AND PC.CC_CLAVECAMPO = 22
            FETCH FIRST 1 ROWS ONLY
          ) AS LUGAR_RECOLECCION,
          (
            SELECT COUNT(*)
            FROM PEDIDOSARTIC A
            WHERE A.CLVVENTA = P.CLAVE
          ) AS NUM_PRODUCTOS
        FROM PEDIDOS P
        WHERE P.SCP_CLAVEVENDEDOR = ?
          AND P.FECHA BETWEEN ? AND ?
        ORDER BY P.FECHA DESC
        
              """, (sc_clave, fecha_inicio, fecha_fin))
        
                
        rows = cur.fetchall()
                
        pedidos = [
            {
                'clave': row[0],
                'fecha': str(row[1]),
                'total': float(row[2]),
                'estado': row[3],
                'cancelado': row[4],
                'mascota': row[5] or 'Sin nombre',
                'lugar_recoleccion': row[6] or 'No especificado',
                'num_productos': row[7]
            } for row in rows
        ]

        
        conn.close()
        return jsonify({'pedidos': pedidos}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@usuarios_bp.route('/get_pedido_detalle/<clave_pedido>', methods=['POST'])
def get_pedido_detalle(clave_pedido):
    try:
        data = request.json
        dsn = data.get('dsn')
        user = data.get('user')
        password = data.get('password')

        if not all([dsn, user, password]):
            return jsonify({'error': 'Faltan parámetros'}), 400

        conn = connect_to_firebird(dsn, user, password)
        if not conn:
            return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500

        cur = conn.cursor()

        cur.execute("""
            SELECT p.referencia, p.fecha, p.hora, e.descripcion as sucursal, p.scc_clave, p."COMMENT"
            FROM pedidos p
            LEFT JOIN entidades e ON p.clvent = e.clave
            WHERE p.clave = ?
        """, (clave_pedido,))
        pedido_info = cur.fetchone()

        if not pedido_info:
            return jsonify({'error': 'Pedido no encontrado'}), 404

        referencia, fecha_pedido, hora_pedido, sucursal, cliente_clave, comentario_blob = pedido_info

        fecha_pedido = str(fecha_pedido) if fecha_pedido else ""
        hora_pedido = str(hora_pedido) if hora_pedido else ""

        if comentario_blob:
            try:
                especificaciones = comentario_blob.read()
                if isinstance(especificaciones, bytes):
                    especificaciones = especificaciones.decode('utf-8')
            except AttributeError:
                if isinstance(comentario_blob, bytes):
                    especificaciones = comentario_blob.decode('utf-8')
                else:
                    especificaciones = str(comentario_blob)
        else:
            especificaciones = ""

        def obtener_campo(clavecampo):
            cur.execute("""
                SELECT pc_valor FROM pedidoscampos
                WHERE pc_claveventa = ?
                AND cc_clavecampo = ?
            """, (clave_pedido, clavecampo))
            resultado = cur.fetchone()
            return resultado[0] if resultado else ""

        campos = {
            "nombre_mascota": obtener_campo(13),
            "veterinario": obtener_campo(14),
            "raza": obtener_campo(15),
            "peso": obtener_campo(16),
            "edad": obtener_campo(17),
            "causa": obtener_campo(18),
            "contratante": obtener_campo(19),
            "domicilio": obtener_campo(22),
            "telefono": obtener_campo(23),
            "difusion": obtener_campo(20),
            "lugar": obtener_campo(21),
            "forma_pago": obtener_campo(25),
            "tipo_pago": obtener_campo(4),
            "monto": obtener_campo(1),
            "otros": obtener_campo(26),
            "fecha_liquidacion": obtener_campo(24),
        }

        print(f"Campos obtenidos: {campos}")

        cur.execute("""
            SELECT 
                pedidosartic.clave,
                pedidosartic.clvarticulo,
                articuloventa.nombre,
                articuloventa.unidad,
                COALESCE(pedidosartic.cantidadalter, 0) AS cantidad,
                COALESCE(pedidosartic.precioalter, 0) AS precio_sin_iva,
                ROUND(COALESCE(pedidosartic.cantidadalter, 0) * COALESCE(pedidosartic.precioalter, 0) * 1.16, 2) AS importe_con_iva,
                ROUND(COALESCE(pedidosartic.precioalter, 0) * 1.16, 2) AS precio_con_iva
            FROM pedidosartic
            LEFT JOIN articuloventa ON pedidosartic.clvarticulo = articuloventa.clave
            WHERE pedidosartic.clvventa = ?
        """, (clave_pedido,))

        articulos_raw = cur.fetchall()
        articulos = [
            {
                'clave': row[1] or '',
                'claveArticulo': row[1] or '',
                'nombre': row[2] or 'Sin nombre',
                'unidad': row[3] or '',
                'cantidad': float(row[4]) if row[4] is not None else 0,
                'precio_unitario': float(row[7]) if row[7] is not None else 0,
                'importe': float(row[6]) if row[6] is not None else 0,
            }
            for row in articulos_raw
        ]

        cur.execute("""
            SELECT p.id_descuento, c.descripcion, p.monto
            FROM pedidos_descuentos p
            JOIN cat_descuento_pedido c ON p.id_descuento = c.id_descuento
            WHERE p.id_pedido = ? AND p.cancelado = 0
        """, (clave_pedido,))

        descuentos_raw = cur.fetchall()
        descuentos = [
            {
                'id_descuento': row[0],
                'descripcion': row[1],
                'monto': float(row[2]) if row[2] is not None else 0
                
                
            }
            for row in descuentos_raw
        ]

        conn.close()

        return jsonify({
            'referencia': referencia,
            'fecha_pedido': fecha_pedido,
            'hora_pedido': hora_pedido,
            'sucursal': sucursal,
            'cliente_clave': cliente_clave,
            'campos': campos,
            'articulos': articulos,
            'especificaciones': especificaciones,
            'descuentos': descuentos   
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@usuarios_bp.route('/actualizar_pedido/<clave_pedido>', methods=['POST'])
def actualizar_pedido(clave_pedido):
    try:
        print(f"Clave pedido recibida (tipo {type(clave_pedido)}): {clave_pedido}")
        data = request.json
        print(f"Datos recibidos: {data}")

        dsn = data.get('dsn')
        user = data.get('user')
        password = data.get('password')
        cambios = data.get('campos')
        articulos = data.get('articulos', [])
        descuentos = data.get('descuentos', [])
        especificaciones = data.get('especificaciones', '')

        if not all([dsn, user, password, cambios]):
            return jsonify({'error': 'Faltan parámetros'}), 400

        conn = connect_to_firebird(dsn, user, password)
        if not conn:
            return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500

        cur = conn.cursor()

        # Mapeo de campos personalizados
        CAMPOS_PEDIDO = {
            "nombre_mascota": 13,
            "veterinario": 14,
            "raza": 15,
            "peso": 16,
            "edad": 17,
            "causa": 18,
            "contratante": 19,
            "difusion": 20,
            "lugar": 21,
            "domicilio": 22,
            "telefono": 23,
            "tipo_pago": 4,
            "forma_pago": 25,
            "monto": 1,
            "otros": 26,
            "fecha_liquidacion": 24,
        }

        for campo_nombre, valor in cambios.items():
            campo_id = CAMPOS_PEDIDO.get(campo_nombre)
            if campo_id is None:
                print(f"[WARN] Campo '{campo_nombre}' no encontrado.")
                continue
        
            if valor == "" or valor is None:
                print(f"[INFO] Campo '{campo_nombre}' viene vacío, se omite.")
                continue
        
            cur.execute("""
                SELECT COUNT(*) FROM PEDIDOSCAMPOS WHERE PC_CLAVEVENTA = ? AND CC_CLAVECAMPO = ?
            """, (clave_pedido, campo_id))
            existe = cur.fetchone()[0]
        
            if existe:
                if campo_nombre == "fecha_liquidacion":
                    cur.execute("""
                        UPDATE PEDIDOSCAMPOS
                        SET PC_VALOR = ?, IPA_CONSECUTIVO = 28
                        WHERE PC_CLAVEVENTA = ? AND CC_CLAVECAMPO = ?
                    """, (valor, clave_pedido, campo_id))
                else:
                    cur.execute("""
                        UPDATE PEDIDOSCAMPOS
                        SET PC_VALOR = ?
                        WHERE PC_CLAVEVENTA = ? AND CC_CLAVECAMPO = ?
                    """, (valor, clave_pedido, campo_id))
            else:
                cur.execute("""
                    SELECT COALESCE(MAX(PC_CONSECUTIVO), 0) + 1 FROM PEDIDOSCAMPOS
                """)
                nuevo_consec = cur.fetchone()[0]
        
                if campo_nombre == "fecha_liquidacion":
                    cur.execute("""
                        INSERT INTO PEDIDOSCAMPOS (PC_CONSECUTIVO, PC_CLAVEVENTA, CC_CLAVECAMPO, PC_VALOR, IPA_CONSECUTIVO)
                        VALUES (?, ?, ?, ?, ?)
                    """, (nuevo_consec, clave_pedido, campo_id, valor, 28))
                else:
                    cur.execute("""
                        INSERT INTO PEDIDOSCAMPOS (PC_CONSECUTIVO, PC_CLAVEVENTA, CC_CLAVECAMPO, PC_VALOR)
                        VALUES (?, ?, ?, ?)
                    """, (nuevo_consec, clave_pedido, campo_id, valor))


        cur.execute("""UPDATE PEDIDOS SET "COMMENT" = ? WHERE clave = ?""", (especificaciones, clave_pedido))

        if 'referencia' in data:
            cur.execute("UPDATE PEDIDOS SET referencia = ? WHERE clave = ?", (data['referencia'], clave_pedido))
        if 'fecha_pedido' in data:
            cur.execute("UPDATE PEDIDOS SET fecha = ? WHERE clave = ?", (data['fecha_pedido'], clave_pedido))
        if 'hora_pedido' in data:
            cur.execute("UPDATE PEDIDOS SET hora = ? WHERE clave = ?", (data['hora_pedido'], clave_pedido))
        if 'cliente' in data:
            cur.execute("UPDATE PEDIDOS SET scc_clave = ? WHERE clave = ?", (data['cliente'], clave_pedido))

        cur.execute("DELETE FROM PEDIDOSARTIC WHERE CLVVENTA = ?", (clave_pedido,))

        import uuid
        for art in articulos:
            clave_articulo = art.get("claveArticulo") or art.get("clave_articulo") or art.get("clave")
            cantidad = float(art.get("cantidad", 0))
            unidad_alter = art.get("unidad") or art.get("unidadAlter") or ""
            cantidad_alter = float(art.get("cantidadAlter", cantidad))
            precio_unitario = float(art.get("precio_unitario") or art.get("precio") or 0)
            precio_alter = float(art.get("precioAlter", precio_unitario))
            iva = round(cantidad * precio_unitario * 0.16, 4)
            total = round((cantidad * precio_unitario) + iva, 4)

            clave_unica = str(uuid.uuid4())[:20]

            cur.execute("""
                INSERT INTO PEDIDOSARTIC (
                    CLAVE, CLVVENTA, CLVARTICULO, CANT, CANTIDADALTER, UNIDADALTER,
                    PRECIO, PRECIOALTER, IVA, PORIVA, TOTAL
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                clave_unica,
                clave_pedido,
                clave_articulo,
                cantidad,
                cantidad_alter,
                unidad_alter,
                precio_unitario,
                precio_alter,
                iva,
                16,
                total
            ))

        cur.execute("""
            SELECT ID_DESCUENTO FROM PEDIDOS_DESCUENTOS 
            WHERE ID_PEDIDO = ? AND CANCELADO = 0
        """, (clave_pedido,))
        descuentos_actuales = set(row[0] for row in cur.fetchall())
        
        # Obtenemos los nuevos que vienen desde el request
        descuentos_nuevos = set()
        
        for desc in descuentos:
            id_descuento = int(desc.get("id_descuento"))
            monto = float(desc.get("monto", 0))
            descuentos_nuevos.add(id_descuento)
        
            # verificamos si ya existe el descuento para este pedido, activo o cancelado
            cur.execute("""
                SELECT ID, CANCELADO FROM PEDIDOS_DESCUENTOS 
                WHERE ID_PEDIDO = ? AND ID_DESCUENTO = ?
            """, (clave_pedido, id_descuento))
            row = cur.fetchone()
        
            if row:
                id_registro, cancelado = row
                if cancelado == 1:
                    # si está cancelado, lo reactivamos y actualiza monto
                    cur.execute("""
                        UPDATE PEDIDOS_DESCUENTOS
                        SET MONTO = ?, CANCELADO = 0
                        WHERE ID = ?
                    """, (monto, id_registro))
                    print(f"descuento reactivado: ID {id_registro}, descuento {id_descuento}, monto {monto}")
                else:
                    # ya existe y está activo, solo se actualizaaa monto
                    cur.execute("""
                        UPDATE PEDIDOS_DESCUENTOS
                        SET MONTO = ?
                        WHERE ID = ?
                    """, (monto, id_registro))
                    print(f"descuento actualizado: ID {id_registro}, descuento {id_descuento}, monto {monto}")
            else:
                # no existe, se insertaa nuevo descuento
                id_unico = cur.execute("SELECT GEN_ID(GEN_PEDIDOS_DESCUENTOS_ID, 1) FROM RDB$DATABASE").fetchone()[0]
                cur.execute("""
                    INSERT INTO PEDIDOS_DESCUENTOS (ID, ID_DESCUENTO, ID_PEDIDO, MONTO, CANCELADO)
                    VALUES (?, ?, ?, ?, 0)
                """, (id_unico, id_descuento, clave_pedido, monto))
                print(f"descuento insertado: ID {id_unico}, descuento {id_descuento}, monto {monto}")
        
        ids_a_cancelar = descuentos_actuales - descuentos_nuevos
        for id_descuento in ids_a_cancelar:
            cur.execute("""
                UPDATE PEDIDOS_DESCUENTOS
                SET CANCELADO = 1
                WHERE ID_PEDIDO = ? AND ID_DESCUENTO = ?
            """, (clave_pedido, id_descuento))
            print(f"descuento cancelado: ID_DESC {id_descuento} (ya no está en el request)")



        conn.commit()
        conn.close()

        print("✅ Pedido actualizado correctamente")
        return jsonify({'mensaje': 'Pedido actualizado correctamente'}), 200

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({'error': str(e)}), 500
