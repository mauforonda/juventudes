const porcentaje = (valor) =>
  `${valor.toLocaleString("es-BO", { minimumFractionDigits: 0, maximumFractionDigits: 2 })}%`;

export const layout = { minWidth: 375, minHeight: 175 };

export async function render({
  rows,
  dimension,
  numerador,
  denominador,
  version = "",
}) {
  const { crearGraficoEdad } = await import(
    `./comun/grafico_edad.js${version ? `?v=${version}` : ""}`
  );
  const edades = new Map();
  rows.forEach((row) => {
    const edad = Number(row[dimension]);
    const total = edades.get(edad) ?? { numerador: 0, denominador: 0 };
    total.numerador += Number(row[numerador]);
    total.denominador += Number(row[denominador]);
    edades.set(edad, total);
  });
  const datos = [...edades]
    .map(([edad, total]) => ({
      edad,
      valor: total.denominador
        ? (100 * total.numerador) / total.denominador
        : 0,
    }))
    .sort((a, b) => a.edad - b.edad);
  return crearGraficoEdad({ datos, formatear: porcentaje });
}
