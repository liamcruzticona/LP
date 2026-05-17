import re

from core.analizadores.base import AnalizadorLexicoBase, ParserBase, AnalizadorLenguaje
from core.token import Token

PALABRAS_RESERVADAS_C = {
    "int", "float", "char", "double", "void", "if", "else", "while",
    "for", "return", "break", "continue", "struct", "const", "static"
}

TOKEN_REGEX_C = [
    ("COMENTARIO", r'//.*'),
    ("STRING", r'"([^"\\]|\\.)*"'),
    ("FLOAT", r'\d+\.\d+'),
    ("NUMERO", r'\d+'),
    ("OP_COMPUESTO", r'(\+=|-=|\*=|/=|==|!=|<=|>=|\+\+|--)'),
    ("ID", r'[a-zA-Z_][a-zA-Z0-9_]*'),
    ("OPERADOR", r'[+\-*/=%<>!&|]'),
    ("SIMBOLO", r'[;{}(),.\[\]]'),
    ("ESPACIO", r'\s+'),
]


class CLexer(AnalizadorLexicoBase):
    def __init__(self, codigo):
        super().__init__(codigo)
        self.pos = 0
        self.linea = 1
        self.columna = 1
        self.tokens = []

    def analizar(self):
        while self.pos < len(self.codigo):
            match = None
            for tipo, regex in TOKEN_REGEX_C:
                patron = re.compile(regex)
                match = patron.match(self.codigo, self.pos)
                if match:
                    texto = match.group(0)
                    if tipo == "ESPACIO":
                        self._manejar_espacios(texto)
                    else:
                        self._crear_token(tipo, texto)
                    self.pos = match.end(0)
                    break
            if not match:
                raise Exception(
                    f"Error léxico en línea {self.linea}, columna {self.columna}: símbolo no reconocido"
                )
        return self.tokens

    def _manejar_espacios(self, texto):
        if "\n" in texto:
            self.linea += texto.count("\n")
            self.columna = 1
        else:
            self.columna += len(texto)

    def _crear_token(self, tipo, texto):
        if tipo == "COMENTARIO":
            self.columna += len(texto)
            return

        if tipo == "ID" and texto in PALABRAS_RESERVADAS_C:
            tipo = "RESERVADA"
        if tipo == "OPERADOR" and texto in ["*", "&"]:
            tipo = "PUNTERO"

        token = Token(tipo, texto, self.linea, self.columna)
        self.tokens.append(token)
        self.columna += len(texto)


