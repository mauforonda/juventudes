export const layout = { minWidth: 300, minHeight: 100 };
export async function render({ rows, dimension, version = "" }) {
  const { render: crear } = await import(`./porcentaje_categorias.js${version ? `?v=${version}` : ""}`);
  const datos = rows.map(row => ({ ...row, _numerador: 100 * (Number(row.media_mujeres) || 0) / (Number(row.media_hombres) || 1), _denominador: 100 }));
  return crear({ rows: datos, dimension, numerador: "_numerador", denominador: "_denominador", formatear: valor => `${valor.toLocaleString("es-BO", { maximumFractionDigits: 2 })} Bs.`, regla: 100 });
}
