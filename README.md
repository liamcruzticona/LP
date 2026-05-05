# Analizador Léxico y Sintáctico para Lenguajes Tipo C

## Descripción
Este proyecto implementa un analizador léxico y sintáctico robusto para lenguajes tipo C, desarrollado bajo el paradigma de **Programación Orientada a Objetos (POO)** aplicando sus 4 pilares: **Abstracción**, **Encapsulamiento**, **Herencia** y **Polimorfismo**. El sistema permite analizar código fuente, identificar tokens, validar sintaxis y calcular métricas avanzadas como entropía de Shannon.

### Pilares de POO aplicados:
- **Abstracción**: Las clases `AnalizadorLexico`, `Parser` y `CalculadorEntropia` ocultan la complejidad interna y exponen interfaces simples.
- **Encapsulamiento**: Atributos como `self.tokens` y `self.pos` están protegidos dentro de las clases; métodos privados con `_`.
- **Herencia**: `Token` hereda de `TokenBase` para reutilizar atributos comunes.
- **Polimorfismo**: Métodos como `consumir()` funcionan con cualquier tipo de token esperado; `calcular()` se redefine en subclases.

## 6 Mejoras Principales Implementadas

### 1. 🔤 Analizador Léxico Mejorado
Soporta:
- **Strings**: `"texto"`, `'caracteres'`
- **Floats**: `3.14`, `2.5e-3`
- **Operadores compuestos**: `==`, `!=`, `+=`, `-=`, `*=`, `/=`, `++`, `--`, `<=`, `>=`
- **Comentarios**: `// comentario` (ignorados automáticamente)
- **Palabras reservadas expandidas**: `if`, `else`, `while`, `for`, `void`, `char`, `double`, `struct`, `break`, `continue`

**Ejemplo léxico**:
```
Código: float pi = 3.14; // constante
Tokens: RESERVADA(float), ID(pi), OPERADOR(=), FLOAT(3.14), SIMBOLO(;)
(comentario ignorado)
```

### 2. 🎯 Analizador Sintáctico Avanzado
Soporta:
- **Declaraciones**: `int x = 10;`
- **Funciones**: `int suma(int a, int b) { return a + b; }`
- **Estructuras de control**:
  - `if (condicion) { bloque } else { bloque }`
  - `while (condicion) { bloque }`
  - `for (init; condicion; incremento) { bloque }`
- **Expresiones complejas**: `(a + b) * c`, `x == 5 && y != 0`
- **Múltiples sentencias en funciones**
- **Llamadas de función**: `printf("Hola")`, `suma(2, 3)`

**Ejemplo sintáctico**:
```
Código: if (x > 5) { y = 1; } else { y = 0; }
Árbol sintáctico:
{
  "tipo": "if",
  "condicion": {"binaria": "x > 5"},
  "bloque_if": [{"tipo": "asignacion", ...}],
  "bloque_else": [{"tipo": "asignacion", ...}]
}
```

### 3. 📊 Entropía de Shannon (Análisis avanzado)
Calcula: `H = -sum(p_i * log2(p_i))` donde p_i es la probabilidad de cada tipo de token.

**Métricas incluidas**:
- **Entropía Shannon**: Medida de "aleatoriedad" en la distribución de tokens (0-10).
- **Entropía máxima**: Máximo valor posible para n tipos de tokens.
- **Normalización**: Valor entre 0 y 1 (0=predecible, 1=aleatorio).
- **Densidad**: Ratio de tipos únicos / total de tokens.
- **Distribución**: Frecuencia y porcentaje de cada tipo.

**Ejemplo**:
```json
{
  "entropia_shannon": 2.5847,
  "entropia_maxima": 3.0,
  "normalizacion": 0.8616,
  "total_tokens": 12,
  "tipos_unicos": 7,
  "densidad": 0.5833,
  "distribucion": {
    "RESERVADA": {"frecuencia": 3, "porcentaje": 25.0},
    "ID": {"frecuencia": 2, "porcentaje": 16.67},
    ...
  }
}
```

### 4. ⚠️ Manejo Robusto de Errores
- **Mensajes claros**: Especifican qué salió mal y dónde.
- **Sugerencias útiles**: Proponen soluciones basadas en el tipo de error.
- **Recuperación gradual**: Intenta continuar análisis tras ciertos errores.
- **Detalles técnicos**: Incluye fase del error (léxica, sintáctica), línea y sugerencia.

**Ejemplo**:
```json
{
  "error": "Error sintáctico: se esperaba OPERADOR",
  "fase": "Análisis Sintáctico",
  "sugerencia": "Verifica que las funciones tengan parámetros válidos y que los bloques estén balanceados",
  "detalles": ["Error en línea 3: se esperaba ';'"]
}
```

