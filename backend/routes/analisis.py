"""
RUTAS: Capa de presentación HTTP.
ABSTRACCIÓN: Las rutas solo manejan request/response y delegan
toda la lógica al servicio (services/analisis_service.py).
"""

from flask import Blueprint, request, jsonify

from services.analisis_service import ServicioAnalisis
from config import VERSION, NOMBRE

bp = Blueprint('analisis', __name__)


@bp.route('/analizar', methods=['POST'])
def analizar():
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "error": "No se proporciono JSON",
                "sugerencia": "Envia un JSON con 'codigo' y 'lenguaje'"
            }), 400

        codigo = data.get("codigo", "").strip()
        lenguaje = data.get("lenguaje", "c").strip().lower()

        if not codigo:
            return jsonify({
                "error": "El campo 'codigo' esta vacio",
                "sugerencia": "Proporciona codigo valido a analizar"
            }), 400

        resultado = ServicioAnalisis.analizar_codigo(codigo, lenguaje)
        return jsonify(resultado), 200

    except ValueError as e:
        return jsonify({
            "error": str(e),
            "fase": "Seleccion de Lenguaje",
            "sugerencia": "Elige un lenguaje soportado"
        }), 400

    except SyntaxError as e:
        return jsonify({
            "error": str(e),
            "fase": "Analisis Sintactico",
            "sugerencia": "Corrige la gramatica y revisa los tokens"
        }), 400

    except RuntimeError as e:
        return jsonify({
            "error": str(e),
            "fase": "Analisis Lexico",
            "sugerencia": "El codigo parece vacio o solo tiene comentarios"
        }), 400

    except Exception as e:
        return jsonify({
            "error": f"Error de analisis: {str(e)}",
            "fase": "Analisis Lexico/Sintactico",
            "sugerencia": "Revisa la estructura del codigo"
        }), 400


@bp.route('/idiomas', methods=['GET'])
def idiomas():
    return jsonify(ServicioAnalisis.obtener_idiomas()), 200


@bp.route('/info', methods=['GET'])
def info():
    return jsonify({
        "nombre": f"{NOMBRE} v{VERSION}",
        "version": VERSION,
        "descripcion": (
            "Plataforma modular con Arquitectura en Capas + POO "
            "(abstraccion, herencia, polimorfismo, encapsulamiento). "
            "Soporta C, C++, Java, JavaScript, Python."
        ),
        "caracteristicas": [
            "Analisis lexico multilenguaje con tokens personalizados",
            "Analisis sintactico con parser propio por lenguaje",
            "Validacion semantica especifica por lenguaje",
            "Entropia de Shannon para medicion de complejidad",
            "Arquitectura escalable (Factory Pattern + Capas)",
            "4 pilares de POO implementados en todo el sistema",
        ],
    }), 200
