"""
Tests unitarios para el analizador léxico, sintáctico y entropía
Demuestra robustez y validez del sistema
"""

import sys
import os

# Agregar ruta del backend al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.lexico import AnalizadorLexico
from core.sintactico import Parser
from core.entropia import CalculadorEntropia


class TestsAnalizador:
    """Pruebas unitarias del analizador"""

    def __init__(self):
        self.tests_pasados = 0
        self.tests_fallidos = 0
        self.errores = []

    def test(self, nombre, condicion, mensaje=""):
        """Ejecuta un test individual"""
        if condicion:
            self.tests_pasados += 1
            print(f"✅ {nombre}")
        else:
            self.tests_fallidos += 1
            print(f"❌ {nombre}")
            self.errores.append(f"{nombre}: {mensaje}")

    # ==================== TESTS LÉXICOS ====================

    def test_lexico_declaracion_simple(self):
        """Test: declaración simple"""
        codigo = "int x = 10;"
        lexer = AnalizadorLexico(codigo)
        tokens = lexer.analizar()
        self.test("Léxico: Declaración simple", 
                  len(tokens) > 0 and tokens[0].valor == "int",
                  f"Se obtuvieron {len(tokens)} tokens")

    def test_lexico_string(self):
        """Test: strings"""
        codigo = 'char* msg = "Hola";'
        try:
            lexer = AnalizadorLexico(codigo)
            tokens = lexer.analizar()
            tiene_string = any(t.tipo == "STRING" for t in tokens)
            self.test("Léxico: Strings", tiene_string, 
                      "No se encontró token STRING")
        except Exception as e:
            self.test("Léxico: Strings", False, str(e))

    def test_lexico_float(self):
        """Test: números flotantes"""
        codigo = "float pi = 3.14;"
        try:
            lexer = AnalizadorLexico(codigo)
            tokens = lexer.analizar()
            tiene_float = any(t.tipo == "FLOAT" for t in tokens)
            self.test("Léxico: Floats", tiene_float,
                      "No se encontró token FLOAT")
        except Exception as e:
            self.test("Léxico: Floats", False, str(e))

    def test_lexico_operadores_compuestos(self):
        """Test: operadores compuestos"""
        codigo = "x += 5; y == 3;"
        try:
            lexer = AnalizadorLexico(codigo)
            tokens = lexer.analizar()
            tiene_op_compuesto = any(t.tipo == "OP_COMPUESTO" for t in tokens)
            self.test("Léxico: Operadores compuestos", tiene_op_compuesto,
                      "No se encontró OP_COMPUESTO")
        except Exception as e:
            self.test("Léxico: Operadores compuestos", False, str(e))

    def test_lexico_comentarios(self):
        """Test: comentarios ignorados"""
        codigo = "int x = 10; // comentario"
        try:
            lexer = AnalizadorLexico(codigo)
            tokens = lexer.analizar()
            tiene_comentario = any(t.tipo == "COMENTARIO" for t in tokens)
            self.test("Léxico: Comentarios ignorados", not tiene_comentario,
                      "Los comentarios no deben ser tokens")
        except Exception as e:
            self.test("Léxico: Comentarios ignorados", False, str(e))

    # ==================== TESTS SINTÁCTICOS ====================

    def test_sintactico_declaracion(self):
        """Test: declaración"""
        codigo = "int x = 10;"
        try:
            lexer = AnalizadorLexico(codigo)
            tokens = lexer.analizar()
            parser = Parser(tokens)
            resultado = parser.analizar()
            es_valido = isinstance(resultado, list) and len(resultado) > 0
            self.test("Sintáctico: Declaración", es_valido,
                      f"Resultado: {resultado}")
        except Exception as e:
            self.test("Sintáctico: Declaración", False, str(e))

    def test_sintactico_funcion(self):
        """Test: función con parámetros"""
        codigo = "int suma(int a, int b) { return a + b; }"
        try:
            lexer = AnalizadorLexico(codigo)
            tokens = lexer.analizar()
            parser = Parser(tokens)
            resultado = parser.analizar()
            es_valido = isinstance(resultado, list) and len(resultado) > 0
            self.test("Sintáctico: Función", es_valido,
                      f"Resultado: {resultado}")
        except Exception as e:
            self.test("Sintáctico: Función", False, str(e))

    def test_sintactico_if(self):
        """Test: estructura if"""
        codigo = "if (x > 5) { y = 1; } else { y = 0; }"
        try:
            lexer = AnalizadorLexico(codigo)
            tokens = lexer.analizar()
            parser = Parser(tokens)
            resultado = parser.analizar()
            es_valido = isinstance(resultado, list)
            self.test("Sintáctico: If/Else", es_valido,
                      f"Resultado: {resultado}")
        except Exception as e:
            self.test("Sintáctico: If/Else", False, str(e))

    def test_sintactico_while(self):
        """Test: bucle while"""
        codigo = "while (i < 10) { i = i + 1; }"
        try:
            lexer = AnalizadorLexico(codigo)
            tokens = lexer.analizar()
            parser = Parser(tokens)
            resultado = parser.analizar()
            es_valido = isinstance(resultado, list)
            self.test("Sintáctico: While", es_valido,
                      f"Resultado: {resultado}")
        except Exception as e:
            self.test("Sintáctico: While", False, str(e))

    def test_sintactico_for(self):
        """Test: bucle for"""
        codigo = "for (int i = 0; i < 10; i++) { printf(i); }"
        try:
            lexer = AnalizadorLexico(codigo)
            tokens = lexer.analizar()
            parser = Parser(tokens)
            resultado = parser.analizar()
            es_valido = isinstance(resultado, list)
            self.test("Sintáctico: For", es_valido,
                      f"Resultado: {resultado}")
        except Exception as e:
            self.test("Sintáctico: For", False, str(e))

    def test_sintactico_expresiones_anidadas(self):
        """Test: expresiones anidadas"""
        codigo = "int z = (a + b) * c;"
        try:
            lexer = AnalizadorLexico(codigo)
            tokens = lexer.analizar()
            parser = Parser(tokens)
            resultado = parser.analizar()
            es_valido = isinstance(resultado, list) and len(resultado) > 0
            self.test("Sintáctico: Expresiones anidadas", es_valido,
                      f"Resultado: {resultado}")
        except Exception as e:
            self.test("Sintáctico: Expresiones anidadas", False, str(e))

    # ==================== TESTS DE ENTROPÍA ====================

    def test_entropia_calculo(self):
        """Test: cálculo de entropía Shannon"""
        codigo = "int x = 10;"
        try:
            lexer = AnalizadorLexico(codigo)
            tokens = lexer.analizar()
            calc = CalculadorEntropia(tokens)
            entropia = calc.calcular()
            self.test("Entropía: Cálculo Shannon", 
                      isinstance(entropia, float) and 0 <= entropia <= 10,
                      f"Entropía: {entropia}")
        except Exception as e:
            self.test("Entropía: Cálculo Shannon", False, str(e))

    def test_entropia_estadisticas(self):
        """Test: estadísticas completas"""
        codigo = "int x = 10; float y = 3.14;"
        try:
            lexer = AnalizadorLexico(codigo)
            tokens = lexer.analizar()
            calc = CalculadorEntropia(tokens)
            stats = calc.estadisticas_completas()
            tiene_campos = all(k in stats for k in 
                              ["entropia_shannon", "total_tokens", "tipos_unicos"])
            self.test("Entropía: Estadísticas completas", tiene_campos,
                      f"Campos: {stats.keys()}")
        except Exception as e:
            self.test("Entropía: Estadísticas completas", False, str(e))

    def test_entropia_normalizacion(self):
        """Test: normalización de entropía"""
        codigo = "int x = 10;"
        try:
            lexer = AnalizadorLexico(codigo)
            tokens = lexer.analizar()
            calc = CalculadorEntropia(tokens)
            norm = calc.normalizacion()
            self.test("Entropía: Normalización", 
                      isinstance(norm, float) and 0 <= norm <= 1,
                      f"Normalización: {norm}")
        except Exception as e:
            self.test("Entropía: Normalización", False, str(e))

    # ==================== TESTS DE MANEJO DE ERRORES ====================

    def test_error_codigo_vacio(self):
        """Test: manejo de código vacío"""
        codigo = ""
        try:
            lexer = AnalizadorLexico(codigo)
            tokens = lexer.analizar()
            self.test("Errores: Código vacío", len(tokens) == 0,
                      f"Se generaron {len(tokens)} tokens")
        except Exception as e:
            self.test("Errores: Código vacío", False, str(e))

    def test_error_lexico_invalido(self):
        """Test: error léxico detectado"""
        codigo = "int x = @#$;"
        try:
            lexer = AnalizadorLexico(codigo)
            tokens = lexer.analizar()
            self.test("Errores: Léxico inválido", False,
                      "Debería lanzar excepción")
        except Exception:
            self.test("Errores: Léxico inválido", True)

    def test_error_sintactico_detectado(self):
        """Test: error sintáctico detectado"""
        codigo = "int x = "  # Incompleto
        try:
            lexer = AnalizadorLexico(codigo)
            tokens = lexer.analizar()
            parser = Parser(tokens)
            resultado = parser.analizar()
            # Si llega aquí sin error, verificamos que sea un error
            self.test("Errores: Sintáctico inválido", 
                      isinstance(resultado, dict) and resultado.get("tipo") == "error",
                      "No se detectó el error sintáctico")
        except Exception:
            self.test("Errores: Sintáctico inválido", True)

    def ejecutar_todos(self):
        """Ejecuta todos los tests"""
        print("\n" + "="*60)
        print("PRUEBAS UNITARIAS DEL ANALIZADOR")
        print("="*60 + "\n")

        print("📝 TESTS LÉXICOS")
        print("-" * 60)
        self.test_lexico_declaracion_simple()
        self.test_lexico_string()
        self.test_lexico_float()
        self.test_lexico_operadores_compuestos()
        self.test_lexico_comentarios()

        print("\n📝 TESTS SINTÁCTICOS")
        print("-" * 60)
        self.test_sintactico_declaracion()
        self.test_sintactico_funcion()
        self.test_sintactico_if()
        self.test_sintactico_while()
        self.test_sintactico_for()
        self.test_sintactico_expresiones_anidadas()

        print("\n📊 TESTS DE ENTROPÍA")
        print("-" * 60)
        self.test_entropia_calculo()
        self.test_entropia_estadisticas()
        self.test_entropia_normalizacion()

        print("\n⚠️ TESTS DE MANEJO DE ERRORES")
        print("-" * 60)
        self.test_error_codigo_vacio()
        self.test_error_lexico_invalido()
        self.test_error_sintactico_detectado()

        print("\n" + "="*60)
        print(f"RESULTADOS: {self.tests_pasados}✅ | {self.tests_fallidos}❌")
        print("="*60)

        if self.errores:
            print("\n❌ ERRORES DETECTADOS:")
            for error in self.errores:
                print(f"  - {error}")

        return self.tests_pasados, self.tests_fallidos


if __name__ == "__main__":
    tester = TestsAnalizador()
    pasados, fallidos = tester.ejecutar_todos()
    exit(1 if fallidos > 0 else 0)
