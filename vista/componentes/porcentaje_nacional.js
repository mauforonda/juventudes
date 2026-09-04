const porcentaje = valor => `${valor.toLocaleString("es-BO", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}%`;

export const layout = { minWidth: 55, minHeight: 55 };

export async function render({ rows, numerador, denominador, version = "" }) {
  const { crearTarjetaNumero } = await import(`./comun/tarjeta_numero.js${version ? `?v=${version}` : ""}`);
  const totales = rows.reduce((total, row) => ({
    numerador: total.numerador + Number(row[numerador]),
    denominador: total.denominador + Number(row[denominador]),
  }), { numerador: 0, denominador: 0 });
  const valor = totales.denominador ? 100 * totales.numerador / totales.denominador : 0;
  return crearTarjetaNumero({ clase: "porcentaje_nacional", valor, etiqueta: "a nivel nacional", formatear: porcentaje });
}
