/**
 * CONFIGURACION: Constantes y configuración del frontend.
 * ENCAPSULAMIENTO: Centraliza valores que pueden cambiar entre entornos.
 * Auto-detecta si está detrás de nginx (Docker) o en desarrollo local.
 */

const CONFIG = (function () {
    return {
        API_URL: 'http://127.0.0.1:5000',
        VERSION: '4.0',
        NOMBRE: 'Analizador Léxico y Sintáctico Multilenguaje',
        DEFAULT_LANGUAGE: 'c',
    };
})();
