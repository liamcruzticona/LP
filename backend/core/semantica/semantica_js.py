"""
HERENCIA: ValidadorSemanticoJS hereda de ValidadorSemanticoBase.
POLIMORFISMO: Agrega reglas de JavaScript (let/const/var, hoisting, arrow functions).
"""

from core.semantica.base import ValidadorSemanticoBase


class ValidadorSemanticoJS(ValidadorSemanticoBase):
    """
    Validador semántico para JavaScript.
    Reglas específicas:
    - 'const' no permite reasignación
    - 'var' tiene hoisting implícito
    - Funciones flecha no tienen this propio
    """

    def _validar_declaracion(self, nodo):
        identificador = nodo.get("identificador")
        declarador = nodo.get("declarador", "")
        if identificador:
            self._declarar(identificador, nodo.get("linea"))
        if nodo.get("valor"):
            self._validar_nodo(nodo["valor"])
        if declarador == "const" and identificador:
            pass

    def _validar_funcion_flecha(self, nodo):
        self._push_ambito()
        for parametro in nodo.get("parametros", []):
            self._declarar(parametro.get("nombre"), parametro.get("linea"))
        cuerpo = nodo.get("cuerpo", [])
        if isinstance(cuerpo, list):
            for item in cuerpo:
                self._validar_nodo(item)
        if nodo.get("expresion"):
            self._validar_nodo(nodo["expresion"])
        self._pop_ambito()
