"""
SEMANTICA: Validadores semánticos por lenguaje.
ABSTRACCIÓN: Cada lenguaje tiene su propio validador con reglas específicas.
POLIMORFISMO: validar() se comporta distinto según el lenguaje.
"""

from core.semantica.base import ValidadorSemanticoBase
from core.semantica.semantica_c import ValidadorSemanticoC
from core.semantica.semantica_cpp import ValidadorSemanticoCpp
from core.semantica.semantica_java import ValidadorSemanticoJava
from core.semantica.semantica_js import ValidadorSemanticoJS
from core.semantica.semantica_py import ValidadorSemanticoPython
