# app/routes/formularios.py
from flask import Blueprint, request, jsonify
from app.utils.firebird import connect_to_firebird

formularios_bp = Blueprint('formularios', __name__)

@formularios_bp.route('/formularios', methods=['POST'])
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


@formularios_bp.route('/formularios/<int:formulario_id>', methods=['PUT'])
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

@formularios_bp.route('/formularios/<int:formulario_id>', methods=['DELETE'])
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
    
@formularios_bp.route('/formularios_get', methods=['POST'])
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

@formularios_bp.route('/columnas', methods=['POST'])
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
    
@formularios_bp.route('/opciones', methods=['POST'])
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



