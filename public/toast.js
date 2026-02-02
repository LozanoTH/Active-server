export function showToast(message, type = "info", durationMs = 4000) {
    let container = document.querySelector(".toast-container");
    if (!container) {
        container = document.createElement("div");
        container.className = "toast-container";
        document.body.appendChild(container);
    }

    const toast = document.createElement("div");
    const typeClass = type === "error" ? " toast--error" : type === "success" ? " toast--success" : "";
    toast.className = `toast${typeClass}`;
    toast.textContent = message;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transform = "translateY(-6px)";
        setTimeout(() => {
            toast.remove();
        }, 250);
    }, durationMs);
}
