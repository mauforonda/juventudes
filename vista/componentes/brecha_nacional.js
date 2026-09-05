const formatear = (valor) => valor.toLocaleString("es-BO", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });

export const layout = { minWidth: 120, minHeight: 55 };

export async function render({
  rows,
  sexo = "sexo",
  campo = "media",
  ponderador = "poblacion_estimada",
  campoHombres,
  campoMujeres,
  ponderadorHombres,
  ponderadorMujeres,
  version = "",
}) {
  const medias = rows.reduce(
    (totales, row) => {
      const campos = row[sexo]
        ? [{ categoria: row[sexo], campo, ponderador }]
        : [
            {
              categoria: "hombre",
              campo: campoHombres,
              ponderador: ponderadorHombres,
            },
            {
              categoria: "mujer",
              campo: campoMujeres,
              ponderador: ponderadorMujeres,
            },
          ];
      campos.forEach(
        ({ categoria, campo: nombreCampo, ponderador: nombrePonderador }) => {
          const valor = Number(row[nombreCampo]);
          const peso = Number(row[nombrePonderador]);
          if (!Number.isFinite(valor) || !Number.isFinite(peso) || peso <= 0)
            return;
          totales[categoria].suma += valor * peso;
          totales[categoria].peso += peso;
        },
      );
      return totales;
    },
    { hombre: { suma: 0, peso: 0 }, mujer: { suma: 0, peso: 0 } },
  );
  const hombre = medias.hombre.peso
    ? medias.hombre.suma / medias.hombre.peso
    : 0;
  const mujer = medias.mujer.peso ? medias.mujer.suma / medias.mujer.peso : 0;
  const brecha = hombre ? 100 * mujer / hombre : 0;
  const tarjeta = document.createElement("div");
  tarjeta.className = "brecha-nacional";
  tarjeta.innerHTML = `<div class="frase">Las mujeres ganan Bs. <span class="valor">${formatear(brecha)}</span> en promedio por cada 100 que ganan los hombres</div>`;
  return tarjeta;
}
