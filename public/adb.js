import { showToast } from "./toast.js";
import { Adb, AdbDaemonTransport } from "@yume-chan/adb";
import { AdbDaemonWebUsbDeviceManager, AdbDaemonWebUsbDevice } from "@yume-chan/adb-daemon-webusb";
import * as AdbCredentialWeb from "@yume-chan/adb-credential-web";

const statusEl = document.getElementById("adb-status");
const deviceEl = document.getElementById("adb-device");
const webusbEl = document.getElementById("adb-webusb");
const devicesEl = document.getElementById("adb-devices");
const outputEl = document.getElementById("adb-output");
const panelEl = document.getElementById("adb-panel");
const btnDetect = document.getElementById("btn-adb-detect");
const btnSelect = document.getElementById("btn-adb-select");
const btnConnect = document.getElementById("btn-adb-connect");
const btnInfo = document.getElementById("btn-adb-info");
const btnDisconnect = document.getElementById("btn-adb-disconnect");
const btnRefresh = document.getElementById("btn-adb-refresh");
const tabs = Array.from(document.querySelectorAll(".tab"));

let adb = null;
let transport = null;
let selectedDevice = null;
let shellProcess = null;
let shellReader = null;
let shellWriter = null;
const textEncoder = new TextEncoder();
const textDecoder = new TextDecoder();

function setStatus(text) {
    statusEl.textContent = text;
}

function setDevice(text) {
    deviceEl.textContent = text || "-";
}

function setOutput(text) {
    outputEl.textContent = text || "";
}

function isSecureContextOk() {
    return location.protocol === "https:" || location.hostname === "localhost" || location.hostname === "127.0.0.1";
}

function updateWebUsbStatus() {
    if (!("usb" in navigator)) {
        webusbEl.textContent = "No compatible";
        return false;
    }
    if (!isSecureContextOk()) {
        webusbEl.textContent = "Requiere HTTPS o localhost";
        return false;
    }
    webusbEl.textContent = "Disponible";
    return true;
}

function renderDevices(list) {
    devicesEl.innerHTML = "";
    if (!list || list.length === 0) {
        const empty = document.createElement("div");
        empty.className = "device-item muted";
        empty.textContent = "Sin dispositivos detectados aun.";
        devicesEl.appendChild(empty);
        return;
    }

    list.forEach((d) => {
        const item = document.createElement("div");
        item.className = "device-item";
        if (selectedDevice && d.serial === selectedDevice.serial) {
            item.classList.add("active");
        }

        const left = document.createElement("div");
        left.innerHTML = `<div><strong>${d.serial || "Android"}</strong></div>
            <div class="device-meta">USB Vendor: ${d.vendorId} | Product: ${d.productId}</div>`;

        const right = document.createElement("div");
        right.textContent = "Seleccionar";
        right.className = "device-meta";

        item.addEventListener("click", () => {
            selectedDevice = d;
            setDevice(d.serial || "Android");
            renderDevices(list);
            showToast("Dispositivo seleccionado.", "success");
            setStatus("Listo para conectar");
        });

        item.appendChild(left);
        item.appendChild(right);
        devicesEl.appendChild(item);
    });
}

async function detectDevices() {
    if (!updateWebUsbStatus()) {
        showToast("WebUSB no esta disponible en este navegador o contexto.", "error");
        return;
    }

    const manager = AdbDaemonWebUsbDeviceManager.BROWSER;
    if (!manager || typeof manager.getDevices !== "function") {
        showToast("No se pudo acceder al administrador WebUSB.", "error");
        return;
    }

    try {
        const list = await manager.getDevices();
        renderDevices(list);
        if (list.length > 0) {
            showToast("Dispositivos detectados.", "success");
        } else {
            showToast("No se detectaron dispositivos.", "error");
        }
    } catch (err) {
        showToast(`Error al detectar: ${err.message || err}`, "error");
    }
}

btnDetect.addEventListener("click", detectDevices);
if (btnRefresh) {
    btnRefresh.addEventListener("click", detectDevices);
}

