# app/routes/formularios.py
from flask import Blueprint, request, jsonify
from app.utils.firebird import get_firebird_connection

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

        with get_firebird_connection(dsn, user, password) as conn:
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

        with get_firebird_connection(dsn, user, password) as conn:
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

        with get_firebird_connection(dsn, user, password) as conn:
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

        with get_firebird_connection(dsn, user, password) as conn:
            cur = conn.cursor()
            
            cur.execute("""
                SELECT
                    f.ID AS formulario_id,
                    f.TITULO AS formulario_titulo,
                    f.FECHA_CREACION AS formulario_fecha,
                    
                    s.ID AS seccion_id,
                    s.NOMBRE AS seccion_nombre,

                    p.ID AS pregunta_id,
                    p.TEXTO AS pregunta_texto,
                    p.TIPO AS pregunta_tipo,
                    COALESCE(p.CON_FILAS, 0) AS pregunta_con_filas,
                    COALESCE(p.CON_FOTO, 0) AS pregunta_con_foto,
                    COALESCE(p.PREGUNTA_PADRE_ID, 0) AS pregunta_padre_id,
                    COALESCE(p.PREGUNTA_PADRE_OPCION_ID, 0) AS pregunta_padre_opcion_id,

                    o.ID AS opcion_id,
                    o.VALOR AS opcion_valor,

                    c.ID AS columna_id,
                    c.NOMBRE AS columna_nombre,
                    c.TIPO AS columna_tipo,

                    oc.ID AS opcion_columna_id,
                    oc.VALOR AS opcion_columna_valor

                FROM FORMULARIOS f
                LEFT JOIN SECCIONES s ON s.FORMULARIO_ID = f.ID
                LEFT JOIN PREGUNTAS p ON (p.SECCION_ID = s.ID OR p.PREGUNTA_PADRE_ID IS NOT NULL OR p.PREGUNTA_PADRE_OPCION_ID IS NOT NULL)
                LEFT JOIN OPCIONES o ON (o.PREGUNTA_ID = p.ID AND o.COLUMNA_ID IS NULL)
                LEFT JOIN COLUMNAS c ON c.PREGUNTA_ID = p.ID
                LEFT JOIN OPCIONES oc ON oc.COLUMNA_ID = c.ID
                ORDER BY f.ID, s.ID, p.ID, o.ID, c.ID, oc.ID
            """)

            rows = cur.fetchall()

            formularios = {}
            preguntas_dict = {}
            opciones_dict = {}
            columnas_dict = {}

            parent_map_pregunta = {} 
            parent_map_opcion = {}

            for row in rows:
                (formulario_id, formulario_titulo, formulario_fecha,
                 seccion_id, seccion_nombre,
                 pregunta_id, pregunta_texto, pregunta_tipo,
                 pregunta_con_filas, pregunta_con_foto,
                 pregunta_padre_id, pregunta_padre_opcion_id,
                 opcion_id, opcion_valor,
                 columna_id, columna_nombre, columna_tipo,
                 opcion_columna_id, opcion_columna_valor) = row

                pregunta_con_filas = bool(pregunta_con_filas)
                pregunta_con_foto = bool(pregunta_con_foto)

                if formulario_id not in formularios:
                    formularios[formulario_id] = {
                        'id': formulario_id,
                        'titulo': formulario_titulo,
                        'fecha_creacion': formulario_fecha.isoformat() if formulario_fecha else None,
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
                            'subPreguntas': [],
                            'columnas': []
                        }

                    if pregunta_padre_id > 0:
                        parent_map_pregunta[pregunta_id] = pregunta_padre_id
                    if pregunta_padre_opcion_id > 0:
                        parent_map_opcion[pregunta_id] = pregunta_padre_opcion_id

                if columna_id is not None:
                    if columna_id not in columnas_dict:
                        columnas_dict[columna_id] = {
                            'id': columna_id,
                            'nombre': columna_nombre,
                            'tipo': columna_tipo,
                            'opciones': []
                        }
                    
                    if pregunta_id is not None:
                        pregunta = preguntas_dict[pregunta_id]
                        if not any(col['id'] == columna_id for col in pregunta['columnas']):
                            pregunta['columnas'].append(columnas_dict[columna_id])
                            print(f"   ✅ Columna agregada: '{columna_nombre}' a pregunta {pregunta_id}")

                if opcion_columna_id is not None and columna_id is not None:
                    opcion_col = {
                        'id': opcion_columna_id,
                        'valor': opcion_columna_valor
                    }
                    columna = columnas_dict[columna_id]
                    if not any(op['id'] == opcion_columna_id for op in columna['opciones']):
                        columna['opciones'].append(opcion_col)
                        print(f"      ✅ Opción columna agregada: '{opcion_columna_valor}' a columna {columna_id}")

                if opcion_id is not None:
                    if opcion_id not in opciones_dict:
                        opciones_dict[opcion_id] = {
                            'id': opcion_id,
                            'valor': opcion_valor,
                            'subPreguntas': []
                        }

                # Agregar opción a pregunta
                if pregunta_id is not None and opcion_id is not None:
                    if opcion_id in opciones_dict:
                        opcion = opciones_dict[opcion_id]
                        if not any(op['id'] == opcion_id for op in preguntas_dict[pregunta_id]['opciones']):
                            preguntas_dict[pregunta_id]['opciones'].append(opcion)

                # Agregar pregunta raíz a sección
                if pregunta_id is not None and pregunta_padre_id == 0 and pregunta_padre_opcion_id == 0 and seccion:
                    if not any(p['id'] == pregunta_id for p in seccion['preguntas']):
                        seccion['preguntas'].append(preguntas_dict[pregunta_id])

            # Construir jerarquía de subpreguntas
            for p_id, p_data in preguntas_dict.items():
                padre_id = parent_map_pregunta.get(p_id, 0)
                padre_opcion_id = parent_map_opcion.get(p_id, 0)

                if padre_id > 0 and padre_id in preguntas_dict:
                    padre_pregunta = preguntas_dict[padre_id]
                    if not any(sp['id'] == p_id for sp in padre_pregunta['subPreguntas']):
                        padre_pregunta['subPreguntas'].append(p_data)

                elif padre_opcion_id > 0 and padre_opcion_id in opciones_dict:
                    padre_opcion = opciones_dict[padre_opcion_id]
                    if not any(sp['id'] == p_id for sp in padre_opcion['subPreguntas']):
                        padre_opcion['subPreguntas'].append(p_data)

            resultado = list(formularios.values())
            print(f"📦 Formularios retornados: {len(resultado)}")
            
            return jsonify(resultado)

    except Exception as e:
        print(f"❌ Error en obtener_formularios: {str(e)}")
        import traceback
        traceback.print_exc()
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

        with get_firebird_connection(dsn, user, password) as conn:
            cur = conn.cursor()
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


