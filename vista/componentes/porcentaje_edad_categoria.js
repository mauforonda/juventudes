const porcentaje = valor => `${valor.toLocaleString("es-BO", {
  minimumFractionDigits: 0,
  maximumFractionDigits: 2,
})}%`;

export const layout = { minWidth: 375, minHeight: 175 };

export async function render({
  rows,
  dimension,
  categoria,
  numerador,
  denominador,
  formatearCategoria = valor => valor.replaceAll("_", " "),
  version = "",
}) {
  const { crearGraficoEdad } = await import(
    `./comun/grafico_edad.js${version ? `?v=${version}` : ""}`
  );
  const { crearMenu } = await import(
    `./comun/menu_categoria.js${version ? `?v=${version}` : ""}`
  );
  const distribuciones = new Map();
  rows.forEach(row => {
    const valorCategoria = String(row[categoria] ?? "");
    const total = distribuciones.get(valorCategoria) ?? {
      numerador: 0,
      denominador: 0,
      edades: new Map(),
    };
    const numeradorFila = Number(row[numerador]) || 0;
    const denominadorFila = Number(row[denominador]) || 0;
    total.numerador += numeradorFila;
    total.denominador += denominadorFila;
    const edad = Number(row[dimension]);
    const edadTotal = total.edades.get(edad) ?? { numerador: 0, denominador: 0 };
    edadTotal.numerador += numeradorFila;
    edadTotal.denominador += denominadorFila;
    total.edades.set(edad, edadTotal);
    distribuciones.set(valorCategoria, total);
  });

  const categorias = [...distribuciones]
    .sort(([, a], [, b]) => {
      const porcentajeA = a.denominador ? a.numerador / a.denominador : 0;
      const porcentajeB = b.denominador ? b.numerador / b.denominador : 0;
      return porcentajeB - porcentajeA;
    })
    .map(([valor]) => valor);

  const crearTarjeta = async valorCategoria => {
    const total = distribuciones.get(valorCategoria);
    const datos = [...total.edades]
      .map(([edad, valores]) => ({
        edad,
        valor: valores.denominador
          ? (100 * valores.numerador) / valores.denominador
          : 0,
      }))
      .sort((a, b) => a.edad - b.edad);
    const tarjeta = await crearGraficoEdad({ datos, formatear: porcentaje });
    tarjeta.classList.add("porcentaje-edad-categoria");
    const menu = crearMenu({
      opciones: categorias.map(opcion => ({
        valor: opcion,
        texto: formatearCategoria(opcion),
      })),
      valor: {
        valor: valorCategoria,
        texto: formatearCategoria(valorCategoria),
      },
      ariaLabel: `Seleccionar ${categoria}`,
      alSeleccionar: async opcion => tarjeta.replaceWith(await crearTarjeta(opcion)),
    });
    tarjeta.querySelector(".cabecera").before(menu);
    return tarjeta;
  };

  return crearTarjeta(categorias[0]);
}
