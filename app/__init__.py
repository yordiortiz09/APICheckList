from flask import Flask
from app.routes import register_routes
from app.utils.logger import setup_logger
from app.utils.error_handlers import register_error_handlers


def create_app():
    app = Flask(__name__)
    setup_logger(app)
    register_error_handlers(app)
    register_routes(app)
    app.logger.info('API iniciada correctamente')
    return app
