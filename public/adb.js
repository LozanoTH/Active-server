import { showToast } from "./toast.js";
import { Adb, AdbDaemonTransport } from "@yume-chan/adb";
import { AdbDaemonWebUsbDeviceManager, AdbDaemonWebUsbDevice } from "@yume-chan/adb-daemon-webusb";
import { AdbWebCryptoCredentialManager, TangoLocalStorage } from "@yume-chan/adb-credential-web";

const statusEl = document.getElementById("adb-status");
const deviceEl = document.getElementById("adb-device");
const webusbEl = document.getElementById("adb-webusb");
const devicesEl = document.getElementById("adb-devices");
const outputEl = document.getElementById("adb-output");
const btnDetect = document.getElementById("btn-adb-detect");
const btnSelect = document.getElementById("btn-adb-select");
const btnConnect = document.getElementById("btn-adb-connect");
const btnInfo = document.getElementById("btn-adb-info");
const btnDisconnect = document.getElementById("btn-adb-disconnect");

let adb = null;
let transport = null;
let selectedDevice = null;

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

        const credentialStore = new AdbWebCryptoCredentialManager(
            new TangoLocalStorage("adb-key")
        );

        transport = await AdbDaemonTransport.authenticate({
            serial: selectedDevice.serial,
            connection,
            credentialStore
        });

        adb = new Adb(transport);
        setStatus("Conectado");
        setDevice(selectedDevice.serial || "Android");
        showToast("Dispositivo conectado.", "success");
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
    } catch (err) {
        showToast(`Error al leer info: ${err.message || err}`, "error");
    }
});

btnDisconnect.addEventListener("click", async () => {
    try {
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
    }
});

updateWebUsbStatus();
