from app.routes.articulos import articulos_bp
from app.routes.clientes import clientes_bp
from app.routes.formularios import formularios_bp
from app.routes.preguntas import preguntas_bp
from app.routes.secciones import secciones_bp
from app.routes.orden_servicio import bp_orden
from app.routes.conexion import conexion_bp
from app.routes.usuarios import usuarios_bp
from app.routes.respuestas import respuestas_bp
from app.routes.descuentos import descuentos_bp
def register_routes(app):
    app.register_blueprint(articulos_bp)
    app.register_blueprint(clientes_bp)
    app.register_blueprint(formularios_bp)
    app.register_blueprint(preguntas_bp)
    app.register_blueprint(secciones_bp)
    app.register_blueprint(bp_orden)
    app.register_blueprint(conexion_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(respuestas_bp)
    app.register_blueprint(descuentos_bp)
