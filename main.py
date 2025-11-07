from app import create_app

app = create_app()

if __name__ == '__main__':
    # Para desarrollo local
    app.run(debug=False, host='0.0.0.0', port=5000, threaded=True)
    
    # Para producción en Windows, usa waitress:
    # pip install waitress
    # waitress-serve --host=0.0.0.0 --port=5000 main:app
