export const layout = { minWidth: 360, minHeight: 310 };

export async function render({
  rows,
  categoria,
  numerador,
  denominador,
  formatear,
  version = "",
}) {
  const [{ render: crearMapa }, { crearMenu }] = await Promise.all([
    import(`./porcentaje_departamentos.js${version ? `?v=${version}` : ""}`),
    import(`./comun/menu_categoria.js${version ? `?v=${version}` : ""}`),
  ]);
  const totales = new Map();
  rows.forEach(row => {
    const valor = String(row[categoria] ?? "");
    const total = totales.get(valor) ?? { numerador: 0, denominador: 0 };
    total.numerador += Number(row[numerador]) || 0;
    total.denominador += Number(row[denominador]) || 0;
    totales.set(valor, total);
  });
  const categorias = [...totales]
    .sort(([, a], [, b]) => {
      const porcentajeA = a.denominador ? a.numerador / a.denominador : 0;
      const porcentajeB = b.denominador ? b.numerador / b.denominador : 0;
      return porcentajeB - porcentajeA;
    })
    .map(([valor]) => valor);

  const crearTarjeta = async valorCategoria => {
    const tarjeta = await crearMapa({
      rows: rows.filter(row => String(row[categoria] ?? "") === valorCategoria),
      numerador,
      denominador,
      formatear,
      version,
    });
    tarjeta.classList.add("porcentaje-departamento-categoria");
    const menu = crearMenu({
      opciones: categorias.map(opcion => ({
        valor: opcion,
        texto: opcion.replaceAll("_", " "),
      })),
      valor: {
        valor: valorCategoria,
        texto: valorCategoria.replaceAll("_", " "),
      },
      ariaLabel: `Seleccionar ${categoria}`,
      alSeleccionar: async opcion => tarjeta.replaceWith(await crearTarjeta(opcion)),
    });
    tarjeta.querySelector(".cabecera").before(menu);
    return tarjeta;
  };

  return crearTarjeta(categorias[0]);
}
