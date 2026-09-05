const decimal = valor => valor.toLocaleString("es-BO", {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

export const layout = { minWidth: 375, minHeight: 175 };

export async function render({ rows, dimension, campo, observaciones, estadistico, filtroCampo = "estadistico", filtroValor, version = "" }) {
  const { crearGraficoEdad } = await import(`./comun/grafico_edad.js${version ? `?v=${version}` : ""}`);
  const filtro = filtroValor ?? estadistico;
  const datos = filtro ? rows.filter(row => row[filtroCampo] === filtro) : rows;
  const edades = new Map();
  datos.forEach(row => {
    const edad = Number(row[dimension]);
    const total = edades.get(edad) ?? { suma: 0, cantidad: 0 };
    const cantidad = Number(row[observaciones]);
    total.suma += Number(row[campo]) * cantidad;
    total.cantidad += cantidad;
    edades.set(edad, total);
  });
  const valores = [...edades].map(([edad, total]) => ({
    edad,
    valor: total.cantidad ? total.suma / total.cantidad : 0,
  })).sort((a, b) => a.edad - b.edad);
  return crearGraficoEdad({ datos: valores, formatear: decimal });
}
