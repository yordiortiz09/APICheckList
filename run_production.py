# run_production.py
"""
Script para ejecutar la API en producción usando Waitress
Waitress es un servidor WSGI de producción puro-Python

Uso:
    python run_production.py

O instala waitress y ejecuta directamente:
    pip install waitress
    waitress-serve --host=0.0.0.0 --port=5000 --threads=6 main:app
"""

from waitress import serve
from app import create_app

app = create_app()

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Iniciando servidor de producción")
    print("=" * 60)
    print("📡 Host: 0.0.0.0")
    print("🔌 Puerto: 5000")
    print("🧵 Threads: 6")
    print("🔧 Servidor: Waitress (Production WSGI)")
    print("=" * 60)
    print("✅ Servidor activo en http://0.0.0.0:5000")
    print("Presiona CTRL+C para detener")
    print("=" * 60)
    
    serve(app, host='0.0.0.0', port=5000, threads=6)
