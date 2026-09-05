const Plot =
  await import("https://cdn.jsdelivr.net/npm/@observablehq/plot@0.6.17/+esm");

const estilo = `
  .grafico-edad svg {
    display: block;
    width: 100%;
    height: auto;
  }

  .grafico-edad .etiqueta,
  .grafico-edad .seleccion_edad {
    color: var(--muted);
    font-size: 12px;
  }

  .grafico-edad .cabecera {
    display: flex;
    justify-content: space-between;
    gap: 10px;
  }

  .grafico-edad .seleccion {
    display: flex;
    text-align: right;
    min-height: 35px;
    flex-direction: column;
  }

  .grafico-edad .seleccion_valor {
    font-size: 12px;
  }
`;

let estiloCargado = false;

function cargarEstilo() {
  if (estiloCargado) return;
  document
    .querySelectorAll('style[data-componente="grafico-edad"]')
    .forEach((elemento) => elemento.remove());
  const elemento = document.createElement("style");
  elemento.dataset.componente = "grafico-edad";
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
  <div class="grafico-edad">
    <div class="cabecera">
      <div class="etiqueta">por edades</div>
      <div class="seleccion">
        <div class="seleccion_valor"></div>
        <div class="seleccion_edad"></div>
      </div>
    </div>
    <div class="grafico"></div>
  </div>
`;

export function crearGraficoEdad({
  datos,
  formatear,
  formatearEje = formatear,
  regla,
}) {
  cargarEstilo();
  const tarjeta = html(plantilla());
  const grafico = tarjeta.querySelector(".grafico");
  const seleccionEdad = tarjeta.querySelector(".seleccion_edad");
  const seleccionValor = tarjeta.querySelector(".seleccion_valor");
  const color = getComputedStyle(document.documentElement)
    .getPropertyValue("--muted")
    .trim();

  const dibujar = (ancho) => {
    if (ancho <= 0 || !datos.length) return;
    const ultimo = datos.at(-1);
    const linea = [...datos, { edad: ultimo.edad + 0.9, valor: ultimo.valor }];
    const plot = Plot.plot({
      width: Math.floor(ancho),
      height: 140,
      marginTop: 5,
      marginBottom: 20,
      marginLeft: 0,
      marginRight: 0,
      insetRight: 50,
      x: { axis: null },
      y: { axis: null },
      style: { color },
      marks: [
        ...(regla == null ? [] : [Plot.ruleY([regla], { stroke: color, strokeOpacity: 0.45, strokeDasharray: "3,3" })]),
        Plot.ruleY([0], {
          x1: 16,
          x2: 29,
          stroke: color,
          strokeOpacity: 0.5,
          strokeWidth: 1,
        }),
        Plot.gridY({
          filter: (d) => d != 0,
          ticks: 2,
          strokeOpacity: 0.8,
          strokeDasharray: "1,2",
          strokeWidth: 0.5,
        }),
        Plot.axisY({
          tickSize: 0,
          label: null,
          ticks: 2,
          tickFormat: (d) => (d == 0 ? "" : formatearEje(d)),
          anchor: "right",
          textAnchor: "right",
          lineAnchor: "top",
          dx: -30,
          dy: 5,
        }),
        Plot.axisX({
          tickSize: 0,
          label: null,
          domain: [16, 29],
          ticks: [16.5, 28.5],
          tickFormat: (d) => Math.floor(d),
          textAnchor: "left",
        }),
        Plot.rectY(datos, {
          x: "edad",
          y: "valor",
          interval: 1,
          fill: color,
          fillOpacity: 0.2,
          insetLeft: 1,
          insetRight: 1,
        }),
        Plot.rectY(
          datos,
          Plot.pointerX({
            x: "edad",
            y: "valor",
            interval: 1,
            fill: color,
            fillOpacity: 0.8,
            insetLeft: 1,
            insetRight: 1,
          }),
        ),
        Plot.line(linea, {
          x: "edad",
          y: "valor",
          stroke: color,
          strokeOpacity: 0.8,
          strokeWidth: 2,
          curve: "step-after",
        }),
      ],
    });
    plot.addEventListener("input", () => {
      seleccionEdad.textContent = plot.value ? `${String(plot.value.edad)} años` : "";
      seleccionValor.textContent = plot.value
        ? formatear(plot.value.valor)
        : "";
    });
    grafico.replaceChildren(plot);
  };

  const observer = new ResizeObserver((entries) =>
    dibujar(entries[0].contentRect.width),
  );
  observer.observe(tarjeta);
  return tarjeta;
}
