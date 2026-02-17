# Configuración de Google OAuth

Para habilitar el inicio de sesión con Google, sigue estos pasos:

## 1. Crear un proyecto en Google Cloud Console

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. Habilita la API de Google+ (Google+ API)

## 2. Configurar OAuth 2.0

1. Ve a **APIs & Services** > **Credentials**
2. Click en **Create Credentials** > **OAuth client ID**
3. Si es tu primera vez, configura la pantalla de consentimiento:
   - User Type: External
   - App name: "Cuidado con el pug"
   - User support email: tu email
   - Developer contact: tu email
   - Scopes: `.../auth/userinfo.email`, `.../auth/userinfo.profile`, `openid`
   - Test users: agrega tu email de prueba

4. Crear OAuth client ID:
   - Application type: **Web application**
   - Name: "Cuidado con el pug - Web"
   - Authorized JavaScript origins:
     - `http://localhost:8000`
     - `http://127.0.0.1:8000`
   - Authorized redirect URIs:
     - `http://localhost:8000/api/auth/google/callback`
     - `http://127.0.0.1:8000/api/auth/google/callback`

5. Guarda el **Client ID** y **Client Secret**

## 3. Configurar variables de entorno

Crea o edita el archivo `.env` en la raíz del proyecto:

```env
GOOGLE_CLIENT_ID=tu_client_id_aqui.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=tu_client_secret_aqui
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback
```

## 4. Migrar la base de datos

Ejecuta el servidor para que se creen las nuevas columnas en la tabla `users`:

```bash
python -m uvicorn app.main:app --reload
```

Las columnas `google_id` y `avatar_url` se agregarán automáticamente.

## 5. Probar el login

1. Inicia el servidor: `uvicorn app.main:app --reload`
2. Abre: `http://localhost:8000/login`
3. Click en "Continuar con Google"
4. Selecciona tu cuenta de Google
5. Autoriza la aplicación
6. Serás redirigido de vuelta con la sesión iniciada

## Notas importantes

- En desarrollo, Google puede mostrar una advertencia de "App no verificada" - click en "Avanzado" y "Ir a [nombre app] (no seguro)"
- Para producción, deberás verificar tu aplicación en Google Cloud Console
- Los usuarios pueden iniciar sesión con Google sin necesidad de contraseña
- Si un usuario ya existe con el mismo email, su cuenta se vinculará automáticamente con Google
