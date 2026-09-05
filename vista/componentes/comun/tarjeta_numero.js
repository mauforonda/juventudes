const estilo = `
  .tarjeta-numero {
    display: grid;
  }

  .tarjeta-numero .numero {
    font-size: 2rem;
    font-weight: 500;
    line-height: 1.2;
    color: var(--accent);
  }

  .tarjeta-numero .etiqueta {
    color: var(--muted);
    font-size: 12px;
  }
`;

let estiloCargado = false;

function cargarEstilo() {
  if (estiloCargado) return;
  document.querySelectorAll('style[data-componente="tarjeta-numero"]')
    .forEach(elemento => elemento.remove());
  const elemento = document.createElement("style");
  elemento.dataset.componente = "tarjeta-numero";
  elemento.textContent = estilo;
  document.head.append(elemento);
  estiloCargado = true;
}

export function crearTarjetaNumero({ clase, valor, etiqueta, formatear }) {
  cargarEstilo();
  const tarjeta = document.createElement("div");
  tarjeta.className = `tarjeta-numero ${clase}`;
  tarjeta.innerHTML = `
    <div class="numero">${formatear(valor)}</div>
    <div class="etiqueta">${etiqueta}</div>`;
  return tarjeta;
}
