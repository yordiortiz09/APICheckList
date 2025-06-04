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

        cur.execute(f"SELECT clave, referencia FROM pedidos WHERE clave = {pedido_id}")
        pedido_info = cur.fetchone()
        if not pedido_info:
            return jsonify({"error": "No se encontró el pedido"}), 404

        clave_pedido = pedido_info[0]
        referencia_pedido = pedido_info[1]

        def obtener_campo(clavecampo):
            cur.execute(f"""
                SELECT pc_valor FROM pedidoscampos
                WHERE pc_claveventa = {pedido_id}
                AND cc_clavecampo = {clavecampo}
            """)
            resultado = cur.fetchone()
            return resultado[0] if resultado else ""

        # 🔹 Datos del pedido
        datos = {
            "NOMBRE DE LA MASCOTA": obtener_campo(13),
            "VETERINARIO": obtener_campo(14),
            "RAZA": obtener_campo(15),
            "PESO": obtener_campo(16),
            "EDAD": obtener_campo(17),
            "CAUSA DE MUERTE": obtener_campo(18),
            "DUEÑO O CONTRATANTE": obtener_campo(19),
            "DOMICILIO": obtener_campo(22),
            "TELEFONO(S)": obtener_campo(23),
            "¿CÓMO SUPO DE NOSOTROS?": obtener_campo(20),
            "LUGAR DE RECOLECCION": obtener_campo(21),
            "ESPECIFICACIONES": "",
            "FAMILIA": obtener_campo(19),
        }

        query_articulos = f"""
            SELECT pedidosartic.clave, pedidosartic.clvarticulo, articuloventa.nombre articulo,
                   ROUND((pedidosartic.cantidadalter * pedidosartic.precioalter) + ((pedidosartic.cantidadalter * pedidosartic.precioalter)*0.16)) AS importe
            FROM pedidosartic
            LEFT OUTER JOIN articuloventa ON pedidosartic.clvarticulo = articuloventa.clave
            WHERE pedidosartic.clvventa = {pedido_id}
        """
        cur.execute(query_articulos)
        articulos = [{"nombre": row[2], "importe": row[3]} for row in cur.fetchall()]

        campos_pago = {
            "tipo_pago": obtener_campo(4),
            "monto": obtener_campo(1),
            "forma_pago": obtener_campo(25),
            "otros": obtener_campo(26),
        }

        pdf_bytes = generar_pdf(datos, articulos, campos_pago, clave_pedido, referencia_pedido)

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
