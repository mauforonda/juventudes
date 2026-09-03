const RAW_ROOT = "https://raw.githubusercontent.com/mauforonda/juventudes/refs/heads/main/";
const INDEX_URL = "indice.json";
const MUNICIPALITIES_URL = `${RAW_ROOT}diccionarios/municipios.csv`;
const BATCH_SIZE = 30;
const TABLE_BATCH_SIZE = 60;

const input = document.querySelector("#search input");
const clearButton = document.querySelector("#search button");
const searchBox = document.querySelector("#search");
const list = document.querySelector("#datasets");
const empty = document.querySelector("#empty");
const catalogueSentinel = document.querySelector("#catalogue-sentinel");

let indicators = [];
let filtered = [];
let shown = 0;
let municipalityMaps = { municipalities: new Map(), departments: new Map() };

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

function resultsTable(csvText, fieldDescriptions = {}) {
  const rows = parseCsv(csvText);
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

  let rowIndex = 0;
  const renderRows = () => {
    const fragment = document.createDocumentFragment();
    values.slice(rowIndex, rowIndex + TABLE_BATCH_SIZE).forEach(row => {
      const tr = document.createElement("tr");
      headers.forEach((header, columnIndex) => {
        const td = document.createElement("td");
        td.textContent = formatValue(row[columnIndex], header);
        td.title = td.textContent;
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
    const [ficha, csvText] = await Promise.all([
      fetchChecked(`${base}ficha.json`, "json"),
      fetchChecked(`${base}resultados.csv`),
    ]);
    const metadata = document.createElement("section");
    metadata.className = "metadata-section";
    metadata.append(metadataMarkup(ficha));
    content.replaceChildren(metadata, resultsTable(csvText, ficha.campos));
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

function search() {
  const query = normalize(input.value.trim());
  filtered = indicators.filter(indicator => normalize([
    indicator.nombre,
    indicator.definicion_conceptual,
    indicator.fuente,
  ].join(" ")).includes(query));
  shown = 0;
  list.replaceChildren();
  searchBox.classList.toggle("has-value", Boolean(input.value));
  empty.hidden = filtered.length > 0;
  renderIndicators();
}

new IntersectionObserver(entries => {
  if (entries[0].isIntersecting) renderIndicators();
}, { rootMargin: "0px 0px 300px" }).observe(catalogueSentinel);

input.addEventListener("input", search);
clearButton.addEventListener("click", () => {
  input.value = "";
  input.focus();
  search();
});

Promise.all([
  fetchChecked(INDEX_URL, "json"),
  loadMunicipalityMaps(),
]).then(([data]) => {
  indicators = data.sort((a, b) => a.slug.localeCompare(b.slug, "es", { numeric: true }));
  search();
}).catch(error => {
  empty.hidden = false;
  empty.textContent = "No fue posible cargar el catálogo. Recarga la página para intentarlo nuevamente.";
  console.error(error);
});
