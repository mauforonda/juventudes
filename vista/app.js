import { cargarComponente } from "./componentes/registro.js";

const RAW_ROOT = "https://raw.githubusercontent.com/mauforonda/juventudes/refs/heads/main/";
const INDEX_URL = "indice.json";
const MUNICIPALITIES_URL = `${RAW_ROOT}diccionarios/municipios.csv`;
const BATCH_SIZE = 30;
const TABLE_BATCH_SIZE = 60;

const input = document.querySelector("#search input");
const clearButton = document.querySelector("#search button");
const searchBox = document.querySelector("#search");
const catalogue = document.querySelector("#catalogue");
const groups = document.querySelector("#groups");
const list = document.querySelector("#datasets");
const empty = document.querySelector("#empty");
const catalogueSentinel = document.querySelector("#catalogue-sentinel");

let indicators = [];
let filtered = [];
let shown = 0;
let municipalityMaps = { municipalities: new Map(), departments: new Map() };
let datasetActivo = null;
let grupoActivo = null;

const normalize = value => String(value ?? "")
  .normalize("NFD")
  .replace(/[\u0300-\u036f]/g, "")
  .toLocaleLowerCase("es");

function parseCsv(text) {
  const rows = [[]];
  let value = "";
  let quoted = false;

  for (let index = 0; index < text.length; index += 1) {
    const character = text[index];
    if (character === '"' && quoted && text[index + 1] === '"') {
      value += '"';
      index += 1;
    } else if (character === '"') {
      quoted = !quoted;
    } else if (character === "," && !quoted) {
      rows.at(-1).push(value);
      value = "";
    } else if ((character === "\n" || character === "\r") && !quoted) {
      if (character === "\r" && text[index + 1] === "\n") index += 1;
      rows.at(-1).push(value);
      value = "";
      rows.push([]);
    } else {
      value += character;
    }
  }
  rows.at(-1).push(value);
  return rows.filter(row => row.some(cell => cell !== ""));
}

function formatValue(value, column) {
  const clean = String(value ?? "").trim();
  if (!clean) return "—";
  if (column === "codigo_municipio") {
    return municipalityMaps.municipalities.get(clean) ?? clean;
  }
  if (column === "departamento" || column === "codigo_departamento") {
    return municipalityMaps.departments.get(clean) ?? clean;
  }
  if (/^-?\d+\.\d+$/.test(clean)) {
    return Number(clean).toLocaleString("es-BO", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
  }
  return clean;
}

async function fetchChecked(url, type = "text") {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`No se pudo cargar ${url} (${response.status})`);
  return type === "json" ? response.json() : response.text();
}

async function loadMunicipalityMaps() {
  const rows = parseCsv(await fetchChecked(MUNICIPALITIES_URL));
  const [headers, ...values] = rows;
  const position = Object.fromEntries(headers.map((header, index) => [header, index]));
  const municipalities = new Map();
  const departments = new Map();

  values.forEach(row => {
    municipalities.set(row[position.codigo_municipio], row[position.municipio]);
    departments.set(row[position.codigo_departamento], row[position.departamento]);
    departments.set(row[position.departamento], row[position.departamento]);
  });
  municipalityMaps = { municipalities, departments };
}

function metadataMarkup(ficha) {
  const fields = [
    ["Objetivo", ficha.objetivo],
    ["Población objetivo", ficha.poblacion_objetivo],
    ["Descripción operativa", ficha.descripcion_operativa],
    ["Unidad de medida", ficha.unidad_medida],
  ];
  const dl = document.createElement("dl");
  dl.className = "metadata-grid";
  fields.forEach(([label, value]) => {
    const item = document.createElement("div");
    const dt = document.createElement("dt");
    const dd = document.createElement("dd");
    dt.textContent = label;
    dd.textContent = value || "—";
    item.append(dt, dd);
    dl.append(item);
  });
  return dl;
}

