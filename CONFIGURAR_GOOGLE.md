# 🚀 Guía Rápida: Configurar Google Login

## Paso 1: Crear Credenciales de Google

1. **Ve a Google Cloud Console**: https://console.cloud.google.com/

2. **Crea un proyecto nuevo** (o selecciona uno existente)

3. **Habilita la API de Google**:
   - En el menú lateral → APIs & Services → Library
   - Busca "Google+ API" y actívala

4. **Configura la pantalla de consentimiento**:
   - APIs & Services → OAuth consent screen
   - User Type: **External**
   - App name: **Cuidado con el pug**
   - User support email: Tu email
   - Developer contact: Tu email
   - Guarda y continúa
   - En Scopes, no necesitas agregar ninguno (ya vienen por defecto)
   - En Test users, agrega tu email para poder probar
   - Guarda

5. **Crea las credenciales OAuth**:
   - APIs & Services → Credentials
   - Click en "**+ CREATE CREDENTIALS**"
   - Selecciona "**OAuth client ID**"
   - Application type: **Web application**
   - Name: "Cuidado con el pug - Local"

   **Authorized JavaScript origins:**

   ```
   http://localhost:8000
   http://127.0.0.1:8000
   ```

   **Authorized redirect URIs:**

   ```
   http://localhost:8000/api/auth/google/callback
   http://127.0.0.1:8000/api/auth/google/callback
   ```

   - Click en **CREATE**

6. **Copia tus credenciales**:
   - Aparecerá un modal con tu **Client ID** y **Client Secret**
   - Cópialos (o descarga el JSON)

## Paso 2: Configurar el archivo .env

Edita el archivo `.env` en la raíz del proyecto:

```env
GOOGLE_CLIENT_ID=1234567890-abc123def456.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-tu_secret_aqui
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback
```

**Reemplaza** los valores con tus credenciales reales de Google.

## Paso 3: Reiniciar el Servidor

```bash
# Si el servidor está corriendo, presiona Ctrl+C para detenerlo
# Luego reinicia:
uvicorn app.main:app --reload
```

## Paso 4: Probar el Login

1. Abre http://localhost:8000/login
2. Click en "**Continuar con Google**"
3. Selecciona tu cuenta de Google
4. Si aparece "Google hasn't verified this app", click en:
   - "Advanced" → "Go to [App name] (unsafe)"
   - Esto es normal en modo desarrollo
5. Autoriza el acceso
6. ¡Listo! Deberías estar logueado

## ⚠️ Solución de Problemas

### Error: "Missing required parameter: client_id"

- Verifica que editaste el archivo `.env` con tus credenciales reales
- Reinicia el servidor después de editar `.env`

### Error: "redirect_uri_mismatch"

- Verifica que la URL de callback en Google Console coincida exactamente:
  `http://localhost:8000/api/auth/google/callback`
- No uses https en desarrollo local
- Asegúrate de no tener espacios al copiar

### "Google hasn't verified this app"

- Es normal en desarrollo
- Click en "Advanced" → "Go to [App name] (unsafe)"
- Para producción, deberás verificar la app

## 📝 Notas

- En modo desarrollo, solo funcionará con `localhost` o `127.0.0.1`
- Las cuentas de prueba deben estar agregadas en "Test users" en Google Console
- No compartas tus credenciales de Google en repositorios públicos
- Para producción, usa variables de entorno del servidor, no el archivo `.env`
