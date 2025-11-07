# app/routes/articulos.py
from flask import Blueprint, request, jsonify
from decimal import Decimal
from app.utils.firebird import get_firebird_connection

articulos_bp = Blueprint('articulos', __name__)

@articulos_bp.route('/servicios', methods=['POST'])
def obtener_todos_los_articulos():
    try:
        data = request.json
        dsn = data.get('dsn')
        user = data.get('user')
        password = data.get('password')

        if not all([dsn, user, password]):
            return jsonify({'error': 'Faltan parámetros: dsn, user, password'}), 400

        with get_firebird_connection(dsn, user, password) as conn:
            cur = conn.cursor()
            cur.execute("SELECT clave, nombre, unidad, precio FROM ARTICULOVENTA")
            resultados = cur.fetchall()

            articulos = [
                {
                    'clave': row[0],
                    'nombre': row[1],
                    'unidad': row[2],
                    'precio': float(round(row[3] + (row[3] * Decimal('0.16')), 2))  
                }
                for row in resultados
            ]

            return jsonify(articulos)

    except Exception as e:
        print(f"Error en /servicios: {str(e)}")
        return jsonify({'error': str(e)}), 500