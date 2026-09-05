const Plot =
  await import("https://cdn.jsdelivr.net/npm/@observablehq/plot@0.6.17/+esm");

const porcentaje = (valor) =>
  `${valor.toLocaleString("es-BO", {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  })}%`;

const estilo = `
  .porcentaje-subcategoria {
    display: flex;
    flex-direction: column;
    gap: 10px;
    max-height: 380px;
    overflow: scroll;
    scrollbar-width: none;
    -ms-overflow-style: none;
  }

  .porcentaje-subcategoria .cabecera {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
  }

  .porcentaje-subcategoria::-webkit-scrollbar {
    display: none;
  }

  .porcentaje-subcategoria svg {
    display: block;
    width: 100%;
    height: auto;
  }

  .porcentaje-subcategoria .etiqueta {
    color: var(--muted);
    font-size: 12px;
  }

  .porcentaje-subcategoria .leyenda {
    display: flex;
    flex-wrap: wrap;
    justify-content: flex-end;
    gap: 8px;
    color: var(--muted);
    font-size: 12px;
  }

  .porcentaje-subcategoria .leyenda-item {
    display: inline-flex;
    align-items: center;
    gap: 4px;
  }

  .porcentaje-subcategoria .swatch {
    width: 10px;
    height: 10px;
  }
`;

let estiloCargado = false;
let patronSiguiente = 0;

