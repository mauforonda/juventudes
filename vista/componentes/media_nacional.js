const decimal = valor => valor.toLocaleString("es-BO", {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

export const layout = { minWidth: 100, minHeight: 55 };

export async function render({ rows, campo, observaciones, estadistico, filtroCampo = "estadistico", filtroValor, version = "" }) {
  const { crearTarjetaNumero } = await import(`./comun/tarjeta_numero.js${version ? `?v=${version}` : ""}`);
  const filtro = filtroValor ?? estadistico;
  const datos = filtro
    ? rows.filter(row => row[filtroCampo] === filtro)
    : rows;
  const totales = datos.reduce((total, row) => {
    const valor = Number(row[campo]);
    const cantidad = Number(row[observaciones]);
    return {
      suma: total.suma + valor * cantidad,
      cantidad: total.cantidad + cantidad,
    };
  }, { suma: 0, cantidad: 0 });
  const valor = totales.cantidad ? totales.suma / totales.cantidad : 0;
  return crearTarjetaNumero({ clase: "media_nacional", valor, etiqueta: "en promedio", formatear: decimal });
}
