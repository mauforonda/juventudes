# Indicadores del Observatorio de la Juventud

Esta base reúne indicadores reproducibles sobre las personas de 16 a 28 años en Bolivia.
Los scripts usan pandas para leer, transformar y guardar los datos.

Cada indicador tiene una carpeta dentro de `indicadores/` con tres archivos:

- `calcular.py`: produce el indicador.
- `ficha.json`: explica qué mide y cómo se construye.
- `resultados.csv`: contiene la tabla final.

Las rutas locales se guardan en `config.local.toml`. Los códigos comunes están en `diccionarios/` y las funciones compartidas en `comun.py`.

Desde esta carpeta, el primer indicador se actualiza con `python -m indicadores.i001_poblacion_joven.calcular`.
