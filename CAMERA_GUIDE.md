# 📸 Guía de Uso - Captura de Fotos

## Configuración Inicial

### 1. Habilitar Firebase Storage

1. Ve a [Firebase Console](https://console.firebase.google.com/)
2. Selecciona tu proyecto
3. En el menú lateral, ve a **Build** > **Storage**
4. Haz clic en **Get Started**
5. Selecciona las reglas de seguridad (usa modo de prueba por ahora)
6. Selecciona la ubicación del servidor (elige la más cercana)
7. Haz clic en **Done**

### 2. Configurar Reglas de Seguridad

#### Realtime Database
Ve a **Realtime Database** > **Rules** y pega:

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

#### Storage
Ve a **Storage** > **Rules** y pega:

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

---

## Cómo Usar la Función

### Paso 1: Acceder a la Cámara
1. Inicia sesión en la aplicación
2. En el dashboard, haz clic en el botón verde **"Capturar Fotos"**
3. Serás redirigido a la página de cámara

### Paso 2: Iniciar la Cámara
1. Haz clic en **"Iniciar Cámara"**
2. El navegador te pedirá permiso para acceder a la cámara
3. Haz clic en **"Permitir"**
4. La cámara se activará automáticamente

**Nota:** En dispositivos móviles, se usará la cámara trasera por defecto.

### Paso 3: Capturar Foto
1. Apunta la cámara al objeto que deseas fotografiar
2. Haz clic en **"Capturar Foto"** (botón verde)
3. La foto se mostrará en la vista previa

### Paso 4: Revisar y Subir
1. Revisa la foto en la vista previa
2. Si te gusta, haz clic en **"Subir Foto"**
3. Si no te gusta, haz clic en **"Descartar"** y toma otra

### Paso 5: Ver Galería
- Las fotos subidas aparecerán automáticamente en la galería
- Las fotos más recientes aparecen primero
- Cada foto muestra la fecha y hora de captura

### Paso 6: Eliminar Fotos
1. Haz clic en cualquier foto de la galería
2. Confirma que deseas eliminarla
3. La foto se eliminará de Firebase Storage y de la base de datos

---

## Características Técnicas

### MediaDevices API
- Acceso a cámara frontal y trasera
- Resolución ideal: 1280x720
- Formato de imagen: JPEG con 80% de calidad
- Compatible con navegadores modernos

### Firebase Storage
- Almacenamiento ilimitado (según plan de Firebase)
- Organización por usuario: `/photos/{userId}/`
- Nombres únicos usando timestamp
- URLs de descarga permanentes

### Seguridad
- Solo usuarios autenticados pueden subir fotos
- Cada usuario solo ve sus propias fotos
- Validación de permisos en Storage
- Eliminación segura de archivos

---

## Solución de Problemas

### La cámara no se inicia
**Problema:** El navegador no solicita permisos o muestra error.

**Soluciones:**
1. Verifica que estés usando HTTPS (o localhost)
2. Revisa los permisos del navegador en Configuración
3. Intenta con otro navegador (Chrome/Firefox)
4. En móvil, verifica permisos de la app del navegador

### Error al subir foto
**Problema:** La foto no se sube a Firebase.

**Soluciones:**
1. Verifica que Firebase Storage esté habilitado
2. Revisa las reglas de seguridad en Storage
3. Verifica tu conexión a Internet
4. Revisa la consola del navegador (F12) para errores

### No veo mis fotos en la galería
**Problema:** Las fotos no aparecen después de subirlas.

**Soluciones:**
1. Refresca la página (F5)
2. Verifica las reglas de Realtime Database
3. Revisa que estés usando el mismo usuario
4. Verifica la consola para errores de Firebase

### Cámara borrosa o mala calidad
**Problema:** Las fotos salen borrosas.

**Soluciones:**
1. Limpia el lente de la cámara
2. Asegúrate de tener buena iluminación
3. Mantén el dispositivo estable al capturar
4. Espera a que la cámara enfoque antes de capturar

---

## Compatibilidad de Navegadores

| Navegador | Desktop | Mobile | Notas |
|-----------|---------|--------|-------|
| Chrome | ✅ | ✅ | Funciona perfectamente |
| Firefox | ✅ | ✅ | Funciona perfectamente |
| Safari | ✅ | ✅ | Requiere iOS 11+ |
| Edge | ✅ | ✅ | Funciona perfectamente |
| Opera | ✅ | ✅ | Funciona perfectamente |

**Requisitos:**
- Navegador con soporte para MediaDevices API
- Conexión a Internet
- Permisos de cámara habilitados
- HTTPS (o localhost para desarrollo)

---

## Consejos de Uso

### Para Mejores Resultados:
1. **Iluminación:** Usa buena luz natural o artificial
2. **Estabilidad:** Mantén el dispositivo firme
3. **Enfoque:** Espera a que la cámara enfoque
4. **Distancia:** No te acerques demasiado al objeto

### Gestión de Fotos:
1. **Organización:** Las fotos se ordenan por fecha automáticamente
2. **Eliminación:** Elimina fotos innecesarias para ahorrar espacio
3. **Backup:** Considera descargar fotos importantes
4. **Privacidad:** Solo tú puedes ver tus fotos

---

## Límites y Cuotas

### Firebase Free Plan (Spark):
- **Storage:** 5 GB total
- **Descargas:** 1 GB/día
- **Operaciones:** 50,000 lecturas/día, 20,000 escrituras/día

### Recomendaciones:
- Elimina fotos antiguas que no necesites
- Comprime fotos grandes antes de subir
- Considera actualizar a plan Blaze si necesitas más espacio

---

## Próximas Mejoras

Funcionalidades planeadas:
- [ ] Filtros y edición de fotos
- [ ] Compartir fotos por link
- [ ] Descargar fotos en lote
- [ ] Organización por álbumes
- [ ] Búsqueda por fecha
- [ ] Compresión automática de imágenes

---

**¿Necesitas ayuda?** Revisa la consola del navegador (F12) para ver errores detallados.
