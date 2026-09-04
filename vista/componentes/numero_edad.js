const entero = valor => valor.toLocaleString("es-BO", { maximumFractionDigits: 0 });

export const layout = { minWidth: 375, minHeight: 175 };

export async function render({ rows, dimension, campo, version = "" }) {
  const { crearGraficoEdad } = await import(`./comun/grafico_edad.js${version ? `?v=${version}` : ""}`);
  const edades = new Map();
  rows.forEach(row => {
    const edad = Number(row[dimension]);
    edades.set(edad, (edades.get(edad) ?? 0) + Number(row[campo]));
  });
  const datos = [...edades].map(([edad, valor]) => ({ edad, valor })).sort((a, b) => a.edad - b.edad);
  return crearGraficoEdad({ datos, formatear: entero });
}
