"""Módulo de definición de tokens para el analizador léxico."""

class TokenBase:
    """
     ABSTRACCIÓN:
    Clase base que representa cualquier elemento léxico con posición en el código.
    No depende del tipo específico de token.
    """

    def __init__(self, valor, linea, columna):
        # ENCAPSULAMIENTO:
        # Se agrupan los datos comunes en una sola clase
        self.valor = valor
        self.linea = linea
        self.columna = columna

    def get_posicion(self):
        return f"Línea {self.linea}, Columna {self.columna}"


class Token(TokenBase):
    """
     HERENCIA:
    Token hereda de TokenBase para reutilizar atributos comunes
    como valor, línea y columna.
    """

    def __init__(self, tipo, valor, linea, columna):
        super().__init__(valor, linea, columna)
        self.tipo = tipo

    def __repr__(self):
        """
         POLIMORFISMO:
        Se redefine el método __repr__ para mostrar el token
        de forma personalizada.
        """
        return f"Token({self.tipo}, {self.valor!r}, linea={self.linea}, columna={self.columna})"

    def to_dict(self):
        """
         ENCAPSULAMIENTO:
        Método controlado para exponer los datos del objeto,
        útil para enviar información al frontend (JSON).
        """
        return {
            "tipo": self.tipo,
            "valor": self.valor,
            "linea": self.linea,
            "columna": self.columna
        }