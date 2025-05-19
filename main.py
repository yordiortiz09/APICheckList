from flask import Flask, request, jsonify
import fdb
import datetime
from decimal import Decimal


app = Flask(__name__)

def connect_to_firebird(dsn, user, password):
    """
    Conecta a Firebird con los parámetros proporcionados dinámicamente.
    """
    try:
        connection = fdb.connect(
            dsn=dsn,
            user=user,
            password=password
        )
        print("Conexión establecida con Firebird")
        return connection
    except Exception as e:
        print(f"Error conectando a Firebird: {str(e)}")
        return None

@app.route('/test_connection', methods=['POST'])
def test_connection():
    """
    Endpoint para probar la conexión a Firebird con parámetros enviados en la solicitud.
    """
    try:
        data = request.json
        dsn = data.get('dsn')
        user = data.get('user')
        password = data.get('password')

        if not all([dsn, user, password]):
            return jsonify({'success': False, 'message': 'Faltan parámetros: dsn, user, password'}), 400

        conn = connect_to_firebird(dsn, user, password)
        if conn:
            conn.close()
            return jsonify({'success': True, 'message': 'Conexión exitosa a Firebird'}), 200
        else:
            return jsonify({'success': False, 'message': 'No se pudo conectar a la base de datos'}), 500

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500
    

@app.route('/servicios', methods=['POST'])
def obtener_todos_los_articulos():
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
@app.route('/clientes', methods=['POST'])
def obtener_clientes():
    try:
        data = request.json
        dsn = data.get('dsn')
        user = data.get('user')
        password = data.get('password')

        if not all([dsn, user, password]):
            return jsonify({'error': 'Faltan parámetros'}), 400

        conn = connect_to_firebird(dsn, user, password)
        if not conn:
            return jsonify({'error': 'No se pudo conectar a Firebird'}), 500

        cur = conn.cursor()
        query = """
            SELECT sc_cliente.sc_clave, cat_sujcolectivos.sc_nombre
            FROM sc_cliente, cat_sujcolectivos, tipocliente
            WHERE sc_cliente.sc_clave = cat_sujcolectivos.sc_clave
              AND sc_cliente.scc_tipo = tipocliente.clave
              AND sc_cliente.SCC_ACTIVO = 1
        """
        cur.execute(query)
        resultados = cur.fetchall()

        clientes = [{'clave': row[0], 'nombre': row[1]} for row in resultados]

        return jsonify(clientes)

    except Exception as e:
        print(f"Error en /clientes: {str(e)}")
        return jsonify({'error': str(e)}), 500



@app.route('/formularios', methods=['POST'])
def insertar_formulario():
    try:
        data = request.json
        dsn = data.get('dsn')
        user = data.get('user')
        password = data.get('password')
        titulo = data.get('titulo')

        if not all([dsn, user, password, titulo]):
            return jsonify({'error': 'Faltan parámetros: dsn, user, password, titulo'}), 400

        conn = connect_to_firebird(dsn, user, password)
        if not conn:
            return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500

        cur = conn.cursor()
        cur.execute("INSERT INTO formularios (titulo) VALUES (?)", (titulo,))
        conn.commit()

        cur.execute("SELECT MAX(id) FROM formularios")
        formulario_id = cur.fetchone()[0]

        return jsonify({'id': formulario_id, 'message': 'Formulario insertado correctamente'})
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/formularios/<int:formulario_id>', methods=['PUT'])
def actualizar_formulario(formulario_id):
    try:
        data = request.json
        dsn = data.get('dsn')
        user = data.get('user')
        password = data.get('password')
        titulo = data.get('titulo')

        if not all([dsn, user, password, titulo]):
            return jsonify({'error': 'Faltan parámetros: dsn, user, password, titulo'}), 400

        conn = connect_to_firebird(dsn, user, password)
        if not conn:
            return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500

        cur = conn.cursor()


        cur.execute(
                "UPDATE formularios SET titulo = ? WHERE id = ?",
                (titulo, formulario_id)
            )
        conn.commit()

        return jsonify({'id': formulario_id, 'message': 'Formulario actualizado correctamente'}), 200

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/formularios/<int:formulario_id>', methods=['DELETE'])
def eliminar_formulario(formulario_id):
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
        cur.execute("DELETE FROM formularios WHERE id = ?", (formulario_id,))
        conn.commit()

        if cur.rowcount == 0:
            return jsonify({'error': 'No se encontró el formulario con el ID proporcionado'}), 404

        return jsonify({'message': 'Formulario eliminado correctamente'}), 200

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500
    

