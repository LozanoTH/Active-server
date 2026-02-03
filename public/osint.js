import { showToast } from "./toast.js";

const DATA_URL = "./osint/arf.json";
const FALLBACK_URL = "https://raw.githubusercontent.com/lockfale/OSINT-Framework/master/public/arf.json";

const searchEl = document.getElementById("osint-search");
const reloadEl = document.getElementById("osint-reload");
const searchBtnEl = document.getElementById("search-action");
const modeOsintEl = document.getElementById("mode-osint");
const modeGithubEl = document.getElementById("mode-github");

const osintCardEl = document.getElementById("osint-card");
const ghCardEl = document.getElementById("gh-card");
const resultsEl = document.getElementById("osint-results");
const countEl = document.getElementById("osint-count");
const sourceEl = document.getElementById("osint-source");
const metaEl = document.getElementById("osint-meta");
const ghResultsEl = document.getElementById("gh-results");

let flatItems = [];
let dataReady = false;
let mode = "osint";

function setMode(next) {
    mode = next;
    const isOsint = mode === "osint";
    modeOsintEl.classList.toggle("active", isOsint);
    modeGithubEl.classList.toggle("active", !isOsint);
    osintCardEl.classList.toggle("hidden", !isOsint);
    ghCardEl.classList.toggle("hidden", isOsint);
    metaEl.classList.toggle("hidden", !isOsint);
    reloadEl.classList.toggle("hidden", !isOsint);
    searchEl.value = "";
    searchEl.placeholder = isOsint ? "Buscar por nombre o categoria..." : "Buscar repositorios en GitHub...";
    if (isOsint) {
        resultsEl.innerHTML = `<div class="osint-empty">Cargando datos...</div>`;
        loadData();
    } else {
        ghResultsEl.innerHTML = `<div class="osint-empty">Sin resultados aun.</div>`;
    }
}

function normalize(text) {
    return (text || "").toLowerCase();
}

function setSource(text) {
    sourceEl.textContent = text;
}

function setEmpty(text) {
    resultsEl.innerHTML = `<div class="osint-empty">${text}</div>`;
}

function flatten(node, path = []) {
    const name = node.name || node.title || "Sin titulo";
    const type = node.type || node.category || "";
    const url = node.url || node.link || "";
    const nextPath = [...path, name];

    if (url) {
        flatItems.push({
            name,
            type,
            url,
            path: nextPath.join(" / ")
        });
    }

    if (Array.isArray(node.children)) {
        node.children.forEach((child) => flatten(child, nextPath));
    }
}

function render(items) {
    resultsEl.innerHTML = "";
    if (!items.length) {
        setEmpty("No hay resultados.");
        return;
    }

    items.forEach((item) => {
        const row = document.createElement("div");
        row.className = "osint-item";
        row.innerHTML = `
            <div class="osint-item-title">${item.name}</div>
            <div class="osint-item-path">${item.path}</div>
            <div class="osint-item-link">
                <a href="${item.url}" target="_blank" rel="noopener noreferrer">${item.url}</a>
            </div>
        `;
        resultsEl.appendChild(row);
    });
}

function applySearch() {
    if (!dataReady) {
        setEmpty("Carga los datos para buscar.");
        return;
    }
    const q = normalize(searchEl.value);
    if (!q) {
        render(flatItems);
        countEl.textContent = flatItems.length;
        return;
    }

    const filtered = flatItems.filter((item) => {
        const hay = `${item.name} ${item.path} ${item.type}`.toLowerCase();
        return hay.includes(q);
    });
    render(filtered);
    countEl.textContent = filtered.length;
}

async function loadData() {
    try {
        dataReady = false;
        searchEl.disabled = true;
        setEmpty("Cargando datos...");

        let res = await fetch(DATA_URL, { cache: "no-store" });
        if (!res.ok) {
            res = await fetch(FALLBACK_URL, { cache: "no-store" });
            setSource("Fuente: GitHub (remota)");
        } else {
            setSource("Fuente: Local");
        }

        const data = await res.json();
        flatItems = [];
        if (Array.isArray(data)) {
            data.forEach((node) => flatten(node));
        } else {
            flatten(data);
        }
        render(flatItems);
        countEl.textContent = flatItems.length;
        dataReady = true;
        searchEl.disabled = false;
        if (flatItems.length === 0) {
            setEmpty("Dataset cargado, pero sin resultados.");
        }
    } catch (err) {
        setEmpty("No se pudo cargar el dataset.");
        showToast("Error cargando OSINT Framework.", "error");
        searchEl.disabled = false;
    }
}

async function ghSearch() {
    const q = (searchEl.value || "").trim();
    if (!q) {
        showToast("Escribe un termino para buscar.", "error");
        return;
    }
    ghResultsEl.innerHTML = `<div class="osint-empty">Buscando en GitHub...</div>`;
    try {
        const url = `https://api.github.com/search/repositories?q=${encodeURIComponent(q)}`;
        const res = await fetch(url, { headers: { "Accept": "application/vnd.github+json" } });
        if (!res.ok) {
            throw new Error(`HTTP ${res.status}`);
        }
        const data = await res.json();
        const items = data.items || [];
        if (!items.length) {
            ghResultsEl.innerHTML = `<div class="osint-empty">Sin resultados.</div>`;
            return;
        }
        ghResultsEl.innerHTML = "";
        items.slice(0, 20).forEach((item) => {
            const row = document.createElement("div");
            row.className = "gh-repo";
            row.innerHTML = `
                <a href="${item.html_url}" target="_blank" rel="noopener noreferrer">
                    <strong>${item.full_name}</strong>
                </a>
                <p>${item.description || "Sin descripcion"}</p>
                ⭐ ${item.stargazers_count}
            `;
            ghResultsEl.appendChild(row);
        });
    } catch (err) {
        ghResultsEl.innerHTML = `<div class="osint-empty">Error al buscar en GitHub. Puede ser limite de API.</div>`;
        showToast("Error buscando en GitHub.", "error");
    }
}

modeOsintEl.addEventListener("click", () => setMode("osint"));
modeGithubEl.addEventListener("click", () => setMode("github"));
reloadEl.addEventListener("click", loadData);
searchEl.addEventListener("input", () => {
    if (mode === "osint") applySearch();
});
searchBtnEl.addEventListener("click", () => {
    if (mode === "osint") {
        applySearch();
    } else {
        ghSearch();
    }
});
searchEl.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
        if (mode === "osint") {
            applySearch();
        } else {
            ghSearch();
        }
    }
});

setMode("osint");
