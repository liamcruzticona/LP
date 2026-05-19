# Analizador Léxico y Sintáctico Multilenguaje v4.0

## Descripción

Analizador léxico, sintáctico y semántico multilenguaje con visualización interactiva. Soporta **C, C++, Java, JavaScript y Python**, cada uno con lexer, parser, AST y validador semántico propios.

Implementa **doble paradigma**: Programación Orientada a Objetos (4 pilares) + Programación Funcional (2 pilares: pureza e inmutabilidad). Incluye cálculo de **Entropía de Shannon** como métrica de complejidad léxica.

---

## Paradigmas de Programación

### POO — 4 Pilares

| Pilar | Aplicación en el proyecto |
|-------|--------------------------|
| **Abstracción** | `TokenBase`, `AnalizadorLexicoBase`, `ParserBase`, `ValidadorSemanticoBase` — definen qué hace cada componente |
| **Herencia** | `CLikeLexerBase` → CLexer, CppLexer, JavaLexer, JavaScriptLexer; 5 validadores heredan de `ValidadorSemanticoBase` |
| **Polimorfismo** | `sentencia()` distinto en cada parser; `validar()` distinto en cada validador; Factory retorna instancia correcta |
| **Encapsulamiento** | Métodos `_privados`, `config.py`, `ServicioAnalisis`, Factory oculta clases concretas |

### Programación Funcional — 2 Pilares

| Pilar | Aplicación en el proyecto |
|-------|--------------------------|
| **Funciones Puras** | `calcular_entropia_pura()`, `map_puro()`, `filter_puro()`, `reduce_puro()`, `composicion()` — sin efectos secundarios |
| **Inmutabilidad** | `EstadisticasInmutables`, `TokenInmutable`, `ResultadoValidacion` con `@dataclass(frozen=True)`, `MappingProxyType` |

---

## Arquitectura del Sistema

```
analizador-proyecto/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .gitignore
├── informe.tex                    ← Documento académico LaTeX
├── diagramas/                     ← UML (Casos de Uso + Clases)
├── backend/
│   ├── app.py                     ← Punto de entrada Flask
│   ├── config.py                  ← Configuración centralizada
│   ├── routes/
│   │   └── analisis.py            ← Endpoints HTTP (capa presentación)
│   ├── services/
│   │   └── analisis_service.py    ← Lógica de negocio (capa servicios)
│   ├── core/
│   │   ├── token.py               ← TokenBase, Token (POO: Abstracción + Herencia)
│   │   ├── analizador_factory.py  ← Factory Pattern (POO: Polimorfismo)
│   │   ├── entropia.py            ← Shannon + doble paradigma (OOP + FP)
│   │   ├── funcional.py           ← Funciones puras + Inmutabilidad (FP)
│   │   ├── semantica/             ← Validadores por lenguaje (POO: Herencia + Polimorfismo)
│   │   │   ├── base.py
│   │   │   ├── semantica_c.py
│   │   │   ├── semantica_cpp.py
│   │   │   ├── semantica_java.py
│   │   │   ├── semantica_js.py
│   │   │   └── semantica_py.py
│   │   └── analizadores/          ← Lexers + Parsers por lenguaje
│   │       ├── base.py            ← Clases abstractas
│   │       ├── base_clike.py      ← Herencia C-like
│   │       ├── c_analyzer.py
│   │       ├── cpp_analyzer.py
│   │       ├── java_analyzer.py
│   │       ├── javascript_analyzer.py
│   │       └── python_analyzer.py
│   └── tests/
│       └── test_analizadores.py   ← 60 pruebas unitarias + HTTP + FP
├── frontend/
│   ├── index.html                 ← Shell HTML
│   ├── nginx.conf                 ← Proxy reverso (Docker)
│   ├── css/
│   │   └── styles.css             ← 5 temas (c, cpp, java, js, python)
│   └── js/
│       ├── config.js              ← Configuración
│       ├── profiles.js            ← Perfiles de lenguaje + ejemplos
│       ├── editor.js              ← CodeMirror + atajos
│       ├── renderer.js            ← Visualización AST + copiar
│       ├── api.js                 ← Conexión backend + spinner
│       └── app.js                 ← Orquestador UI + comparador
└── diagramas/
    ├── casos_de_uso.puml / .svg / .png
    └── diagrama_clases.puml / .svg / .png
```

---

## Diferenciación por Lenguaje

| Característica | C | C++ | Java | JavaScript | Python |
|---------------|:--:|:---:|:----:|:----------:|:------:|
| Keywords | 15 | 25 | 24 | 13 | 19 |
| Operadores únicos | `*`, `&` | `<<`, `>>` | -- | `===`, `!==`, `=>` | `**`, `//=` |
| Comentarios | `//`, `/* */` | `//`, `/* */` | `//`, `/* */` | `//`, `/* */` | `#` |
| Tokens especiales | PUNTERO | PUNTERO, PREPROC | -- | -- | INDENT, DEDENT |
| Clases | -- | `class` | `class` (obligatorio) | -- | `class` |
| Funciones flecha | -- | Lambda | -- | `=>` | -- |
| `import`/`from` | -- | -- | `import`, `package` | -- | `import`, `from` |
| `elif` | -- | -- | -- | -- | Sí |
| Type Checking | Sí | Sí | Sí | -- | -- |
| Tema visual | Azul | Púrpura | Naranja | Amarillo | Verde |

