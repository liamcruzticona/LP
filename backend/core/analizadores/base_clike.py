import re

from core.analizadores.base import AnalizadorLexicoBase, ParserBase
from core.token import Token


class CLikeLexerBase(AnalizadorLexicoBase):
    """
    ABSTRACCIÓN: Oculta la complejidad del análisis léxico (regex,
    posición, manejo de espacios) exponiendo solo analizar().

    HERENCIA: CLexer, CppLexer, JavaLexer, JavaScriptLexer heredan
    de esta clase y solo configuran palabras reservadas y patrones.

    ENCAPSULAMIENTO: _manejar_espacios y _crear_token son privados.
    """

    PALABRAS_RESERVADAS = set()
    TOKEN_REGEX = []

    def __init__(self, codigo):
        super().__init__(codigo)
        self.pos = 0
        self.linea = 1
        self.columna = 1
        self.tokens = []

    def analizar(self):
        while self.pos < len(self.codigo):
            match = None
            for tipo, regex in self.TOKEN_REGEX:
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
                    f"Error léxico en línea {self.linea}, "
                    f"columna {self.columna}: símbolo no reconocido"
                )
        return self.tokens

    def _manejar_espacios(self, texto):
        if "\n" in texto:
            self.linea += texto.count("\n")
            self.columna = 1
        else:
            self.columna += len(texto)

    def _crear_token(self, tipo, texto):
        if tipo in ("COMENTARIO", "COMENTARIO_BLOQUE"):
            self.columna += len(texto)
            return
        if tipo == "ID" and texto in self.PALABRAS_RESERVADAS:
            tipo = "RESERVADA"
        token = Token(tipo, texto, self.linea, self.columna)
        self.tokens.append(token)
        self.columna += len(texto)


