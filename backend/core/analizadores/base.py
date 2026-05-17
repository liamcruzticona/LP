from abc import ABC, abstractmethod


class AnalizadorLexicoBase(ABC):
    """Clase base para analizadores léxicos de cada lenguaje."""

    def __init__(self, codigo):
        self.codigo = codigo

    @abstractmethod
    def analizar(self):
        raise NotImplementedError("analizar debe implementarse en la subclase")


class ParserBase(ABC):
    """Clase base para parsers de cada lenguaje."""

    def __init__(self, tokens):
        self.tokens = tokens

    @abstractmethod
    def analizar(self):
        raise NotImplementedError("analizar debe implementarse en la subclase")


class AnalizadorLenguaje:
    """Componente que agrupa lexer y parser para un lenguaje específico."""

    def __init__(self, nombre, lexer_cls, parser_cls, slug=None, metadata=None):
        self.nombre = nombre
        self.slug = slug or nombre.lower()
        self.lexer_cls = lexer_cls
        self.parser_cls = parser_cls
        self.metadata = metadata or {}

    def analizar(self, codigo):
        lexer = self.lexer_cls(codigo)
        tokens = lexer.analizar()
        parser = self.parser_cls(tokens)
        ast = parser.analizar()
        return {
            "lenguaje": self.nombre,
            "slug": self.slug,
            "metadata": self.metadata,
            "tokens": tokens,
            "ast": ast
        }
