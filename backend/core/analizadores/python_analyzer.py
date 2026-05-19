"""
HERENCIA: PythonLexer(AnalizadorLexicoBase), PythonParser(ParserBase)
heredan directamente de las clases base abstractas, NO de CLikeBase,
porque Python tiene sintaxis basada en indentación.

ABSTRACCIÓN: Oculta la complejidad del análisis de indentación
(INDENT/DEDENT) exponiendo solo analizar().
"""

import re

from core.analizadores.base import AnalizadorLexicoBase, ParserBase, AnalizadorLenguaje
from core.token import Token


PALABRAS_RESERVADAS_PY = {
    "def", "class", "if", "elif", "else", "while", "for", "in", "return",
    "True", "False", "None", "and", "or", "not", "pass",
    "import", "from", "as",
}

TOKEN_REGEX_PY = [
    ("COMENTARIO", r'#.*'),
    ("STRING", r'"([^"\\]|\\.)*"|\'([^\'\\]|\\.)*\''),
    ("FLOAT", r'\d+\.\d+'),
    ("NUMERO", r'\d+'),
    ("OP_COMPUESTO", r'(==|!=|<=|>=|\+=|-=|\*=|/=|//=|\*\*|\+\+|--)'),
    ("ID", r'[a-zA-Z_][a-zA-Z0-9_]*'),
    ("OPERADOR", r'[+\-*/%=<>!&|^]'),
    ("SIMBOLO", r'[:;(),.\[\]]'),
    ("ESPACIO", r'[ \t]+'),
]


class PythonLexer(AnalizadorLexicoBase):
    """
    ABSTRACCIÓN: Oculta la lógica de indentación significativa.

    ENCAPSULAMIENTO: _procesar_indentacion y _crear_token
    son métodos privados.
    """

    def __init__(self, codigo):
        super().__init__(codigo)
        self.tokens = []
        self.indent_stack = [0]

    def analizar(self):
        line_inicio = True
        for numero_linea, line in enumerate(
            self.codigo.splitlines(True), start=1
        ):
            if line_inicio:
                self._procesar_indentacion(line, numero_linea)
                line_inicio = False

            if line.strip() == "" or line.lstrip().startswith("#"):
                if line.endswith("\n"):
                    line_inicio = True
                continue

            pos = 0
            while pos < len(line):
                if line[pos] == "\n":
                    line_inicio = True
                    pos += 1
                    continue

                match = None
                for tipo, regex in TOKEN_REGEX_PY:
                    patron = re.compile(regex)
                    match = patron.match(line, pos)
                    if match:
                        texto = match.group(0)
                        if tipo == "ESPACIO":
                            pos = match.end(0)
                            continue
                        if tipo == "COMENTARIO":
                            pos = len(line)
                            break
                        self._crear_token(tipo, texto, numero_linea, pos + 1)
                        pos = match.end(0)
                        break
                if not match:
                    raise Exception(
                        f"Error léxico Python en línea {numero_linea}, "
                        f"columna {pos + 1}: símbolo no reconocido"
                    )

        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            self.tokens.append(Token("DEDENT", "", numero_linea, 0))

        return self.tokens

    def _procesar_indentacion(self, line, linea):
        indent = len(line) - len(line.lstrip(" \t"))
        if indent > self.indent_stack[-1]:
            self.indent_stack.append(indent)
            self.tokens.append(Token("INDENT", "", linea, 1))
        while indent < self.indent_stack[-1]:
            self.indent_stack.pop()
            self.tokens.append(Token("DEDENT", "", linea, 1))

    def _crear_token(self, tipo, texto, linea, columna):
        if tipo == "ID" and texto in PALABRAS_RESERVADAS_PY:
            tipo = "RESERVADA"
        self.tokens.append(Token(tipo, texto, linea, columna))


