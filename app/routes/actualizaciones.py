import os
from flask import Blueprint, jsonify, send_from_directory, abort

actualizaciones_bp = Blueprint('actualizaciones', __name__)

APK_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'static', 'apk')
APK_FILENAME = 'cremapet.apk'

APP_VERSION = '1.1.0'
FORZAR_ACTUALIZACION = False
NOTAS_VERSION = 'Mejoras en el flujo de pedidos y correcciones de bugs.'


@actualizaciones_bp.route('/app/version', methods=['GET'])
def obtener_version():
    return jsonify({
        'version': APP_VERSION,
        'url_descarga': '/app/descargar',
        'forzar_actualizacion': FORZAR_ACTUALIZACION,
        'notas': NOTAS_VERSION
    })


@actualizaciones_bp.route('/app/ping', methods=['GET'])
def ping():
    return 'pong', 200


@actualizaciones_bp.route('/app/descargar', methods=['GET'])
def descargar_apk():
    apk_path = os.path.join(APK_FOLDER, APK_FILENAME)
    if not os.path.exists(apk_path):
        abort(404, description='APK no disponible en el servidor')
    response = send_from_directory(
        APK_FOLDER,
        APK_FILENAME,
        as_attachment=True,
        mimetype='application/vnd.android.package-archive'
    )
    response.headers['Content-Disposition'] = f'attachment; filename="{APK_FILENAME}"'
    response.headers['Cache-Control'] = 'no-cache'
    return response
