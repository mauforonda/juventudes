# Página para explorar indicadores

Esta página permite navegar, buscar, y consultar los indicadores del Observatorio de la Juventud.

Cada indicador reúne una ficha descriptiva, una tabla de resultados y representaciones visuales específicas.

## Organización

```text
index.html              Estructura de la página
style.css               Estilos compartidos
app.js                  Coordinación de la interfaz y los datos
construir_indice.py     Construcción del índice de navegación
desarrollar.py          Servidor local para desarrollo
indice.json             Índice generado para la página
componentes/            Representaciones visuales
componentes/comun/      Comportamientos compartidos
configuraciones/        Configuración visual de los indicadores
datos/                  Datos estáticos para las representaciones
```

La página separa los datos de la presentación. Los indicadores aportan sus fichas y resultados. La página decide cómo navegarlos y cada configuración decide qué representaciones mostrar.

## Flujo de datos

Al iniciar, la página carga el índice y construye el catálogo de indicadores.

Al abrir un indicador:

1. carga su ficha descriptiva;
2. carga sus resultados;
3. carga su configuración visual, cuando existe;
4. muestra los metadatos y la tabla de resultados;
5. construye las representaciones declaradas.

Los datos se leen como archivos estáticos del repositorio público. Esto permite publicar la página sin un servidor de datos propio y conservar una relación directa entre cada indicador y sus archivos fuente.

## Índice de navegación

`indice.json` contiene los datos mínimos para construir el catálogo.

Incluye los indicadores organizados por slug y sus campos de presentación. También reúne los grupos temáticos y los espacios de política con los indicadores relacionados.

El índice se genera a partir de las fichas. Se reconstruye como parte del proceso de publicación.

## Configuración visual

Cada archivo de `configuraciones/` corresponde a un indicador. Contiene una lista ordenada de representaciones y sus parámetros.

```json
[
  {
    "tipo": "media_nacional",
    "campo": "valor",
    "observaciones": "poblacion_estimada"
  }
]
```

La configuración conecta los campos de resultados con una representación. Así, un mismo comportamiento puede adaptarse a indicadores con estructuras de datos diferentes.

## Arquitectura de componentes

Cada representación es un módulo independiente. Recibe los resultados y los parámetros declarados en la configuración. Puede combinar funciones compartidas y definir la presentación necesaria para su caso.

El registro central relaciona cada tipo declarado en una configuración con su módulo. La página carga los módulos cuando un indicador los necesita.

Los componentes comunes concentran comportamientos reutilizables. Los componentes específicos agregan la lógica de lectura y presentación propia de cada caso.

## Desarrollo

`desarrollar.py` inicia un servidor local y observa los archivos de la página. Los cambios en la aplicación, las configuraciones y los componentes se reflejan durante la sesión de desarrollo.

Este flujo permite revisar un indicador abierto mientras se ajustan sus representaciones.

## Publicación

La publicación ejecuta estos pasos:

1. reconstruye el índice;
2. prepara los archivos estáticos;
3. publica la página en GitHub Pages.

El workflow puede ejecutarse manualmente o a partir de cambios en esta carpeta.
