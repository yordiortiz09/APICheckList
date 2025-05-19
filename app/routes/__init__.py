from app.routes.articulos import articulos_bp
from app.routes.clientes import clientes_bp
from app.routes.formularios import formularios_bp
from app.routes.preguntas import preguntas_bp
from app.routes.secciones import secciones_bp

def register_routes(app):
    app.register_blueprint(articulos_bp)
    app.register_blueprint(clientes_bp)
    app.register_blueprint(formularios_bp)
    app.register_blueprint(preguntas_bp)
    app.register_blueprint(secciones_bp)
