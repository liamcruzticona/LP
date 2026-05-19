"""
HERENCIA: CppLexer(CLikeLexerBase), CppParser(CLikeParserBase)
heredan la lógica común y agregan sintaxis específica de C++
(clases, namespace, cout/cin).
"""

from core.analizadores.base import AnalizadorLenguaje
from core.analizadores.base_clike import CLikeLexerBase, CLikeParserBase
from core.token import Token


PALABRAS_RESERVADAS_CPP = {
    "class", "namespace", "using", "std", "public", "private", "protected",
    "template", "typename", "int", "double", "float", "char", "bool",
    "void", "auto", "new", "delete", "return", "if", "else", "for", "while",
    "cout", "cin", "nullptr", "true", "false",
}

TOKEN_REGEX_CPP = [
    ("PREPROCESADOR", r'#.*'),
    ("COMENTARIO_BLOQUE", r'/\*[\s\S]*?\*/'),
    ("COMENTARIO", r'//.*'),
    ("STRING", r'"([^"\\]|\\.)*"'),
    ("FLOAT", r'\d+\.\d+'),
    ("NUMERO", r'\d+'),
    ("OP_COMPUESTO", r'(<<|>>|\+=|-=|\*=|/=|==|!=|<=|>=|\+\+|--)'),
    ("ID", r'[a-zA-Z_][a-zA-Z0-9_]*'),
    ("OPERADOR", r'[+\-*/=%<>!&|]'),
    ("SIMBOLO", r'[;{}(),.\[\]<>:]'),
    ("ESPACIO", r'\s+'),
]


class CppLexer(CLikeLexerBase):
    PALABRAS_RESERVADAS = PALABRAS_RESERVADAS_CPP
    TOKEN_REGEX = TOKEN_REGEX_CPP

    """
    ENCAPSULAMIENTO: Sobrescribe _crear_token para detectar
    punteros (*, &) como en C.
    """
    def _crear_token(self, tipo, texto):
        if tipo in ("COMENTARIO", "COMENTARIO_BLOQUE", "PREPROCESADOR"):
            self.columna += len(texto)
            return
        if tipo == "ID" and texto in self.PALABRAS_RESERVADAS:
            tipo = "RESERVADA"
        if tipo == "OPERADOR" and texto in ["*", "&"]:
            tipo = "PUNTERO"
        token = Token(tipo, texto, self.linea, self.columna)
        self.tokens.append(token)
        self.columna += len(texto)


class CppParser(CLikeParserBase):
    """
    POLIMORFISMO: sentencia() maneja class, using namespace,
    además de lo que soporta C.
    """

    def sentencia(self):
        token = self.actual()
        if not token:
            return None
        if token.tipo == "RESERVADA":
            if token.valor == "class":
                return self._clase()
            if token.valor == "using":
                return self._declaracion_using()
            if token.valor in {"int", "double", "float", "char",
                               "bool", "auto", "void"}:
                return self.declaracion_o_funcion()
            if token.valor == "if":
                return self.sentencia_if()
            if token.valor == "while":
                return self.sentencia_while()
            if token.valor == "for":
                return self.sentencia_for()
            if token.valor == "return":
                return self.sentencia_return()
            if token.valor in ("cout", "cin", "endl", "true", "false", "nullptr", "std"):
                return self.sentencia_expresion()
            raise Exception(f"Sentencia desconocida: {token.valor}")
        if token.tipo in ("ID", "NUMERO", "FLOAT", "STRING") or token.valor == "(":
            return self.sentencia_expresion()
        raise Exception(
            f"Error sintactico C++: token inesperado '{token.valor}' "
            f"en linea {token.linea}"
        )

    def _clase(self):
        self.consumir("RESERVADA")
        nombre = self.consumir("ID")
        self.consumir("SIMBOLO", "se esperaba '{'")
        miembros = []
        while self.actual() and self.actual().valor != "}":
            miembros.append(self._miembro())
        self.consumir("SIMBOLO", "se esperaba '}'")
        if self.actual() and self.actual().valor == ";":
            self.consumir("SIMBOLO")
        return {"tipo": "clase", "nombre": nombre.valor, "miembros": miembros}

    def _miembro(self):
        if self.actual() and self.actual().valor in ("public", "private", "protected"):
            self.consumir("RESERVADA")
            self.consumir("SIMBOLO", "se esperaba ':'")
            return {"tipo": "etiqueta_acceso", "acceso": self.tokens[-2].valor}
        if self.actual() and self.actual().valor == "static":
            self.consumir("RESERVADA")
        return self.declaracion_o_funcion()

    def _declaracion_using(self):
        self.consumir("RESERVADA")
        self.consumir("RESERVADA")
        if self.actual() and self.actual().tipo in ("ID", "RESERVADA"):
            self.consumir(self.actual().tipo)
        self.consumir("SIMBOLO", "se esperaba ';'")
        return {"tipo": "using_namespace"}

    def _precedencia(self, token):
        precs = super()._precedencia(token)
        custom = {"<<": 3, ">>": 3}
        return custom.get(token.valor, precs)

    def _primaria(self):
        token = self.actual()
        if token and token.tipo == "RESERVADA" and token.valor in ("endl", "true", "false", "nullptr", "cout", "cin"):
            self.avanzar()
            return {"tipo": "id", "valor": token.valor, "linea": token.linea}
        return super()._primaria()


class CppAnalizadorLenguaje(AnalizadorLenguaje):
    def __init__(self):
        metadata = {
            "identidad": "C++",
            "tema": "Clases, templates y memoria estática",
            "keywords": sorted(PALABRAS_RESERVADAS_CPP),
            "descripcion": "C++ mezcla programación de bajo nivel "
                           "con abstracciones de clase y STL.",
        }
        super().__init__("C++", CppLexer, CppParser, slug="cpp", metadata=metadata)
