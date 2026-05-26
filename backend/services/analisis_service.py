"""
SERVICIOS: Capa de lógica de negocio entre las rutas HTTP y el core.
ABSTRACCIÓN: Las rutas no conocen detalles de análisis, solo llaman al servicio.
"""

from core.analizador_factory import get_analizador, get_validador_semantico, idiomas_disponibles
from core.entropia import CalculadorEntropia


class ServicioAnalisis:
    

    @staticmethod
    def analizar_codigo(codigo: str, lenguaje: str) -> dict:
        if not codigo:
            raise ValueError("El campo 'codigo' está vacío")

        analizador = get_analizador(lenguaje)
        resultado = analizador.analizar(codigo)

        if isinstance(resultado, dict) and resultado.get("tipo") == "error":
            raise SyntaxError(resultado.get("mensaje", "Error sintáctico"))

        tokens = resultado.get("tokens")
        if not tokens:
            raise RuntimeError("No se generaron tokens")

        validador = get_validador_semantico(lenguaje, resultado.get("ast"))
        validacion = validador.validar()

        calc = CalculadorEntropia(tokens)
        estadisticas = calc.estadisticas_completas()

        return {
            "lenguaje": resultado.get("lenguaje"),
            "slug": resultado.get("slug"),
            "metadata": resultado.get("metadata", {}),
            "tokens": [t.to_dict() for t in tokens],
            "ast": resultado.get("ast"),
            "validacion": validacion,
            "estadisticas": estadisticas,
            "exito": True,
        }

    @staticmethod
    def obtener_idiomas() -> dict:
        disponibles = {}
        for clave in idiomas_disponibles():
            analizador = get_analizador(clave)
            disponibles[clave] = {
                "nombre": analizador.nombre,
                "slug": analizador.slug,
                "metadata": analizador.metadata,
            }
        return {"disponibles": disponibles}
