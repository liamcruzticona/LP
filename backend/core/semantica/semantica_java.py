"""
HERENCIA: ValidadorSemanticoJava hereda de ValidadorSemanticoBase.
POLIMORFISMO: Agrega reglas de Java (clases obligatorias, campos, métodos, type checking).
"""

from core.semantica.base import ValidadorSemanticoBase

_TIPOS_NUMERICOS_JAVA = {"int", "float", "double", "char", "boolean", "short", "long", "byte"}


class ValidadorSemanticoJava(ValidadorSemanticoBase):
    """
    Validador semántico para Java.
    Reglas específicas:
    - Toplevel debe ser una clase
    - Métodos tienen tipo de retorno
    - Type checking: detecta asignaciones de tipos incompatibles
    """

    def _validar_declaracion(self, nodo):
        super()._validar_declaracion(nodo)
        tipo = nodo.get("tipo_dato", "")
        valor = nodo.get("valor", {})
        if tipo in _TIPOS_NUMERICOS_JAVA and valor:
            if valor.get("tipo") == "string":
                self.advertencias.append({
                    "linea": nodo.get("linea"),
                    "mensaje": f"Asignacion de String a variable de tipo '{tipo}' no compatible",
                })
            elif valor.get("tipo") == "float" and tipo in ("int", "long"):
                self.advertencias.append({
                    "linea": nodo.get("linea"),
                    "mensaje": f"Asignacion de float a '{tipo}' requiere cast explícito",
                })

    def _validar_campo(self, nodo):
        identificador = nodo.get("identificador")
        if identificador:
            self._declarar(identificador, nodo.get("linea"))
        tipo = nodo.get("tipo_dato", "")
        valor = nodo.get("valor", {})
        if tipo in _TIPOS_NUMERICOS_JAVA and valor:
            if valor.get("tipo") == "string":
                self.advertencias.append({
                    "linea": nodo.get("linea"),
                    "mensaje": f"Campo '{identificador}' de tipo '{tipo}' no puede recibir String",
                })

    def _validar_clase(self, nodo):
        nombre = nodo.get("nombre")
        if nombre:
            self._declarar(nombre, nodo.get("linea"))
        self._push_ambito()
        for miembro in nodo.get("miembros", []):
            self._validar_nodo(miembro)
        self._pop_ambito()

    def _validar_metodo(self, nodo):
        self._declarar(nodo.get("nombre"), nodo.get("linea"))
        self._push_ambito()
        for parametro in nodo.get("parametros", []):
            self._declarar(parametro.get("nombre"), parametro.get("linea"))
        cuerpo = nodo.get("cuerpo", [])
        if isinstance(cuerpo, list):
            for item in cuerpo:
                self._validar_nodo(item)
        self._pop_ambito()
