from flask import Blueprint, request, jsonify
from app.utils.firebird import get_firebird_connection

descuentos_bp = Blueprint('descuentos', __name__)


@descuentos_bp.route('/descuentos/catalogo', methods=['POST'])
def obtener_catalogo_descuentos():
    try:
        data = request.json
        dsn = data.get('dsn')
        user = data.get('user')
        password = data.get('password')

        with get_firebird_connection(dsn, user, password) as conn:
            cur = conn.cursor()
            cur.execute("SELECT ID_DESCUENTO, DESCRIPCION FROM CAT_DESCUENTO_PEDIDO")
            rows = cur.fetchall()

            descuentos = [{"id": row[0], "descripcion": row[1]} for row in rows]
            return jsonify(descuentos), 200

    except Exception as e:
        print(f"🔴 Error al obtener catálogo de descuentos: {str(e)}")
        return jsonify({"error": str(e)}), 500


@descuentos_bp.route('/descuentos/guardar', methods=['POST'])
def guardar_descuento_pedido():
    try:
        data = request.json
        dsn = data.get('dsn')
        user = data.get('user')
        password = data.get('password')

        id_pedido = data.get('id_pedido')
        id_descuento = data.get('id_descuento')
        monto = data.get('monto')

        if not all([dsn, user, password, id_pedido, id_descuento, monto]):
            return jsonify({'error': 'Faltan parámetros obligatorios'}), 400

        with get_firebird_connection(dsn, user, password) as conn:
            cur = conn.cursor()

            # Obtener nuevo ID
            cur.execute("SELECT COALESCE(MAX(ID), 0) + 1 FROM PEDIDOS_DESCUENTOS")
            nuevo_id = cur.fetchone()[0]

            cur.execute("""
                INSERT INTO PEDIDOS_DESCUENTOS (ID, ID_DESCUENTO, ID_PEDIDO, MONTO, CANCELADO)
                VALUES (?, ?, ?, ?, 0)
            """, (nuevo_id, id_descuento, id_pedido, monto))

            conn.commit()
            print(f"🟢 Descuento guardado para pedido {id_pedido} (ID: {nuevo_id})")
            return jsonify({'id': nuevo_id, 'message': 'Descuento guardado correctamente'}), 200

    except Exception as e:
        print(f"🔴 Error al guardar descuento: {str(e)}")
        return jsonify({'error': str(e)}), 500