btnSelect.addEventListener("click", async () => {
    if (!updateWebUsbStatus()) {
        showToast("WebUSB no esta disponible en este navegador o contexto.", "error");
        return;
    }

    const manager = AdbDaemonWebUsbDeviceManager.BROWSER;
    if (!manager) {
        showToast("WebUSB requiere HTTPS o localhost.", "error");
        return;
    }

    try {
        btnSelect.disabled = true;
        const device = await manager.requestDevice();
        if (!device) {
            showToast("No se selecciono dispositivo.", "error");
            return;
        }
        selectedDevice = device;
        setDevice(device.serial || "Android");
        await detectDevices();
        showToast("Dispositivo seleccionado.", "success");
        setStatus("Listo para conectar");
    } catch (err) {
        showToast(`Error al seleccionar: ${err.message || err}`, "error");
    } finally {
        btnSelect.disabled = false;
    }
});

btnConnect.addEventListener("click", async () => {
    if (!updateWebUsbStatus()) {
        showToast("WebUSB no esta disponible en este navegador o contexto.", "error");
        return;
    }

    const manager = AdbDaemonWebUsbDeviceManager.BROWSER;
    if (!manager) {
        showToast("WebUSB requiere HTTPS o localhost.", "error");
        return;
    }

    try {
        btnConnect.disabled = true;
        setStatus("Conectando...");

        if (!selectedDevice) {
            const list = await manager.getDevices();
            if (list.length === 0) {
                setStatus("Desconectado");
                showToast("No hay dispositivos. Usa Seleccionar dispositivo.", "error");
                return;
            }
            selectedDevice = list[0];
        }

        const connection = await selectedDevice.connect();

        const credentialStore = createCredentialStore();

        transport = await AdbDaemonTransport.authenticate({
            serial: selectedDevice.serial,
            connection,
            credentialStore
        });

        adb = new Adb(transport);
        setStatus("Conectado");
        setDevice(selectedDevice.serial || "Android");
        showToast("Dispositivo conectado.", "success");
        panelEl.innerHTML = `<div class="panel-title">Conexion activa</div>
            <p>Ya puedes usar las herramientas. Selecciona una pestaña arriba.</p>`;
    } catch (err) {
        if (err instanceof AdbDaemonWebUsbDevice.DeviceBusyError) {
            showToast("El dispositivo esta ocupado por ADB de escritorio.", "error");
        } else {
            showToast(`Error al conectar: ${err.message || err}`, "error");
        }
        setStatus("Desconectado");
        setDevice("-");
    } finally {
        btnConnect.disabled = false;
    }
});

btnInfo.addEventListener("click", async () => {
    if (!adb) {
        showToast("Primero conecta un dispositivo.", "error");
        return;
    }

    try {
        const model = await adb.getProp("ro.product.model");
        const version = await adb.getProp("ro.build.version.release");
        const brand = await adb.getProp("ro.product.brand");
        setOutput(`Marca: ${brand}\nModelo: ${model}\nAndroid: ${version}`);
        showToast("Informacion obtenida.", "success");
        panelEl.innerHTML = `<div class="panel-title">Device Info</div>
            <p>Marca: <strong>${brand}</strong></p>
            <p>Modelo: <strong>${model}</strong></p>
            <p>Android: <strong>${version}</strong></p>`;
    } catch (err) {
        showToast(`Error al leer info: ${err.message || err}`, "error");
    }
});

btnDisconnect.addEventListener("click", async () => {
    try {
        await stopShell();
        if (transport && typeof transport.close === "function") {
            await transport.close();
        }
    } catch {
    } finally {
        adb = null;
        transport = null;
        selectedDevice = null;
        setStatus("Desconectado");
        setDevice("-");
        setOutput("Sin datos aun.");
        showToast("Sesion cerrada.", "success");
        panelEl.innerHTML = `<div class="panel-title">Device Info</div>
            <p>Selecciona un dispositivo y presiona "Obtener Info" para ver los datos basicos.</p>`;
    }
});

updateWebUsbStatus();

function createCredentialStore() {
    if (AdbCredentialWeb.AdbWebCryptoCredentialManager && AdbCredentialWeb.TangoLocalStorage) {
        return new AdbCredentialWeb.AdbWebCryptoCredentialManager(
            new AdbCredentialWeb.TangoLocalStorage("adb-key")
        );
    }
    if (AdbCredentialWeb.AdbWebCredentialStore) {
        return new AdbCredentialWeb.AdbWebCredentialStore();
    }
    throw new Error("No se encontró un gestor de credenciales compatible.");
}

tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
        tabs.forEach((t) => t.classList.remove("active"));
        tab.classList.add("active");
        const name = tab.dataset.tab || "info";
        if (name === "shell") {
            renderShellPanel();
        } else if (name === "info") {
            panelEl.innerHTML = `<div class="panel-title">Device Info</div>
                <p>Selecciona un dispositivo y presiona "Obtener Info" para ver los datos basicos.</p>`;
        } else {
            panelEl.innerHTML = `<div class="panel-title">${tab.textContent}</div>
                <p>Esta seccion esta lista para integrarse. Conecta un dispositivo para habilitar funciones.</p>`;
        }
    });
});

function renderShellPanel() {
    panelEl.innerHTML = `
        <div class="panel-title">Interactive Shell</div>
        <div class="shell-wrap">
            <div class="shell-output" id="shell-output">Shell lista. Presiona "Iniciar shell" para abrir una sesion.</div>
            <textarea class="shell-input" id="shell-input" placeholder="Escribe un comando... (ej: ls /)"></textarea>
            <div class="shell-actions">
                <button class="btn-inline" id="shell-start">Iniciar shell</button>
                <button class="btn-secondary btn-inline" id="shell-send">Enviar</button>
                <button class="btn-ghost btn-inline" id="shell-clear">Limpiar</button>
                <button class="btn-ghost btn-inline" id="shell-stop">Cerrar shell</button>
            </div>
        </div>
    `;

    const output = document.getElementById("shell-output");
    const input = document.getElementById("shell-input");
    const btnStart = document.getElementById("shell-start");
    const btnSend = document.getElementById("shell-send");
    const btnClear = document.getElementById("shell-clear");
    const btnStop = document.getElementById("shell-stop");

    btnStart.addEventListener("click", async () => {
        await startShell(output);
    });

    btnSend.addEventListener("click", async () => {
        const cmd = input.value.trim();
        if (!cmd) return;
        await sendShell(cmd + "\n");
        input.value = "";
    });

    btnClear.addEventListener("click", () => {
        output.textContent = "";
    });

    btnStop.addEventListener("click", async () => {
        await stopShell();
        output.textContent = "Shell cerrada.";
    });

    input.addEventListener("keydown", async (e) => {
        if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
            e.preventDefault();
            const cmd = input.value.trim();
            if (!cmd) return;
            await sendShell(cmd + "\n");
            input.value = "";
        }
    });
}

async function startShell(outputEl) {
    if (!adb) {
        showToast("Primero conecta un dispositivo.", "error");
        return;
    }
    if (shellProcess) {
        showToast("La shell ya esta activa.", "success");
        return;
    }

    try {
        shellProcess = await adb.subprocess.noneProtocol.spawn("sh");
        shellReader = shellProcess.output.getReader();
        shellWriter = shellProcess.stdin.getWriter();
        outputEl.textContent = "Shell iniciada. Puedes escribir comandos.";

        readShellLoop(outputEl);
    } catch (err) {
        shellProcess = null;
        showToast(`Error al iniciar shell: ${err.message || err}`, "error");
    }
}

async function readShellLoop(outputEl) {
    try {
        while (shellReader) {
            const { value, done } = await shellReader.read();
            if (done) break;
            if (value) {
                outputEl.textContent += textDecoder.decode(value, { stream: true });
                outputEl.scrollTop = outputEl.scrollHeight;
            }
        }
    } catch (err) {
        showToast(`Shell cerrada: ${err.message || err}`, "error");
    }
}

async function sendShell(text) {
    if (!shellWriter) {
        showToast("Inicia la shell primero.", "error");
        return;
    }
    try {
        await shellWriter.write(textEncoder.encode(text));
    } catch (err) {
        showToast(`Error al enviar: ${err.message || err}`, "error");
    }
}

async function stopShell() {
    try {
        if (shellWriter) {
            await shellWriter.write(textEncoder.encode("exit\n"));
            shellWriter.releaseLock();
        }
    } catch {
    }

    try {
        if (shellReader) {
            await shellReader.cancel();
        }
    } catch {
    }

    shellProcess = null;
    shellReader = null;
    shellWriter = null;
}
