const loaders = {
  numero_nacional: "./numero_nacional.js",
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