class PythonParser(ParserBase):
    """
    POLIMORFISMO: sentencia(), funcion(), sentencia_if() se
    comportan distinto que en CParser/JavaParser porque Python
    usa indentación en vez de llaves {}.
    """

    def __init__(self, tokens):
        super().__init__(tokens)
        self.pos = 0

    def actual(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def avanzar(self):
        self.pos += 1

    def peek(self, offset=1):
        idx = self.pos + offset
        return self.tokens[idx] if idx < len(self.tokens) else None

    def consumir(self, tipo_esperado, mensaje_custom=None):
        token = self.actual()
        if not token:
            raise Exception(
                mensaje_custom
                or f"Se esperaba {tipo_esperado} pero llegó fin de archivo"
            )
        if token.tipo == tipo_esperado or (
            isinstance(tipo_esperado, list) and token.tipo in tipo_esperado
        ):
            self.avanzar()
            return token
        msg = mensaje_custom or (
            f"Se esperaba {tipo_esperado} "
            f"pero se encontró {token.tipo}"
        )
        raise Exception(
            f"Error sintáctico Python: {msg} en línea {token.linea}"
        )

    def analizar(self):
        ast = []
        try:
            while self.actual() is not None:
                if self.actual().tipo == "DEDENT":
                    self.avanzar()
                    continue
                ast.append(self.sentencia())
        except Exception as e:
            return {"tipo": "error", "mensaje": str(e)}
        return ast

    def sentencia(self):
        token = self.actual()
        if not token:
            return None
        if token.tipo == "RESERVADA":
            if token.valor == "def":
                return self.funcion()
            if token.valor == "class":
                return self._clase()
            if token.valor == "if":
                return self.sentencia_if()
            if token.valor == "elif":
                raise Exception(
                    f"Error sintactico Python: 'elif' sin 'if' previo "
                    f"en linea {token.linea}"
                )
            if token.valor == "while":
                return self.sentencia_while()
            if token.valor == "for":
                return self.sentencia_for()
            if token.valor == "return":
                return self.sentencia_return()
            if token.valor == "import":
                return self._sentencia_import()
            if token.valor == "from":
                return self._sentencia_from()
            if token.valor == "pass":
                self.avanzar()
                return {"tipo": "pass"}
        if token.tipo == "ID" and self.peek() and self.peek().valor == "=":
            return self.asignacion()
        return self.sentencia_expresion()

    def _clase(self):
        self.consumir("RESERVADA")
        nombre = self.consumir("ID")
        self.consumir("SIMBOLO", "se esperaba ':'")
        self.consumir("INDENT", "se esperaba indentacion")
        cuerpo = self.bloque()
        self.consumir("DEDENT", "se esperaba fin de indentacion")
        return {
            "tipo": "clase",
            "nombre": nombre.valor,
            "linea": nombre.linea,
            "cuerpo": cuerpo,
        }

    def _sentencia_import(self):
        self.consumir("RESERVADA")
        modulos = []
        nombre = self.consumir("ID")
        modulos.append(nombre.valor)
        while self.actual() and self.actual().valor == ".":
            self.consumir("SIMBOLO")
            parte = self.consumir("ID")
            modulos.append(parte.valor)
        alias = None
        if self.actual() and self.actual().tipo == "RESERVADA" and self.actual().valor == "as":
            self.consumir("RESERVADA")
            alias = self.consumir("ID").valor
        return {"tipo": "import", "modulo": ".".join(modulos), "alias": alias}

    def _sentencia_from(self):
        self.consumir("RESERVADA")
        partes = []
        parte = self.consumir("ID")
        partes.append(parte.valor)
        while self.actual() and self.actual().valor == ".":
            self.consumir("SIMBOLO")
            parte = self.consumir("ID")
            partes.append(parte.valor)
        self.consumir("RESERVADA", "se esperaba 'import'")
        nombre = self.consumir("ID")
        alias = None
        if self.actual() and self.actual().tipo == "RESERVADA" and self.actual().valor == "as":
            self.consumir("RESERVADA")
            alias = self.consumir("ID").valor
        return {
            "tipo": "from_import",
            "modulo": ".".join(partes),
            "nombre": nombre.valor,
            "alias": alias,
        }

    def funcion(self):
        self.consumir("RESERVADA")
        nombre = self.consumir("ID")
        self.consumir("SIMBOLO", "se esperaba '('")
        parametros = self.parametros()
        self.consumir("SIMBOLO", "se esperaba ')'")
        self.consumir("SIMBOLO", "se esperaba ':'")
        self.consumir("INDENT", "se esperaba indentación")
        cuerpo = self.bloque()
        self.consumir("DEDENT", "se esperaba fin de indentación")
        return {
            "tipo": "funcion",
            "nombre": nombre.valor,
            "linea": nombre.linea,
            "parametros": parametros,
            "cuerpo": cuerpo,
        }

    def parametros(self):
        params = []
        if self.actual() and self.actual().valor != ")":
            while True:
                identificador = self.consumir("ID")
                params.append(
                    {"nombre": identificador.valor, "linea": identificador.linea}
                )
                if self.actual() and self.actual().valor == ",":
                    self.consumir("SIMBOLO")
                    continue
                break
        return params

    def bloque(self):
        sentencias = []
        while self.actual() and self.actual().tipo != "DEDENT":
            sentencias.append(self.sentencia())
        return sentencias

    def sentencia_if(self):
        self.consumir("RESERVADA")
        condicion = self.expresion()
        self.consumir("SIMBOLO", "se esperaba ':'")
        self.consumir("INDENT", "se esperaba indentacion")
        bloque_if = self.bloque()
        self.consumir("DEDENT", "se esperaba fin de indentacion")
        elif_chain = []
        bloque_else = None
        while (
            self.actual()
            and self.actual().tipo == "RESERVADA"
            and self.actual().valor == "elif"
        ):
            self.consumir("RESERVADA")
            elif_cond = self.expresion()
            self.consumir("SIMBOLO", "se esperaba ':'")
            self.consumir("INDENT", "se esperaba indentacion")
            elif_bloque = self.bloque()
            self.consumir("DEDENT", "se esperaba fin de indentacion")
            elif_chain.append({"condicion": elif_cond, "bloque": elif_bloque})
        if (
            self.actual()
            and self.actual().tipo == "RESERVADA"
            and self.actual().valor == "else"
        ):
            self.consumir("RESERVADA")
            self.consumir("SIMBOLO", "se esperaba ':'")
            self.consumir("INDENT", "se esperaba indentacion")
            bloque_else = self.bloque()
            self.consumir("DEDENT", "se esperaba fin de indentacion")
        return {
            "tipo": "if",
            "condicion": condicion,
            "bloque_if": bloque_if,
            "bloque_else": bloque_else,
            "elif_chain": elif_chain,
        }

    def sentencia_while(self):
        self.consumir("RESERVADA")
        condicion = self.expresion()
        self.consumir("SIMBOLO", "se esperaba ':'")
        self.consumir("INDENT", "se esperaba indentación")
        bloque = self.bloque()
        self.consumir("DEDENT", "se esperaba fin de indentación")
        return {"tipo": "while", "condicion": condicion, "bloque": bloque}

    def sentencia_for(self):
        self.consumir("RESERVADA")
        variable = self.consumir("ID")
        self.consumir("RESERVADA", "se esperaba 'in'")
        coleccion = self.expresion()
        self.consumir("SIMBOLO", "se esperaba ':'")
        self.consumir("INDENT", "se esperaba indentación")
        bloque = self.bloque()
        self.consumir("DEDENT", "se esperaba fin de indentación")
        return {
            "tipo": "for",
            "variable": variable.valor,
            "coleccion": coleccion,
            "bloque": bloque,
        }

    def sentencia_return(self):
        self.consumir("RESERVADA")
        valor = (
            self.expresion()
            if self.actual()
            and self.actual().valor != ":"
            and self.actual().tipo != "DEDENT"
            else None
        )
        return {"tipo": "return", "valor": valor}

    def asignacion(self):
        identificador = self.consumir("ID")
        self.consumir("OPERADOR", "se esperaba '='")
        valor = self.expresion()
        return {
            "tipo": "asignacion",
            "identificador": identificador.valor,
            "valor": valor,
            "linea": identificador.linea,
        }

    def sentencia_expresion(self):
        expr = self.expresion()
        return {"tipo": "expresion", "expresion": expr}

    def expresion(self):
        return self._expresion_binaria(0)

    def _expresion_binaria(self, min_precedencia):
        izquierda = self._primaria()
        while self.actual() and self._es_operador_binario(self.actual()):
            op = self.actual()
            prec = self._precedencia(op)
            if prec < min_precedencia:
                break
            self.avanzar()
            derecha = self._expresion_binaria(prec + 1)
            izquierda = {
                "tipo": "binaria",
                "izquierda": izquierda,
                "operador": op.valor,
                "derecha": derecha,
                "linea": op.linea,
            }
        return izquierda

    def _primaria(self):
        token = self.actual()
        if not token:
            raise Exception("Expresión inesperada: fin de archivo")
        if token.tipo in ("NUMERO", "FLOAT", "STRING"):
            self.avanzar()
            return {"tipo": token.tipo.lower(), "valor": token.valor, "linea": token.linea}
        if token.tipo == "ID":
            nombre = token.valor
            linea = token.linea
            self.avanzar()
            nodo = {"tipo": "id", "valor": nombre, "linea": linea}
            while self.actual() and self.actual().valor == ".":
                self.consumir("SIMBOLO")
                miembro = self.consumir("ID")
                nodo = {
                    "tipo": "miembro",
                    "objeto": nodo,
                    "propiedad": miembro.valor,
                    "linea": miembro.linea,
                }
            if self.actual() and self.actual().valor == "(":
                self.consumir("SIMBOLO")
                args = self._argumentos()
                self.consumir("SIMBOLO")
                return {
                    "tipo": "llamada_funcion",
                    "nombre": nombre,
                    "argumentos": args,
                    "linea": linea,
                }
            return nodo
        if token.valor == "(":
            self.consumir("SIMBOLO")
            expr = self.expresion()
            self.consumir("SIMBOLO")
            return expr
        raise Exception(
            f"Error sintáctico Python: token inesperado '{token.valor}' "
            f"en línea {token.linea}"
        )

    def _argumentos(self):
        args = []
        if self.actual() and self.actual().valor != ")":
            args.append(self.expresion())
            while self.actual() and self.actual().valor == ",":
                self.consumir("SIMBOLO")
                args.append(self.expresion())
        return args

    def _es_operador_binario(self, token):
        return token.tipo in ("OPERADOR", "OP_COMPUESTO")

    def _precedencia(self, token):
        precs = {
            "=": 1, "+=": 1, "-=": 1, "*=": 1, "/=": 1,
            "and": 1, "or": 1,
            "==": 2, "!=": 2, "<": 2, ">": 2, "<=": 2, ">=": 2,
            "+": 3, "-": 3,
            "*": 4, "/": 4, "%": 4,
        }
        return precs.get(token.valor, 0)


class PythonAnalizadorLenguaje(AnalizadorLenguaje):
    def __init__(self):
        metadata = {
            "identidad": "Python",
            "tema": "Indentación, funciones y dinámicas de alto nivel",
            "keywords": sorted(PALABRAS_RESERVADAS_PY),
            "descripcion": "Python usa indentación significativa y una "
                           "sintaxis de alto nivel que prioriza legibilidad.",
        }
        super().__init__(
            "Python", PythonLexer, PythonParser, slug="python", metadata=metadata
        )
