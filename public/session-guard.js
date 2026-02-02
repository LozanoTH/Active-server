import { showToast } from "./toast.js";

function getOrCreateSessionId() {
    const key = "active_session_id";
    let id = localStorage.getItem(key);
    if (!id) {
        const rand = Math.random().toString(36).slice(2);
        id = `${Date.now().toString(36)}-${rand}`;
        localStorage.setItem(key, id);
    }
    return id;
}

function getDeviceInfo() {
    const platform = navigator.platform || "N/A";
    const lang = navigator.language || "N/A";
    const ua = navigator.userAgent || "N/A";
    return `${platform} | ${lang} | ${ua}`;
}

export function ensureSingleSession({ auth, db, ref, set, onValue, onDisconnect, signOut, user }) {
    if (!user) return;

    const sessionId = getOrCreateSessionId();
    const device = getDeviceInfo();
    const sessionRef = ref(db, `sessions/${user.uid}/current`);

    set(sessionRef, {
        sessionId,
        device,
        updatedAt: Date.now()
    });

    onDisconnect(sessionRef).set(null);

    const unsubscribe = onValue(sessionRef, (snap) => {
        if (!snap.exists()) return;
        const data = snap.val();
        if (data.sessionId && data.sessionId !== sessionId) {
            showToast("Tu cuenta se inició en otro dispositivo. Se cerrará esta sesión.", "error", 4500);
            setTimeout(() => {
                signOut(auth).finally(() => {
                    location.href = "index.html";
                });
            }, 1200);
        }
    });

    const heartbeat = setInterval(() => {
        set(sessionRef, {
            sessionId,
            device,
            updatedAt: Date.now()
        });
    }, 30000);

    return () => {
        clearInterval(heartbeat);
        unsubscribe();
    };
}