function cargarEstilo() {
  if (estiloCargado) return;
  document
    .querySelectorAll('style[data-componente="porcentaje-subcategoria"]')
    .forEach((elemento) => elemento.remove());
  const elemento = document.createElement("style");
  elemento.dataset.componente = "porcentaje-subcategoria";
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
  <div class="porcentaje-subcategoria">
    <div class="cabecera">
      <div class="etiqueta"></div>
      <div class="leyenda"></div>
    </div>
    <div class="grafico"></div>
  </div>
`;

export const layout = { minWidth: 300, minHeight: 180 };

export function render({
  rows,
  dimension,
  subdimension,
  numerador,
  denominador,
  formatear = porcentaje,
}) {
  cargarEstilo();
  const tarjeta = html(plantilla());
  tarjeta.querySelector(".etiqueta").textContent = `${String(dimension)
    .replaceAll("_", " ")
    .toLocaleLowerCase("es-BO")} por ${String(subdimension)
    .replaceAll("_", " ")
    .toLocaleLowerCase("es-BO")}`;
  const grafico = tarjeta.querySelector(".grafico");
  const estilos = getComputedStyle(document.documentElement);
  const colores = {
    muted: estilos.getPropertyValue("--accent").trim(),
    ink: estilos.getPropertyValue("--accent").trim(),
    texto: estilos.getPropertyValue("--muted").trim(),
  };
  const totales = new Map();
  const subcategorias = new Map();

  rows.forEach((row) => {
    const categoria = String(row[dimension] ?? "");
    const subcategoria = String(row[subdimension] ?? "");
    const clave = `${categoria}\u0000${subcategoria}`;
    const total = totales.get(clave) ?? { numerador: 0, denominador: 0 };
    total.numerador += Number(row[numerador]) || 0;
    total.denominador += Number(row[denominador]) || 0;
    totales.set(clave, total);
    if (!subcategorias.has(subcategoria))
      subcategorias.set(subcategoria, subcategorias.size);
  });
  const ordenSubcategorias = [...subcategorias.keys()].sort((a, b) => a.localeCompare(b, "es"));
  subcategorias.clear();
  ordenSubcategorias.forEach((valor, indice) => subcategorias.set(valor, indice));
  const leyenda = tarjeta.querySelector(".leyenda");
  [...subcategorias].forEach(([subcategoria, indice]) => {
    const item = html(
      `<span class="leyenda-item"><span class="swatch"></span><span></span></span>`,
    );
    item.lastElementChild.textContent = subcategoria.replaceAll("_", " ");
    const swatch = item.querySelector(".swatch");
    swatch.style.backgroundColor = colores.muted;
    swatch.style.opacity = "0.2";
    if (indice === 1) {
      swatch.style.backgroundColor = "transparent";
      swatch.style.opacity = "1";
      swatch.style.backgroundImage = `repeating-linear-gradient(135deg, transparent 0px, transparent 2px, color-mix(in srgb, ${colores.ink} 20%, transparent) 2px, color-mix(in srgb, ${colores.ink} 20%, transparent) 5px)`;
    }
    leyenda.append(item);
  });

  const datos = [...totales].map(([clave, total]) => {
    const [categoria, subcategoria] = clave.split("\u0000");
    return {
      categoria,
      etiqueta: categoria.replaceAll("_", " "),
      subcategoria,
      fila: clave,
      filaEtiqueta: `${categoria}\u0000__etiqueta`,
      valor: total.denominador
        ? (100 * total.numerador) / total.denominador
        : 0,
    };
  });
  const maximos = new Map();
  datos.forEach((dato) =>
    maximos.set(
      dato.categoria,
      Math.max(maximos.get(dato.categoria) ?? -Infinity, dato.valor),
    ),
  );
  const ordenCategorias = [...maximos]
    .sort(([, a], [, b]) => b - a)
    .map(([categoria]) => categoria);
  const etiquetas = ordenCategorias.map((categoria) =>
    datos.find((dato) => dato.categoria === categoria),
  );
  const ordenY = [];
  etiquetas.forEach((dato) => {
    ordenY.push(dato.filaEtiqueta);
    datos
      .filter((fila) => fila.categoria === dato.categoria)
      .sort((a, b) => subcategorias.get(a.subcategoria) - subcategorias.get(b.subcategoria))
      .forEach((fila) => ordenY.push(fila.fila));
  });

  const dibujar = (ancho) => {
    if (ancho <= 0 || !datos.length) return;
    const patronId = `porcentaje-subcategoria-patron-${patronSiguiente++}`;
    const color = (d) =>
      subcategorias.get(d.subcategoria) === 1
        ? `url(#${patronId})`
        : colores.muted;
    const barras = [...subcategorias].flatMap(([subcategoria]) => {
      const datosSubcategoria = datos.filter(
        (dato) => dato.subcategoria === subcategoria,
      );
      return [
        Plot.barX(datosSubcategoria, {
          y: "fila",
          x: "valor",
          insetTop: 2,
          fill: color,
          fillOpacity: 0.4,
        }),
        Plot.barX(
          datosSubcategoria,
          Plot.pointerY({
            y: "fila",
            x: "valor",
            fill: color,
            fillOpacity: 0.8,
            maxRadius: 12,
          }),
        ),
      ];
    });
    const plot = Plot.plot({
      width: Math.floor(ancho),
      height: Math.max(140, ordenY.length * 24),
      marginTop: 18,
      marginBottom: 0,
      marginLeft: 0,
      marginRight: 0,
      insetRight: 58,
      x: { axis: null },
      y: { axis: null, domain: ordenY, padding: 0.3 },
      style: { color: colores.texto },
      marks: [
        Plot.gridX({
          ticks: 3,
          strokeOpacity: 0.8,
          strokeDasharray: "1,2",
          strokeWidth: 0.5,
        }),
        Plot.axisX({
          anchor: "top",
          tickSize: 0,
          label: null,
          ticks: 3,
          tickFormat: (d) => (d == 0 ? "" : formatear(d)),
        }),
        ...barras,
        Plot.text(etiquetas, {
          x: 0,
          y: "filaEtiqueta",
          text: "etiqueta",
          textAnchor: "start",
          dx: 4,
          fill: colores.texto,
          fontSize: 12,
        }),
        Plot.text(
          datos,
          Plot.pointerY({
            x: "valor",
            y: "fila",
            text: (d) => formatear(d.valor),
            textAnchor: "start",
            dx: 5,
            fill: colores.texto,
            fontSize: 12,
          }),
        ),
      ],
    });
    plot.insertAdjacentHTML(
      "afterbegin",
      `
      <defs>
        <pattern id="${patronId}" width="6" height="6" patternUnits="userSpaceOnUse">
          <path d="M-1,1 l2,-2 M0,6 L6,0 M5,7 l2,-2"
            stroke="${colores.ink}" stroke-width="2" stroke-opacity="1" />
        </pattern>
      </defs>
    `,
    );
    grafico.replaceChildren(plot);
  };

  const observer = new ResizeObserver((entries) =>
    dibujar(entries[0].contentRect.width),
  );
  observer.observe(tarjeta);
  return tarjeta;
}
