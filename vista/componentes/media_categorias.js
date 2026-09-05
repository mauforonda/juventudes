export const layout = { minWidth: 300, minHeight: 140 };
export async function render({ rows, dimension, campo = "media", ponderador = "poblacion_estimada", filtroCampo, filtroValor, formato = "moneda", version = "" }) {
  const { render: crear } = await import(`./porcentaje_categorias.js${version ? `?v=${version}` : ""}`);
  const datos = rows.filter(row => !filtroValor || row[filtroCampo] === filtroValor).map(row => ({
    ...row,
    _numerador: (Number(row[campo]) || 0) * (Number(row[ponderador]) || 0) / 100,
    _denominador: Number(row[ponderador]) || 0,
  }));
  return crear({
    rows: datos,
    dimension,
    numerador: "_numerador",
    denominador: "_denominador",
    formatear: valor => formato === "porcentaje" ? `${valor.toLocaleString("es-BO", { maximumFractionDigits: 1 })}%` : formato === "moneda" ? `${valor.toLocaleString("es-BO", { maximumFractionDigits: 0 })} Bs.` : valor.toLocaleString("es-BO", { maximumFractionDigits: 1 }),
    version,
  });
}