@app.route('/secciones/<int:seccion_id>', methods=['DELETE'])
def eliminar_seccion(seccion_id):
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
        cur.execute("DELETE FROM secciones WHERE id = ?", (seccion_id,))
        conn.commit()

        if cur.rowcount == 0:
                return jsonify({'error': 'No se encontró la sección con el ID proporcionado'}), 404

        return jsonify({'message': 'Sección eliminada correctamente'}), 200

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/secciones', methods=['POST'])
def insertar_seccion():
    try:
        data = request.json
        dsn = data.get('dsn')
        user = data.get('user')
        password = data.get('password')
        formulario_id = data.get('formulario_id')
        nombre = data.get('nombre')

        if not all([dsn, user, password, formulario_id, nombre]):
            return jsonify({'error': 'Faltan parámetros: dsn, user, password, formulario_id, nombre'}), 400

        conn = connect_to_firebird(dsn, user, password)
        if not conn:
            return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500

        cur = conn.cursor()
        cur.execute(
            "INSERT INTO secciones (formulario_id, nombre) VALUES (?, ?) RETURNING id",
            (formulario_id, nombre)
        )
        seccion_id = cur.fetchone()[0]
        conn.commit()

        return jsonify({'id': seccion_id, 'message': 'Sección insertada correctamente'}), 200

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
@app.route('/preguntas', methods=['POST'])
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

@app.route('/preguntas/<int:pregunta_id>', methods=['PUT'])
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
@app.route('/preguntas/<int:pregunta_id>', methods=['DELETE'])
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


