const TopoJSON = await import("https://cdn.jsdelivr.net/npm/topojson-client@3/+esm");
const Geo = await import("https://cdn.jsdelivr.net/npm/d3-geo@3/+esm");
const normalizar = codigo => String(codigo ?? "").replace(/^0+/, "");
const topojson = await fetch("./datos/departamentos.json").then(response => response.json());
const geojson = TopoJSON.feature(topojson, topojson.objects.departamentos);
geojson.features.forEach(feature => {
  feature.properties.codigo = feature.properties.departamento;
  feature.properties.centroid = Geo.geoCentroid(feature);
});
const nombres = await fetch("https://raw.githubusercontent.com/mauforonda/juventudes/refs/heads/main/diccionarios/municipios.csv")
  .then(response => response.text()).then(texto => {
    const [cabecera, ...filas] = texto.trim().split(/\r?\n/);
    const columnas = cabecera.split(",");
    const codigo = columnas.indexOf("codigo_departamento");
    const nombre = columnas.indexOf("departamento");
    return new Map(filas.map(fila => { const valores = fila.split(","); return [normalizar(valores[codigo]), valores[nombre]]; }));
  });

export const layout = { minWidth: 360, minHeight: 310 };

export async function render({ rows, campo, observaciones, estadistico, filtroCampo = "estadistico", filtroValor, formato = "numero", version = "" }) {
  const { render: crearMapa } = await import(`./comun/porcentaje_territorios.js${version ? `?v=${version}` : ""}`);
  const formatear = formato === "porcentaje" ? valor => `${valor.toLocaleString("es-BO", { maximumFractionDigits: 1 })}%` : formato === "moneda" ? valor => `Bs. ${valor.toLocaleString("es-BO", { maximumFractionDigits: 0 })}` : valor => valor.toLocaleString("es-BO", { maximumFractionDigits: 1 });
  return crearMapa({ rows, campo, observaciones, estadistico, filtroCampo, filtroValor, formatear, geojson, nombres, campoCodigo: "codigo_departamento", normalizar, etiqueta: "por departamento", clase: "media_departamentos", modo: "media" });
}