function descargarCsv(rows, slug) {
  const csv = rows.map(row => row.map(value => {
    const clean = String(value ?? "");
    return /[",\n\r]/.test(clean) ? `"${clean.replaceAll('"', '""')}"` : clean;
  }).join(",")).join("\r\n");
  const url = URL.createObjectURL(new Blob(["\ufeff", csv], { type: "text/csv;charset=utf-8" }));
  const enlace = document.createElement("a");
  enlace.href = url;
  enlace.download = `${slug}.csv`;
  enlace.click();
  setTimeout(() => URL.revokeObjectURL(url), 0);
}

function resultsTable(rows, fieldDescriptions = {}, slug) {
  const [headers = [], ...values] = rows;
  const section = document.createElement("section");
  section.className = "results-section";

  const wrapper = document.createElement("div");
  wrapper.className = "table-wrap";
  wrapper.tabIndex = 0;
  wrapper.setAttribute("role", "region");
  wrapper.setAttribute("aria-label", "Tabla de resultados");
  const table = document.createElement("table");
  const thead = document.createElement("thead");
  const headerRow = document.createElement("tr");
  headers.forEach(header => {
    const th = document.createElement("th");
    th.scope = "col";
    th.textContent = header.replaceAll("_", " ");
    if (fieldDescriptions[header]) th.title = fieldDescriptions[header];
    headerRow.append(th);
  });
  thead.append(headerRow);
  const tbody = document.createElement("tbody");
  const sentinelRow = document.createElement("tr");
  sentinelRow.className = "table-sentinel";
  const sentinelCell = document.createElement("td");
  sentinelCell.colSpan = Math.max(headers.length, 1);
  sentinelRow.append(sentinelCell);
  tbody.append(sentinelRow);
  table.append(thead, tbody);
  wrapper.append(table);
  section.append(wrapper);
  const download = document.createElement("button");
  download.className = "download-button";
  download.type = "button";
  download.textContent = "descarga";
  download.addEventListener("click", () => descargarCsv(rows, slug));
  section.append(download);

  let rowIndex = 0;
  const renderRows = () => {
    const fragment = document.createDocumentFragment();
    values.slice(rowIndex, rowIndex + TABLE_BATCH_SIZE).forEach(row => {
      const tr = document.createElement("tr");
      headers.forEach((header, columnIndex) => {
        const td = document.createElement("td");
        td.textContent = formatValue(row[columnIndex], header);
        tr.append(td);
      });
      fragment.append(tr);
    });
    rowIndex = Math.min(rowIndex + TABLE_BATCH_SIZE, values.length);
    tbody.insertBefore(fragment, sentinelRow);
    sentinelRow.hidden = rowIndex >= values.length;
  };

  const observer = new IntersectionObserver(entries => {
    if (entries[0].isIntersecting && rowIndex < values.length) renderRows();
  }, { root: wrapper, rootMargin: "0px 0px 160px" });
  observer.observe(sentinelRow);
  renderRows();
  return section;
}

async function visualizations(config, rows, version = "") {
  if (!config) return null;
  const section = document.createElement("section");
  section.className = "visualizations";
  for (const definition of config) {
    const modulo = await cargarComponente(definition.tipo, version);
    const component = document.createElement("article");
    component.className = "visualization";
    if (modulo.layout) {
      component.style.minWidth = `${modulo.layout.minWidth}px`;
      component.style.minHeight = `${modulo.layout.minHeight}px`;
    }
    component.append(await modulo.render({ rows, ...definition, version }));
    section.append(component);
  }
  return section;
}

async function actualizarVisualizaciones(version = "") {
  if (!datasetActivo?.article.classList.contains("open")) return;
  const section = await visualizations(datasetActivo.config, datasetActivo.rows, version);
  const anterior = datasetActivo.article.querySelector(".visualizations");
  if (section?.childElementCount) {
    if (anterior) anterior.replaceWith(section);
    else datasetActivo.article.querySelector(".results-section").before(section);
  } else {
    anterior?.remove();
  }
}

async function actualizarConfiguracion(version) {
  if (!datasetActivo) return;
  const url = `configuraciones/${datasetActivo.indicator.slug}.json?v=${version}`;
  try {
    datasetActivo.config = await fetchChecked(url, "json");
  } catch {
    datasetActivo.config = null;
  }
  await actualizarVisualizaciones(version);
}

async function openDataset(article, indicator) {
  const button = article.querySelector(".dataset-summary");
  const shell = article.querySelector(".details-shell");
  const content = article.querySelector(".details-content");
  const opening = !article.classList.contains("open");

  article.classList.toggle("open", opening);
  button.setAttribute("aria-expanded", String(opening));
  if (!opening || article.dataset.loaded) return;

  content.innerHTML = '<div class="loading"><span></span>Cargando ficha y resultados…</div>';
  try {
    const base = `${RAW_ROOT}indicadores/${indicator.slug}/`;
    const [ficha, csvText, config] = await Promise.all([
      fetchChecked(`${base}ficha.json`, "json"),
      fetchChecked(`${base}resultados.csv`),
      indicator.tiene_config
        ? fetchChecked(`configuraciones/${indicator.slug}.json`, "json")
        : Promise.resolve(null),
    ]);
    const rows = parseCsv(csvText);
    const [headers = [], ...values] = rows;
    const objects = values.map(row => Object.fromEntries(headers.map((header, index) => [header, row[index]])));
    const metadata = document.createElement("section");
    metadata.className = "metadata-section";
    metadata.append(metadataMarkup(ficha));
    const visualizationSection = await visualizations(config, objects);
    content.replaceChildren(metadata);
    if (visualizationSection && visualizationSection.childElementCount) {
      content.append(visualizationSection);
    }
    content.append(resultsTable(rows, ficha.campos, indicator.slug));
    datasetActivo = { article, config, ficha, indicator, rows: objects };
    article.dataset.loaded = "true";
  } catch (error) {
    content.innerHTML = "";
    const message = document.createElement("p");
    message.className = "error";
    message.textContent = "No fue posible cargar este indicador. Intenta nuevamente.";
    content.append(message);
    console.error(error);
  }
  shell.addEventListener("transitionend", () => {
    if (opening) shell.scrollIntoView({ block: "nearest", behavior: "smooth" });
  }, { once: true });
}

function createDataset(indicator) {
  const article = document.createElement("article");
  article.className = "dataset";
  const detailsId = `details-${indicator.slug}`;
  article.innerHTML = `
    <button class="dataset-summary" type="button" aria-expanded="false" aria-controls="${detailsId}">
      <span class="top"><span class="name"></span><svg class="chevron" viewBox="0 0 16 16" aria-hidden="true"><path d="m4 6 4 4 4-4"></path></svg></span>
      <span class="page"></span>
      <span class="meta"></span>
    </button>
    <div class="details-shell" id="${detailsId}">
      <div class="details-content"></div>
    </div>`;
  article.querySelector(".name").textContent = indicator.nombre;
  article.querySelector(".page").textContent = indicator.definicion_conceptual;
  article.querySelector(".meta").textContent = indicator.fuente;
  article.querySelector(".dataset-summary").addEventListener("click", () => openDataset(article, indicator));
  return article;
}

function renderIndicators() {
  const batch = filtered.slice(shown, shown + BATCH_SIZE);
  const fragment = document.createDocumentFragment();
  batch.forEach(indicator => fragment.append(createDataset(indicator)));
  shown += batch.length;
  list.append(fragment);
}

function renderGroups(data) {
  const grupos = data.espacios_politica.map(grupo => ({ ...grupo, tipo: "espacio" }));
  const fragment = document.createDocumentFragment();
  grupos.forEach(grupo => {
    const button = document.createElement("button");
    button.className = "group-button";
    button.type = "button";
    button.textContent = grupo.nombre;
    button.setAttribute("aria-pressed", "false");
    button.addEventListener("click", () => {
      const clave = `${grupo.tipo}:${grupo.id}`;
      grupoActivo = grupoActivo?.clave === clave ? null : { clave, indicadores: new Set(grupo.indicadores) };
      groups.querySelectorAll(".group-button").forEach(elemento => {
        elemento.classList.toggle("selected", elemento === button && grupoActivo !== null);
        elemento.setAttribute("aria-pressed", String(elemento === button && grupoActivo !== null));
      });
      search();
    });
    fragment.append(button);
  });
  groups.replaceChildren(fragment);
}

function search() {
  const query = normalize(input.value.trim());
  const subset = grupoActivo
    ? indicators.filter(indicator => grupoActivo.indicadores.has(indicator.slug))
    : indicators;
  filtered = subset.filter(indicator => normalize([
    indicator.nombre,
    indicator.definicion_conceptual,
    indicator.fuente,
  ].join(" ")).includes(query));
  shown = 0;
  list.replaceChildren();
  catalogue.scrollTop = 0;
  searchBox.classList.toggle("has-value", Boolean(input.value));
  empty.hidden = filtered.length > 0;
  renderIndicators();
}

new IntersectionObserver(entries => {
  if (entries[0].isIntersecting) renderIndicators();
}, { root: catalogue, rootMargin: "0px 0px 300px" }).observe(catalogueSentinel);

input.addEventListener("input", search);
clearButton.addEventListener("click", () => {
  input.value = "";
  input.focus();
  search();
});

if (["localhost", "127.0.0.1", "::1"].includes(location.hostname)) {
  const liveReload = new EventSource("/__livereload");
  liveReload.addEventListener("message", async event => {
    const change = JSON.parse(event.data);
    if (change.tipo === "componente") await actualizarVisualizaciones(change.version);
    else if (change.tipo === "configuracion" && change.slugs.includes(datasetActivo?.indicator.slug)) {
      await actualizarConfiguracion(change.version);
    }
    else if (change.tipo === "recargar") location.reload();
  });
}

Promise.all([
  fetchChecked(INDEX_URL, "json"),
  loadMunicipalityMaps(),
]).then(([data]) => {
  indicators = Object.values(data.indicadores).sort((a, b) =>
    a.slug.localeCompare(b.slug, "es", { numeric: true }));
  renderGroups(data);
  search();
}).catch(error => {
  empty.hidden = false;
  empty.textContent = "No fue posible cargar el catálogo. Recarga la página para intentarlo nuevamente.";
  console.error(error);
});
