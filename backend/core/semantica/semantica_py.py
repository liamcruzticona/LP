"""
HERENCIA: ValidadorSemanticoPython hereda de ValidadorSemanticoBase.
POLIMORFISMO: Agrega reglas específicas de Python (asignación = declaración,
indentación, self en métodos).
"""

from core.semantica.base import ValidadorSemanticoBase


class ValidadorSemanticoPython(ValidadorSemanticoBase):
    """
    Validador semántico para Python.
    Reglas específicas:
    - 'asignacion' funciona como declaración (tipado dinámico)
    - 'self' debe usarse dentro de clases
    - Indentación ya validada en el parser
    """

    def _validar_asignacion(self, nodo):
        identificador = nodo.get("identificador")
        if identificador:
            if not self._existe(identificador):
                self._declarar(identificador, nodo.get("linea"))
        if nodo.get("valor"):
            self._validar_nodo(nodo["valor"])

    def _validar_for(self, nodo):
        variable = nodo.get("variable")
        if variable and not self._existe(variable):
            self._declarar(variable, nodo.get("linea"))
        self._push_ambito()
        for item in nodo.get("bloque", []):
            self._validar_nodo(item)
        self._pop_ambito()
