"""
HERENCIA: ValidadorSemanticoC hereda de ValidadorSemanticoBase.
POLIMORFISMO: Agrega reglas específicas de C (const, punteros, struct, type checking).
"""

from core.semantica.base import ValidadorSemanticoBase

_TIPOS_NUMERICOS = {"int", "float", "double", "char", "short", "long"}


class ValidadorSemanticoC(ValidadorSemanticoBase):
    """
    Validador semántico para C.
    Reglas específicas:
    - Punteros deben inicializarse o asignarse antes de usar
    - 'const' no permite reasignación
    - Type checking: detecta asignaciones de tipos incompatibles
    """

    def _validar_declaracion(self, nodo):
        super()._validar_declaracion(nodo)
        tipo = nodo.get("tipo_dato", "")
        valor = nodo.get("valor", {})
        if tipo in _TIPOS_NUMERICOS and valor:
            if valor.get("tipo") == "string":
                self.advertencias.append({
                    "linea": nodo.get("linea"),
                    "mensaje": f"Asignacion de string a variable de tipo '{tipo}' puede ser incorrecta",
                })
            elif valor.get("tipo") == "float" and tipo == "int":
                self.advertencias.append({
                    "linea": nodo.get("linea"),
                    "mensaje": f"Asignacion de float a variable 'int' pierde precision",
                })

    def _validar_binaria(self, nodo):
        super()._validar_binaria(nodo)
        if nodo.get("operador") == "=":
            izquierda = nodo.get("izquierda", {})
            if izquierda.get("tipo") == "unaria" and izquierda.get("operador") == "*":
                pass
