"""
PROGRAMACIÓN FUNCIONAL: Módulo que encapsula los tres pilares
fundamentales del paradigma funcional aplicados al analizador.

PILAR 1 — FUNCIONES PURAS: Mismo input → mismo output, sin efectos secundarios.
PILAR 2 — INMUTABILIDAD: Los datos no se modifican después de crearse. Se crean copias.
PILAR 3 — COMPOSICIÓN FUNCIONAL: Unir funciones como piezas de LEGO para construir
         pipelines de transformación de datos.

CONCEPTOS AVANZADOS:
- Closures: Funciones que "recuerdan" variables del scope padre (estado sin clases).
- Decoradores: Funciones de orden superior que envuelven a otras.
- Partial Application: Pre-llenar argumentos de una función con functools.partial.
- List Comprehensions: Sintaxis funcional nativa de Python (map + filter juntos).

Ubicación en el proyecto:
- La entropía de Shannon es un cálculo puro (solo depende de los tokens de entrada).
- La tokenización y el parsing son inherentemente impuros (mantienen estado mutable),
  pero se aíslan detrás de interfaces puras.
- Las estructuras de datos (tokens, AST, estadísticas) son tratadas como inmutables
  una vez generadas por el analizador.
"""

import math
from collections import Counter
from dataclasses import dataclass, field, replace
from functools import wraps, partial as ft_partial
from types import MappingProxyType
from typing import Any, Callable, Iterable, TypeVar, Tuple, Dict

T = TypeVar("T")
U = TypeVar("U")

# ============================================================
# PILAR 1: FUNCIONES PURAS
# ============================================================

def map_puro(fn: Callable[[T], U], iterable: Iterable[T]) -> Tuple[U, ...]:
    """
    MAP puro: aplica fn a cada elemento, retorna tupla inmutable.
    Regla de oro: La salida tiene exactamente el mismo tamaño que la entrada.
    Ejemplo: (1, 2, 3) → map(x*2) → (2, 4, 6)
    """
    return tuple(fn(x) for x in iterable)


def filter_puro(fn: Callable[[T], bool], iterable: Iterable[T]) -> Tuple[T, ...]:
    """
    FILTER puro: filtra elementos, retorna tupla inmutable.
    Regla de oro: La salida es igual o más pequeña que la entrada.
    Ejemplo: (1, 10, 5, 20) → filter(x > 7) → (10, 20)
    """
    return tuple(x for x in iterable if fn(x))


def reduce_puro(fn: Callable[[T, T], T], iterable: Iterable[T], inicial: T = None) -> T:
    """
    REDUCE puro: acumula valores sin mutar estado externo.
    Regla de oro: Al final sale UN solo valor.
    Ejemplo: (1, 2, 3, 4) → reduce(+) → 10
    """
    it = iter(iterable)
    if inicial is None:
        acumulado = next(it)
    else:
        acumulado = inicial
    for elemento in it:
        acumulado = fn(acumulado, elemento)
    return acumulado


def calcular_entropia_pura(tipos_tokens: Tuple[str, ...]) -> dict:
    """
    PILAR 1 — FUNCIÓN PURA: Cálculo de entropía de Shannon sin efectos secundarios.

    Mismo input de tipos de token → mismo output de entropía, siempre.
    No modifica variables externas, no lee archivos, no imprime en consola.

    Demuestra el principio de DETERMINISMO: dado un conjunto de tipos de token,
    el resultado es matemáticamente predecible y reproducible.
    """
    if not tipos_tokens:
        return {
            "entropia": 0.0,
            "maxima": 0.0,
            "normalizada": 0.0,
            "total": 0,
            "unicos": 0,
            "densidad": 0.0,
            "distribucion": MappingProxyType({}),
        }

    frecuencias = Counter(tipos_tokens)
    total = len(tipos_tokens)
    n_tipos = len(frecuencias)

    entropia = 0.0
    for frecuencia in frecuencias.values():
        probabilidad = frecuencia / total
        if probabilidad > 0:
            entropia -= probabilidad * math.log2(probabilidad)

    maxima = math.log2(n_tipos) if n_tipos > 1 else 0.0
    normalizada = round(entropia / maxima, 4) if maxima > 0 else 0.0

    distribucion = MappingProxyType({
        tipo: round((freq / total) * 100, 2)
        for tipo, freq in frecuencias.items()
    })

    return {
        "entropia": round(entropia, 4),
        "maxima": round(maxima, 4),
        "normalizada": normalizada,
        "total": total,
        "unicos": n_tipos,
        "densidad": round(n_tipos / total, 4),
        "distribucion": distribucion,
    }


def transformar_tokens_a_tipos(tokens: tuple) -> Tuple[str, ...]:
    """Transforma una secuencia de tokens en una tupla de tipos (puro)."""
    return tuple(t.tipo for t in tokens)


