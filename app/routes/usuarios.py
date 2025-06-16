from flask import Blueprint, request, jsonify
from app.utils.firebird import connect_to_firebird

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
            SELECT CLAVE, FECHA, TOTAL, ESTADO, CANCELADO
            FROM PEDIDOS
            WHERE SCP_CLAVEVENDEDOR = ?
            AND FECHA BETWEEN ? AND ?
            ORDER BY FECHA DESC
        """, (sc_clave, fecha_inicio, fecha_fin))
        
        rows = cur.fetchall()
        
        pedidos = [
            {
                'clave': row[0],
                'fecha': str(row[1]),
                'total': float(row[2]),
                'estado': row[3],
                'cancelado': row[4]
            } for row in rows
        ]
        
        conn.close()
        return jsonify({'pedidos': pedidos}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
