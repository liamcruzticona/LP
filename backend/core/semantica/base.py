"""
ABSTRACCIÓN: ValidadorSemanticoBase es la clase abstracta que define
la interfaz común para todos los validadores semánticos por lenguaje.

HERENCIA: Cada lenguaje (C, C++, Java, JS, Python) hereda de esta clase
y sobrescribe los métodos necesarios.

ENCAPSULAMIENTO: El manejo de ámbitos (_push_ambito, _pop_ambito, _declarar, _existe)
es privado y compartido.

POLIMORFISMO: _validar_nodo despacha al método específico según el tipo de nodo AST.
"""

from abc import ABC, abstractmethod


class ValidadorSemanticoBase(ABC):
    """Validador semántico base con lógica de ámbitos compartida."""

    def __init__(self, ast):
        self.ast = ast or []
        self.errores = []
        self.advertencias = []
        self.ambitos = [{}]

    def validar(self):
        for nodo in self.ast:
            self._validar_nodo(nodo)
        return {
            "exito": len(self.errores) == 0,
            "errores": self.errores,
            "advertencias": self.advertencias,
        }

    # ── Manejo de ámbitos (encapsulado) ──

    def _push_ambito(self):
        self.ambitos.append({})

    def _pop_ambito(self):
        if len(self.ambitos) > 1:
            self.ambitos.pop()

    def _declarar(self, nombre, linea=None, tipo_info=None):
        actual = self.ambitos[-1]
        if nombre in actual:
            self.errores.append({
                "linea": linea,
                "mensaje": f"Variable '{nombre}' ya declarada en el mismo ámbito",
            })
        actual[nombre] = tipo_info or True

    def _existe(self, nombre):
        for ambito in reversed(self.ambitos):
            if nombre in ambito:
                return True
        return False

    # ── Despacho polimórfico ──

    def _validar_nodo(self, nodo):
        if not isinstance(nodo, dict):
            return
        tipo = nodo.get("tipo", "")
        metodo = getattr(self, f"_validar_{tipo}", None)
        if metodo:
            metodo(nodo)
        else:
            self._validar_general(nodo)

    def _validar_general(self, nodo):
        for clave, valor in nodo.items():
            if isinstance(valor, dict):
                self._validar_nodo(valor)
            elif isinstance(valor, list):
                for item in valor:
                    self._validar_nodo(item)

    # ── Validaciones comunes (compartidas por herencia) ──

    def _validar_declaracion(self, nodo):
        identificador = nodo.get("identificador")
        if identificador:
            self._declarar(identificador, nodo.get("linea"))
        if nodo.get("valor"):
            self._validar_nodo(nodo["valor"])

    def _validar_asignacion(self, nodo):
        identificador = nodo.get("identificador")
        if identificador:
            if not self._existe(identificador):
                self._declarar(identificador, nodo.get("linea"))
            else:
                pass
        if nodo.get("valor"):
            self._validar_nodo(nodo["valor"])

    def _validar_funcion(self, nodo):
        self._declarar(nodo.get("nombre"), nodo.get("linea"))
        self._push_ambito()
        for parametro in nodo.get("parametros", []):
            self._declarar(parametro.get("nombre"), parametro.get("linea"))
        cuerpo = nodo.get("cuerpo", [])
        if isinstance(cuerpo, list):
            for item in cuerpo:
                self._validar_nodo(item)
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

    def _validar_campo(self, nodo):
        identificador = nodo.get("identificador")
        if identificador:
            self._declarar(identificador, nodo.get("linea"))
        if nodo.get("valor"):
            self._validar_nodo(nodo["valor"])

    def _validar_bloque(self, nodo):
        for item in nodo.get("valor", []):
            self._validar_nodo(item)

    def _validar_expresion(self, nodo):
        if nodo.get("expresion"):
            self._validar_nodo(nodo["expresion"])

    def _validar_binaria(self, nodo):
        self._validar_nodo(nodo.get("izquierda"))
        self._validar_nodo(nodo.get("derecha"))
        if nodo.get("operador") == "=":
            izquierda = nodo.get("izquierda")
            if izquierda and izquierda.get("tipo") == "id":
                nombre = izquierda.get("valor")
                if not self._existe(nombre):
                    self.errores.append({
                        "linea": izquierda.get("linea"),
                        "mensaje": f"Asignación a '{nombre}' sin declaración previa",
                    })

    def _validar_id(self, nodo):
        if not self._existe(nodo.get("valor")):
            self.errores.append({
                "linea": nodo.get("linea"),
                "mensaje": f"Uso de variable '{nodo.get('valor')}' sin declaración previa",
            })

    def _validar_miembro(self, nodo):
        self._validar_nodo(nodo.get("objeto"))

    def _validar_llamada_funcion(self, nodo):
        for arg in nodo.get("argumentos", []):
            self._validar_nodo(arg)

    def _validar_while(self, nodo):
        self._validar_nodo(nodo.get("condicion"))
        self._push_ambito()
        for item in nodo.get("bloque", []):
            self._validar_nodo(item)
        self._pop_ambito()

    def _validar_if(self, nodo):
        self._validar_nodo(nodo.get("condicion"))
        self._push_ambito()
        for item in nodo.get("bloque_if", []):
            self._validar_nodo(item)
        self._pop_ambito()
        if nodo.get("bloque_else"):
            self._push_ambito()
            for item in nodo.get("bloque_else", []):
                self._validar_nodo(item)
            self._pop_ambito()

    def _validar_for(self, nodo):
        self._push_ambito()
        if nodo.get("inicializacion"):
            self._validar_nodo(nodo.get("inicializacion"))
        if nodo.get("condicion"):
            self._validar_nodo(nodo.get("condicion"))
        if nodo.get("incremento"):
            self._validar_nodo(nodo.get("incremento"))
        for item in nodo.get("bloque", []):
            self._validar_nodo(item)
        self._pop_ambito()

    def _validar_return(self, nodo):
        if nodo.get("valor"):
            self._validar_nodo(nodo.get("valor"))

    def _validar_unaria(self, nodo):
        if nodo.get("operando"):
            self._validar_nodo(nodo["operando"])

    def _validar_numero(self, nodo):
        pass

    def _validar_float(self, nodo):
        pass

    def _validar_string(self, nodo):
        pass

    def _validar_pass(self, nodo):
        pass
