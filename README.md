# 🔗 Active Server - Sistema de Rastreo de Visitas

Sistema web moderno para rastrear visitas mediante links personalizados. Captura información de visitantes (IP, ciudad, fecha) y la almacena en Firebase Realtime Database. Incluye captura de fotos con la cámara del dispositivo.

## ✨ Características

- 🔐 **Autenticación segura** con Firebase Auth
- 🌐 **Rastreo de visitas** con captura de IP y geolocalización
- 📸 **Captura de fotos** usando la cámara del dispositivo
- ☁️ **Almacenamiento en la nube** con Firebase Storage
- 📊 **Dashboard en tiempo real** para visualizar visitas y fotos
- 📱 **Diseño responsive** optimizado para móviles
- 🎨 **Interfaz moderna** con animaciones y gradientes
- ⚡ **Feedback instantáneo** con estados de carga

## 🚀 Tecnologías

- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Backend**: Firebase (Authentication + Realtime Database + Storage)
- **APIs**: 
  - MediaDevices API (captura de cámara)
  - ipapi.co (geolocalización)
- **Deploy**: Cloudflare Workers (configurado con Wrangler)

## 📁 Estructura del Proyecto

```
Active-server/
├── index.html          # Página de login
├── home.html           # Dashboard principal
├── rastreo.html        # Panel de rastreo y estadísticas
├── camera.html         # Captura de fotos con cámara
├── view.html           # Endpoint de captura de visitas
├── style.css           # Estilos globales responsive
├── firebase-config.js  # Configuración de Firebase
└── wrangler.jsonc      # Configuración de Cloudflare Workers
```

## 🎯 Cómo Funciona

### Rastreo de Visitas
1. **Login**: El usuario inicia sesión con email/password
2. **Dashboard**: Accede al panel principal
3. **Generar Link**: Se crea un link único de rastreo
4. **Compartir**: El usuario comparte el link
5. **Captura**: Cuando alguien visita el link, se captura:
   - Dirección IP
   - Ciudad (vía geolocalización)
   - Fecha y hora
6. **Visualización**: Los datos aparecen en tiempo real en la tabla

### Captura de Fotos
1. **Acceder**: Desde el dashboard, clic en "Capturar Fotos"
2. **Permisos**: El navegador solicita acceso a la cámara
3. **Capturar**: Tomar foto con el botón de captura
4. **Preview**: Revisar la foto antes de subir
5. **Subir**: La foto se almacena en Firebase Storage
6. **Galería**: Ver todas las fotos capturadas
7. **Eliminar**: Clic en cualquier foto para eliminarla

## 🔧 Instalación

1. **Clonar el repositorio**
   ```bash
   git clone <tu-repositorio>
   cd Active-server
   ```

2. **Configurar Firebase**
   - Crea un proyecto en [Firebase Console](https://console.firebase.google.com/)
   - Habilita **Authentication** (Email/Password)
   - Habilita **Realtime Database**
   - Habilita **Storage** (para fotos)
   - Configura las reglas de seguridad (ver sección de Seguridad)
   - Copia las credenciales a `firebase-config.js`

3. **Ejecutar localmente**
   ```bash
   # Opción 1: Con Python
   python -m http.server 8000

   # Opción 2: Con Node.js
   npx serve

   # Opción 3: Con Live Server (VS Code)
   # Instala la extensión "Live Server" y haz clic derecho > "Open with Live Server"
   ```

4. **Acceder**
   - Abre `http://localhost:8000` en tu navegador

## 🌐 Deploy en Cloudflare Workers

```bash
# Instalar Wrangler CLI
npm install -g wrangler

# Login en Cloudflare
wrangler login

# Deploy
wrangler pages deploy .
```

## 🎨 Características del Diseño

### Responsive Design
- ✅ Mobile-first approach
- ✅ Breakpoints: 768px (tablet), 480px (móvil)
- ✅ Viewport optimizado para prevenir zoom en iOS
- ✅ Tablas con scroll horizontal en móviles

### Estética Moderna
- 🌈 Gradiente de fondo (púrpura a azul)
- 💫 Animaciones suaves (slide-up, hover effects)
- 🎯 Botones con efecto ripple
- 🔄 Loading spinners
- 📦 Cards con sombras elevadas

## 🔒 Seguridad

### Reglas de Realtime Database
Configura estas reglas en Firebase Console:

```json
{
  "rules": {
    "visitas": {
      "$uid": {
        ".read": "$uid === auth.uid",
        ".write": true
      }
    },
    "fotos": {
      "$uid": {
        ".read": "$uid === auth.uid",
        ".write": "$uid === auth.uid"
      }
    }
  }
}
```

### Reglas de Storage
Configura estas reglas en Firebase Console > Storage:

```
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    match /photos/{userId}/{allPaths=**} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
  }
}
```

**Características de seguridad:**
- Autenticación mediante Firebase Auth
- Cada usuario solo puede ver/editar sus propios datos
- Validación de permisos en Storage
- Meta tag `robots: noindex` en página de captura

- ✅ Chrome/Edge (últimas versiones)
- ✅ Firefox (últimas versiones)
- ✅ Safari (iOS 12+)
- ✅ Chrome Mobile / Safari Mobile

## 🛠️ Mejoras Futuras

- [ ] Agregar gráficos de estadísticas
- [ ] Exportar datos a CSV/Excel
- [ ] Filtros por fecha/país
- [ ] Múltiples links por usuario
- [ ] Notificaciones push
- [ ] Dark mode

## 📄 Licencia

Este proyecto es de código abierto. Úsalo libremente.

## 👨‍💻 Autor

Desarrollado con ❤️ para rastrear visitas de forma simple y efectiva.

---

**Nota**: Recuerda configurar las reglas de seguridad en Firebase Realtime Database:

```json
{
  "rules": {
    "visitas": {
      "$uid": {
        ".read": "$uid === auth.uid",
        ".write": true
      }
    }
  }
}
```
