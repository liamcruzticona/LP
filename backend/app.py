from flask import Flask
from flask_cors import CORS

from routes.analisis import bp

app = Flask(__name__)
CORS(app)



# Registrar rutas
app.register_blueprint(bp)

@app.route("/")
def home():
    return "API Analizador funcionando"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)