---

## Instalación

### Opción 1: Docker (recomendado)

```bash
git clone https://github.com/liamcruzticona/LP.git
cd LP
docker-compose up --build
```

- Frontend: `http://localhost:8080`
- Backend API: `http://localhost:5000`

### Opción 2: Desarrollo local

```bash
pip install -r requirements.txt
python backend/app.py                          # Terminal 1: Backend
python -m http.server 8080 --directory frontend # Terminal 2: Frontend
```

- Frontend: `http://127.0.0.1:8080`
- Backend API: `http://127.0.0.1:5000`

---

## Uso

### Interfaz Web
1. Selecciona el lenguaje en el dropdown (C, C++, Java, JavaScript, Python)
2. Escribe código o carga un ejemplo predefinido
3. Presiona **Ctrl+Enter** o clic en **Analizar**
4. Explora los resultados en 4 pestañas: Tokens, AST, Semántica, Estadísticas

### Atajos de teclado
| Atajo | Acción |
|-------|--------|
| `Ctrl+Space` | Autocompletado |
| `Ctrl+Enter` | Ejecutar análisis |

### API REST

**`POST /analizar`**
```json
{
  "codigo": "int x = 5;",
  "lenguaje": "c"
}
```

Respuesta:
```json
{
  "lenguaje": "C",
  "tokens": [{"tipo": "RESERVADA", "valor": "int", "linea": 1, "columna": 1}, ...],
  "ast": [{"tipo": "declaracion", "tipo_dato": "int", "identificador": "x", ...}],
  "validacion": {"exito": true, "errores": [], "advertencias": []},
  "estadisticas": {"entropia_shannon": 2.3219, "normalizacion": 1.0, ...},
  "exito": true
}
```

**`GET /idiomas`** — Lista los lenguajes soportados  
**`GET /info`** — Metadata del sistema

---

## Pruebas

```bash
python backend/tests/test_analizadores.py
```

**60 pruebas, 0 fallos:**

| Categoría | Tests |
|-----------|:-----:|
| Lenguaje C | 12 |
| Lenguaje C++ | 5 |
| Lenguaje Java | 7 |
| Lenguaje JavaScript | 5 |
| Lenguaje Python | 8 |
| Semántica + Entropía | 4 |
| Manejo de errores | 3 |
| Factory / POO | 3 |
| Integración HTTP | 3 |
| Programación Funcional | 10 |
| **TOTAL** | **60** |

---

## Funcionalidades

- Análisis léxico con tokens personalizados por lenguaje
- Análisis sintáctico con parser recursivo descendente y AST propio por lenguaje
- Validación semántica: scope de variables, redeclaración, uso sin declaración, type checking (C/C++/Java)
- Entropía de Shannon + barra visual normalizada
- Panel de Teoría de la Información en tiempo real
- Comparador sintáctico entre los 5 lenguajes con resalte dinámico
- Editor CodeMirror con syntax highlighting, autocompletado y bracket matching
- 5 temas visuales (uno por lenguaje) con cambio dinámico de colores e íconos
- Ejemplos automáticos por lenguaje
- Arquitectura en 3 capas: routes → services → core
- Factory Pattern para selección dinámica de analizador/validador
- Doble paradigma: POO (4 pilares) + Programación Funcional (pureza + inmutabilidad)
- Contenedorizado con Docker + Nginx reverse proxy
- 60 pruebas automatizadas (unitarias + HTTP + funcionales)

---

## Diagramas UML

Disponibles en la carpeta `diagramas/` (PlantUML + SVG + PNG):

- **Casos de Uso**: 10 casos con relaciones `<<include>>` y `<<extend>>`
- **Clases**: Arquitectura POO completa con los 4 pilares anotados

---

## Tecnologías

| Capa | Tecnología |
|------|-----------|
| Backend | Python 3.13 + Flask |
| Frontend | HTML5, CSS3, JavaScript (ES6) |
| Editor | CodeMirror 5.65.2 |
| Estilos | Bootstrap 5.3.0 |
| Íconos | Font Awesome 6.0.0 |
| Contenedores | Docker + Docker Compose 3.9 |
| Servidor web | Nginx Alpine |
| Diagramas | PlantUML |

---

## Autor

Liam Cruz Ticona — Proyecto académico del curso de Lenguajes de Programación  
Universidad Nacional del Altiplano — Facultad de Ingeniería de Sistemas  
Semestre 2026-I

---

**Versión**: 4.0  
**Última actualización**: Mayo 2026
