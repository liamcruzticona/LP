"""Módulo para cálculo de entropía Shannon y métricas avanzadas"""

import math
from collections import Counter


class CalculadorEntropia:
    """
    🔹 ABSTRACCIÓN:
    Clase que encapsula el cálculo de la entropía de los tokens
    """

    def __init__(self, tokens):
        #  ENCAPSULAMIENTO
        self.tokens = tokens
        self._calcular_frecuencias()

    def _calcular_frecuencias(self):
        """ Método privado: calcula frecuencias de tokens"""
        self.tipos = [token.tipo for token in self.tokens]
        self.frecuencias = Counter(self.tipos)
        self.total = len(self.tokens) if self.tokens else 1

    def calcular(self):
        """
        Calcula entropía de Shannon: H = -sum(p_i * log2(p_i))
        Mide la "aleatoriedad" o "incertidumbre" en la distribución de tokens.
        Valor alto = distribución uniforme, Valor bajo = distribución sesgada
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
        """
         ENCAPSULAMIENTO:
        Devuelve información detallada (útil para frontend)
        """
        detalle = {}
        for tipo, freq in self.frecuencias.items():
            prob = round((freq / self.total) * 100, 2)
            detalle[tipo] = {
                "frecuencia": freq,
                "porcentaje": prob
            }
        return detalle

    def complejidad_tokenica(self):
        """
         POLIMORFISMO: Análisis adicional - complejidad
        Devuelve número de tipos únicos de tokens
        """
        return len(self.frecuencias)

    def densidad(self):
        """Densidad de tokens: tipos únicos / total"""
        if not self.tokens:
            return 0.0
        return round(len(self.frecuencias) / self.total, 4)

    def entropia_maxima(self):
        """Entropía máxima posible para n tipos de tokens"""
        n_tipos = len(self.frecuencias)
        if n_tipos <= 1:
            return 0.0
        return round(math.log2(n_tipos), 4)

    def normalizacion(self):
        """
        Normaliza entropía entre 0 y 1
        0 = completamente predecible, 1 = completamente aleatoria
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
            "distribucion": self.detalle()
        }