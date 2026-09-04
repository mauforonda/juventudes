const Plot =
  await import("https://cdn.jsdelivr.net/npm/@observablehq/plot@0.6.17/+esm");

const porcentaje = (valor) =>
  `${valor.toLocaleString("es-BO", {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  })}%`;

const estilo = `
  .porcentaje-categorias {
    display: flex;
    flex-direction: column;
    gap: 10px;
    max-height: 305px;
    overflow: scroll;
    scrollbar-width: none;
    -ms-overflow-style: none;
  }

  .porcentaje-categorias::-webkit-scrollbar {
    display: none;
  }
  .porcentaje-categorias svg {
    display: block;
    width: 100%;
    height: auto;
  }

  .porcentaje-categorias .etiqueta {
    color: var(--muted);
    font-size: 12px;
  }
`;

let estiloCargado = false;

function cargarEstilo() {
  if (estiloCargado) return;
  document
    .querySelectorAll('style[data-componente="porcentaje-categorias"]')
    .forEach((elemento) => elemento.remove());
  const elemento = document.createElement("style");
  elemento.dataset.componente = "porcentaje-categorias";
  elemento.textContent = estilo;
  document.head.append(elemento);
  estiloCargado = true;
}

const html = (contenido) => {
  const plantilla = document.createElement("template");
  plantilla.innerHTML = contenido.trim();
  return plantilla.content.firstElementChild;
};

const plantilla = () => `
  <div class="porcentaje-categorias">
    <div class="etiqueta"></div>
    <div class="grafico"></div>
  </div>
`;

export const layout = { minWidth: 300, minHeight: 100 };

export function render({ rows, dimension, numerador, denominador }) {
  cargarEstilo();
  const tarjeta = html(plantilla());
  tarjeta.querySelector(".etiqueta").textContent = `por ${String(dimension)
    .replaceAll("_", " ")
    .toLocaleLowerCase("es-BO")}`;
  const grafico = tarjeta.querySelector(".grafico");
  const color = getComputedStyle(document.documentElement)
    .getPropertyValue("--muted")
    .trim();
  const datosPorCategoria = new Map();

  rows.forEach((row) => {
    const categoria = String(row[dimension] ?? "");
    const total = datosPorCategoria.get(categoria) ?? {
      numerador: 0,
      denominador: 0,
    };
    total.numerador += Number(row[numerador]) || 0;
    total.denominador += Number(row[denominador]) || 0;
    datosPorCategoria.set(categoria, total);
  });

  const datos = [...datosPorCategoria].map(([categoria, total]) => ({
    categoria,
    etiqueta: categoria.replaceAll("_", " "),
    valor: total.denominador ? (100 * total.numerador) / total.denominador : 0,
  }));

  const dibujar = (ancho) => {
    if (ancho <= 0 || !datos.length) return;
    const plot = Plot.plot({
      width: Math.floor(ancho),
      height: Math.max(100, datos.length * 40),
      marginTop: 18,
      marginBottom: 0,
      marginLeft: 0,
      marginRight: 0,
      insetRight: 52,
      x: { axis: null },
      y: { axis: null, padding: 0.3 },
      style: { color },
      marks: [
        Plot.gridX({
          ticks: 4,
          strokeOpacity: 0.8,
          strokeDasharray: "1,2",
          strokeWidth: 0.5,
        }),
        Plot.axisX({
          anchor: "top",
          tickSize: 0,
          label: null,
          ticks: 4,
          tickFormat: (d) => (d == 0 ? "" : porcentaje(d)),
        }),
        Plot.barX(datos, {
          y: "categoria",
          x: "valor",
          insetTop: 10,
          fill: color,
          fillOpacity: 0.2,
          sort: {
            y: "-x",
          },
        }),
        Plot.barX(
          datos,
          Plot.pointerY({
            y: "categoria",
            x: "valor",
            insetTop: 10,
            fill: color,
            fillOpacity: 0.8,
          }),
        ),
        Plot.text(datos, {
          x: 0,
          y: "categoria",
          text: "etiqueta",
          textAnchor: "start",
          fillOpacity: 0.8,
          dx: 4,
          dy: -13,
          fill: color,
          fontSize: 12,
        }),
        Plot.text(
          datos,
          Plot.pointerY({
            x: 0,
            y: "categoria",
            text: "etiqueta",
            textAnchor: "start",
            fillOpacity: 0.8,
            dx: 4,
            dy: -13,
            fill: color,
            fontSize: 12,
          }),
        ),
        Plot.text(
          datos,
          Plot.pointerY({
            x: "valor",
            y: "categoria",
            text: (d) => porcentaje(d.valor),
            textAnchor: "start",
            lineAnchor: "top",
            dx: 5,
            fill: color,
            fontSize: 12,
          }),
        ),
      ],
    });
    grafico.replaceChildren(plot);
  };

  const observer = new ResizeObserver((entries) =>
    dibujar(entries[0].contentRect.width),
  );
  observer.observe(tarjeta);
  return tarjeta;
}