class CLikeParserBase(ParserBase):
    """
    ABSTRACCIÓN: Encapsula la lógica común de parsing (expresiones,
    bloques, estructura de control) en métodos reutilizables.

    HERENCIA: CParser, CppParser, JavaParser, JavaScriptParser
    heredan y extienden con sintaxis específica de cada lenguaje.

    POLIMORFISMO: sentencia(), declaracion(), funcion() son
    redefinidos en cada subclase para comportarse distinto según
    el lenguaje.

    ENCAPSULAMIENTO: Los métodos _precedencia, _es_operador_binario
    y _crear_nodo son de uso interno.
    """

    def __init__(self, tokens):
        super().__init__(tokens)
        self.pos = 0
        self.errores = []

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
            f"Error sintáctico: {msg} en línea {token.linea}"
        )

    def analizar(self):
        ast = []
        try:
            while self.actual() is not None:
                self._skip_dedent()
                ast.append(self.sentencia())
        except Exception as e:
            return {"tipo": "error", "mensaje": str(e), "errores": self.errores}
        return ast

    def _skip_dedent(self):
        while self.actual() and self.actual().tipo == "DEDENT":
            self.avanzar()

    def sentencia(self):
        raise NotImplementedError(
            "POLIMORFISMO: cada lenguaje implementa su propia sentencia()"
        )

    def sentencia_if(self):
        self.consumir("RESERVADA")
        self.consumir("SIMBOLO")
        condicion = self.expresion()
        self.consumir("SIMBOLO")
        self.consumir("SIMBOLO")
        bloque_if = self.bloque()
        self.consumir("SIMBOLO")
        bloque_else = None
        if (
            self.actual()
            and self.actual().tipo == "RESERVADA"
            and self.actual().valor == "else"
        ):
            self.consumir("RESERVADA")
            self.consumir("SIMBOLO")
            bloque_else = self.bloque()
            self.consumir("SIMBOLO")
        return {
            "tipo": "if",
            "condicion": condicion,
            "bloque_if": bloque_if,
            "bloque_else": bloque_else,
        }

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
        init = self._for_init()
        self.consumir("SIMBOLO")
        condicion = (
            self.expresion()
            if self.actual() and self.actual().valor != ";"
            else None
        )
        self.consumir("SIMBOLO")
        incremento = (
            self.expresion()
            if self.actual() and self.actual().valor != ")"
            else None
        )
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

    def _for_init(self):
        if self.actual() and self.actual().valor != ";":
            if (
                self.actual().tipo == "RESERVADA"
                and self.peek()
                and self.peek().tipo == "ID"
            ):
                return self._declaracion_for()
            return self.expresion()
        return None

    def _declaracion_for(self):
        tipo = self.consumir("RESERVADA")
        identificador = self.consumir("ID")
        valor = None
        if (
            self.actual()
            and self.actual().tipo == "OPERADOR"
            and self.actual().valor == "="
        ):
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
        if self.actual() and self.actual().valor == ";":
            self.consumir("SIMBOLO", "se esperaba ';'")
        return {"tipo": "expresion", "expresion": expr}

    def funcion(self):
        tipo_retorno = self.consumir("RESERVADA")
        nombre = self.consumir("ID")
        self.consumir("SIMBOLO", "se esperaba '('")
        parametros = self.parametros()
        self.consumir("SIMBOLO", "se esperaba ')'")
        self.consumir("SIMBOLO", "se esperaba '{'")
        cuerpo = self.bloque()
        self.consumir("SIMBOLO", "se esperaba '}'")
        return {
            "tipo": "funcion",
            "tipo_retorno": tipo_retorno.valor,
            "nombre": nombre.valor,
            "linea": nombre.linea,
            "parametros": parametros,
            "cuerpo": cuerpo,
        }

    def parametros(self):
        params = []
        while self.actual() and self.actual().valor != ")":
            if self.actual().tipo == "RESERVADA":
                tipo = self.consumir("RESERVADA")
                nombre = self.consumir("ID")
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

    def bloque(self):
        sentencias = []
        while self.actual() and self.actual().valor != "}":
            sentencias.append(self.sentencia())
        return sentencias

    def declaracion(self):
        tipo = self.consumir("RESERVADA")
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
            return self.funcion()
        except Exception:
            self.pos = pos_guardada
            return self.declaracion()

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
            izquierda = self._crear_nodo_binario(izquierda, op, derecha)
        return izquierda

    def _crear_nodo_binario(self, izquierda, op, derecha):
        return {
            "tipo": "binaria",
            "izquierda": izquierda,
            "operador": op.valor,
            "derecha": derecha,
            "linea": op.linea,
        }

    def _primaria(self):
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
            return self._id_primaria(token)
        if token.valor == "(":
            self.consumir("SIMBOLO")
            expr = self.expresion()
            self.consumir("SIMBOLO")
            return expr
        if token.tipo == "OP_COMPUESTO" and token.valor in ["++", "--"]:
            op = token.valor
            linea = token.linea
            self.avanzar()
            expr = self._primaria()
            return {
                "tipo": "unaria",
                "operador": op,
                "operando": expr,
                "prefijo": True,
                "linea": linea,
            }
        raise Exception(
            f"Error sintáctico: token inesperado '{token.valor}' "
            f"en línea {token.linea}"
        )

    def _id_primaria(self, token):
        nombre = token.valor
        linea = token.linea
        self.avanzar()
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
                "operando": {"tipo": "id", "valor": nombre, "linea": linea},
                "prefijo": False,
                "linea": linea,
            }
        return {"tipo": "id", "valor": nombre, "linea": linea}

    def _argumentos(self):
        args = []
        if self.actual() and self.actual().valor != ")":
            args.append(self.expresion())
            while self.actual() and self.actual().valor == ",":
                self.consumir("SIMBOLO")
                args.append(self.expresion())
        return args

    def _es_operador_binario(self, token):
        return token.tipo in ["OPERADOR", "OP_COMPUESTO", "PUNTERO"]

    def _precedencia(self, token):
        precedencias = {
            "=": 1,
            "+=": 1, "-=": 1, "*=": 1, "/=": 1,
            "&&": 1, "||": 1,
            "==": 2, "!=": 2, "===": 2, "!==": 2,
            "<": 2, ">": 2, "<=": 2, ">=": 2,
            "+": 3, "-": 3,
            "*": 4, "/": 4, "%": 4,
            "++": 5, "--": 5,
        }
        return precedencias.get(token.valor, 0)