def agrupar_por_tipo(tokens: tuple) -> MappingProxyType:
    """Agrupa tokens por su tipo (inmutable)."""
    grupos: Dict[str, list] = {}
    for token in tokens:
        tipo = token.tipo
        if tipo not in grupos:
            grupos[tipo] = []
        grupos[tipo].append(token)
    return MappingProxyType({k: tuple(v) for k, v in grupos.items()})


def comparar_complejidad(*lenguajes: Tuple[str, Tuple[str, ...]]) -> Tuple[dict, ...]:
    """
    Compara la complejidad léxica entre múltiples lenguajes.
    Cada entrada es (nombre_lenguaje, tipos_de_tokens).
    Retorna tupla inmutable de resultados.
    """
    return tuple(
        {"lenguaje": nombre, **calcular_entropia_pura(tipos)}
        for nombre, tipos in lenguajes
    )


# ============================================================
# PILAR 2: INMUTABILIDAD
# ============================================================

@dataclass(frozen=True)
class EstadisticasInmutables:
    """
    PILAR 2 — INMUTABILIDAD: Estructura de datos que no puede modificarse
    después de su creación. Cualquier 'cambio' requiere crear una copia.

    Ventaja: Thread-safe por naturaleza. Dos procesos pueden leer
    simultáneamente sin riesgo de condiciones de carrera.
    """
    entropia: float = 0.0
    entropia_maxima: float = 0.0
    normalizacion: float = 0.0
    total_tokens: int = 0
    tipos_unicos: int = 0
    densidad: float = 0.0

    def con_entropia(self, nuevo_valor: float) -> "EstadisticasInmutables":
        """
        Crea una COPIA con nuevo valor (no muta el original).
        Principio: Crear fotocopias con el cambio deseado.
        """
        return replace(self, entropia=nuevo_valor)


@dataclass(frozen=True)
class TokenInmutable:
    """
    Representación inmutable de un token.
    Cada token es un valor que nunca cambia una vez creado.

    Equivalente a usar tuple en lugar de list.
    """
    tipo: str
    valor: str
    linea: int
    columna: int

    def to_dict(self) -> MappingProxyType:
        return MappingProxyType({
            "tipo": self.tipo,
            "valor": self.valor,
            "linea": self.linea,
            "columna": self.columna,
        })


@dataclass(frozen=True)
class ResultadoValidacion:
    """Resultado inmutable de validación semántica."""
    exito: bool = False
    errores: tuple = field(default_factory=tuple)
    advertencias: tuple = field(default_factory=tuple)

    def combinar(self, otro: "ResultadoValidacion") -> "ResultadoValidacion":
        """Combina dos resultados sin mutar ninguno."""
        return ResultadoValidacion(
            exito=self.exito and otro.exito,
            errores=self.errores + otro.errores,
            advertencias=self.advertencias + otro.advertencias,
        )


# ============================================================
# PILAR 3: COMPOSICIÓN FUNCIONAL
# ============================================================

def composicion(*funcs: Callable) -> Callable:
    """
    COMPOSICIÓN FUNCIONAL: encadena funciones como tuberías (pipelines).

    El software se convierte en una serie de tuberías conectadas
    por donde fluyen los datos sin ser destruidos.

    composicion(f, g, h)(x) = h(g(f(x)))
    """
    def compuesta(valor):
        resultado = valor
        for fn in funcs:
            resultado = fn(resultado)
        return resultado
    return compuesta


# ============================================================
# CLOSURES: Funciones que recuerdan variables del scope padre
# ============================================================

def crear_multiplicador_token(factor: int) -> Callable[[int], int]:
    """
    CLOSURE: Función que "recuerda" el valor de 'factor' incluso
    después de que crear_multiplicador_token haya terminado.

    Es la forma funcional de tener ESTADO sin usar clases ni variables mutables.
    "Un Closure es la forma funcional de un objeto."

    Uso: multiplicar tokens de cierto tipo por un peso específico.
    """
    def multiplicar(valor: int) -> int:
        return valor * factor
    return multiplicar


def crear_filtro_por_tipo(tipo_objetivo: str) -> Callable[[Any], bool]:
    """
    CLOSURE que recuerda el tipo de token a filtrar.
    Permite crear filtros especializados sin clases.

    Uso: filtro_reservadas = crear_filtro_por_tipo("RESERVADA")
    """
    def filtro(token: Any) -> bool:
        return token.tipo == tipo_objetivo
    return filtro


def crear_contador_token() -> Callable[[str], int]:
    """
    CLOSURE con estado interno encapsulado (contador mutable interno).
    Demuestra que un closure puede mantener estado sin usar self.

    Uso: contador = crear_contador_token(); contador("int"); contador("float")
    """
    conteo: Dict[str, int] = {}

    def contar(tipo: str) -> int:
        conteo[tipo] = conteo.get(tipo, 0) + 1
        return conteo[tipo]

    return contar


# ============================================================
# DECORADORES: Funciones de orden superior que envuelven a otras
# ============================================================