### 5. ✅ Validación Frontend
- **Validación de longitud**: Máximo 10,000 caracteres.
- **Advertencias en tiempo real**: Detecta llaves/paréntesis sin cerrar.
- **Validación de entrada vacía**: Rechaza código vacío con mensaje claro.
- **Manejo mejorado de errores HTTP**: Muestra sugerencias del servidor.

### 6. 🧪 Pruebas Unitarias
Archivo: `backend/tests/test_analizadores.py`

**Cobertura**:
- 5 tests léxicos (declaraciones, strings, floats, operadores, comentarios)
- 6 tests sintácticos (declaraciones, funciones, if/else, while, for, expresiones anidadas)
- 3 tests de entropía (cálculo, estadísticas, normalización)
- 3 tests de manejo de errores (código vacío, léxico inválido, sintáctico inválido)

**Ejecutar tests**:
```bash
docker-compose exec backend python -m tests.test_analizadores
```

**Salida esperada**:
```
✅ Léxico: Declaración simple
✅ Léxico: Strings
✅ Léxico: Floats
... (17 tests más)
RESULTADOS: 17✅ | 0❌
```

## Instalación
1. Clona el repositorio:
   ```bash
   git clone <url-del-repo>
   cd analizador-proyecto
   ```

2. Construye y ejecuta con Docker:
   ```bash
   docker-compose up --build
   ```

3. Accede a la interfaz: `http://localhost:8080`
   - Backend API: `http://localhost:5000`
   - Info API: `http://localhost:5000/info`

## Uso

### Interfaz Web
- Escribe código tipo C en el editor CodeMirror (con resaltado de sintaxis).
- Selecciona un ejemplo predefinido del dropdown.
- Haz clic en "Analizar".
- Visualiza tokens, árbol sintáctico y estadísticas de entropía en pestañas.

### API REST
**Endpoint**: `POST /analizar`

**Request**:
```json
{
  "codigo": "int x = 10;"
}
```

**Response**:
```json
{
  "tokens": [...],
  "sintactico": [...],
  "estadisticas": {...},
  "exito": true
}
```

## Ejemplos de Código Soportado

| Tipo | Ejemplo |
|------|---------|
| Declaración | `int x = 10;` |
| Float | `float pi = 3.14;` |
| String | `char* msg = "Hola";` |
| Función | `int suma(int a, int b) { return a + b; }` |
| If/Else | `if (x > 5) { y = 1; } else { y = 0; }` |
| While | `while (i < 10) { i++; }` |
| For | `for (int i = 0; i < 10; i++) { x += i; }` |
| Expresión anidada | `int z = (a + b) * c;` |

## Metodología
- **Análisis Léxico**: Tokenización usando expresiones regulares con patrones ordenados por prioridad.
- **Análisis Sintáctico**: Parsing recursivo descendente con precedencia de operadores.
- **Entropía**: Cálculo de Shannon con análisis estadístico completo.
- **Arquitectura**: Separación backend (Flask) / frontend (HTML/JS/CodeMirror) con Docker.
- **Testing**: Suite completa de pruebas unitarias (17 tests).

## Resultados
✅ **Análisis léxico**: Identifica 9+ tipos de tokens (números, strings, floats, operadores compuestos, etc.)  
✅ **Análisis sintáctico**: Valida 7+ estructuras (declaraciones, funciones, if/while/for, expresiones complejas)  
✅ **Entropía Shannon**: Calcula con 5 métricas adicionales (máxima, normalización, densidad, etc.)  
✅ **Manejo de errores**: 15+ casos de error con sugerencias contextuales  
✅ **Validación frontend**: 3+ validaciones previas al análisis  
✅ **Tests**: 17 pruebas unitarias con 100% de cobertura en funcionalidades clave

## Arquitectura
```
analizador-proyecto/
├── backend/
│   ├── core/
│   │   ├── lexico.py          (análisis léxico mejorado)
│   │   ├── sintactico.py      (análisis sintáctico avanzado)
│   │   ├── token.py           (definición de tokens con POO)
│   │   └── entropia.py        (entropía Shannon + estadísticas)
│   ├── routes/
│   │   └── analisis.py        (API con manejo de errores robusto)
│   ├── tests/
│   │   └── test_analizadores.py  (17 pruebas unitarias)
│   ├── app.py                 (aplicación Flask)
│   └── requirements.txt
├── frontend/
│   └── index.html             (interfaz con validación)
├── docker/
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## Contribución
1. Fork el repo.
2. Crea una rama para tu feature.
3. Envía un PR.

## Licencia
MIT

## Autor
Desarrollado como proyecto académico de Lenguaje de Programación (Semestre 7)

---

**Última actualización**: 4 de mayo de 2026  
**Versión**: 2.0 (Versión Robusta con 6 mejoras principales)