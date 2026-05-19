"""
HERENCIA: JavaLexer(CLikeLexerBase), JavaParser(CLikeParserBase)
heredan la lógica común y agregan sintaxis específica de Java
(clases, métodos, modificadores de acceso).
"""

from core.analizadores.base import AnalizadorLenguaje
from core.analizadores.base_clike import CLikeLexerBase, CLikeParserBase
from core.token import Token


PALABRAS_RESERVADAS_JAVA = {
    "package", "import", "class", "public", "private", "protected", "static",
    "void", "int", "double", "boolean", "String", "new", "extends", "implements",
    "if", "else", "for", "while", "return", "null", "true", "false", "this",
}

TOKEN_REGEX_JAVA = [
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


class JavaLexer(CLikeLexerBase):
    PALABRAS_RESERVADAS = PALABRAS_RESERVADAS_JAVA
    TOKEN_REGEX = TOKEN_REGEX_JAVA


class JavaParser(CLikeParserBase):
    """
    POLIMORFISMO: analizar() y sentencia() se comportan distinto
    aquí que en CParser. Java parsea clases a nivel superior.
    """

    def analizar(self):
        ast = []
        try:
            while self.actual() is not None:
                ast.append(self._declaracion_toplevel())
        except Exception as e:
            return {"tipo": "error", "mensaje": str(e)}
        return ast

    def _declaracion_toplevel(self):
        token = self.actual()
        if not token:
            return None
        if token.tipo == "RESERVADA" and token.valor == "import":
            return self._declaracion_import()
        if token.tipo == "RESERVADA" and token.valor == "package":
            return self._declaracion_package()
        if token.tipo == "RESERVADA" and token.valor in ("public", "private", "protected"):
            self.consumir("RESERVADA")
            if self.actual() and self.actual().valor == "class":
                return self._clase()
            raise Exception(
                f"Error sintactico Java: se esperaba 'class' despues del modificador "
                f"en linea {token.linea}"
            )
        if token.tipo == "RESERVADA" and token.valor == "class":
            return self._clase()
        return self.sentencia()

    def _declaracion_import(self):
        self.consumir("RESERVADA")
        partes = []
        while self.actual() and self.actual().tipo in ("ID", "RESERVADA"):
            partes.append(self.consumir(self.actual().tipo).valor)
            if self.actual() and self.actual().valor == ".":
                self.consumir("SIMBOLO")
            else:
                break
        self.consumir("SIMBOLO", "se esperaba ';'")
        return {"tipo": "import", "ruta": ".".join(partes)}

    def _declaracion_package(self):
        self.consumir("RESERVADA")
        partes = []
        while self.actual() and self.actual().tipo in ("ID", "RESERVADA"):
            partes.append(self.consumir(self.actual().tipo).valor)
            if self.actual() and self.actual().valor == ".":
                self.consumir("SIMBOLO")
            else:
                break
        self.consumir("SIMBOLO", "se esperaba ';'")
        return {"tipo": "package", "ruta": ".".join(partes)}

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
        if token.tipo in ("ID", "NUMERO", "FLOAT", "STRING") or token.valor == "(":
            return self.sentencia_expresion()
        raise Exception(
            f"Error sintactico Java: token inesperado '{token.valor}' "
            f"en linea {token.linea}"
        )

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

    def _clase(self):
        self.consumir("RESERVADA")
        nombre = self.consumir("ID")
        self._opt_extends()
        self.consumir("SIMBOLO", "se esperaba '{'")
        miembros = []
        while self.actual() and self.actual().valor != "}":
            miembros.append(self._miembro())
        self.consumir("SIMBOLO", "se esperaba '}'")
        return {
            "tipo": "clase",
            "nombre": nombre.valor,
            "miembros": miembros,
            "linea": nombre.linea,
        }

    def _opt_extends(self):
        if self.actual() and self.actual().valor == "extends":
            self.consumir("RESERVADA")
            return self.consumir("ID").valor
        return None

    def parametros(self):
        params = []
        while self.actual() and self.actual().valor != ")":
            if self.actual().tipo == "RESERVADA":
                tipo = self.consumir("RESERVADA")
                while self.actual() and self.actual().tipo == "SIMBOLO" and self.actual().valor in ("[", "]"):
                    self.consumir("SIMBOLO")
                nombre = self.consumir("ID")
                while self.actual() and self.actual().tipo == "SIMBOLO" and self.actual().valor in ("[", "]"):
                    self.consumir("SIMBOLO")
                params.append(
                    {"tipo": tipo.valor, "nombre": nombre.valor, "linea": nombre.linea}
                )
            elif self.actual().tipo == "ID":
                nombre = self.consumir("ID")
                params.append({"nombre": nombre.valor, "linea": nombre.linea})
            else:
                break
            if self.actual() and self.actual().valor == ",":
                self.consumir("SIMBOLO")
            else:
                break
        return params

    def _miembro(self):
        if self.actual() and self.actual().valor in ("public", "private", "protected"):
            self.consumir("RESERVADA")
        if self.actual() and self.actual().valor == "static":
            self.consumir("RESERVADA")
        if self.actual() and self.actual().tipo == "RESERVADA":
            return self._funcion_o_declaracion()
        raise Exception(
            f"Miembro inesperado en clase: "
            f"{self.actual().valor if self.actual() else 'EOF'}"
        )

    def _funcion_o_declaracion(self):
        tipo = self.consumir("RESERVADA")
        nombre = self.consumir("ID")
        if self.actual() and self.actual().valor == "(":
            self.consumir("SIMBOLO")
            parametros = self.parametros()
            self.consumir("SIMBOLO", "se esperaba ')'")
            self.consumir("SIMBOLO", "se esperaba '{'")
            cuerpo = self.bloque()
            self.consumir("SIMBOLO", "se esperaba '}'")
            return {
                "tipo": "metodo",
                "nombre": nombre.valor,
                "retorno": tipo.valor,
                "parametros": parametros,
                "cuerpo": cuerpo,
            }
        valor = None
        if self.actual() and self.actual().valor == "=":
            self.consumir("OPERADOR")
            valor = self.expresion()
        self.consumir("SIMBOLO", "se esperaba ';'")
        return {
            "tipo": "campo",
            "tipo_dato": tipo.valor,
            "identificador": nombre.valor,
            "valor": valor,
        }


class JavaAnalizadorLenguaje(AnalizadorLenguaje):
    def __init__(self):
        metadata = {
            "identidad": "Java",
            "tema": "Capas, clases y JVM",
            "keywords": sorted(PALABRAS_RESERVADAS_JAVA),
            "descripcion": "Java exige clases y métodos, con una sintaxis "
                           "estructurada orientada a objetos.",
        }
        super().__init__("Java", JavaLexer, JavaParser, slug="java", metadata=metadata)
