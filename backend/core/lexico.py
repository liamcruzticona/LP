"""Módulo de análisis léxico"""

import re
from core.token import Token

#  ABSTRACCIÓN:
PALABRAS_RESERVADAS = {
    "int", "float", "if", "else", "while", "return", "for", "void", "char", "double", "struct", "break", "continue"
}

# Patrones léxicos mejorados (orden importa)
TOKEN_REGEX = [
    ("COMENTARIO", r'//.*'),
    ("STRING", r'"[^"]*"'),
    ("FLOAT", r'\d+\.\d+'),
    ("NUMERO", r'\d+'),
    ("OP_COMPUESTO", r'(\+=|-=|\*=|/=|==|!=|<=|>=|\+\+|--)'),
    ("ID", r'[a-zA-Z_][a-zA-Z0-9_]*'),
    ("OPERADOR", r'[+\-*/=%<>!&|]'),
    ("SIMBOLO", r'[;{}(),.?\[\]:]'),
    ("ESPACIO", r'\s+'),
]


class AnalizadorLexico:
    """
     ABSTRACCIÓN:
    Clase que encapsula todo el proceso de análisis léxico.
    """

    def __init__(self, codigo):
        #  ENCAPSULAMIENTO
        self.codigo = codigo
        self.pos = 0
        self.linea = 1
        self.columna = 1
        self.tokens = []

    def analizar(self):
        """
        Punto de entrada del análisis léxico
        """
        while self.pos < len(self.codigo):
            match = None

            for tipo, regex in TOKEN_REGEX:
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
                    f"Error léxico en línea {self.linea}, columna {self.columna}"
                )

        return self.tokens

    def _manejar_espacios(self, texto):
        """
        ENCAPSULAMIENTO:
        Método interno para manejar espacios y saltos de línea
        """
        if "\n" in texto:
            self.linea += texto.count("\n")
            self.columna = 1
        else:
            self.columna += len(texto)

    def _crear_token(self, tipo, texto):
        """
        ENCAPSULAMIENTO:
        Método interno para crear tokens
        """
        # Ignorar comentarios
        if tipo == "COMENTARIO":
            self.columna += len(texto)
            return

        # Identificar palabras reservadas
        if tipo == "ID" and texto in PALABRAS_RESERVADAS:
            tipo = "RESERVADA"

        # Crear objeto Token (POO real)
        token = Token(tipo, texto, self.linea, self.columna)
        self.tokens.append(token)

        self.columna += len(texto)