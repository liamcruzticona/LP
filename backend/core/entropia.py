"""
Módulo para cálculo de entropía Shannon y métricas avanzadas.

DOBLE PARADIGMA:
- OOP: CalculadorEntropia encapsula estado mutable (tokens, frecuencias) y
  expone métodos que calculan métricas. (ABSTRACCIÓN + ENCAPSULAMIENTO)
- FUNCIONAL: Las funciones puras en core.funcional.py reciben datos y
  retornan resultados sin modificar estado externo. (PUREZA + INMUTABILIDAD)

Se eligió la clase (OOP) para el flujo principal porque el backend procesa
una secuencia de tokens una vez y necesita consultar múltiples métricas
sin recalcular. Las funciones puras se usan para cálculos aislados y
comparaciones entre lenguajes.
"""

import math
from collections import Counter

from core.funcional import (
    calcular_entropia_pura,
    EstadisticasInmutables,
    transformar_tokens_a_tipos,
)


class CalculadorEntropia:
    """
    ABSTRACCIÓN + ENCAPSULAMIENTO (OOP):
    Clase que encapsula el cálculo de la entropía de los tokens.
    Mantiene estado interno (frecuencias) para consultas múltiples.

    PILAR FP — PUREZA: El método calcular() es una función pura:
    - Dados los mismos tokens → misma entropía siempre.
    - No modifica estado externo ni produce efectos secundarios.
    """

    def __init__(self, tokens):
        self.tokens = tokens
        self._calcular_frecuencias()

        # Versión inmutable de tipos (FP)
        self._tipos_inmutables = transformar_tokens_a_tipos(tuple(tokens))

    def _calcular_frecuencias(self):
        self.tipos = [token.tipo for token in self.tokens]
        self.frecuencias = Counter(self.tipos)
        self.total = len(self.tokens) if self.tokens else 1

    def calcular(self):
        """
        PILAR FP — FUNCIÓN PURA:
        H = -sum(p_i * log2(p_i))

        Misma entrada → misma salida. Sin efectos secundarios.
        Mide la incertidumbre en la distribución de tokens.
        """
        if not self.tokens:
            return 0.0

        entropia = 0.0
        for frecuencia in self.frecuencias.values():
            probabilidad = frecuencia / self.total
            if probabilidad > 0:
                entropia -= probabilidad * math.log2(probabilidad)

        return round(entropia, 4)

    def calcular_puro(self) -> dict:
        """
        Versión 100% funcional del cálculo completo.
        Usa la función pura importada de core.funcional.
        No depende del estado de la clase.
        """
        return calcular_entropia_pura(self._tipos_inmutables)

    def detalle(self):
        detalle = {}
        for tipo, freq in self.frecuencias.items():
            prob = round((freq / self.total) * 100, 2)
            detalle[tipo] = {
                "frecuencia": freq,
                "porcentaje": prob
            }
        return detalle

    def complejidad_tokenica(self):
        return len(self.frecuencias)

    def densidad(self):
        if not self.tokens:
            return 0.0
        return round(len(self.frecuencias) / self.total, 4)

    def entropia_maxima(self):
        n_tipos = len(self.frecuencias)
        if n_tipos <= 1:
            return 0.0
        return round(math.log2(n_tipos), 4)

    def normalizacion(self):
        """
        PILAR FP — PUREZA: Normaliza entropía entre 0 y 1.
        0 = completamente predecible (baja diversidad léxica).
        1 = completamente aleatoria (alta diversidad léxica).
        """
        e_max = self.entropia_maxima()
        if e_max == 0:
            return 0.0
        return round(self.calcular() / e_max, 4)

    def estadisticas_completas(self):
        """Devuelve estadísticas completas del análisis"""
        return {
            "entropia_shannon": self.calcular(),
            "entropia_maxima": self.entropia_maxima(),
            "normalizacion": self.normalizacion(),
            "total_tokens": self.total,
            "tipos_unicos": self.complejidad_tokenica(),
            "densidad": self.densidad(),
            "distribucion": self.detalle(),
            # PILAR FP: estadísticas en formato inmutable (dataclass frozen)
            "inmutables": {
                "entropia": EstadisticasInmutables(
                    entropia=self.calcular(),
                    entropia_maxima=self.entropia_maxima(),
                    normalizacion=self.normalizacion(),
                    total_tokens=self.total,
                    tipos_unicos=self.complejidad_tokenica(),
                    densidad=self.densidad(),
                ).__dict__
            }
        }

    def estadisticas_puras(self) -> dict:
        """
        PILAR FP: Obtiene estadísticas usando exclusivamente
        la función pura calcular_entropia_pura().
        Demuestra que el mismo resultado se obtiene sin estado mutable.
        """
        return calcular_entropia_pura(self._tipos_inmutables)
