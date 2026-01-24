#!/usr/bin/env python3
"""
Servidor HTTP básico para pruebas
Ejecutar: python3 servidor.py
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from datetime import datetime

class ManejadorSimple(BaseHTTPRequestHandler):
    
    def do_GET(self):
        """Maneja peticiones GET"""
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            html = """
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Servidor Activo</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        max-width: 600px;
                        margin: 50px auto;
                        padding: 20px;
                        background: #f0f0f0;
                    }
                    .container {
                        background: white;
                        padding: 30px;
                        border-radius: 10px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }
                    h1 { color: #2c3e50; }
                    .status { color: #27ae60; font-weight: bold; }
                    .info { margin: 20px 0; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>✅ Servidor Funcionando</h1>
                    <p class="status">Estado: ACTIVO</p>
                    <div class="info">
                        <p><strong>Rutas disponibles:</strong></p>
                        <ul>
                            <li><a href="/">/</a> - Página principal</li>
                            <li><a href="/api/status">/api/status</a> - Estado en JSON</li>
                            <li><a href="/test">/test</a> - Página de prueba</li>
                        </ul>
                    </div>
                </div>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
            
        elif self.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            respuesta = {
                'status': 'online',
                'timestamp': datetime.now().isoformat(),
                'mensaje': 'Servidor funcionando correctamente'
            }
            self.wfile.write(json.dumps(respuesta, indent=2).encode())
            
        elif self.path == '/test':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            html = """
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <title>Test</title>
            </head>
            <body>
                <h1>Página de Prueba</h1>
                <p>Esta es una ruta de prueba.</p>
                <a href="/">Volver al inicio</a>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
            
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(b'<h1>404 - Pagina no encontrada</h1>')
    
    def log_message(self, format, *args):
        """Sobrescribe para mostrar logs personalizados"""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {format % args}")


def ejecutar_servidor(puerto=8000):
    """Inicia el servidor HTTP"""
    direccion = ('', puerto)
    servidor = HTTPServer(direccion, ManejadorSimple)
    
    print(f"""
╔════════════════════════════════════════╗
║   Servidor HTTP Iniciado               ║
╚════════════════════════════════════════╝

🌐 Dirección: http://localhost:{puerto}
📱 También: http://127.0.0.1:{puerto}

Presiona Ctrl+C para detener el servidor
    """)
    
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 Servidor detenido")
        servidor.server_close()


if __name__ == '__main__':
    ejecutar_servidor()
