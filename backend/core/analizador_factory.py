from core.analizadores.base import AnalizadorLenguaje
from core.analizadores.c_analyzer import CAnalizadorLenguaje
from core.analizadores.cpp_analyzer import CppAnalizadorLenguaje
from core.analizadores.java_analyzer import JavaAnalizadorLenguaje
from core.analizadores.javascript_analyzer import JavaScriptAnalizadorLenguaje
from core.analizadores.python_analyzer import PythonAnalizadorLenguaje


ANALIZADORES = {
    "c": CAnalizadorLenguaje(),
    "cpp": CppAnalizadorLenguaje(),
    "java": JavaAnalizadorLenguaje(),
    "javascript": JavaScriptAnalizadorLenguaje(),
    "python": PythonAnalizadorLenguaje(),
}


def get_analizador(lenguaje):
    llave = (lenguaje or "").strip().lower()
    analizador = ANALIZADORES.get(llave)
    if analizador is None:
        soportados = [k for k, v in ANALIZADORES.items() if v is not None]
        raise ValueError(
            f"Lenguaje '{lenguaje}' no soportado todavía. Soportados: {', '.join(soportados)}"
        )
    return analizador


def idiomas_disponibles():
    return {
        "c": "C",
        "cpp": "C++",
        "java": "Java",
        "javascript": "JavaScript",
        "python": "Python"
    }


def get_analizador(lenguaje):
    llave = (lenguaje or "").strip().lower()
    analizador = ANALIZADORES.get(llave)
    if analizador is None:
        soportados = [k for k, v in ANALIZADORES.items() if v is not None]
        raise ValueError(
            f"Lenguaje '{lenguaje}' no soportado todavía. Soportados: {', '.join(soportados)}"
        )
    return analizador


def idiomas_disponibles():
    return {
        "c": "C",
        "cpp": "C++ (compatible con C básico)",
        "java": "Java (compatible con C básico)",
        "javascript": "JavaScript",
"python": "Python"
    }
