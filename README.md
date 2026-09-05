# Observatorio de la Juventud

Este proyecto reúne indicadores sobre las condiciones de vida de las personas jóvenes de 16 a 28 años en Bolivia.

Su objetivo es facilitar el análisis de la situación de las juventudes y aportar evidencia para diseñar políticas públicas. Cada indicador reúne su definición, el código que lo produce y una tabla de resultados.

## Alcance actual

Los indicadores utilizan cuatro fuentes:

- Censo de Población y Vivienda 2024.
- Encuesta de Demografía y Salud 2023.
- Encuesta de Hogares 2025.
- Encuesta Continua de Empleo del cuarto trimestre de 2025.

## Estructura

```text
indicadores/        Indicadores, fichas y resultados
diccionarios/       Definiciones compartidas
comun.py            Operaciones generales
cpv.py              Lectura y armonización del censo
edsa.py             Lectura y armonización de la EDSA
eh.py               Lectura y armonización de la EH
ece.py              Lectura y armonización de la ECE
encuestas.py        Operaciones comunes para encuestas
vista/              Página estática para explorar los resultados
config.example.toml Plantilla de rutas a las fuentes
```

`indicadores/` tiene una organización plana. Los módulos de la raíz reúnen definiciones y operaciones compartidas entre indicadores.

## Estructura de un indicador

Cada indicador tiene una carpeta identificada por su código y nombre:

```text
indicadores/i001_poblacion_joven/
├── calcular.py
├── ficha.json
└── resultados.csv
```

- `calcular.py` lee las fuentes y produce el resultado.
- `ficha.json` describe el objetivo, la definición, la población, el método y los campos.
- `resultados.csv` contiene la tabla publicada.

### Ficha del indicador

`ficha.json` contiene los metadatos necesarios para interpretar el resultado:

| Campo | Contenido |
|---|---|
| `codigo` | Identificador del indicador. |
| `nombre` | Nombre breve. |
| `objetivo` | Pregunta o necesidad que atiende. |
| `definicion_conceptual` | Significado de la medida. |
| `poblacion_objetivo` | Personas u hogares incluidos. |
| `descripcion_operativa` | Forma general de construir la medida. |
| `unidad_medida` | Unidad en que se expresa el resultado. |
| `fuente` | Base y tablas utilizadas. |
| `desagregaciones` | Dimensiones disponibles en la tabla. |
| `temas` | Temas asociados mediante sus claves. |
| `espacios_politica` | Espacios de política asociados mediante sus claves. |
| `campos` | Nombre y descripción de cada columna de `resultados.csv`. |
| `metodo` | Variables, reglas y operaciones aplicadas. |

## Diccionarios comunes

`diccionarios/` reúne definiciones utilizadas por varios indicadores:

| Archivo | Contenido |
|---|---|
| `municipios.csv` | Códigos y nombres de municipios y departamentos vigentes en 2024. |
| `area.csv` | Equivalencias de área urbana y rural entre fuentes. |
| `sexo.csv` | Equivalencias de sexo entre fuentes. |
| `temas.json` | Temas usados para describir y reunir indicadores. |
| `espacios_politica.json` | Ámbitos de política pública relacionados con los indicadores. |

Las fichas guardan las claves de `temas.json` y `espacios_politica.json`. Cada entrada de estos diccionarios contiene un nombre y una descripción.

## Uso local

Instala los paquetes requeridos:

```bash
python -m pip install -r requirements.txt
```

Copia la plantilla de configuración y completa las rutas a las fuentes:

```bash
cp config.example.toml config.local.toml
```

Ejecuta un indicador desde la raíz del observatorio:

```bash
python -m indicadores.i001_poblacion_joven.calcular
```

La ejecución valida la ficha y reemplaza `resultados.csv` con la tabla calculada.
