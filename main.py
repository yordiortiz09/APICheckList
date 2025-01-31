from flask import Flask, request, jsonify
import fdb

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

        # Manejo del cursor manualmente (sin contexto 'with')
        cur = conn.cursor()
        cur.execute("INSERT INTO formularios (titulo) VALUES (?)", (titulo,))
        conn.commit()

        cur.execute("SELECT MAX(id) FROM formularios")
        formulario_id = cur.fetchone()[0]

        return jsonify({'id': formulario_id, 'message': 'Formulario insertado correctamente'})
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Actualizar un formulario
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
        texto = data.get('texto')
        tipo = data.get('tipo')
        con_filas = data.get('con_filas', False)

        if not all([dsn, user, password, seccion_id, texto, tipo]):
            return jsonify({'error': 'Faltan parámetros: dsn, user, password, seccion_id, texto, tipo'}), 400

        conn = connect_to_firebird(dsn, user, password)
        if not conn:
            return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500

        cur = conn.cursor() 
        cur.execute(
            "INSERT INTO preguntas (seccion_id, texto, tipo, con_filas) VALUES (?, ?, ?, ?)",
            (seccion_id, texto, tipo, int(con_filas))
        )        
        conn.commit()

        cur.execute("SELECT MAX(id) FROM preguntas")
        pregunta_id = cur.fetchone()[0]
        conn.commit()

        return jsonify({'id': pregunta_id, 'message': 'Pregunta insertada correctamente'})

    except Exception as e:
        print(f"Error: {str(e)}")
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

        if not all([dsn, user, password, texto, tipo]):
            return jsonify({'error': 'Faltan parámetros: dsn, user, password, texto, tipo'}), 400

        conn = connect_to_firebird(dsn, user, password)
        if not conn:
            return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500

        cur = conn.cursor() 
        cur.execute(
            "UPDATE preguntas SET texto = ?, tipo = ?, con_filas = ? WHERE id = ?",
            (texto, tipo, int(con_filas), pregunta_id)
        )
        conn.commit()

        return jsonify({'id': pregunta_id, 'message': 'Pregunta actualizada correctamente'}), 200

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

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
        # Leer los datos desde el cuerpo de la solicitud
        data = request.json
        dsn = data.get('dsn')
        user = data.get('user')
        password = data.get('password')

        # Validar que los parámetros estén presentes
        if not all([dsn, user, password]):
            return jsonify({'error': 'Faltan parámetros: dsn, user, password'}), 400

        # Conectar a la base de datos
        conn = connect_to_firebird(dsn, user, password)
        if not conn:
            return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500

        # Crear el cursor de manera manual
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
                c.id AS columna_id,
                c.nombre AS columna_nombre,
                c.tipo AS columna_tipo,
                o_col.id AS opcion_columna_id,
                o_col.valor AS opcion_columna_valor,
                o_preg.id AS opcion_pregunta_id,
                o_preg.valor AS opcion_pregunta_valor
            FROM formularios f
            LEFT JOIN secciones s ON s.formulario_id = f.id
            LEFT JOIN preguntas p ON p.seccion_id = s.id
            LEFT JOIN columnas c ON c.pregunta_id = p.id
            LEFT JOIN opciones o_col ON o_col.columna_id = c.id
            LEFT JOIN opciones o_preg ON o_preg.pregunta_id = p.id
            ORDER BY f.id, s.id, p.id, c.id, o_col.id, o_preg.id
        """)

        rows = cur.fetchall()

        # Cerrar el cursor y la conexión
        cur.close()
        conn.close()

        # Procesar los resultados como antes
        formularios = {}
        for row in rows:
            (formulario_id, formulario_titulo, formulario_fecha,
             seccion_id, seccion_nombre,
             pregunta_id, pregunta_texto, pregunta_tipo, pregunta_con_filas,
             columna_id, columna_nombre, columna_tipo,
             opcion_columna_id, opcion_columna_valor,
             opcion_pregunta_id, opcion_pregunta_valor) = row

            pregunta_con_filas = bool(pregunta_con_filas)

            if formulario_id not in formularios:
                formularios[formulario_id] = {
                    'id': formulario_id,
                    'titulo': formulario_titulo,
                    'fecha_creacion': formulario_fecha,
                    'secciones': []
                }
            formulario = formularios[formulario_id]

            seccion = next((s for s in formulario['secciones'] if s['id'] == seccion_id), None)
            if not seccion and seccion_id is not None:
                seccion = {
                    'id': seccion_id,
                    'nombre': seccion_nombre,
                    'preguntas': []
                }
                formulario['secciones'].append(seccion)

            pregunta = next((p for p in seccion['preguntas'] if p['id'] == pregunta_id), None) if seccion else None
            if not pregunta and pregunta_id is not None:
                pregunta = {
                    'id': pregunta_id,
                    'texto': pregunta_texto,
                    'tipo': pregunta_tipo,
                    'con_filas': pregunta_con_filas,
                    'columnas': [],
                    'opciones': []
                }
                seccion['preguntas'].append(pregunta)

            if columna_id and pregunta:
                columna = next((c for c in pregunta['columnas'] if c['id'] == columna_id), None)
                if not columna:
                    columna = {
                        'id': columna_id,
                        'nombre': columna_nombre,
                        'tipo': columna_tipo,
                        'opciones': []
                    }
                    pregunta['columnas'].append(columna)

                if opcion_columna_id and opcion_columna_valor:
                    columna['opciones'].append({
                        'id': opcion_columna_id,
                        'valor': opcion_columna_valor
                    })

            if pregunta and opcion_pregunta_id and opcion_pregunta_valor:
                pregunta['opciones'].append({
                    'id': opcion_pregunta_id,
                    'valor': opcion_pregunta_valor
                })

        formularios_list = list(formularios.values())

        return jsonify(formularios_list)

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
        pregunta_id = data.get('pregunta_id')
        valor = data.get('valor')

        if not all([dsn, user, password, valor, pregunta_id]):
            return jsonify({'error': 'Faltan parámetros: dsn, user, password, pregunta_id, valor'}), 400

        conn = connect_to_firebird(dsn, user, password)
        if not conn:
            return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500

        cur = conn.cursor()
        if columna_id:
            cur.execute(
                "SELECT id FROM opciones WHERE columna_id = ? AND valor = ?",
                (columna_id, valor)
            )
        else:
            cur.execute(
                "SELECT id FROM opciones WHERE columna_id IS NULL AND pregunta_id = ? AND valor = ?",
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
        for respuesta in data['respuestas']:
            formulario_id = respuesta.get('formulario_id')
            seccion_id = respuesta.get('seccion_id')
            pregunta_id = respuesta.get('pregunta_id')
            columna_id = respuesta.get('columna_id')
            texto_respuesta = respuesta.get('texto_respuesta')
            numero_respuesta = respuesta.get('numero_respuesta')
            if not all([formulario_id, seccion_id, pregunta_id]):
                return jsonify({'error': 'Faltan datos en una de las respuestas'}), 400
            cur.execute("""
                INSERT INTO respuestas (
                    formulario_id, seccion_id, pregunta_id, columna_id,
                    texto_respuesta, numero_respuesta
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (formulario_id, seccion_id, pregunta_id, columna_id, texto_respuesta, numero_respuesta))
        conn.commit()

        return jsonify({'message': 'Respuestas guardadas correctamente'}), 200

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)