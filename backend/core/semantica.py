class ValidadorSemantico:
    """Validador semántico general para el AST unificado."""

    def __init__(self, ast):
        self.ast = ast or []
        self.errores = []
        self.ambitos = [{}]

    def validar(self):
        for nodo in self.ast:
            self._validar_nodo(nodo)
        return {"exito": len(self.errores) == 0, "errores": self.errores}

    def _push_ambito(self):
        self.ambitos.append({})

    def _pop_ambito(self):
        self.ambitos.pop()

    def _declarar(self, nombre, linea=None):
        actual = self.ambitos[-1]
        if nombre in actual:
            self.errores.append({
                "linea": linea,
                "mensaje": f"Variable '{nombre}' ya declarada en el mismo ambito"
            })
        actual[nombre] = True

    def _existe(self, nombre):
        for ambito in reversed(self.ambitos):
            if nombre in ambito:
                return True
        return False

    def _validar_nodo(self, nodo):
        if not isinstance(nodo, dict):
            return
        metodo = getattr(self, f"_validar_{nodo.get('tipo')}", self._validar_general)
        metodo(nodo)

    def _validar_general(self, nodo):
        for clave, valor in nodo.items():
            if isinstance(valor, dict):
                self._validar_nodo(valor)
            elif isinstance(valor, list):
                for item in valor:
                    self._validar_nodo(item)

    def _validar_declaracion(self, nodo):
        self._declarar(nodo.get("identificador"), nodo.get("linea"))
        if nodo.get("valor"):
            self._validar_nodo(nodo["valor"])

    def _validar_funcion(self, nodo):
        self._declarar(nodo.get("nombre"), nodo.get("linea"))
        self._push_ambito()
        for parametro in nodo.get("parametros", []):
            self._declarar(parametro.get("nombre"), parametro.get("linea"))
        self._validar_nodo({"tipo": "bloque", "valor": nodo.get("cuerpo", [])})
        self._pop_ambito()

    def _validar_bloque(self, nodo):
        for item in nodo.get("valor", []):
            self._validar_nodo(item)

    def _validar_expresion(self, nodo):
        self._validar_nodo(nodo.get("expresion"))

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
                        "mensaje": f"Asignación a '{nombre}' antes de declararlo"
                    })

    def _validar_id(self, nodo):
        if not self._existe(nodo.get("valor")):
            self.errores.append({
                "linea": nodo.get("linea"),
                "mensaje": f"Uso de variable '{nodo.get('valor')}' sin declaración previa"
            })

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
        self._validar_nodo(nodo.get("operando"))

    def _validar_numero(self, nodo):
        pass

    def _validar_float(self, nodo):
        pass

    def _validar_string(self, nodo):
        pass
