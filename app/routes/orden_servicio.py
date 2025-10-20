import datetime
from flask import Blueprint, request, send_file, jsonify
from app.utils.firebird import connect_to_firebird
from app.utils.pdf_service import generar_pdf
from io import BytesIO
from flask import make_response

import traceback

bp_orden = Blueprint("orden_servicio", __name__)

@bp_orden.route("/api/pdf/orden_servicio/<int:pedido_id>", methods=["POST"])
def generar_orden_servicio(pedido_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Se requiere un JSON con dsn, user y password"}), 400

        dsn = data.get("dsn")
        user = data.get("user")
        password = data.get("password")

        if not all([dsn, user, password]):
            return jsonify({"error": "Faltan parámetros: dsn, user o password"}), 400

        conn = connect_to_firebird(dsn, user, password)
        if not conn:
            return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

        cur = conn.cursor()
        pedido_id_str = str(pedido_id)

        cur.execute(f"""
            SELECT 
                p.clave, p.referencia, p.fecha, p.hora, 
                entidades.descripcion AS sucursal,
                cs.sc_nombre AS cliente_nombre
            FROM pedidos p
            LEFT OUTER JOIN entidades ON p.clvent = entidades.clave
            LEFT OUTER JOIN cat_sujcolectivos cs ON p.scc_clave = cs.sc_clave
            WHERE p.clave = {pedido_id}
        """)
        pedido_info = cur.fetchone()
        if not pedido_info:
            return jsonify({"error": "No se encontró el pedido"}), 404

        clave_pedido = pedido_info[0]
        referencia_pedido = pedido_info[1]
        fecha_pedido = pedido_info[2]
        if isinstance(fecha_pedido, str):
            try:
                fecha_pedido = datetime.strptime(fecha_pedido, "%Y-%m-%d")
            except ValueError:
              print("❌ Error al parsear la fecha del pedido, usando valor crudo.")
        hora_pedido = pedido_info[3]
        sucursal = pedido_info[4] or "No especificada"
        nombre_cliente = pedido_info[5] or "NO IDENTIFICADO"


        print(f"Pedido encontrado: {clave_pedido}, Referencia: {referencia_pedido}, Fecha: {fecha_pedido}, Hora: {hora_pedido}, Sucursal: {sucursal}")

        recolector_nombre = "NO IDENTIFICADO"
        grupo_resp = None
        firma_bytes = None  

        cur.execute(f"SELECT grupo_resp FROM pedidos WHERE clave = {pedido_id}")
        grupo_resp_row = cur.fetchone()
        if grupo_resp_row and grupo_resp_row[0]:
            grupo_resp = grupo_resp_row[0]

            cur.execute(f"""
                SELECT FIRST 1 sc_clave 
                FROM respuestas 
                WHERE respuesta_grupo_id = {grupo_resp}
            """)
            sc_row = cur.fetchone()
            if sc_row and sc_row[0]:
                sc_clave = sc_row[0]
                cur.execute(f"""
                    SELECT c.SC_NOMBRE 
                    FROM USERS_APP u
                    JOIN CAT_SUJCOLECTIVOS c ON u.SC_CLAVE = c.SC_CLAVE
                    WHERE u.SC_CLAVE = '{sc_clave}'
                """)
                nombre_row = cur.fetchone()
                if nombre_row:
                    recolector_nombre = nombre_row[0]

            cur.execute(f"""
                SELECT FIRST 1 FIRMA
                FROM RESPUESTAS
                WHERE RESPUESTA_GRUPO_ID = {grupo_resp}
                AND FIRMA IS NOT NULL
            """)
            firma_row = cur.fetchone()
            if firma_row and firma_row[0]:
                firma_bytes = bytes(firma_row[0])  

        def obtener_campo(clavecampo):
            cur.execute(f"""
                SELECT pc_valor FROM pedidoscampos
                WHERE pc_claveventa = {pedido_id}
                AND cc_clavecampo = {clavecampo}
            """)
            resultado = cur.fetchone()
            return resultado[0] if resultado else ""

        datos = {
            "NOMBRE DE LA MASCOTA": obtener_campo(13),
            "VETERINARIO": obtener_campo(14),
            "RAZA": obtener_campo(15),
            "PESO": obtener_campo(16),
            "EDAD": obtener_campo(17),
            "CAUSA DE MUERTE": obtener_campo(18),
            "DUEÑO O CONTRATANTE": nombre_cliente,
            "DOMICILIO": obtener_campo(22),
            "TELEFONO(S)": obtener_campo(23),
            "¿CÓMO SUPO DE NOSOTROS?": obtener_campo(20),
            "LUGAR DE RECOLECCION": obtener_campo(21),
            "ESPECIFICACIONES": "",
            "FAMILIA": obtener_campo(19),
            "FECHA DE LIQUIDACIÓN": obtener_campo(24),
        }

        cur.execute(f"""
            SELECT "COMMENT"
            FROM PEDIDOS
            WHERE CLAVE = {pedido_id}
        """)
        comment_row = cur.fetchone()
        if comment_row and comment_row[0]:
            try:
                comentario = str(comment_row[0])
                datos["ESPECIFICACIONES"] = comentario
            except Exception:
                datos["ESPECIFICACIONES"] = ""
                
        cur.execute(f"""
            SELECT pedidosartic.clave, pedidosartic.clvarticulo, articuloventa.nombre,
                   ROUND((pedidosartic.cantidadalter * pedidosartic.precioalter) + 
                         ((pedidosartic.cantidadalter * pedidosartic.precioalter)*0.16)) AS importe
            FROM pedidosartic
            LEFT OUTER JOIN articuloventa ON pedidosartic.clvarticulo = articuloventa.clave
            WHERE pedidosartic.clvventa = {pedido_id}
        """)
        articulos = [{"nombre": row[2], "importe": row[3]} for row in cur.fetchall()]

        cur.execute(f"""
            SELECT COALESCE(SUM(monto), 0)
            FROM pedidos_descuentos
            WHERE id_pedido = {pedido_id} AND cancelado = 0
        """)
        total_descuentos = cur.fetchone()[0] or 0.0

        cur.execute("""
             SELECT FIRST 1 c.DESCRIPCION
             FROM pedidos_descuentos p
             JOIN cat_descuento_pedido c ON p.id_descuento = c.id_descuento
             WHERE CAST(p.id_pedido AS INTEGER) = ? AND p.cancelado = 0
                    
         """, (pedido_id,))
        row = cur.fetchone()
        descripcion_descuento = row[0] if row else ""

        campos_pago = {
            "tipo_pago": obtener_campo(4),
            "monto": obtener_campo(1),
            "forma_pago": obtener_campo(25),
            "otros": obtener_campo(26),
        }

        pdf_bytes = generar_pdf(
            datos, articulos, campos_pago,
            clave_pedido, referencia_pedido,
            fecha_pedido, hora_pedido,
            sucursal, recolector_nombre,
            total_descuentos, descripcion_descuento,
            firma_bytes  
        )

        print("✅ PDF generado exitosamente")
        response = make_response(pdf_bytes)
        response.headers.set('Content-Type', 'application/pdf')
        response.headers.set('Content-Disposition', f'attachment; filename=orden_servicio_{pedido_id}.pdf')
        return response

    except Exception as e:
        print("Error en /api/pdf/orden_servicio:", e)
        traceback.print_exc()
        return jsonify({"error": f"Ocurrió un error: {str(e)}"}), 500

    finally:
        if 'cur' in locals() and cur:
            cur.close()
        if 'conn' in locals() and conn:
            conn.close()
