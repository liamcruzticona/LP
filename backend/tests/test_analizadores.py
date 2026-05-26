"""
Tests unitarios para el analizador multilenguaje.
Demuestra: herencia, polimorfismo, encapsulamiento, abstraccin.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.analizador_factory import get_analizador, get_validador_semantico
from core.entropia import CalculadorEntropia
from core.semantica.base import ValidadorSemanticoBase as ValidadorSemantico


class TestsAnalizador:
    def __init__(self):
        self.tests_pasados = 0
        self.tests_fallidos = 0
        self.errores = []

    def test(self, nombre, condicion, mensaje=""):
        if condicion:
            self.tests_pasados += 1
            print(f"[OK] {nombre}")
        else:
            self.tests_fallidos += 1
            print(f"[FAIL] {nombre}")
            self.errores.append(f"{nombre}: {mensaje}")

    # ==================== C ====================

    def test_c_declaracion(self):
        c = get_analizador("c")
        r = c.analizar("int x = 10;")
        ok = len(r["tokens"]) > 0 and r["tokens"][0].valor == "int"
        self.test("C: Declaracin simple", ok, f"tokens={len(r['tokens'])}")

    def test_c_string(self):
        c = get_analizador("c")
        r = c.analizar('char* msg = "Hola";')
        ok = any(t.tipo == "STRING" for t in r["tokens"])
        self.test("C: Strings", ok)

    def test_c_float(self):
        c = get_analizador("c")
        r = c.analizar("float pi = 3.14;")
        ok = any(t.tipo == "FLOAT" for t in r["tokens"])
        self.test("C: Floats", ok)

    def test_c_operadores(self):
        c = get_analizador("c")
        r = c.analizar("x += 5; y == 3;")
        ok = any(t.tipo == "OP_COMPUESTO" for t in r["tokens"])
        self.test("C: Operadores compuestos", ok)

    def test_c_comentarios(self):
        c = get_analizador("c")
        r = c.analizar("int x = 10; // comentario")
        ok = not any(t.tipo == "COMENTARIO" for t in r["tokens"])
        self.test("C: Comentarios ignorados", ok)

    def test_c_funcion(self):
        c = get_analizador("c")
        r = c.analizar("int suma(int a, int b) { return a + b; }")
        ok = isinstance(r["ast"], list) and len(r["ast"]) > 0
        self.test("C: Funcin con parmetros", ok)

    def test_c_if_else(self):
        c = get_analizador("c")
        r = c.analizar("if (x > 5) { y = 1; } else { y = 0; }")
        ok = isinstance(r["ast"], list)
        self.test("C: If/Else", ok)

    def test_c_while(self):
        c = get_analizador("c")
        r = c.analizar("while (i < 10) { i = i + 1; }")
        ok = isinstance(r["ast"], list)
        self.test("C: While", ok)

    def test_c_for(self):
        c = get_analizador("c")
        r = c.analizar("for (i = 0; i < 10; i++) { printf(i); }")
        ok = isinstance(r["ast"], list)
        self.test("C: For", ok)

    def test_c_expresiones_anidadas(self):
        c = get_analizador("c")
        r = c.analizar("int z = (a + b) * c;")
        ok = isinstance(r["ast"], list) and len(r["ast"]) > 0
        self.test("C: Expresiones anidadas", ok)

    def test_c_bloque_comentario(self):
        c = get_analizador("c")
        r = c.analizar("int x = 5; /* comentario\nmultilinea */ int y = 10;")
        tokens = r["tokens"]
        ok = len(tokens) >= 6 and not any(t.tipo == "COMENTARIO_BLOQUE" for t in tokens)
        self.test("C: Comentario /* */ ignorado", ok)

    def test_c_type_check(self):
        c = get_analizador("c")
        r = c.analizar('int x = "hola";')
        val = get_validador_semantico("c", r["ast"]).validar()
        ok = len(val.get("advertencias", [])) >= 1
        self.test("C: Type check string->int", ok)

    # ==================== C++ ====================

    def test_cpp_clase(self):
        cpp = get_analizador("cpp")
        r = cpp.analizar("class MiClase { public: int x; };")
        ok = isinstance(r["ast"], list)
        self.test("C++: Clase", ok)

    def test_cpp_funcion(self):
        cpp = get_analizador("cpp")
        r = cpp.analizar("int suma(int a, int b) { return a + b; }")
        ok = isinstance(r["ast"], list) and len(r["ast"]) > 0
        self.test("C++: Funcion", ok)

    def test_cpp_cout(self):
        cpp = get_analizador("cpp")
        r = cpp.analizar('int main() { cout << "Hola" << endl; return 0; }')
        ok = isinstance(r["ast"], list)
        self.test("C++: cout <<", ok)

    def test_cpp_namespace(self):
        cpp = get_analizador("cpp")
        r = cpp.analizar("using namespace std; int main() { return 0; }")
        ok = isinstance(r["ast"], list)
        self.test("C++: using namespace", ok)

    def test_cpp_if(self):
        cpp = get_analizador("cpp")
        r = cpp.analizar("if (x > 0) { x = 1; } else { x = 0; }")
        ok = isinstance(r["ast"], list)
        self.test("C++: If/Else", ok)

    # ==================== Java ====================

    def test_java_clase(self):
        java = get_analizador("java")
        r = java.analizar("class Main { public static void main(String[] args) { } }")
        ok = isinstance(r["ast"], list)
        self.test("Java: Clase con metodo", ok)

    def test_java_extends(self):
        java = get_analizador("java")
        r = java.analizar("class Perro extends Animal { }")
        ok = isinstance(r["ast"], list)
        self.test("Java: extends", ok)

    def test_java_campo(self):
        java = get_analizador("java")
        r = java.analizar("class Punto { int x; int y; }")
        ok = isinstance(r["ast"], list)
        self.test("Java: Campos", ok)

    def test_java_if(self):
        java = get_analizador("java")
        r = java.analizar("class X { void m() { if (x > 0) { x = 1; } } }")
        ok = isinstance(r["ast"], list)
        self.test("Java: If/Else en metodo", ok)

    def test_java_for(self):
        java = get_analizador("java")
        r = java.analizar("class X { void m() { for (int i = 0; i < 10; i++) { } } }")
        ok = isinstance(r["ast"], list)
        self.test("Java: For en metodo", ok)

    def test_java_import(self):
        java = get_analizador("java")
        r = java.analizar("import java.util.List; class X { }")
        ok = isinstance(r["ast"], list) and any(n.get("tipo") == "import" for n in r["ast"])
        self.test("Java: import", ok)

    def test_java_package(self):
        java = get_analizador("java")
        r = java.analizar("package com.ejemplo; class X { }")
        ok = isinstance(r["ast"], list) and any(n.get("tipo") == "package" for n in r["ast"])
        self.test("Java: package", ok)

    # ==================== JavaScript ====================

    def test_javascript_var_funcion(self):
        js = get_analizador("javascript")
        r = js.analizar("var x = 10; function saludo() { return x; }")
        ok = r["lenguaje"] == "JavaScript" and isinstance(r["tokens"], list)
        self.test("JavaScript: var + function", ok)

    def test_javascript_let_const(self):
        js = get_analizador("javascript")
        r = js.analizar("let x = 5; const y = x * 2;")
        ok = isinstance(r["ast"], list) and len(r["ast"]) >= 1
        self.test("JavaScript: let + const", ok)

    def test_javascript_arrow(self):
        js = get_analizador("javascript")
        r = js.analizar("const suma = (a, b) => a + b;")
        ok = isinstance(r["ast"], list)
        self.test("JavaScript: Arrow function", ok)

    def test_javascript_if(self):
        js = get_analizador("javascript")
        r = js.analizar("if (x > 0) { x = 1; } else { x = 0; }")
        ok = isinstance(r["ast"], list)
        self.test("JavaScript: If/Else", ok)

    def test_javascript_for(self):
        js = get_analizador("javascript")
        r = js.analizar("for (let i = 0; i < 5; i++) { }")
        ok = isinstance(r["ast"], list)
        self.test("JavaScript: For", ok)

    # ==================== Python ====================

    def test_python_funcion(self):
        py = get_analizador("python")
        r = py.analizar("def saludar(nombre):\n    return nombre")
        ok = r["lenguaje"] == "Python" and isinstance(r["tokens"], list)
        self.test("Python: Funcion con indentacion", ok)

    def test_python_clase(self):
        py = get_analizador("python")
        r = py.analizar("class Persona:\n    def __init__(self, nombre):\n        self.nombre = nombre")
        ok = isinstance(r["ast"], list) or (isinstance(r["ast"], dict) and "error" not in str(r["ast"]).lower())
        self.test("Python: Clase con metodo", ok)

    def test_python_for_in(self):
        py = get_analizador("python")
        r = py.analizar("for i in range(5):\n    print(i)")
        ok = isinstance(r["ast"], list)
        self.test("Python: For...in", ok)

    def test_python_if_else(self):
        py = get_analizador("python")
        r = py.analizar("if x > 0:\n    print('positivo')\nelse:\n    print('negativo')")
        ok = isinstance(r["ast"], list)
        self.test("Python: If/Else con indentacion", ok)

    def test_python_asignacion(self):
        py = get_analizador("python")
        r = py.analizar("x = 5\ny = x + 1")
        ok = isinstance(r["ast"], list) and len(r["ast"]) >= 2
        self.test("Python: Asignacion multiple", ok)

    def test_python_elif(self):
        py = get_analizador("python")
        r = py.analizar("if x > 0:\n    print('positivo')\nelif x == 0:\n    print('cero')\nelse:\n    print('negativo')")
        ok = isinstance(r["ast"], list)
        self.test("Python: If/Elif/Else", ok)

    def test_python_import(self):
        py = get_analizador("python")
        r = py.analizar("import os")
        ok = isinstance(r["ast"], list) and any(n.get("tipo") == "import" for n in r["ast"])
        self.test("Python: import", ok)

    def test_python_from_import(self):
        py = get_analizador("python")
        r = py.analizar("from math import sqrt")
        ok = isinstance(r["ast"], list) and any(n.get("tipo") == "from_import" for n in r["ast"])
        self.test("Python: from import", ok)

    # ==================== Semntica ====================

    def test_semantica_valida(self):
        c = get_analizador("c")
        r = c.analizar("int x = 5; x = x + 1;")
        val = ValidadorSemantico(r["ast"]).validar()
        self.test("Semntica: Declaracin y uso vlido", val.get("exito") is True,
                  f"Errores: {val.get('errores')}")

    # ==================== Entropa ====================

    def test_entropia_calculo(self):
        c = get_analizador("c")
        r = c.analizar("int x = 10;")
        calc = CalculadorEntropia(r["tokens"])
        e = calc.calcular()
        self.test("Entropa: Clculo Shannon",
                  isinstance(e, float) and 0 <= e <= 10, f"e={e}")

    def test_entropia_estadisticas(self):
        c = get_analizador("c")
        r = c.analizar("int x = 10; float y = 3.14;")
        calc = CalculadorEntropia(r["tokens"])
        stats = calc.estadisticas_completas()
        ok = all(k in stats for k in ["entropia_shannon", "total_tokens", "tipos_unicos"])
        self.test("Entropa: Estadsticas completas", ok)

    def test_entropia_normalizacion(self):
        c = get_analizador("c")
        r = c.analizar("int x = 10;")
        calc = CalculadorEntropia(r["tokens"])
        n = calc.normalizacion()
        self.test("Entropa: Normalizacin 0-1",
                  isinstance(n, float) and 0 <= n <= 1, f"n={n}")

    # ==================== Errores ====================

    def test_error_codigo_vacio(self):
        c = get_analizador("c")
        r = c.analizar("")
        ok = len(r["tokens"]) == 0
        self.test("Errores: Cdigo vaco", ok, f"tokens={len(r['tokens'])}")

    def test_error_lexico_invalido(self):
        c = get_analizador("c")
        try:
            c.analizar("int x = @#$;")
            self.test("Errores: Lxico invlido", False, "Debera fallar")
        except Exception:
            self.test("Errores: Lxico invlido", True)

    def test_error_sintactico_detectado(self):
        c = get_analizador("c")
        try:
            r = c.analizar("int x = ")
            ok = isinstance(r["ast"], dict) and r["ast"].get("tipo") == "error"
            self.test("Errores: Sintctico invlido", ok)
        except Exception:
            self.test("Errores: Sintctico invlido", True)

    # ==================== Factory / OOP ====================

    def test_factory_polimorfismo(self):
        """
        POLIMORFISMO: get_analizador retorna objetos distintos
        (CAnalizadorLenguaje, PythonAnalizadorLenguaje, etc.)
        pero todos responden a .analizar().
        """
        for lang in ("c", "python", "javascript"):
            a = get_analizador(lang)
            r = a.analizar("x = 1;")
            ok = "tokens" in r
            self.test(f"Factory: Polimorfismo {lang}", ok)

    # ==================== Integracion HTTP ====================

    def test_http_info(self):
        try:
            from app import app
            with app.test_client() as cliente:
                resp = cliente.get("/info")
                ok = resp.status_code == 200 and "version" in resp.get_json()
                self.test("HTTP: GET /info", ok)
        except Exception as e:
            self.test("HTTP: GET /info", False, str(e))

    def test_http_analizar(self):
        try:
            from app import app
            with app.test_client() as cliente:
                resp = cliente.post("/analizar", json={"codigo": "int x = 5;", "lenguaje": "c"})
                data = resp.get_json()
                ok = resp.status_code == 200 and data.get("exito") is True
                self.test("HTTP: POST /analizar", ok)
        except Exception as e:
            self.test("HTTP: POST /analizar", False, str(e))

    def test_http_idiomas(self):
        try:
            from app import app
            with app.test_client() as cliente:
                resp = cliente.get("/idiomas")
                data = resp.get_json()
                ok = resp.status_code == 200 and "disponibles" in data
                self.test("HTTP: GET /idiomas", ok)
        except Exception as e:
            self.test("HTTP: GET /idiomas", False, str(e))

    # ==================== Ejecucin ====================

    def ejecutar_todos(self):
        print("\n" + "=" * 60)
        print("PRUEBAS UNITARIAS -- ANALIZADOR MULTILENGUAJE v4.0")
        print("=" * 60 + "\n")

        print("--- C ---")
        print("-" * 40)
        self.test_c_declaracion()
        self.test_c_string()
        self.test_c_float()
        self.test_c_operadores()
        self.test_c_comentarios()
        self.test_c_funcion()
        self.test_c_if_else()
        self.test_c_while()
        self.test_c_for()
        self.test_c_expresiones_anidadas()
        self.test_c_bloque_comentario()
        self.test_c_type_check()

        print("\n--- C++ ---")
        print("-" * 40)
        self.test_cpp_clase()
        self.test_cpp_funcion()
        self.test_cpp_cout()
        self.test_cpp_namespace()
        self.test_cpp_if()

        print("\n--- Java ---")
        print("-" * 40)
        self.test_java_clase()
        self.test_java_extends()
        self.test_java_campo()
        self.test_java_if()
        self.test_java_for()
        self.test_java_import()
        self.test_java_package()

        print("\n--- JavaScript ---")
        print("-" * 40)
        self.test_javascript_var_funcion()
        self.test_javascript_let_const()
        self.test_javascript_arrow()
        self.test_javascript_if()
        self.test_javascript_for()

        print("\n--- Python ---")
        print("-" * 40)
        self.test_python_funcion()
        self.test_python_clase()
        self.test_python_for_in()
        self.test_python_if_else()
        self.test_python_asignacion()
        self.test_python_elif()
        self.test_python_import()
        self.test_python_from_import()

        print("\n--- Semantica + Entropia ---")
        print("-" * 40)
        self.test_semantica_valida()
        self.test_entropia_calculo()
        self.test_entropia_estadisticas()
        self.test_entropia_normalizacion()

        print("\n--- Errores ---")
        print("-" * 40)
        self.test_error_codigo_vacio()
        self.test_error_lexico_invalido()
        self.test_error_sintactico_detectado()

        print("\n--- Factory / OOP ---")
        print("-" * 40)
        self.test_factory_polimorfismo()

        print("\n--- Integracion HTTP ---")
        print("-" * 40)
        self.test_http_info()
        self.test_http_analizar()
        self.test_http_idiomas()

        print("\n" + "=" * 60)
        print(f"RESULTADOS: OK={self.tests_pasados}  FAIL={self.tests_fallidos}")
        print("=" * 60)

        if self.errores:
            print("\nERRORES:")
            for e in self.errores:
                print(f"  - {e}")

        return self.tests_pasados, self.tests_fallidos


if __name__ == "__main__":
    t = TestsAnalizador()
    pasados, fallidos = t.ejecutar_todos()
    exit(1 if fallidos > 0 else 0)