class CParser(ParserBase):
    def __init__(self, tokens):
        super().__init__(tokens)
        self.pos = 0
        self.errores = []

    def actual(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def avanzar(self):
        self.pos += 1

    def consumir(self, tipo_esperado, mensaje_custom=None):
        token = self.actual()
        if not token:
            raise Exception(mensaje_custom or f"Se esperaba {tipo_esperado} pero llegó fin de archivo")
        if token.tipo == tipo_esperado or (
            isinstance(tipo_esperado, list) and token.tipo in tipo_esperado
        ):
            self.avanzar()
            return token
        msg = mensaje_custom or f"Se esperaba {tipo_esperado} pero se encontró {token.tipo}"
        raise Exception(f"Error sintáctico: {msg} en línea {token.linea}")

    def analizar(self):
        ast = []
        try:
            while self.actual() is not None:
                ast.append(self.sentencia())
        except Exception as e:
            return {"tipo": "error", "mensaje": str(e), "errores": self.errores}
        return ast

    def sentencia(self):
        token = self.actual()
        if not token:
            return None
        if token.tipo == "RESERVADA":
            if token.valor in ["int", "float", "char", "double", "void", "const", "static"]:
                return self.declaracion_o_funcion()
            if token.valor == "if":
                return self.sentencia_if()
            if token.valor == "while":
                return self.sentencia_while()
            if token.valor == "for":
                return self.sentencia_for()
            if token.valor == "return":
                return self.sentencia_return()
            raise Exception(f"Sentencia desconocida: {token.valor}")
        if token.tipo in ["ID", "NUMERO", "FLOAT", "STRING"] or token.valor == "(":
            return self.sentencia_expresion()
        raise Exception(f"Error sintáctico: token inesperado '{token.valor}' en línea {token.linea}")

    def declaracion_o_funcion(self):
        pos_guardada = self.pos
        try:
            return self.funcion()
        except Exception:
            self.pos = pos_guardada
            return self.declaracion()

    def declaracion(self):
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
            "linea": tipo.linea,
            "valor": valor,
        }

    def funcion(self):
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
            "linea": nombre.linea,
            "parametros": parametros,
            "cuerpo": sentencias,
        }

    def parametros(self):
        params = []
        while self.actual() and self.actual().tipo == "RESERVADA":
            tipo = self.consumir("RESERVADA")
            nombre = self.consumir("ID")
            params.append({"tipo": tipo.valor, "nombre": nombre.valor, "linea": nombre.linea})
            if self.actual() and self.actual().valor == ",":
                self.consumir("SIMBOLO")
            else:
                break
        return params

    def bloque(self):
        sentencias = []
        while self.actual() and self.actual().valor != "}":
            sentencias.append(self.sentencia())
        return sentencias

    def sentencia_if(self):
        self.consumir("RESERVADA")
        self.consumir("SIMBOLO")
        condicion = self.expresion()
        self.consumir("SIMBOLO")
        self.consumir("SIMBOLO")
        bloque_if = self.bloque()
        self.consumir("SIMBOLO")
        bloque_else = None
        if self.actual() and self.actual().tipo == "RESERVADA" and self.actual().valor == "else":
            self.consumir("RESERVADA")
            self.consumir("SIMBOLO")
            bloque_else = self.bloque()
            self.consumir("SIMBOLO")
        return {"tipo": "if", "condicion": condicion, "bloque_if": bloque_if, "bloque_else": bloque_else}

    def sentencia_while(self):
        self.consumir("RESERVADA")
        self.consumir("SIMBOLO")
        condicion = self.expresion()
        self.consumir("SIMBOLO")
        self.consumir("SIMBOLO")
        bloque = self.bloque()
        self.consumir("SIMBOLO")
        return {"tipo": "while", "condicion": condicion, "bloque": bloque}

    def sentencia_for(self):
        self.consumir("RESERVADA")
        self.consumir("SIMBOLO")
        init = None
        if self.actual() and self.actual().valor != ";":
            if self.actual().tipo == "RESERVADA" and self.peek() and self.peek().tipo == "ID":
                init = self.declaracion_for()
            else:
                init = self.expresion()
        self.consumir("SIMBOLO")
        condicion = self.expresion() if self.actual() and self.actual().valor != ";" else None
        self.consumir("SIMBOLO")
        incremento = self.expresion() if self.actual() and self.actual().valor != ")" else None
        self.consumir("SIMBOLO")
        self.consumir("SIMBOLO")
        bloque = self.bloque()
        self.consumir("SIMBOLO")
        return {
            "tipo": "for",
            "inicializacion": init,
            "condicion": condicion,
            "incremento": incremento,
            "bloque": bloque,
        }

    def declaracion_for(self):
        tipo = self.consumir("RESERVADA")
        identificador = self.consumir("ID")
        valor = None
        if self.actual() and self.actual().tipo == "OPERADOR" and self.actual().valor == "=":
            self.consumir("OPERADOR")
            valor = self.expresion()
        return {
            "tipo": "declaracion",
            "tipo_dato": tipo.valor,
            "identificador": identificador.valor,
            "linea": tipo.linea,
            "valor": valor,
        }

    def sentencia_return(self):
        token = self.consumir("RESERVADA")
        valor = None
        if self.actual() and self.actual().valor != ";":
            valor = self.expresion()
        self.consumir("SIMBOLO")
        return {"tipo": "return", "valor": valor, "linea": token.linea}

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
            izquierda = {
                "tipo": "binaria",
                "izquierda": izquierda,
                "operador": op.valor,
                "derecha": derecha,
                "linea": op.linea,
            }
        return izquierda

    def primaria(self):
        token = self.actual()
        if not token:
            raise Exception("Expresión inesperada: fin de archivo")
        if token.tipo == "NUMERO":
            self.avanzar()
            return {"tipo": "numero", "valor": token.valor, "linea": token.linea}
        if token.tipo == "FLOAT":
            self.avanzar()
            return {"tipo": "float", "valor": token.valor, "linea": token.linea}
        if token.tipo == "STRING":
            self.avanzar()
            return {"tipo": "string", "valor": token.valor, "linea": token.linea}
        if token.tipo == "ID":
            nombre = token.valor
            linea = token.linea
            self.avanzar()
            if self.actual() and self.actual().valor == "(":
                self.consumir("SIMBOLO")
                args = self.argumentos()
                self.consumir("SIMBOLO")
                return {"tipo": "llamada_funcion", "nombre": nombre, "argumentos": args, "linea": linea}
            if self.actual() and self.actual().tipo == "OP_COMPUESTO" and self.actual().valor in ["++", "--"]:
                operador = self.actual().valor
                self.avanzar()
                return {"tipo": "unaria", "operador": operador, "operando": {"tipo": "id", "valor": nombre, "linea": linea}, "prefijo": False, "linea": linea}
            return {"tipo": "id", "valor": nombre, "linea": linea}
        if token.tipo == "OP_COMPUESTO" and token.valor in ["++", "--"]:
            op = token.valor
            linea = token.linea
            self.avanzar()
            expr = self.primaria()
            return {"tipo": "unaria", "operador": op, "operando": expr, "prefijo": True, "linea": linea}
        if token.valor == "(":
            self.consumir("SIMBOLO")
            expr = self.expresion()
            self.consumir("SIMBOLO")
            return expr
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
            "+=": 1, "-=": 1, "*=": 1, "/=": 1,
            "==": 2, "!=": 2, "<": 2, ">": 2, "<=": 2, ">=": 2,
            "+": 3, "-": 3,
            "*": 4, "/": 4, "%": 4,
            "++": 5, "--": 5,
        }
        return precedencias.get(token.valor, 0)


class CAnalizadorLenguaje(AnalizadorLenguaje):
    def __init__(self):
        metadata = {
            "identidad": "C",
            "tema": "Memoria, punteros y compilación directa",
            "keywords": ["int", "char", "float", "struct", "typedef", "return", "*", "&"],
            "descripcion": "C es un lenguaje de sistemas con punteros y declaracion explícita de tipos."
        }
        super().__init__("C", CLexer, CParser, slug="c", metadata=metadata)
