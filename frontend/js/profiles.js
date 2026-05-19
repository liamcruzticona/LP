/**
 * PERFILES de lenguaje: Datos específicos para cada lenguaje.
 * Cada perfil define: nombre, ícono, tema, ejemplos, keywords, autocompletado.
 */

const languageProfiles = {
    c: {
        name: "C",
        icon: "fas fa-memory",
        tagline: "Punteros y memoria manual.",
        description: "C es un lenguaje de sistemas con punteros, estructuras y tipos estáticos.",
        theme: "theme-c",
        examples: [
            "int *p; int x = 10; p = &x;",
            "struct Punto { int x; int y; };",
            "int suma(int a, int b) { return a + b; }",
            "for (int i = 0; i < 5; i++) { printf(\"%d\\n\", i); }"
        ],
        keywords: ["int", "char", "float", "struct", "typedef", "return", "*", "&"],
        hintWords: ["int", "char", "float", "double", "struct", "typedef", "for", "while", "return", "printf", "scanf", "malloc", "free"]
    },
    cpp: {
        name: "C++",
        icon: "fas fa-atom",
        tagline: "Clases, templates y STL.",
        description: "C++ mezcla abstracción de objetos con acceso de bajo nivel y templates.",
        theme: "theme-cpp",
        examples: [
            "int main() { cout << \"Hola C++\" << endl; return 0; }",
            "class Persona { public: string nombre; };",
            "vector<int> datos = {1, 2, 3};",
            "auto suma = [](int a, int b) { return a + b; };"
        ],
        keywords: ["class", "namespace", "std", "auto", "new", "delete", "cout", "cin"],
        hintWords: ["class", "namespace", "using", "std", "cout", "cin", "vector", "string", "auto", "new", "delete"]
    },
    java: {
        name: "Java",
        icon: "fab fa-java",
        tagline: "Clases, métodos y JVM.",
        description: "Java exige clases y métodos públicos, con un estilo orientado a objetos y gestión automática de memoria.",
        theme: "theme-java",
        examples: [
            "public class Prueba {\n    public static void main(String[] args) {\n        System.out.println(\"Hola Java\");\n    }\n}\n",
            "class Persona { private String nombre; }",
            "public int sumar(int a, int b) { return a + b; }",
            "if (x > 0) { System.out.println(x); } else { System.out.println(-x); }"
        ],
        keywords: ["class", "public", "static", "void", "String", "new", "extends", "implements"],
        hintWords: ["class", "public", "static", "void", "String", "new", "extends", "implements", "if", "for", "while"]
    },
    javascript: {
        name: "JavaScript",
        icon: "fab fa-js",
        tagline: "DOM, funciones y asincronía.",
        description: "JavaScript es el lenguaje dinámico de la web, con let/const/var y funciones modernas.",
        theme: "theme-javascript",
        examples: [
            "const saludo = (nombre) => 'Hola ' + nombre;",
            "let x = 5; const y = x * 2;",
            "if (x > 0) { console.log('OK'); }",
            "for (let i = 0; i < 5; i++) { console.log(i); }"
        ],
        keywords: ["var", "let", "const", "function", "=>", "document", "window", "async", "await"],
        hintWords: ["var", "let", "const", "function", "document", "window", "console.log", "if", "for", "while", "return"]
    },
    python: {
        name: "Python",
        icon: "fab fa-python",
        tagline: "Indentación significativa.",
        description: "Python usa indentación para definir bloques y prefiere una sintaxis limpia y legible.",
        theme: "theme-python",
        examples: [
            "def saludar(nombre):\n    return f'Hola {nombre}'\n",
            "class Persona:\n    def __init__(self, nombre):\n        self.nombre = nombre\n",
            "for i in range(5):\n    print(i)\n",
            "if x > 0:\n    print('positivo')\nelse:\n    print('negativo')\n"
        ],
        keywords: ["def", "class", "if", "elif", "else", "for", "in", "return", "lambda"],
        hintWords: ["def", "class", "import", "for", "in", "if", "elif", "else", "return", "print", "self"]
    }
};

const syntaxComparison = {
    variable: {
        c: "int x = 5;",
        cpp: "int x = 5;",
        java: "int x = 5;",
        javascript: "let x = 5;",
        python: "x = 5"
    },
    function: {
        c: "int suma(int a, int b) { return a + b; }",
        cpp: "int suma(int a, int b) { return a + b; }",
        java: "int suma(int a, int b) { return a + b; }",
        javascript: "const suma = (a, b) => a + b;",
        python: "def suma(a, b):\n    return a + b"
    },
    if: {
        c: "if (x > 0) { return 1; }",
        cpp: "if (x > 0) { return 1; }",
        java: "if (x > 0) { return 1; }",
        javascript: "if (x > 0) { return 1; }",
        python: "if x > 0:\n    return 1"
    },
    loop: {
        c: "for (int i = 0; i < 5; i++) { }",
        cpp: "for (int i = 0; i < 5; i++) { }",
        java: "for (int i = 0; i < 5; i++) { }",
        javascript: "for (let i = 0; i < 5; i++) { }",
        python: "for i in range(5):\n    pass"
    }
};

function obtenerModoPorLenguaje(lenguaje) {
    const modos = {
        c: "text/x-csrc",
        cpp: "text/x-csrc",
        java: "text/x-java",
        javascript: "javascript",
        python: "python"
    };
    return modos[lenguaje] || "text/x-csrc";
}

function detectarLenguaje() {
    const code = editor.getValue();
    if (/\b(def |elif |import |print\()/m.test(code)) return "Detectado: Python probable.";
    if (/\b(public static void main|System\.out\.println|class \w+)/m.test(code)) return "Detectado: Java probable.";
    if (/\b(let |const |var |document\.|window\.|=>)/m.test(code)) return "Detectado: JavaScript probable.";
    if (/\bstd::|cout|cin|using namespace std/m.test(code)) return "Detectado: C++ probable.";
    if (/\bint |char |float |printf\(|scanf\(/m.test(code)) return "Detectado: C probable.";
    return "Lenguaje no identificado automáticamente.";
}
