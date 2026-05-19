"""
CONFIGURACION: Parámetros centralizados de la aplicación.
ENCAPSULAMIENTO: Las constantes de configuración se agrupan aquí
para que el resto del sistema no dependa de valores mágicos.
"""

import os

HOST = os.environ.get("ANALIZADOR_HOST", "0.0.0.0")
PUERTO = int(os.environ.get("ANALIZADOR_PUERTO", "5000"))
DEBUG = os.environ.get("ANALIZADOR_DEBUG", "false").lower() == "true"
VERSION = "4.0"
NOMBRE = "Analizador Léxico y Sintáctico Multilenguaje"
