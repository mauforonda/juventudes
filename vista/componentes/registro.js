const loaders = {
  numero_nacional: "./numero_nacional.js",
  media_nacional: "./media_nacional.js",
  media_edad: "./media_edad.js",
  media_departamentos: "./media_departamentos.js",
  media_municipios: "./media_municipios.js",
  brecha_nacional: "./brecha_nacional.js",
  brecha_edad: "./brecha_edad.js",
  brecha_departamentos: "./brecha_departamentos.js",
  brecha_categorias: "./brecha_categorias.js",
  media_categorias: "./media_categorias.js",
  media_subcategoria: "./media_subcategoria.js",
  media_departamento_categoria: "./media_departamento_categoria.js",
  numero_edad: "./numero_edad.js",
  porcentaje_nacional: "./porcentaje_nacional.js",
  porcentaje_edad: "./porcentaje_edad.js",
  porcentaje_municipios: "./porcentaje_municipios.js",
  porcentaje_departamentos: "./porcentaje_departamentos.js",
  porcentaje_categorias: "./porcentaje_categorias.js",
  porcentaje_subcategoria: "./porcentaje_subcategoria.js",
  porcentaje_edad_categoria: "./porcentaje_edad_categoria.js",
  porcentaje_departamento_categoria: "./porcentaje_departamento_categoria.js",
  porcentaje_municipio_categoria: "./porcentaje_municipio_categoria.js",
};

const cache = new Map();

export function cargarComponente(tipo, version = "") {
  const clave = `${tipo}:${version}`;
  if (!cache.has(clave)) {
    const ruta = loaders[tipo];
    cache.set(clave, import(`${ruta}${version ? `?v=${version}` : ""}`));
  }
  return cache.get(clave);
}
