"""
HERENCIA: ValidadorSemanticoCpp hereda de ValidadorSemanticoBase.
POLIMORFISMO: Agrega reglas de clases, namespace, type checking.
"""

from core.semantica.base import ValidadorSemanticoBase

_TIPOS_NUMERICOS_CPP = {"int", "float", "double", "char", "bool", "short", "long", "auto"}


class ValidadorSemanticoCpp(ValidadorSemanticoBase):
    """
    Validador semántico para C++.
    Reglas específicas:
    - Clases con miembros públicos/privados/protegidos
    - 'using namespace' válido a nivel archivo
    - Type checking: detecta asignaciones de tipos incompatibles
    """

    def _validar_declaracion(self, nodo):
        super()._validar_declaracion(nodo)
        tipo = nodo.get("tipo_dato", "")
        valor = nodo.get("valor", {})
        if tipo in _TIPOS_NUMERICOS_CPP and tipo != "auto" and valor:
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

    def _validar_clase(self, nodo):
        nombre = nodo.get("nombre")
        if nombre:
            self._declarar(nombre, nodo.get("linea"))
        self._push_ambito()
        for miembro in nodo.get("miembros", []):
            self._validar_nodo(miembro)
        self._pop_ambito()

    def _validar_etiqueta_acceso(self, nodo):
        pass

    def _validar_using_namespace(self, nodo):
        pass
