"""
HERENCIA: CLexer(CLikeLexerBase), CParser(CLikeParserBase)
heredan la lógica común y solo definen lo específico de C.
"""

from core.analizadores.base import AnalizadorLenguaje
from core.analizadores.base_clike import CLikeLexerBase, CLikeParserBase
from core.token import Token


PALABRAS_RESERVADAS_C = {
    "int", "float", "char", "double", "void", "if", "else", "while",
    "for", "return", "break", "continue", "struct", "const", "static",
}

TOKEN_REGEX_C = [
    ("COMENTARIO_BLOQUE", r'/\*[\s\S]*?\*/'),
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


class CLexer(CLikeLexerBase):
    PALABRAS_RESERVADAS = PALABRAS_RESERVADAS_C
    TOKEN_REGEX = TOKEN_REGEX_C

    """
    ENCAPSULAMIENTO: Sobrescribe _crear_token para manejar
    el tipo PUNTERO (*, &) específico de C.
    """
    def _crear_token(self, tipo, texto):
        if tipo in ("COMENTARIO", "COMENTARIO_BLOQUE"):
            self.columna += len(texto)
            return
        if tipo == "ID" and texto in self.PALABRAS_RESERVADAS:
            tipo = "RESERVADA"
        if tipo == "OPERADOR" and texto in ["*", "&"]:
            tipo = "PUNTERO"
        token = Token(tipo, texto, self.linea, self.columna)
        self.tokens.append(token)
        self.columna += len(texto)


class CParser(CLikeParserBase):
    """
    POLIMORFISMO: sentencia() se comporta distinto aquí
    que en JavaParser o JavaScriptParser.
    """

    def sentencia(self):
        token = self.actual()
        if not token:
            return None
        if token.tipo == "RESERVADA":
            if token.valor in PALABRAS_RESERVADAS_C:
                if token.valor in ("if",):
                    return self.sentencia_if()
                if token.valor == "while":
                    return self.sentencia_while()
                if token.valor == "for":
                    return self.sentencia_for()
                if token.valor == "return":
                    return self.sentencia_return()
                if token.valor in {"int", "float", "char", "double",
                                   "void", "const", "static"}:
                    return self.declaracion_o_funcion()
            raise Exception(
                f"Sentencia desconocida: {token.valor}"
            )
        if token.tipo in ("ID", "NUMERO", "FLOAT", "STRING") or token.valor == "(":
            return self.sentencia_expresion()
        raise Exception(
            f"Error sintactico C: token inesperado '{token.valor}' "
            f"en linea {token.linea}"
        )

    def _declaracion_c(self):
        tipo = self.consumir("RESERVADA")
        while self.actual() and self.actual().tipo == "PUNTERO":
            self.consumir("PUNTERO")
        identificador = self.consumir("ID")
        valor = None
        if (
            self.actual()
            and self.actual().tipo == "OPERADOR"
            and self.actual().valor == "="
        ):
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

    def declaracion_o_funcion(self):
        pos_guardada = self.pos
        try:
            return super().funcion()
        except Exception:
            self.pos = pos_guardada
            return self._declaracion_c()

    def _primaria(self):
        token = self.actual()
        if token and token.tipo == "PUNTERO" and token.valor in ("*", "&"):
            op = token.valor
            linea = token.linea
            self.avanzar()
            operando = super()._primaria()
            return {
                "tipo": "unaria",
                "operador": op,
                "operando": operando,
                "prefijo": True,
                "linea": linea,
            }
        return super()._primaria()
        if token.tipo in ("ID", "NUMERO", "FLOAT", "STRING") or token.valor == "(":
            return self.sentencia_expresion()
        raise Exception(
            f"Error sintáctico: token inesperado '{token.valor}' "
            f"en línea {token.linea}"
        )


class CAnalizadorLenguaje(AnalizadorLenguaje):
    def __init__(self):
        metadata = {
            "identidad": "C",
            "tema": "Memoria, punteros y compilación directa",
            "keywords": sorted(PALABRAS_RESERVADAS_C),
            "descripcion": "C es un lenguaje de sistemas con punteros "
                           "y declaración explícita de tipos.",
        }
        super().__init__("C", CLexer, CParser, slug="c", metadata=metadata)
