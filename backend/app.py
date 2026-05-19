"""
APP: Punto de entrada de la API Flask.
ABSTRACCIÓN: Oculta la configuración del servidor usando el módulo config.
"""

from flask import Flask
from flask_cors import CORS

from routes.analisis import bp
from config import HOST, PUERTO, DEBUG, VERSION, NOMBRE

app = Flask(__name__)
CORS(app)

app.register_blueprint(bp)


@app.route("/")
def home():
    return f"{NOMBRE} v{VERSION} funcionando"


if __name__ == "__main__":
    app.run(host=HOST, port=PUERTO, debug=DEBUG)
