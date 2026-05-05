from flask import Blueprint, request, jsonify
from core.lexico import AnalizadorLexico
from core.sintactico import Parser
from core.entropia import CalculadorEntropia

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
                "sugerencia": "Envía un JSON con el campo 'codigo'"
            }), 400
        
        codigo = data.get("codigo", "").strip()
        
        if not codigo:
            return jsonify({
                "error": "El campo 'codigo' está vacío",
                "sugerencia": "Proporciona código válido a analizar"
            }), 400

        #  LÉXICO
        try:
            lexer = AnalizadorLexico(codigo)
            tokens = lexer.analizar()
        except Exception as e:
            return jsonify({
                "error": f"Error léxico: {str(e)}",
                "fase": "Análisis Léxico",
                "sugerencia": "Verifica caracteres no permitidos o sintaxis inválida"
            }), 400

        # Si no hay tokens
        if not tokens:
            return jsonify({
                "error": "No se generaron tokens",
                "sugerencia": "El código parece estar vacío o contiene solo comentarios"
            }), 400

        #  SINTÁCTICO
        sintactico_result = None
        try:
            parser = Parser(tokens)
            sintactico_result = parser.analizar()
            
            # Verificar si el parser devolvió error
            if isinstance(sintactico_result, dict) and sintactico_result.get("tipo") == "error":
                return jsonify({
                    "error": sintactico_result.get("mensaje"),
                    "fase": "Análisis Sintáctico",
                    "detalles": sintactico_result.get("errores", []),
                    "sugerencia": "Revisa la estructura del código (funciones, declaraciones, llaves balanceadas)"
                }), 400
        except Exception as e:
            return jsonify({
                "error": f"Error sintáctico: {str(e)}",
                "fase": "Análisis Sintáctico",
                "sugerencia": "Verifica que las funciones tengan parámetros válidos y que los bloques estén balanceados"
            }), 400

        #  ENTROPÍA
        try:
            entropia_calc = CalculadorEntropia(tokens)
            entropia_valor = entropia_calc.calcular()
            estadisticas = entropia_calc.estadisticas_completas()
        except Exception as e:
            return jsonify({
                "error": f"Error en cálculo de entropía: {str(e)}",
                "fase": "Análisis de Entropía"
            }), 400

        # Respuesta exitosa
        return jsonify({
            "tokens": [t.to_dict() for t in tokens],
            "sintactico": sintactico_result,
            "entropia": entropia_valor,
            "estadisticas": estadisticas,
            "exito": True
        }), 200

    except Exception as e:
        return jsonify({
            "error": f"Error inesperado: {str(e)}",
            "sugerencia": "Contacta al administrador si el error persiste"
        }), 500


@bp.route('/info', methods=['GET'])
def info():
    """Endpoint de información del analizador"""
    return jsonify({
        "nombre": "Analizador Léxico y Sintáctico",
        "version": "2.0",
        "descripcion": "Analizador para lenguajes tipo C con soporte para estructuras de control",
        "caracteristicas": [
            "Análisis léxico mejorado (strings, floats, operadores compuestos, comentarios)",
            "Análisis sintáctico avanzado (if, while, for, expresiones complejas)",
            "Cálculo de entropía Shannon",
            "Manejo robusto de errores"
        ]
    }), 200