@app.route('/secciones/<int:seccion_id>', methods=['PUT'])
def actualizar_seccion(seccion_id):
    try:
        data = request.json
        dsn = data.get('dsn')
        user = data.get('user')
        password = data.get('password')
        nombre = data.get('nombre')

        if not all([dsn, user, password, nombre]):
            return jsonify({'error': 'Faltan parámetros: dsn, user, password, nombre'}), 400

        conn = connect_to_firebird(dsn, user, password)
        if not conn:
            return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500

        cur = conn.cursor() 
        cur.execute(
            "UPDATE secciones SET nombre = ? WHERE id = ?",
            (nombre, seccion_id)
        )
        conn.commit()

        return jsonify({'id': seccion_id, 'message': 'Sección actualizada correctamente'}), 200

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/formularios_get', methods=['POST'])
def obtener_formularios():
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
                f.id AS formulario_id,
                f.titulo AS formulario_titulo,
                f.fecha_creacion AS formulario_fecha,
                s.id AS seccion_id,
                s.nombre AS seccion_nombre,

                p.id AS pregunta_id,
                p.texto AS pregunta_texto,
                p.tipo AS pregunta_tipo,
                COALESCE(p.con_filas, 0) AS pregunta_con_filas,
                COALESCE(p.con_foto, 0) AS pregunta_con_foto,

                COALESCE(p.pregunta_padre_id, 0) AS pregunta_padre_id,
                COALESCE(p.pregunta_padre_opcion_id, 0) AS pregunta_padre_opcion_id,

                o.id AS opcion_id,
                o.valor AS opcion_valor

            FROM formularios f
            LEFT JOIN secciones s ON s.formulario_id = f.id
            LEFT JOIN preguntas p ON p.seccion_id = s.id OR p.pregunta_padre_id IS NOT NULL OR p.pregunta_padre_opcion_id IS NOT NULL
            LEFT JOIN opciones o ON o.pregunta_id = p.id
            ORDER BY f.id, s.id, p.id, o.id;
        """)

        rows = cur.fetchall()
        cur.close()
        conn.close()

        formularios = {}
        preguntas_dict = {}
        opciones_dict = {}

        parent_map_pregunta = {} 
        parent_map_opcion = {}  


        for row in rows:
            (formulario_id, formulario_titulo, formulario_fecha,
             seccion_id, seccion_nombre,
             pregunta_id, pregunta_texto, pregunta_tipo,
             pregunta_con_filas, pregunta_con_foto,
             pregunta_padre_id, pregunta_padre_opcion_id,
             opcion_id, opcion_valor) = row

            pregunta_con_filas = bool(pregunta_con_filas)
            pregunta_con_foto = bool(pregunta_con_foto)

            if formulario_id not in formularios:
                formularios[formulario_id] = {
                    'id': formulario_id,
                    'titulo': formulario_titulo,
                    'fecha_creacion': formulario_fecha,
                    'secciones': []
                }
            formulario = formularios[formulario_id]

            seccion = None
            if seccion_id is not None:
                seccion = next((sec for sec in formulario['secciones'] if sec['id'] == seccion_id), None)
                if not seccion:
                    seccion = {
                        'id': seccion_id,
                        'nombre': seccion_nombre,
                        'preguntas': []
                    }
                    formulario['secciones'].append(seccion)

            if pregunta_id is not None:
                if pregunta_id not in preguntas_dict:
                    preguntas_dict[pregunta_id] = {
                        'id': pregunta_id,
                        'texto': pregunta_texto,
                        'tipo': pregunta_tipo,
                        'con_filas': pregunta_con_filas,
                        'con_foto': pregunta_con_foto,
                        'opciones': [],
                        'subPreguntas': []
                    }

                if pregunta_padre_id > 0:
                    parent_map_pregunta[pregunta_id] = pregunta_padre_id
                if pregunta_padre_opcion_id > 0:
                    parent_map_opcion[pregunta_id] = pregunta_padre_opcion_id

            if opcion_id is not None:
                if opcion_id not in opciones_dict:
                    opciones_dict[opcion_id] = {
                        'id': opcion_id,
                        'valor': opcion_valor,
                        'subPreguntas': []
                    }

            if pregunta_id is not None and opcion_id is not None:
                if opcion_id in opciones_dict:
                    opcion = opciones_dict[opcion_id]
                    if opcion not in preguntas_dict[pregunta_id]['opciones']:
                        preguntas_dict[pregunta_id]['opciones'].append(opcion)

            if pregunta_id is not None and pregunta_padre_id == 0 and pregunta_padre_opcion_id == 0 and seccion:
                if preguntas_dict[pregunta_id] not in seccion['preguntas']:
                    seccion['preguntas'].append(preguntas_dict[pregunta_id])

       
        for p_id, p_data in preguntas_dict.items():
            padre_id = parent_map_pregunta.get(p_id, 0)
            padre_opcion_id = parent_map_opcion.get(p_id, 0)

            if padre_id > 0 and padre_id in preguntas_dict:
                padre_pregunta = preguntas_dict[padre_id]
                if p_data not in padre_pregunta['subPreguntas']:
                    padre_pregunta['subPreguntas'].append(p_data)

            elif padre_opcion_id > 0 and padre_opcion_id in opciones_dict:
                padre_opcion = opciones_dict[padre_opcion_id]
                if p_data not in padre_opcion['subPreguntas']:
                    padre_opcion['subPreguntas'].append(p_data)

        return jsonify(list(formularios.values()))

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500



@app.route('/columnas', methods=['POST'])
def insertar_columna():
    try:
        data = request.json
        dsn = data.get('dsn')
        user = data.get('user')
        password = data.get('password')
        pregunta_id = data.get('pregunta_id')
        nombre = data.get('nombre')
        tipo = data.get('tipo')

        if not all([dsn, user, password, pregunta_id, nombre, tipo]):
            return jsonify({'error': 'Faltan parámetros: dsn, user, password, pregunta_id, nombre, tipo'}), 400

        conn = connect_to_firebird(dsn, user, password)
        if not conn:
            return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500

        cur =  conn.cursor()
        cur.execute(
            "SELECT id FROM columnas WHERE pregunta_id = ? AND nombre = ?",
            (pregunta_id, nombre)
        )
        columna_existente = cur.fetchone()

        if columna_existente:
            return jsonify({'id': columna_existente[0], 'message': 'Columna ya existe'}), 200
        cur.execute(
            "INSERT INTO columnas (pregunta_id, nombre, tipo) VALUES (?, ?, ?)",
            (pregunta_id, nombre, tipo)
        )
        conn.commit()

        cur.execute("SELECT MAX(id) FROM columnas")
        columna_id = cur.fetchone()[0]

        return jsonify({'id': columna_id, 'message': 'Columna insertada correctamente'})

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
@app.route('/opciones', methods=['POST'])
def insertar_opcion():
    try:
        data = request.json
        dsn = data.get('dsn')
        user = data.get('user')
        password = data.get('password')
        columna_id = data.get('columna_id')
        pregunta_id = data.get('pregunta_id')  # Pregunta principal o subpregunta
        valor = data.get('valor')

        if not all([dsn, user, password, valor, pregunta_id]):
            return jsonify({'error': 'Faltan parámetros obligatorios'}), 400

        conn = connect_to_firebird(dsn, user, password)
        if not conn:
            return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500

        cur = conn.cursor()

        cur.execute(
            "SELECT id FROM opciones WHERE pregunta_id = ? AND valor = ?",
            (pregunta_id, valor)
        )

        opcion_existente = cur.fetchone()
        if opcion_existente:
            return jsonify({'id': opcion_existente[0], 'message': 'Opción ya existe'}), 200

        cur.execute(
            "INSERT INTO opciones (columna_id, pregunta_id, valor) VALUES (?, ?, ?)",
            (columna_id, pregunta_id, valor)
        )
        conn.commit()

        cur.execute("SELECT MAX(id) FROM opciones")
        opcion_id = cur.fetchone()[0]

        return jsonify({'id': opcion_id, 'message': 'Opción insertada correctamente'}), 200

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/sync_users', methods=['POST'])
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


@app.route('/verify_user', methods=['POST'])
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

    
@app.route('/get_users', methods=['POST'])
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


@app.route('/guardar_respuestas', methods=['POST'])
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


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)