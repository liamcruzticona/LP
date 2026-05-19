"""
HERENCIA: JavaScriptLexer(CLikeLexerBase), JavaScriptParser(CLikeParserBase)
heredan la lógica común y agregan sintaxis de JavaScript
(var/let/const, funciones flecha, operadores ===/!==).
"""

from core.analizadores.base import AnalizadorLenguaje
from core.analizadores.base_clike import CLikeLexerBase, CLikeParserBase
from core.token import Token


PALABRAS_RESERVADAS_JS = {
    "var", "let", "const", "function", "if", "else", "while", "for", "return",
    "true", "false", "null", "undefined",
}

TOKEN_REGEX_JS = [
    ("COMENTARIO_BLOQUE", r'/\*[\s\S]*?\*/'),
    ("COMENTARIO", r'//.*'),
    ("STRING", r'"([^"\\]|\\.)*"|\'([^\'\\]|\\.)*\''),
    ("FLOAT", r'\d+\.\d+'),
    ("NUMERO", r'\d+'),
    ("OP_COMPUESTO", r'(===|!==|=>|\+=|-=|\*=|/=|==|!=|<=|>=|\+\+|--|&&|\|\|)'),
    ("ID", r'[a-zA-Z_$][a-zA-Z0-9_$]*'),
    ("OPERADOR", r'[+\-*/=%<>!&|]'),
    ("SIMBOLO", r'[;{}(),.\[\]]'),
    ("ESPACIO", r'\s+'),
]


class JavaScriptLexer(CLikeLexerBase):
    """
    HERENCIA: JavaScriptLexer hereda de CLikeLexerBase,
    solo configura sus patrones léxicos específicos.
    """
    PALABRAS_RESERVADAS = PALABRAS_RESERVADAS_JS
    TOKEN_REGEX = TOKEN_REGEX_JS


class JavaScriptParser(CLikeParserBase):
    """
    POLIMORFISMO: sentencia() maneja var/let/const y function
    de forma distinta a C/Java/C++.
    """

    def sentencia(self):
        token = self.actual()
        if not token:
            return None
        if token.tipo == "RESERVADA":
            if token.valor in ("var", "let", "const"):
                return self._declaracion_js()
            if token.valor == "function":
                return self._funcion_js()
            if token.valor == "if":
                return self.sentencia_if()
            if token.valor == "while":
                return self.sentencia_while()
            if token.valor == "for":
                return self.sentencia_for()
            if token.valor == "return":
                return self.sentencia_return()
            raise Exception(f"Sentencia JS desconocida: {token.valor}")
        if token.tipo == "ID" and self.peek() and self.peek().valor == "=":
            return self._asignacion_js()
        if token.tipo in ("ID", "NUMERO", "FLOAT", "STRING") or token.valor == "(":
            return self.sentencia_expresion()
        raise Exception(
            f"Error sintactico JS: token inesperado '{token.valor}' "
            f"en linea {token.linea}"
        )

    def _declaracion_js(self):
        declarador = self.consumir("RESERVADA")
        identificador = self.consumir("ID")
        valor = None
        if self.actual() and self.actual().valor == "=":
            self.consumir("OPERADOR")
            valor = self._expresion_o_flecha()
        self.consumir("SIMBOLO", "se esperaba ';'")
        return {
            "tipo": "declaracion",
            "declarador": declarador.valor,
            "identificador": identificador.valor,
            "linea": declarador.linea,
            "valor": valor,
        }

    def _funcion_js(self):
        self.consumir("RESERVADA")
        nombre = self.consumir("ID")
        self.consumir("SIMBOLO", "se esperaba '('")
        parametros = self.parametros()
        self.consumir("SIMBOLO", "se esperaba ')'")
        self.consumir("SIMBOLO", "se esperaba '{'")
        cuerpo = self.bloque()
        self.consumir("SIMBOLO", "se esperaba '}'")
        return {
            "tipo": "funcion",
            "nombre": nombre.valor,
            "linea": nombre.linea,
            "parametros": parametros,
            "cuerpo": cuerpo,
        }

    def _asignacion_js(self):
        identificador = self.consumir("ID")
        self.consumir("OPERADOR", "se esperaba '='")
        valor = self._expresion_o_flecha()
        self.consumir("SIMBOLO", "se esperaba ';'")
        return {
            "tipo": "declaracion",
            "declarador": "const",
            "identificador": identificador.valor,
            "linea": identificador.linea,
            "valor": valor,
        }

    def _expresion_o_flecha(self):
        if self.actual() and self.actual().valor == "(":
            return self._funcion_flecha_con_parentesis()
        if self.actual() and self.actual().tipo == "ID":
            if self.peek() and self.peek().valor == "=>":
                return self._funcion_flecha_simple()
        return self.expresion()

    def _funcion_flecha_con_parentesis(self):
        self.consumir("SIMBOLO", "se esperaba '('")
        parametros = self.parametros()
        self.consumir("SIMBOLO", "se esperaba ')'")
        self.consumir("OP_COMPUESTO", "se esperaba '=>'")
        if self.actual() and self.actual().valor == "{":
            self.consumir("SIMBOLO")
            cuerpo = self.bloque()
            self.consumir("SIMBOLO")
            return {
                "tipo": "funcion_flecha",
                "parametros": parametros,
                "cuerpo": cuerpo,
            }
        expr = self.expresion()
        return {
            "tipo": "funcion_flecha",
            "parametros": parametros,
            "expresion": expr,
        }

    def _funcion_flecha_simple(self):
        parametro = self.consumir("ID")
        self.consumir("OP_COMPUESTO", "se esperaba '=>'")
        if self.actual() and self.actual().valor == "{":
            self.consumir("SIMBOLO")
            cuerpo = self.bloque()
            self.consumir("SIMBOLO")
            return {
                "tipo": "funcion_flecha",
                "parametros": [{"nombre": parametro.valor, "linea": parametro.linea}],
                "cuerpo": cuerpo,
            }
        expr = self.expresion()
        return {
            "tipo": "funcion_flecha",
            "parametros": [{"nombre": parametro.valor, "linea": parametro.linea}],
            "expresion": expr,
        }

    def _id_primaria(self, token):
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
        if (
            self.actual()
            and self.actual().tipo == "OP_COMPUESTO"
            and self.actual().valor in ["++", "--"]
        ):
            operador = self.actual().valor
            self.avanzar()
            return {
                "tipo": "unaria",
                "operador": operador,
                "operando": nodo,
                "prefijo": False,
                "linea": linea,
            }
        return nodo


class JavaScriptAnalizadorLenguaje(AnalizadorLenguaje):
    def __init__(self):
        metadata = {
            "identidad": "JavaScript",
            "tema": "Web, DOM y funciones dinámicas",
            "keywords": sorted(PALABRAS_RESERVADAS_JS),
            "descripcion": "JavaScript es un lenguaje dinámico de alto nivel "
                           "para la web y la manipulación del DOM.",
        }
        super().__init__(
            "JavaScript", JavaScriptLexer, JavaScriptParser,
            slug="javascript", metadata=metadata,
        )
