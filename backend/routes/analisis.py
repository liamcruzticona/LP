from flask import Blueprint, request, jsonify
from core.analizador_factory import get_analizador, idiomas_disponibles
from core.semantica import ValidadorSemantico

bp = Blueprint('analisis', __name__)

@bp.route('/analizar', methods=['POST'])
def analizar():
    """
    Endpoint principal para análisis léxico, sintáctico y entropía
    Manejo robusto de errores con sugerencias útiles
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "error": "No se proporcionó JSON",
                "sugerencia": "Envía un JSON con los campos 'codigo' y 'lenguaje'"
            }), 400

        codigo = data.get("codigo", "").strip()
        lenguaje = data.get("lenguaje", "c").strip().lower()

        if not codigo:
            return jsonify({
                "error": "El campo 'codigo' está vacío",
                "sugerencia": "Proporciona código válido a analizar"
            }), 400

        try:
            analizador = get_analizador(lenguaje)
        except ValueError as e:
            return jsonify({
                "error": str(e),
                "fase": "Selección de Lenguaje",
                "sugerencia": "Elige un lenguaje soportado o agrega soporte en el backend"
            }), 400

        try:
            resultado = analizador.analizar(codigo)
        except Exception as e:
            return jsonify({
                "error": f"Error de análisis: {str(e)}",
                "fase": "Análisis Léxico/Sintáctico",
                "sugerencia": "Revisa la estructura del código y la sintaxis del lenguaje seleccionado"
            }), 400

        if isinstance(resultado, dict) and resultado.get("tipo") == "error":
            return jsonify({
                "error": resultado.get("mensaje"),
                "fase": "Análisis Sintáctico",
                "sugerencia": "Corrige la gramática y revisa los tokens generados"
            }), 400

        if not resultado.get("tokens"):
            return jsonify({
                "error": "No se generaron tokens",
                "fase": "Análisis Léxico",
                "sugerencia": "El código parece estar vacío o contiene solo comentarios"
            }), 400

        validacion = ValidadorSemantico(resultado.get("ast")).validar()

        return jsonify({
            "lenguaje": resultado.get("lenguaje"),
            "slug": resultado.get("slug"),
            "metadata": resultado.get("metadata", {}),
            "tokens": [t.to_dict() for t in resultado.get("tokens")],
            "ast": resultado.get("ast"),
            "validacion": validacion,
            "exito": True
        }), 200

    except Exception as e:
        return jsonify({
            "error": f"Error inesperado: {str(e)}",
            "sugerencia": "Contacta al administrador si el error persiste"
        }), 500


@bp.route('/idiomas', methods=['GET'])
def idiomas():
    """Endpoint para listar los lenguajes disponibles."""
    analizadores = {
        clave: {
            "nombre": analizador.nombre,
            "slug": analizador.slug,
            "metadata": analizador.metadata,
        }
        for clave, analizador in [(k, get_analizador(k)) for k in idiomas_disponibles().keys()]
    }
    return jsonify({
        "disponibles": analizadores
    }), 200


@bp.route('/info', methods=['GET'])
def info():
    """Endpoint de información del analizador"""
    return jsonify({
        "nombre": "Analizador Léxico y Sintáctico Multilenguaje",
        "version": "3.0",
        "descripcion": "Plataforma modular de análisis de código para múltiples lenguajes.",
        "caracteristicas": [
            "Análisis léxico multilenguaje",
            "Análisis sintáctico avanzado",
            "Validación semántica básica",
            "Estructura modular y escalable",
            "Soporte para C y JavaScript con base para más lenguajes"
        ]
    }), 200