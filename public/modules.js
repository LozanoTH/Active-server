const listEl = document.getElementById("module-list");
const countEl = document.getElementById("module-count");
const formEl = document.getElementById("module-form");
const nameEl = document.getElementById("module-name");
const zipEl = document.getElementById("module-zip");
const descEl = document.getElementById("module-desc");
const btnAdd = document.getElementById("btn-add");
const btnRefresh = document.getElementById("btn-refresh");
const btnExport = document.getElementById("btn-export");
const btnClearForm = document.getElementById("btn-clear-form");

let modulesCache = [];

loadModules();

btnRefresh.addEventListener("click", () => {
    loadModules();
});

btnExport.addEventListener("click", async () => {
    try {
        const data = await fetchModules();
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "modules.json";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    } catch (err) {
        showToast("No se pudo exportar: " + err.message, "error");
    }
});

btnClearForm.addEventListener("click", () => {
    formEl.reset();
});

formEl.addEventListener("submit", async (e) => {
    e.preventDefault();
    const name = nameEl.value.trim();
    const zipUrl = zipEl.value.trim();
    const description = descEl.value.trim();

    if (!name || !zipUrl) {
        showToast("Nombre y URL son obligatorios", "error");
        return;
    }

    btnAdd.disabled = true;
    btnAdd.textContent = "Agregando...";

    try {
        const res = await fetch("/api/modules", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name, description, zip_url: zipUrl }),
        });

        if (!res.ok) {
            const err = await safeJson(res);
            throw new Error(err.error || "Error al guardar");
        }

        formEl.reset();
        showToast("Módulo agregado", "success");
        await loadModules();
    } catch (err) {
        showToast(err.message, "error");
    } finally {
        btnAdd.disabled = false;
        btnAdd.textContent = "Agregar";
    }
});

listEl.addEventListener("click", async (event) => {
    const button = event.target.closest("button[data-action]");
    if (!button) return;

    const index = Number(button.dataset.index);
    const action = button.dataset.action;
    const moduleItem = modulesCache[index];

    if (!moduleItem) {
        showToast("Módulo no encontrado", "error");
        return;
    }

    if (action === "copy") {
        try {
            await navigator.clipboard.writeText(moduleItem.zip_url || "");
            showToast("URL copiada", "success");
        } catch (err) {
            showToast("No se pudo copiar", "error");
        }
        return;
    }

    if (action === "delete") {
        const ok = confirm(`¿Eliminar el módulo "${moduleItem.name}"?`);
        if (!ok) return;

        try {
            const res = await fetch(`/api/modules?index=${index}`, { method: "DELETE" });
            if (!res.ok) {
                const err = await safeJson(res);
                throw new Error(err.error || "Error al eliminar");
            }
            showToast("Módulo eliminado", "success");
            await loadModules();
        } catch (err) {
            showToast(err.message, "error");
        }
    }
});

async function loadModules() {
    listEl.innerHTML = `
        <div class="module-empty">
            <span class="loading"></span> Cargando módulos...
        </div>
    `;

    try {
        const data = await fetchModules();
        modulesCache = Array.isArray(data) ? data : [];
        renderModules(modulesCache);
    } catch (err) {
        listEl.innerHTML = `
            <div class="module-empty">
                Error al cargar módulos.
            </div>
        `;
        showToast("Error al cargar: " + err.message, "error");
    }
}

async function fetchModules() {
    const res = await fetch("/api/modules");
    if (!res.ok) {
        throw new Error("Servidor no disponible");
    }
    return res.json();
}

function renderModules(modules) {
    listEl.innerHTML = "";
    countEl.textContent = `${modules.length} módulo${modules.length === 1 ? "" : "s"}`;

    if (modules.length === 0) {
        const empty = document.createElement("div");
        empty.className = "module-empty";
        empty.textContent = "No hay módulos cargados.";
        listEl.appendChild(empty);
        return;
    }

    modules.forEach((module, index) => {
        const item = document.createElement("div");
        item.className = "module-item";

        const main = document.createElement("div");
        main.className = "module-main";

        const title = document.createElement("div");
        title.className = "module-title";
        title.textContent = module.name || "Sin nombre";

        const desc = document.createElement("div");
        desc.className = "module-desc";
        desc.textContent = module.description || "Sin descripción";

        const urlWrap = document.createElement("div");
        urlWrap.className = "module-url";
        const link = document.createElement("a");
        link.href = module.zip_url || "#";
        link.target = "_blank";
        link.rel = "noopener";
        link.textContent = module.zip_url || "Sin URL";
        urlWrap.appendChild(link);

        main.appendChild(title);
        main.appendChild(desc);
        main.appendChild(urlWrap);

        const actions = document.createElement("div");
        actions.className = "module-actions";

        const copyBtn = document.createElement("button");
        copyBtn.className = "btn-ghost btn-inline";
        copyBtn.type = "button";
        copyBtn.dataset.action = "copy";
        copyBtn.dataset.index = index;
        copyBtn.textContent = "Copiar URL";

        const delBtn = document.createElement("button");
        delBtn.className = "btn-secondary btn-inline";
        delBtn.type = "button";
        delBtn.dataset.action = "delete";
        delBtn.dataset.index = index;
        delBtn.textContent = "Eliminar";

        actions.appendChild(copyBtn);
        actions.appendChild(delBtn);

        item.appendChild(main);
        item.appendChild(actions);
        listEl.appendChild(item);
    });
}

async function safeJson(res) {
    try {
        return await res.json();
    } catch (err) {
        return {};
    }
}

function showToast(message, type = "info") {
    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);

    requestAnimationFrame(() => {
        toast.classList.add("show");
    });

    setTimeout(() => {
        toast.classList.remove("show");
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}
