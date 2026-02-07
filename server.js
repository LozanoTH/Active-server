const http = require("http");
const fs = require("fs");
const path = require("path");

const PORT = process.env.PORT || 8000;
const PUBLIC_DIR = path.join(__dirname, "public");
const MODULES_PATH = path.join(PUBLIC_DIR, "modules.json");

const MIME_TYPES = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "application/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".svg": "image/svg+xml",
  ".ico": "image/x-icon",
};

function sendFile(res, filePath) {
  fs.readFile(filePath, (err, data) => {
    if (err) {
      const notFoundPath = path.join(PUBLIC_DIR, "404.html");
      fs.readFile(notFoundPath, (nfErr, nfData) => {
        if (nfErr) {
          res.writeHead(404, { "Content-Type": "text/plain; charset=utf-8" });
          res.end("404 - Not Found");
          return;
        }
        res.writeHead(404, { "Content-Type": "text/html; charset=utf-8" });
        res.end(nfData);
      });
      return;
    }
    const ext = path.extname(filePath).toLowerCase();
    const mime = MIME_TYPES[ext] || "application/octet-stream";
    res.writeHead(200, { "Content-Type": mime });
    res.end(data);
  });
}

function readModules() {
  try {
    const raw = fs.readFileSync(MODULES_PATH, "utf8");
    const data = JSON.parse(raw || "[]");
    return Array.isArray(data) ? data : [];
  } catch (err) {
    return [];
  }
}

function writeModules(modules, res) {
  try {
    fs.writeFileSync(MODULES_PATH, JSON.stringify(modules, null, 2), "utf8");
    res.writeHead(200, { "Content-Type": "application/json; charset=utf-8" });
    res.end(JSON.stringify(modules));
  } catch (err) {
    res.writeHead(500, { "Content-Type": "application/json; charset=utf-8" });
    res.end(JSON.stringify({ error: "No se pudo guardar modules.json" }));
  }
}

function handleModulesApi(req, res) {
  if (req.method === "GET") {
    const modules = readModules();
    res.writeHead(200, { "Content-Type": "application/json; charset=utf-8" });
    res.end(JSON.stringify(modules));
    return;
  }

  if (req.method === "POST") {
    let body = "";
    req.on("data", (chunk) => {
      body += chunk;
      if (body.length > 1_000_000) {
        res.writeHead(413, { "Content-Type": "application/json; charset=utf-8" });
        res.end(JSON.stringify({ error: "Payload demasiado grande" }));
        req.destroy();
      }
    });
    req.on("end", () => {
      let payload = {};
      try {
        payload = JSON.parse(body || "{}");
      } catch (err) {
        res.writeHead(400, { "Content-Type": "application/json; charset=utf-8" });
        res.end(JSON.stringify({ error: "JSON invalido" }));
        return;
      }

      const name = String(payload.name || "").trim();
      const description = String(payload.description || "").trim();
      const zipUrl = String(payload.zip_url || "").trim();

      if (!name || !zipUrl) {
        res.writeHead(400, { "Content-Type": "application/json; charset=utf-8" });
        res.end(JSON.stringify({ error: "name y zip_url son obligatorios" }));
        return;
      }

      const modules = readModules();
      modules.push({ name, description, zip_url: zipUrl });
      writeModules(modules, res);
    });
    return;
  }

  if (req.method === "DELETE") {
    const url = new URL(req.url, `http://${req.headers.host}`);
    const indexParam = url.searchParams.get("index");
    const name = url.searchParams.get("name");
    const zipUrl = url.searchParams.get("zip_url");

    const modules = readModules();

    if (indexParam !== null) {
      const index = Number(indexParam);
      if (!Number.isInteger(index) || index < 0 || index >= modules.length) {
        res.writeHead(404, { "Content-Type": "application/json; charset=utf-8" });
        res.end(JSON.stringify({ error: "Indice no encontrado" }));
        return;
      }
      modules.splice(index, 1);
      writeModules(modules, res);
      return;
    }

    if (name) {
      const idx = modules.findIndex(
        (m) => m.name === name && (!zipUrl || m.zip_url === zipUrl)
      );
      if (idx === -1) {
        res.writeHead(404, { "Content-Type": "application/json; charset=utf-8" });
        res.end(JSON.stringify({ error: "Modulo no encontrado" }));
        return;
      }
      modules.splice(idx, 1);
      writeModules(modules, res);
      return;
    }

    res.writeHead(400, { "Content-Type": "application/json; charset=utf-8" });
    res.end(JSON.stringify({ error: "Falta index o name" }));
    return;
  }

  res.writeHead(405, { "Content-Type": "application/json; charset=utf-8" });
  res.end(JSON.stringify({ error: "Metodo no permitido" }));
}

const server = http.createServer((req, res) => {
  const urlPath = decodeURIComponent(req.url.split("?")[0]);
  if (urlPath === "/api/modules") {
    handleModulesApi(req, res);
    return;
  }
  const safePath = path.normalize(urlPath).replace(/^(\.\.[\/\\])+/, "");
  let filePath = path.join(PUBLIC_DIR, safePath);

  if (urlPath === "/" || urlPath === "") {
    filePath = path.join(PUBLIC_DIR, "modules.html");
  }

  sendFile(res, filePath);
});

server.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
});
