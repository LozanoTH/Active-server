# Solución al Error CORS de Firebase Storage

## 🔴 Problema
Firebase Storage está bloqueando las subidas desde tu dominio de Cloudflare Workers debido a la política CORS.

## ✅ Solución

### Opción 1: Usar Google Cloud Console (Recomendado)

1. **Instalar Google Cloud SDK** (si no lo tienes):
   - Descarga desde: https://cloud.google.com/sdk/docs/install
   - O usa Cloud Shell directamente en: https://console.cloud.google.com/

2. **Ejecutar comando CORS:**
   ```bash
   gsutil cors set cors.json gs://lozano-1690859356322.firebasestorage.app
   ```

3. **Verificar:**
   ```bash
   gsutil cors get gs://lozano-1690859356322.firebasestorage.app
   ```

---

### Opción 2: Usar Cloud Shell (Más Fácil)

1. Ve a: https://console.cloud.google.com/
2. Selecciona tu proyecto: `lozano-1690859356322`
3. Haz clic en el icono de **Cloud Shell** (arriba a la derecha)
4. Sube el archivo `cors.json` (botón de 3 puntos → Upload)
5. Ejecuta:
   ```bash
   gsutil cors set cors.json gs://lozano-1690859356322.firebasestorage.app
   ```

---

### Opción 3: Cambiar Reglas de Storage (Alternativa Temporal)

Si no puedes usar gsutil, cambia las reglas de Storage a:

```
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    match /{allPaths=**} {
      allow read, write: if true;
    }
  }
}
```

**⚠️ ADVERTENCIA:** Esto permite acceso público total. Solo úsalo temporalmente para probar.

---

### Opción 4: Usar Realtime Database en lugar de Storage

Si no puedes configurar CORS, podemos guardar las imágenes en base64 directamente en Realtime Database.

**Ventajas:**
- No requiere configuración CORS
- Funciona inmediatamente
- Más simple

**Desventajas:**
- Límite de tamaño por entrada (1MB)
- Más costoso en términos de ancho de banda

¿Quieres que implemente esta opción?

---

## 📝 Notas

- El archivo `cors.json` ya está creado en tu proyecto
- Reemplaza `lozano-1690859356322.firebasestorage.app` con tu bucket real si es diferente
- Después de aplicar CORS, espera 1-2 minutos para que se propague

## 🔍 Verificar que funcionó

Después de aplicar CORS, recarga tu página y prueba capturar una foto. El error debería desaparecer.
