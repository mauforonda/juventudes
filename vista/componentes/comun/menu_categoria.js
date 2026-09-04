const estilo = `
  .menu-categoria {
    display: flex;
    justify-content: center;
  }

  .menu-categoria .selector {
    position: relative;
  }

  .menu-categoria .menu-trigger {
    max-width: 150px;
    padding: 5px 26px 5px 8px;
    border: 1px solid var(--line);
    border-radius: 6px;
    background: transparent;
    color: var(--muted);
    cursor: pointer;
    font: inherit;
    font-size: 12px;
  }

  .menu-categoria .menu-content {
    position: absolute;
    z-index: 4;
    top: calc(100% + 4px);
    left: 50%;
    display: grid;
    min-width: min(180px, calc(100vw - 32px));
    max-width: calc(100vw - 32px);
    max-height: 240px;
    padding: 4px;
    overflow-y: auto;
    border: 1px solid var(--line);
    border-radius: 8px;
    background: var(--background);
    box-shadow: 0 4px 12px color-mix(in srgb, var(--ink) 12%, transparent);
    transform: translateX(-50%);
  }

  .menu-categoria .menu-content[hidden] {
    display: none;
  }

  .menu-categoria .menu-option {
    padding: 6px 8px;
    border: 0;
    border-radius: 5px;
    background: transparent;
    color: var(--ink);
    font: inherit;
    font-size: 12px;
    text-align: left;
    cursor: pointer;
  }

  .menu-categoria .menu-option:hover,
  .menu-categoria .menu-option:focus-visible {
    outline: 0;
    background: var(--hover);
    color: var(--accent);
  }

  .menu-categoria .selector svg {
    position: absolute;
    top: 50%;
    right: 8px;
    width: 12px;
    height: 12px;
    pointer-events: none;
    fill: none;
    stroke: var(--muted);
    stroke-width: 1.5;
    transform: translateY(-50%);
  }
`;

let estiloCargado = false;

function cargarEstilo() {
  if (estiloCargado) return;
  const elemento = document.createElement("style");
  elemento.dataset.componente = "menu-categoria";
  elemento.textContent = estilo;
  document.head.append(elemento);
  estiloCargado = true;
}

const html = contenido => {
  const plantilla = document.createElement("template");
  plantilla.innerHTML = contenido.trim();
  return plantilla.content.firstElementChild;
};

export function crearMenu({ opciones, valor, ariaLabel, alSeleccionar }) {
  cargarEstilo();
  const fila = html(`
    <div class="menu-categoria">
      <div class="selector">
        <button type="button" class="menu-trigger" aria-haspopup="listbox" aria-expanded="false"></button>
        <div class="menu-content" role="listbox" hidden></div>
        <svg viewBox="0 0 16 16" aria-hidden="true"><path d="m4 6 4 4 4-4" /></svg>
      </div>
    </div>
  `);
  const trigger = fila.querySelector(".menu-trigger");
  const menu = fila.querySelector(".menu-content");
  trigger.setAttribute("aria-label", ariaLabel);
  trigger.textContent = valor.texto;
  opciones.forEach(opcion => {
    const item = document.createElement("button");
    item.type = "button";
    item.className = "menu-option";
    item.setAttribute("role", "option");
    item.setAttribute("aria-selected", String(opcion.valor === valor.valor));
    item.textContent = opcion.texto;
    item.addEventListener("click", () => alSeleccionar(opcion.valor));
    menu.append(item);
  });
  trigger.addEventListener("click", () => {
    menu.hidden = !menu.hidden;
    trigger.setAttribute("aria-expanded", String(!menu.hidden));
    if (!menu.hidden) menu.querySelector('[aria-selected="true"]')?.focus();
  });
  trigger.addEventListener("keydown", event => {
    if (event.key === "Escape") {
      menu.hidden = true;
      trigger.setAttribute("aria-expanded", "false");
    }
  });
  return fila;
}
