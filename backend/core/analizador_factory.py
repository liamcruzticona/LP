"""
ABSTRACCIÓN: El Factory Pattern oculta qué analizador concreto
se instancia. El cliente solo pide un lenguaje y recibe el analizador.

ENCAPSULAMIENTO: Los analizadores y validadores concretos se almacenan
en diccionarios privados al módulo.

POLIMORFISMO: get_analizador() y get_validador_semantico() retornan
la instancia correcta según el lenguaje, pero el cliente los usa igual.
"""

from core.analizadores.c_analyzer import CAnalizadorLenguaje
from core.analizadores.cpp_analyzer import CppAnalizadorLenguaje
from core.analizadores.java_analyzer import JavaAnalizadorLenguaje
from core.analizadores.javascript_analyzer import JavaScriptAnalizadorLenguaje
from core.analizadores.python_analyzer import PythonAnalizadorLenguaje

from core.semantica.semantica_c import ValidadorSemanticoC
from core.semantica.semantica_cpp import ValidadorSemanticoCpp
from core.semantica.semantica_java import ValidadorSemanticoJava
from core.semantica.semantica_js import ValidadorSemanticoJS
from core.semantica.semantica_py import ValidadorSemanticoPython

_ANALIZADORES = {
    "c": CAnalizadorLenguaje(),
    "cpp": CppAnalizadorLenguaje(),
    "java": JavaAnalizadorLenguaje(),
    "javascript": JavaScriptAnalizadorLenguaje(),
    "python": PythonAnalizadorLenguaje(),
}

_VALIDADORES = {
    "c": ValidadorSemanticoC,
    "cpp": ValidadorSemanticoCpp,
    "java": ValidadorSemanticoJava,
    "javascript": ValidadorSemanticoJS,
    "python": ValidadorSemanticoPython,
}


def get_analizador(lenguaje):
    """POLIMORFISMO: retorna el analizador adecuado según el lenguaje."""
    llave = (lenguaje or "").strip().lower()
    analizador = _ANALIZADORES.get(llave)
    if analizador is None:
        soportados = list(_ANALIZADORES.keys())
        raise ValueError(
            f"Lenguaje '{lenguaje}' no soportado. "
            f"Soportados: {', '.join(soportados)}"
        )
    return analizador


def get_validador_semantico(lenguaje, ast):
    """
    POLIMORFISMO: retorna el validador semántico correcto según el lenguaje.
    Cada lenguaje tiene su propia clase que hereda de ValidadorSemanticoBase.
    """
    llave = (lenguaje or "").strip().lower()
    clase = _VALIDADORES.get(llave, ValidadorSemanticoC)
    return clase(ast)


def idiomas_disponibles():
    return {k: v.nombre for k, v in _ANALIZADORES.items()}
