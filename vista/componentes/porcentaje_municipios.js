const TopoJSON = await import("https://cdn.jsdelivr.net/npm/topojson-client@3/+esm");
const Geo = await import("https://cdn.jsdelivr.net/npm/d3-geo@3/+esm");
const normalizar = codigo => String(codigo ?? "").replace(/^0+/, "");
const topojson = await fetch("./datos/municipios_mini.topo.json").then(response => response.json());
const geojson = TopoJSON.feature(topojson, topojson.objects.municipios);
geojson.features.forEach(feature => { feature.properties.centroid = Geo.geoCentroid(feature); });
const nombres = await fetch("https://raw.githubusercontent.com/mauforonda/juventudes/refs/heads/main/diccionarios/municipios.csv")
  .then(response => response.text()).then(texto => {
    const [cabecera, ...filas] = texto.trim().split(/\r?\n/);
    const columnas = cabecera.split(",");
    const codigo = columnas.indexOf("codigo_municipio");
    const nombre = columnas.indexOf("municipio");
    return new Map(filas.map(fila => { const valores = fila.split(","); return [normalizar(valores[codigo]), valores[nombre]]; }));
  });
export const layout = { minWidth: 360, minHeight: 310 };
export async function render({ rows, numerador, denominador, version = "" }) {
  const { render: crearMapa } = await import(`./comun/porcentaje_territorios.js${version ? `?v=${version}` : ""}`);
  return crearMapa({ rows, numerador, denominador, geojson, nombres, campoCodigo: "codigo_municipio", normalizar, etiqueta: "por municipio", clase: "porcentaje_municipios" });
}
