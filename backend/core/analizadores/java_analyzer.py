import re

from core.analizadores.base import AnalizadorLexicoBase, ParserBase, AnalizadorLenguaje
from core.token import Token

PALABRAS_RESERVADAS_JAVA = {
    "package", "import", "class", "public", "private", "protected", "static",
    "void", "int", "double", "boolean", "String", "new", "extends", "implements",
    "if", "else", "for", "while", "return", "null", "true", "false", "this"
}

TOKEN_REGEX_JAVA = [
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


class JavaLexer(AnalizadorLexicoBase):
    def __init__(self, codigo):
        super().__init__(codigo)
        self.pos = 0
        self.linea = 1
        self.columna = 1
        self.tokens = []

    def analizar(self):
        while self.pos < len(self.codigo):
            match = None
            for tipo, regex in TOKEN_REGEX_JAVA:
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
                    f"Error léxico Java en línea {self.linea}, columna {self.columna}: símbolo no reconocido"
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
        if tipo == "ID" and texto in PALABRAS_RESERVADAS_JAVA:
            tipo = "RESERVADA"
        token = Token(tipo, texto, self.linea, self.columna)
        self.tokens.append(token)
        self.columna += len(texto)


class JavaParser(ParserBase):
    def __init__(self, tokens):
        super().__init__(tokens)
        self.pos = 0

    def actual(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def avanzar(self):
        self.pos += 1

    def consumir(self, tipo_esperado, mensaje_custom=None):
        token = self.actual()
        if not token:
            raise Exception(mensaje_custom or f"Se esperaba {tipo_esperado} pero llegó fin de archivo")
        if token.tipo == tipo_esperado or (isinstance(tipo_esperado, list) and token.tipo in tipo_esperado):
            self.avanzar()
            return token
        msg = mensaje_custom or f"Se esperaba {tipo_esperado} pero se encontró {token.tipo}"
        raise Exception(f"Error sintáctico Java: {msg} en línea {token.linea}")

    def analizar(self):
        ast = []
        try:
            while self.actual() is not None:
                ast.append(self.declaracion())
        except Exception as e:
            return {"tipo": "error", "mensaje": str(e)}
        return ast

    def declaracion(self):
        token = self.actual()
        if not token:
            return None
        if token.tipo == "RESERVADA" and token.valor == "class":
            return self.clase()
        return self.sentencia()

    def clase(self):
        self.consumir("RESERVADA")
        nombre = self.consumir("ID")
        self._opt_extends()
        self.consumir("SIMBOLO", "se esperaba '{'")
        miembros = []
        while self.actual() and self.actual().valor != "}":
            miembros.append(self.miembro())
        self.consumir("SIMBOLO", "se esperaba '}'")
        return {"tipo": "clase", "nombre": nombre.valor, "miembros": miembros, "linea": nombre.linea}

    def _opt_extends(self):
        if self.actual() and self.actual().valor == "extends":
            self.consumir("RESERVADA")
            base = self.consumir("ID")
            return base.valor
        return None

    def miembro(self):
        if self.actual() and self.actual().valor in ["public", "private", "protected"]:
            self.consumir("RESERVADA")
        if self.actual() and self.actual().valor == "static":
            self.consumir("RESERVADA")
        if self.actual() and self.actual().tipo == "RESERVADA":
            return self.funcion_o_declaracion()
        raise Exception(f"Miembro inesperado en clase: {self.actual().valor}")

    def funcion_o_declaracion(self):
        tipo = self.consumir("RESERVADA")
        nombre = self.consumir("ID")
        if self.actual() and self.actual().valor == "(":
            self.consumir("SIMBOLO")
            parametros = self.parametros()
            self.consumir("SIMBOLO", "se esperaba ')'")
            self.consumir("SIMBOLO", "se esperaba '{'")
            cuerpo = self.bloque()
            self.consumir("SIMBOLO", "se esperaba '}'")
            return {"tipo": "metodo", "nombre": nombre.valor, "retorno": tipo.valor, "parametros": parametros, "cuerpo": cuerpo}
        identificador = nombre
        valor = None
        if self.actual() and self.actual().valor == "=":
            self.consumir("OPERADOR")
            valor = self.expresion()
        self.consumir("SIMBOLO", "se esperaba ';'")
        return {"tipo": "campo", "tipo_dato": tipo.valor, "identificador": identificador.valor, "valor": valor}

    def parametros(self):
        params = []
        while self.actual() and self.actual().valor != ")":
            tipo = self.consumir("RESERVADA")
            nombre = self.consumir("ID")
            params.append({"tipo": tipo.valor, "nombre": nombre.valor})
            if self.actual() and self.actual().valor == ",":
                self.consumir("SIMBOLO")
                continue
            break
        return params

    def bloque(self):
        sentencias = []
        while self.actual() and self.actual().valor != "}":
            sentencias.append(self.sentencia())
        return sentencias

    def sentencia(self):
        token = self.actual()
        if not token:
            return None
        if token.tipo == "RESERVADA":
            if token.valor == "if":
                return self.sentencia_if()
            if token.valor == "while":
                return self.sentencia_while()
            if token.valor == "for":
                return self.sentencia_for()
            if token.valor == "return":
                return self.sentencia_return()
        return self.sentencia_expresion()

    def sentencia_if(self):
        self.consumir("RESERVADA")
        self.consumir("SIMBOLO")
        condicion = self.expresion()
        self.consumir("SIMBOLO")
        self.consumir("SIMBOLO")
        bloque = self.bloque()
        self.consumir("SIMBOLO")
        bloque_else = None
        if self.actual() and self.actual().tipo == "RESERVADA" and self.actual().valor == "else":
            self.consumir("RESERVADA")
            self.consumir("SIMBOLO")
            bloque_else = self.bloque()
            self.consumir("SIMBOLO")
        return {"tipo": "if", "condicion": condicion, "bloque": bloque, "bloque_else": bloque_else}

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
        inicializacion = self.sentencia_expresion() if self.actual() and self.actual().valor != ";" else None
        self.consumir("SIMBOLO")
        condicion = self.expresion() if self.actual() and self.actual().valor != ";" else None
        self.consumir("SIMBOLO")
        incremento = self.expresion() if self.actual() and self.actual().valor != ")" else None
        self.consumir("SIMBOLO")
        self.consumir("SIMBOLO")
        bloque = self.bloque()
        self.consumir("SIMBOLO")
        return {"tipo": "for", "inicializacion": inicializacion, "condicion": condicion, "incremento": incremento, "bloque": bloque}

    def sentencia_return(self):
        self.consumir("RESERVADA")
        valor = self.expresion() if self.actual() and self.actual().valor != ";" else None
        self.consumir("SIMBOLO")
        return {"tipo": "return", "valor": valor}

    def sentencia_expresion(self):
        expr = self.expresion()
        if self.actual() and self.actual().valor == ";":
            self.consumir("SIMBOLO")
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
        raise Exception(f"Token inesperado '{token.valor}' en línea {token.linea}")

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
        }
        return precedencias.get(token.valor, 0)


class JavaAnalizadorLenguaje(AnalizadorLenguaje):
    def __init__(self):
        metadata = {
            "identidad": "Java",
            "tema": "Capas, clases y JVM",
            "keywords": ["class", "public", "static", "void", "new", "String", "extends", "implements"],
            "descripcion": "Java exige clases y métodos, con una sintaxis estructurada orientada a objetos."
        }
        super().__init__("Java", JavaLexer, JavaParser, slug="java", metadata=metadata)
