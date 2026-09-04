const Plot =
  await import("https://cdn.jsdelivr.net/npm/@observablehq/plot@0.6.17/+esm");

const estilo = `
  .porcentaje_territorios svg { display: block; width: 100%; height: auto; }
  .porcentaje_territorios { display: flex; flex-direction: column; gap: 10px; }
  .porcentaje_territorios .cabecera { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
  .porcentaje_territorios .etiqueta, .porcentaje_territorios .leyenda { color: var(--muted); font-size: 12px; }
  .porcentaje_territorios .leyenda { display: flex; align-items: center; gap: 6px; }
  .porcentaje_territorios .barra { width: 90px; height: 8px; border-radius: 2px; }
`;

let estiloCargado = false;
function cargarEstilo() {
  if (estiloCargado) return;
  document
    .querySelectorAll('style[data-componente="porcentaje_territorios"]')
    .forEach((elemento) => elemento.remove());
  const elemento = document.createElement("style");
  elemento.dataset.componente = "porcentaje_territorios";
  elemento.textContent = estilo;
  document.head.append(elemento);
  estiloCargado = true;
}

const formatear = (valor) =>
  `${valor.toLocaleString("es-BO", { minimumFractionDigits: 0, maximumFractionDigits: 1 })}%`;

const mezclar = (fondo, tinta, proporcion) => {
  const parsear = color => {
    const hex = color.match(/^#([0-9a-f]{3}|[0-9a-f]{6})$/i)?.[1];
    if (!hex) return null;
    const completo = hex.length === 3
      ? hex.split("").map(digito => digito + digito).join("")
      : hex;
    return [0, 2, 4].map(indice => parseInt(completo.slice(indice, indice + 2), 16));
  };
  const rgbFondo = parsear(fondo);
  const rgbTinta = parsear(tinta);
  if (!rgbFondo || !rgbTinta) return tinta;
  const rgb = rgbFondo.map((valor, indice) =>
    Math.round(valor + (rgbTinta[indice] - valor) * proporcion));
  return `rgb(${rgb.join(", ")})`;
};
const agrupar = (rows, campoCodigo, normalizar, numerador, denominador) => {
  const totales = new Map();
  rows.forEach((row) => {
    const codigo = normalizar(row[campoCodigo]);
    const total = totales.get(codigo) ?? { numerador: 0, denominador: 0 };
    total.numerador += Number(row[numerador]);
    total.denominador += Number(row[denominador]);
    totales.set(codigo, total);
  });
  return new Map(
    [...totales].map(([codigo, total]) => [
      codigo,
      total.denominador ? (100 * total.numerador) / total.denominador : 0,
    ]),
  );
};

export function render({
  rows,
  numerador,
  denominador,
  geojson,
  nombres,
  campoCodigo,
  normalizar,
  etiqueta,
  clase,
}) {
  cargarEstilo();
  const valores = agrupar(
    rows,
    campoCodigo,
    normalizar,
    numerador,
    denominador,
  );
  const extremos = [...valores.values()];
  const minimo = extremos.length ? Math.min(...extremos) : 0;
  const maximo = extremos.length ? Math.max(...extremos) : 0;
  const puntos = geojson.features.map((feature) => {
    const codigo = normalizar(feature.properties.codigo);
    return {
      ...feature,
      properties: {
        ...feature.properties,
        porcentaje: valores.get(codigo) ?? 0,
        territorio: nombres.get(codigo) ?? codigo,
      },
    };
  });
  const tarjeta = document.createElement("div");
  tarjeta.className = `porcentaje_territorios ${clase}`;
  const cabecera = document.createElement("div");
  cabecera.className = "cabecera";
  cabecera.innerHTML = `<div class="etiqueta">${etiqueta}</div><div class="leyenda"><span class="minimo"></span><span class="barra"></span><span class="maximo"></span></div>`;
  const grafico = document.createElement("div");
  tarjeta.append(cabecera, grafico);
  const estilos = getComputedStyle(document.documentElement);
  const color = estilos.getPropertyValue("--muted").trim();
  const fondo = estilos.getPropertyValue("--background").trim();
  const tinta = estilos.getPropertyValue("--ink").trim();
  const rango = [mezclar(fondo, tinta, 0.12), mezclar(fondo, tinta, 0.65)];
  cabecera.querySelector(".minimo").textContent = formatear(minimo);
  cabecera.querySelector(".maximo").textContent = formatear(maximo);
  cabecera.querySelector(".barra").style.background =
    `linear-gradient(to right, ${rango[0]}, ${rango[1]})`;
  const dominio = minimo === maximo ? [minimo, minimo + 1] : [minimo, maximo];
  const dibujar = (ancho) => {
    if (ancho <= 0) return;
    grafico.replaceChildren(
      Plot.plot({
        width: Math.floor(ancho),
        height: Math.min(520, Math.max(280, Math.floor(ancho * 0.75))),
        projection: { type: "mercator", domain: geojson },
        color: { domain: dominio, range: rango },
        marks: [
          Plot.geo(geojson, {
            fill: (feature) =>
              valores.get(normalizar(feature.properties.codigo)) ?? 0,
            stroke: color,
            strokeOpacity: 0.35,
            strokeWidth: 0.35,
          }),
          Plot.geo(
            geojson,
            Plot.pointer(
              Plot.centroid({
                stroke: fondo,
                strokeOpacity: 0.8,
                strokeWidth: 1,
              }),
            ),
          ),
          Plot.text(
            puntos,
            Plot.pointer({
              px: (d) => d.properties.centroid[0],
              py: (d) => d.properties.centroid[1],
              text: (punto) => formatear(punto.properties.porcentaje),
              frameAnchor: "top-right",
              fill: tinta,
              fontSize: 12,
              dy: 10,
            }),
          ),
          Plot.text(
            puntos,
            Plot.pointer({
              px: (d) => d.properties.centroid[0],
              py: (d) => d.properties.centroid[1],
              text: (punto) => punto.properties.territorio,
              frameAnchor: "top-right",
              fill: color,
              fontSize: 12,
              dy: 28,
              textOverflow: "ellipsis",
              lineWidth: 12,
            }),
          ),
        ],
      }),
    );
  };
  new ResizeObserver((entries) =>
    dibujar(entries[0].contentRect.width),
  ).observe(tarjeta);
  return tarjeta;
}
