import traceback
from flask import jsonify, request
from werkzeug.exceptions import HTTPException
from app.utils.logging_utils import (
    obtener_contexto_request,
    limpiar_texto_error,
)


def register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        ctx = obtener_contexto_request()
        app.logger.warning(
            f'HTTP {e.code} en {ctx.get("metodo")} {ctx.get("ruta")} '
            f'ip={ctx.get("ip")} body={ctx.get("body")} | descripcion={e.description}'
        )
        return jsonify({
            'error': e.description or e.name,
            'codigo': e.code,
            'ruta': ctx.get('ruta'),
        }), e.code

    @app.errorhandler(Exception)
    def handle_uncaught_exception(e):
        ctx = obtener_contexto_request()
        tb = traceback.format_exc()
        app.logger.error(
            f'Excepcion no manejada en {ctx.get("metodo")} {ctx.get("ruta")} '
            f'ip={ctx.get("ip")} body={ctx.get("body")} | excepcion={limpiar_texto_error(str(e))}'
            f'\nStackTrace:\n{limpiar_texto_error(tb)}'
        )
        return jsonify({
            'error': 'Ocurrio un error interno en el servidor.',
            'detalle': limpiar_texto_error(str(e)),
            'ruta': ctx.get('ruta'),
        }), 500

    @app.before_request
    def log_request_init():
        if request.path.startswith('/static'):
            return
        app.logger.info(
            f'>>> {request.method} {request.path} desde ip={request.remote_addr} '
            f'ua="{request.headers.get("User-Agent", "")}"'
        )

    @app.after_request
    def log_response(response):
        if request.path.startswith('/static'):
            return response
        nivel = 'info'
        if response.status_code >= 500:
            nivel = 'error'
        elif response.status_code >= 400:
            nivel = 'warning'
        mensaje = f'<<< {request.method} {request.path} -> {response.status_code}'
        if nivel == 'error':
            app.logger.error(mensaje)
        elif nivel == 'warning':
            app.logger.warning(mensaje)
        else:
            app.logger.info(mensaje)
        return response
