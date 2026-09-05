export const layout = { minWidth: 360, minHeight: 310 };
export async function render({ rows, categoria = "area", version = "" }) {
  const [{ render: crear }, { crearMenu }] = await Promise.all([
    import(`./porcentaje_departamentos.js${version ? `?v=${version}` : ""}`),
    import(`./comun/menu_categoria.js${version ? `?v=${version}` : ""}`),
  ]);
  const categorias = [...new Set(rows.map(row => String(row[categoria] ?? "")))].filter(Boolean).sort();
  const crearTarjeta = async valorCategoria => {
    const grupos = new Map();
    rows.filter(row => String(row[categoria] ?? "") === valorCategoria).forEach(row => {
      const grupo = grupos.get(row.codigo_departamento) ?? { mujeres: 0, hombres: 0 };
      grupo.mujeres += (Number(row.media_mujeres) || 0) * (Number(row.poblacion_mujeres) || 0);
      grupo.hombres += (Number(row.media_hombres) || 0) * (Number(row.poblacion_hombres) || 0);
      grupos.set(row.codigo_departamento, grupo);
    });
    const datos = [...grupos].map(([codigo_departamento, grupo]) => ({ codigo_departamento, _numerador: grupo.mujeres, _denominador: grupo.hombres }));
    const tarjeta = await crear({ rows: datos, numerador: "_numerador", denominador: "_denominador", version, formatear: valor => `${valor.toLocaleString("es-BO", { maximumFractionDigits: 2 })} Bs.` });
    const menu = crearMenu({ opciones: categorias.map(opcion => ({ valor: opcion, texto: opcion.replaceAll("_", " ") })), valor: { valor: valorCategoria, texto: valorCategoria.replaceAll("_", " ") }, ariaLabel: `Seleccionar ${categoria}`, alSeleccionar: async opcion => tarjeta.replaceWith(await crearTarjeta(opcion)) });
    tarjeta.querySelector(".cabecera").before(menu);
    return tarjeta;
  };
  return crearTarjeta(categorias[0]);
}
