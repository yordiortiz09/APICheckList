import re
import json
import traceback
from functools import wraps
from flask import current_app, request, jsonify


CAMPOS_SENSIBLES = {'password', 'dsn', 'user'}


def limpiar_datos_sensibles(data):
    if not isinstance(data, dict):
        return data
    limpio = {}
    for k, v in data.items():
        if k.lower() in CAMPOS_SENSIBLES:
            limpio[k] = '***'
        elif isinstance(v, dict):
            limpio[k] = limpiar_datos_sensibles(v)
        elif isinstance(v, list):
            limpio[k] = [
                limpiar_datos_sensibles(item) if isinstance(item, dict) else item
                for item in v
            ]
        else:
            limpio[k] = v
    return limpio


def limpiar_texto_error(texto):
    if not isinstance(texto, str):
        texto = str(texto)
    texto = re.sub(r'password=[^\s,;]+', 'password=***', texto, flags=re.IGNORECASE)
    texto = re.sub(r"'password'\s*:\s*'[^']*'", "'password': '***'", texto, flags=re.IGNORECASE)
    return texto


def obtener_contexto_request():
    try:
        body = None
        if request.is_json:
            try:
                body = request.get_json(silent=True)
            except Exception:
                body = None
        return {
            'metodo': request.method,
            'ruta': request.path,
            'ip': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', 'desconocido'),
            'body': limpiar_datos_sensibles(body) if body else None,
            'query_args': dict(request.args) if request.args else None,
        }
    except Exception:
        return {'ruta': 'desconocida'}


def log_info(mensaje, **extras):
    ctx = obtener_contexto_request()
    detalle = f'{mensaje} | ruta={ctx.get("ruta")} ip={ctx.get("ip")}'
    if extras:
        detalle += f' | extras={extras}'
    current_app.logger.info(detalle)


def log_error(mensaje, excepcion=None, **extras):
    ctx = obtener_contexto_request()
    detalle = (
        f'{mensaje} | ruta={ctx.get("ruta")} ip={ctx.get("ip")} '
        f'metodo={ctx.get("metodo")} body={ctx.get("body")}'
    )
    if extras:
        detalle += f' | extras={extras}'
    if excepcion is not None:
        detalle += f' | excepcion={limpiar_texto_error(str(excepcion))}'
        tb = traceback.format_exc()
        if tb and tb.strip() != 'NoneType: None':
            detalle += f'\nStackTrace:\n{limpiar_texto_error(tb)}'
    current_app.logger.error(detalle)


def log_warning(mensaje, **extras):
    ctx = obtener_contexto_request()
    detalle = f'{mensaje} | ruta={ctx.get("ruta")} ip={ctx.get("ip")} body={ctx.get("body")}'
    if extras:
        detalle += f' | extras={extras}'
    current_app.logger.warning(detalle)


def manejar_errores(nombre_endpoint=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            etiqueta = nombre_endpoint or func.__name__
            try:
                log_info(f'Inicio {etiqueta}')
                resultado = func(*args, **kwargs)
                return resultado
            except Exception as e:
                log_error(f'Error no manejado en {etiqueta}', excepcion=e)
                return jsonify({
                    'error': 'Ocurrio un error procesando la peticion.',
                    'detalle': limpiar_texto_error(str(e)),
                    'endpoint': etiqueta,
                }), 500
        return wrapper
    return decorator
