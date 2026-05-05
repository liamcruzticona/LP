"""Módulo de análisis sintáctico mejorado"""

from core.token import Token

class Parser:
    """
     ABSTRACCIÓN:
    Clase que encapsula toda la lógica del análisis sintáctico.
    """

    def __init__(self, tokens):
        # 🔒 ENCAPSULAMIENTO
        self.tokens = tokens
        self.pos = 0
        self.errores = []

    def actual(self):
        """Devuelve el token actual"""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def peek(self, offset=1):
        """Mira adelante sin consumir"""
        if self.pos + offset < len(self.tokens):
            return self.tokens[self.pos + offset]
        return None

    def avanzar(self):
        """Avanza al siguiente token"""
        self.pos += 1

    def consumir(self, tipo_esperado, mensaje_custom=None):
        """
        POLIMORFISMO (conceptual):
        Este método funciona para cualquier tipo de token esperado
        """
        token = self.actual()

        if not token:
            self.errores.append(f"Se esperaba {tipo_esperado} pero llegó fin de archivo")
            raise Exception(f"Error sintáctico: se esperaba {tipo_esperado}")

        if token.tipo == tipo_esperado or (isinstance(tipo_esperado, list) and token.tipo in tipo_esperado):
            self.avanzar()
            return token
        else:
            msg = mensaje_custom or f"se esperaba {tipo_esperado} pero se encontró {token.tipo}"
            self.errores.append(f"Error en línea {token.linea}: {msg}")
            raise Exception(f"Error sintáctico: {msg} en línea {token.linea}")

    def analizar(self):
        """
        ABSTRACCIÓN:
        
        """
        resultados = []

        try:
            while self.actual() is not None:
                resultados.append(self.sentencia())
        except Exception as e:
            return {"tipo": "error", "mensaje": str(e), "errores": self.errores}

        return resultados

    def sentencia(self):
        """Parsea cualquier sentencia"""
        token = self.actual()

        if not token:
            return None

        if token.tipo == "RESERVADA":
            if token.valor in ["int", "float", "char", "double", "void"]:
                return self.declaracion_o_funcion()
            elif token.valor == "if":
                return self.sentencia_if()
            elif token.valor == "while":
                return self.sentencia_while()
            elif token.valor == "for":
                return self.sentencia_for()
            elif token.valor == "return":
                return self.sentencia_return()
            else:
                raise Exception(f"Sentencia desconocida: {token.valor}")

        if token.tipo in ["ID", "NUMERO", "FLOAT", "STRING"] or token.valor == "(":
            return self.sentencia_expresion()

        raise Exception(f"Error sintáctico: token inesperado '{token.valor}' en línea {token.linea}")

    def sentencia_expresion(self):
        expr = self.expresion()
        self.consumir("SIMBOLO", "se esperaba ';'")
        return {"tipo": "expresion", "expresion": expr}

    def declaracion_o_funcion(self):
        """Determina si es una declaración o función"""
        pos_guardada = self.pos
        errores_guardados = self.errores.copy()

        try:
            return self.funcion()
        except Exception:
            self.pos = pos_guardada
            self.errores = errores_guardados
            return self.declaracion()

    def declaracion(self):
        """Regla: tipo ID [= valor] ;"""
        tipo = self.consumir("RESERVADA")
        identificador = self.consumir("ID")

        valor = None
        if self.actual() and self.actual().tipo == "OPERADOR" and self.actual().valor == "=":
            self.consumir("OPERADOR")
            valor = self.expresion()

        self.consumir("SIMBOLO", "se esperaba ';'")

        return {
            "tipo": "declaracion",
            "tipo_dato": tipo.valor,
            "identificador": identificador.valor,
            "valor": valor
        }

    def funcion(self):
        """Regla: tipo ID ( parametros ) { sentencias }"""
        tipo_retorno = self.consumir("RESERVADA")
        nombre = self.consumir("ID")
        self.consumir("SIMBOLO", "se esperaba '('")

        parametros = self.parametros()

        self.consumir("SIMBOLO", "se esperaba ')'")
        self.consumir("SIMBOLO", "se esperaba '{'")

        sentencias = self.bloque()

        self.consumir("SIMBOLO", "se esperaba '}'")

        return {
            "tipo": "funcion",
            "tipo_retorno": tipo_retorno.valor,
            "nombre": nombre.valor,
            "parametros": parametros,
            "cuerpo": sentencias
        }

    def parametros(self):
        """Parsea parámetros de función"""
        params = []

        if self.actual() and self.actual().tipo == "RESERVADA":
            while True:
                tipo = self.consumir("RESERVADA")
                nombre = self.consumir("ID")
                params.append({"tipo": tipo.valor, "nombre": nombre.valor})

                if self.actual() and self.actual().valor == ",":
                    self.consumir("SIMBOLO")
                else:
                    break

        return params

    def bloque(self):
        """Parsea un bloque de sentencias"""
        sentencias = []

        while self.actual() and self.actual().valor != "}":
            sentencias.append(self.sentencia())

        return sentencias

    def sentencia_if(self):
        self.consumir("RESERVADA")  # if
        self.consumir("SIMBOLO")  # (
        condicion = self.expresion()
        self.consumir("SIMBOLO")  # )
        self.consumir("SIMBOLO")  # {
        bloque_if = self.bloque()
        self.consumir("SIMBOLO")  # }

        bloque_else = None
        if self.actual() and self.actual().tipo == "RESERVADA" and self.actual().valor == "else":
            self.consumir("RESERVADA")
            self.consumir("SIMBOLO")  # {
            bloque_else = self.bloque()
            self.consumir("SIMBOLO")  # }

        return {"tipo": "if", "condicion": condicion, "bloque_if": bloque_if, "bloque_else": bloque_else}

    def sentencia_while(self):
        self.consumir("RESERVADA")  # while
        self.consumir("SIMBOLO")  # (
        condicion = self.expresion()
        self.consumir("SIMBOLO")  # )
        self.consumir("SIMBOLO")  # {
        bloque = self.bloque()
        self.consumir("SIMBOLO")  # }

        return {"tipo": "while", "condicion": condicion, "bloque": bloque}

    def sentencia_for(self):
        self.consumir("RESERVADA")  # for
        self.consumir("SIMBOLO")  # (

        init = None
        if self.actual() and self.actual().valor != ";":
            init = self.expresion()
        self.consumir("SIMBOLO")  # ;

        condicion = self.expresion()
        self.consumir("SIMBOLO")  # ;

        incremento = None
        if self.actual() and self.actual().valor != ")":
            incremento = self.expresion()
        self.consumir("SIMBOLO")  # )

        self.consumir("SIMBOLO")  # {
        bloque = self.bloque()
        self.consumir("SIMBOLO")  # }

        return {"tipo": "for", "inicializacion": init, "condicion": condicion, "incremento": incremento, "bloque": bloque}

    def sentencia_return(self):
        self.consumir("RESERVADA")
        valor = None
        if self.actual() and self.actual().valor != ";":
            valor = self.expresion()
        self.consumir("SIMBOLO")  # ;
        return {"tipo": "return", "valor": valor}

    def sentencia_expresion(self):
        expr = self.expresion()
        self.consumir("SIMBOLO", "se esperaba ';'")
        return {"tipo": "expresion", "expresion": expr}

    def expresion(self):
        return self.expresion_binaria(0)

    def expresion_binaria(self, min_precedencia):
        izquierda = self.primaria()

        while self.actual() and self.es_operador_binario(self.actual()):
            op = self.actual()
            prec = self.precedencia(op)

            if prec < min_precedencia:
                break

            self.avanzar()
            derecha = self.expresion_binaria(prec + 1)
            izquierda = {"tipo": "binaria", "izquierda": izquierda, "operador": op.valor, "derecha": derecha}

        return izquierda

    def primaria(self):
        token = self.actual()

        if not token:
            raise Exception("Expresión inesperada: fin de archivo")

        if token.tipo == "NUMERO":
            self.avanzar()
            return {"tipo": "numero", "valor": token.valor}

        if token.tipo == "FLOAT":
            self.avanzar()
            return {"tipo": "float", "valor": token.valor}

        if token.tipo == "STRING":
            self.avanzar()
            return {"tipo": "string", "valor": token.valor}

        if token.tipo == "ID":
            nombre = token.valor
            self.avanzar()
            if self.actual() and self.actual().valor == "(":
                self.consumir("SIMBOLO")
                args = self.argumentos()
                self.consumir("SIMBOLO")
                return {"tipo": "llamada_funcion", "nombre": nombre, "argumentos": args}
            return {"tipo": "id", "valor": nombre}

        if token.valor == "(":
            self.consumir("SIMBOLO")
            expr = self.expresion()
            self.consumir("SIMBOLO")
            return expr

        if token.tipo == "OP_COMPUESTO" and token.valor in ["++", "--"]:
            op = token.valor
            self.avanzar()
            expr = self.primaria()
            return {"tipo": "unaria", "operador": op, "operando": expr, "prefijo": True}

        raise Exception(f"Error sintáctico: token inesperado '{token.valor}' en línea {token.linea}")

    def argumentos(self):
        args = []
        if self.actual() and self.actual().valor != ")":
            args.append(self.expresion())
            while self.actual() and self.actual().valor == ",":
                self.consumir("SIMBOLO")
                args.append(self.expresion())
        return args

    def es_operador_binario(self, token):
        return token.tipo in ["OPERADOR", "OP_COMPUESTO"]

    def precedencia(self, token):
        precedencias = {
            "=": 1,
            "+=": 1, "-=" : 1, "*=" : 1, "/=" : 1,
            "==": 2, "!=": 2, "<": 2, ">": 2, "<=": 2, ">=": 2,
            "+": 3, "-": 3,
            "*": 4, "/": 4, "%": 4,
            "++": 5, "--": 5
        }
        return precedencias.get(token.valor, 0)