@formularios_bp.route('/columnas/<int:columna_id>', methods=['PUT'])
def actualizar_columna(columna_id):
    try:
        data = request.json
        dsn = data.get('dsn')
        user = data.get('user')
        password = data.get('password')
        nombre = data.get('nombre')
        tipo = data.get('tipo')

        if not all([dsn, user, password]):
            return jsonify({'error': 'Faltan parámetros: dsn, user, password'}), 400

        if not nombre and not tipo:
            return jsonify({'error': 'Debe proporcionar al menos un campo a actualizar: nombre o tipo'}), 400

        with get_firebird_connection(dsn, user, password) as conn:
            cur = conn.cursor()

            campos_actualizar = []
            valores = []

            if nombre:
                campos_actualizar.append("nombre = ?")
                valores.append(nombre)
            if tipo:
                campos_actualizar.append("tipo = ?")
                valores.append(tipo)

            valores.append(columna_id)

            query = f"UPDATE columnas SET {', '.join(campos_actualizar)} WHERE id = ?"
            cur.execute(query, tuple(valores))
            conn.commit()

            if cur.rowcount == 0:
                return jsonify({'error': 'No se encontró la columna con el ID proporcionado'}), 404

            return jsonify({'id': columna_id, 'message': 'Columna actualizada correctamente'}), 200

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@formularios_bp.route('/columnas/<int:columna_id>', methods=['DELETE'])
def eliminar_columna(columna_id):
    try:
        data = request.json
        dsn = data.get('dsn')
        user = data.get('user')
        password = data.get('password')

        if not all([dsn, user, password]):
            return jsonify({'error': 'Faltan parámetros: dsn, user, password'}), 400

        with get_firebird_connection(dsn, user, password) as conn:
            cur = conn.cursor()

            cur.execute("DELETE FROM opciones WHERE columna_id = ?", (columna_id,))
            
            cur.execute("DELETE FROM columnas WHERE id = ?", (columna_id,))
            conn.commit()

            if cur.rowcount == 0:
                return jsonify({'error': 'No se encontró la columna con el ID proporcionado'}), 404

            return jsonify({'message': 'Columna eliminada correctamente'}), 200

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
        pregunta_id = data.get('pregunta_id') 
        valor = data.get('valor')

        if not valor or (pregunta_id is None and columna_id is None ) or (dsn is None or user is None or password is None):
            return jsonify({'error': 'Faltan parámetros obligatorios: valor y (pregunta_id o columna_id), dsn, user, password'}), 400

        with get_firebird_connection(dsn, user, password) as conn:
            cur = conn.cursor()

            if pregunta_id is not None:
                cur.execute(
                    "SELECT id FROM opciones WHERE pregunta_id = ? AND valor = ?",
                    (pregunta_id, valor)
                )
            else:
                cur.execute(
                    "SELECT id FROM opciones WHERE columna_id = ? AND valor = ?",
                    (columna_id, valor)
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
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@formularios_bp.route('/opciones/<int:opcion_id>', methods=['PUT'])
def actualizar_opcion(opcion_id):
    try:
        data = request.json
        dsn = data.get('dsn')
        user = data.get('user')
        password = data.get('password')
        valor = data.get('valor')

        if not all([dsn, user, password, valor]):
            return jsonify({'error': 'Faltan parámetros: dsn, user, password, valor'}), 400

        with get_firebird_connection(dsn, user, password) as conn:
            cur = conn.cursor()
            cur.execute(
                "UPDATE opciones SET valor = ? WHERE id = ?",
                (valor, opcion_id)
            )
            conn.commit()

            if cur.rowcount == 0:
                return jsonify({'error': 'No se encontró la opción con el ID proporcionado'}), 404

            return jsonify({'id': opcion_id, 'message': 'Opción actualizada correctamente'}), 200

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@formularios_bp.route('/opciones/<int:opcion_id>', methods=['DELETE'])
def eliminar_opcion(opcion_id):
    try:
        data = request.json
        dsn = data.get('dsn')
        user = data.get('user')
        password = data.get('password')

        if not all([dsn, user, password]):
            return jsonify({'error': 'Faltan parámetros: dsn, user, password'}), 400

        with get_firebird_connection(dsn, user, password) as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM opciones WHERE id = ?", (opcion_id,))
            conn.commit()

            if cur.rowcount == 0:
                return jsonify({'error': 'No se encontró la opción con el ID proporcionado'}), 404

            return jsonify({'message': 'Opción eliminada correctamente'}), 200

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500