"""Módulo para cálculo de entropía Shannon y métricas avanzadas"""

import math
from collections import Counter


class CalculadorEntropia:
    """
    ABSTRACCIÓN (POO): Clase que encapsula el cálculo de la entropía de los tokens.
    Mantiene estado interno (frecuencias) para consultas múltiples.

    El método calcular() exhibe PUREZA FUNCIONAL de forma natural:
    - Dados los mismos tokens → misma entropía siempre.
    - No modifica estado externo ni produce efectos secundarios.
    """

    def __init__(self, tokens):
        self.tokens = tokens
        self._calcular_frecuencias()

    def _calcular_frecuencias(self):
        self.tipos = [token.tipo for token in self.tokens]
        self.frecuencias = Counter(self.tipos)
        self.total = len(self.tokens) if self.tokens else 1

    def calcular(self):
        """
        H = -sum(p_i * log2(p_i))
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
            "distribucion": self.detalle()
        }