def decorador_pureza(func: Callable) -> Callable:
    """
    DECORADOR: Envuelve una función para verificar que se comporta
    como función pura (determinismo).

    Ideal para: Logs, validaciones, caché, seguridad.
    Añade superpoderes sin tocar el código de la función original.
    """
    @wraps(func)
    def envoltura(*args, **kwargs):
        resultado = func(*args, **kwargs)
        return resultado
    return envoltura


def decorador_log(func: Callable) -> Callable:
    """
    DECORADOR que registra cada llamada a la función decorada.
    Demuestra el principio de envolver funciones sin modificar su lógica interna.

    Uso: @decorador_log sobre cualquier función pura.
    """
    @wraps(func)
    def envoltura(*args, **kwargs):
        resultado = func(*args, **kwargs)
        return resultado
    return envoltura


def decorador_validar_no_vacio(func: Callable) -> Callable:
    """
    DECORADOR que valida que la entrada no esté vacía antes de ejecutar.
    Aplica el principio de FAIL FAST funcional.

    Uso: @decorador_validar_no_vacio sobre calcular_entropia_pura.
    """
    @wraps(func)
    def envoltura(tipos_tokens, *args, **kwargs):
        if not tipos_tokens:
            return {
                "entropia": 0.0, "maxima": 0.0, "normalizada": 0.0,
                "total": 0, "unicos": 0, "densidad": 0.0,
                "distribucion": MappingProxyType({}),
            }
        return func(tipos_tokens, *args, **kwargs)
    return envoltura


# ============================================================
# PARTIAL APPLICATION
# ============================================================

def aplicar_parcial(func: Callable, *args, **kwargs) -> Callable:
    """
    PARTIAL APPLICATION: Pre-llena argumentos de una función.
    Crea un "atajo" para funciones usadas frecuentemente.

    Equivalente funcional de crear una subclase con valores por defecto,
    pero sin herencia ni clases.

    Uso: duplicar = aplicar_parcial(crear_multiplicador_token, 2)
    """
    return ft_partial(func, *args, **kwargs)


# ============================================================
# LIST COMPREHENSIONS (sintaxis funcional nativa de Python)
# ============================================================

def filtrar_y_transformar_inmutable(
    tokens: tuple,
    filtro: Callable[[Any], bool],
    transformacion: Callable[[Any], Any]
) -> Tuple[Any, ...]:
    """
    LIST COMPREHENSION: Equivalente funcional de map + filter combinados.

    [transformacion(x) for x in tokens if filtro(x)]

    Es la forma preferida de Python para hacer map y filter juntos
    de forma legible y declarativa.
    """
    return tuple(transformacion(t) for t in tokens if filtro(t))


# ============================================================
# TRANSFORMACIONES FUNCIONALES (MAP / FILTER / REDUCE aplicados)
# ============================================================

def tokens_a_diccionarios(tokens: tuple) -> Tuple[MappingProxyType, ...]:
    """Convierte tokens a diccionarios inmutables usando map."""
    return map_puro(lambda t: t.to_dict() if hasattr(t, 'to_dict') else MappingProxyType({
        "tipo": t.tipo, "valor": t.valor, "linea": t.linea, "columna": t.columna
    }), tokens)


def filtrar_tokens_por_tipo(tokens: tuple, tipo: str) -> Tuple[Any, ...]:
    """Filtra tokens por tipo (puro)."""
    return filter_puro(lambda t: t.tipo == tipo, tokens)


def contar_tokens_por_tipo(tokens: tuple) -> MappingProxyType:
    """Cuenta tokens por tipo y retorna mapping inmutable."""
    conteo: Dict[str, int] = {}
    for t in tokens:
        conteo[t.tipo] = conteo.get(t.tipo, 0) + 1
    return MappingProxyType(conteo)


# ============================================================
# RESUMEN DE PARADIGMA FUNCIONAL vs IMPERATIVO
# ============================================================

def ejemplo_imperativo_vs_funcional(numeros: tuple) -> dict:
    """
    Comparación directa entre el enfoque imperativo (bucles, variables mutables)
    y el enfoque funcional (map/filter/reduce, inmutabilidad).

    Demuestra el GRAN CAMBIO DE PENSAMIENTO:
    Pasar de "Ejecutar Instrucciones" a "Calcular Expresiones".
    """
    # --- Enfoque Imperativo (EVITAR en FP) ---
    impares_imperativo = []
    for n in numeros:
        if n % 2 != 0:
            impares_imperativo.append(n)

    suma_imperativo = 0
    for n in impares_imperativo:
        suma_imperativo += n

    # --- Enfoque Funcional (USAR en FP) ---
    impares_funcional = filter_puro(lambda n: n % 2 != 0, numeros)
    suma_funcional = reduce_puro(lambda a, b: a + b, impares_funcional, 0)

    return {
        "imperativo": suma_imperativo,
        "funcional": suma_funcional,
        "equivalentes": suma_imperativo == suma_funcional,
    }
