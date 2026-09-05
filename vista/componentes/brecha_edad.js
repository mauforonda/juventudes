const porcentaje = v => `${v.toLocaleString("es-BO", { maximumFractionDigits: 2 })} Bs.`;
export const layout = { minWidth: 375, minHeight: 175 };
export async function render({ rows, dimension = "edad", categoria = "area", version = "" }) {
  const [{ crearGraficoEdad }, { crearMenu }] = await Promise.all([
    import(`./comun/grafico_edad.js${version ? `?v=${version}` : ""}`),
    import(`./comun/menu_categoria.js${version ? `?v=${version}` : ""}`),
  ]);
  const categorias = [...new Set(rows.map(row => String(row[categoria] ?? "")))].filter(Boolean).sort();
  const crearTarjeta = valorCategoria => {
    const grupos = new Map();
    rows.filter(row => String(row[categoria] ?? "") === valorCategoria).forEach(row => {
    const grupo = grupos.get(row[dimension]) ?? { h: [0, 0], m: [0, 0] };
    const h = Number(row.poblacion_hombres) || 0, m = Number(row.poblacion_mujeres) || 0;
    grupo.h[0] += (Number(row.media_hombres) || 0) * h; grupo.h[1] += h;
    grupo.m[0] += (Number(row.media_mujeres) || 0) * m; grupo.m[1] += m; grupos.set(row[dimension], grupo);
    });
    const datos = [...grupos].map(([edad, g]) => ({ edad: Number(edad), valor: g.h[1] && g.m[1] ? 100 * (g.m[0] / g.m[1]) / (g.h[0] / g.h[1]) : 0 })).sort((a,b) => a.edad-b.edad);
    const tarjeta = crearGraficoEdad({ datos, formatear: porcentaje, regla: 100 });
    const menu = crearMenu({ opciones: categorias.map(opcion => ({ valor: opcion, texto: opcion.replaceAll("_", " ") })), valor: { valor: valorCategoria, texto: valorCategoria.replaceAll("_", " ") }, ariaLabel: `Seleccionar ${categoria}`, alSeleccionar: opcion => tarjeta.replaceWith(crearTarjeta(opcion)) });
    tarjeta.querySelector(".cabecera").before(menu);
    return tarjeta;
  };
  return crearTarjeta(categorias[0]);
}
