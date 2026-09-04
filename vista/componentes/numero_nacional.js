const entero = valor => valor.toLocaleString("es-BO", { maximumFractionDigits: 0 });

export const layout = { minWidth: 55, minHeight: 55 };

export async function render({ rows, campo, version = "" }) {
  const { crearTarjetaNumero } = await import(`./comun/tarjeta_numero.js${version ? `?v=${version}` : ""}`);
  const valor = rows.reduce((total, row) => total + Number(row[campo]), 0);
  return crearTarjetaNumero({ clase: "numero_nacional", valor, etiqueta: "a nivel nacional", formatear: entero });
}
