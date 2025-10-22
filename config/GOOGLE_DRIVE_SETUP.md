# Configuración de Google Drive API

Esta guía explica cómo configurar las credenciales de Google Drive para usar la funcionalidad de búsqueda y descarga de PDFs.

## Paso 1: Crear Proyecto en Google Cloud Console

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. Anota el **Project ID**

## Paso 2: Habilitar Google Drive API

1. En el menú lateral, ve a **APIs & Services** > **Library**
2. Busca "Google Drive API"
3. Haz clic en **Enable** (Habilitar)

## Paso 3: Configurar Pantalla de Consentimiento OAuth

1. Ve a **APIs & Services** > **OAuth consent screen**
2. Selecciona **Internal** (si es para uso interno) o **External**
3. Completa la información requerida:
   - **App name**: Sistema de Facturación Finkargo
   - **User support email**: Tu email
   - **Developer contact**: Tu email
4. En **Scopes**, agrega:
   - `https://www.googleapis.com/auth/drive.readonly`
   - `https://www.googleapis.com/auth/drive.file`
5. Guarda y continúa

## Paso 4: Crear Credenciales OAuth 2.0

1. Ve a **APIs & Services** > **Credentials**
2. Haz clic en **+ CREATE CREDENTIALS** > **OAuth client ID**
3. Selecciona **Application type**: **Web application**
4. Configura:
   - **Name**: Facturacion Finkargo Client
   - **Authorized JavaScript origins**:
     - `http://localhost:8501`
     - `http://localhost` (si usas otro puerto)
   - **Authorized redirect URIs**:
     - `http://localhost:8501`
     - `http://localhost:8501/component/streamlit_google_auth.login_button/`
5. Haz clic en **CREATE**
6. Descarga el archivo JSON de credenciales

## Paso 5: Configurar en Streamlit

### Opción A: Usar secrets.toml (Recomendado para desarrollo local)

1. Crea el archivo `.streamlit/secrets.toml` si no existe:

```toml
[google_oauth]
client_id = "TU_CLIENT_ID.apps.googleusercontent.com"
client_secret = "TU_CLIENT_SECRET"
redirect_uri = "http://localhost:8501"
```

2. Reemplaza `TU_CLIENT_ID` y `TU_CLIENT_SECRET` con los valores del archivo JSON descargado

### Opción B: Variables de Entorno (Para producción)

```bash
export GOOGLE_OAUTH_CLIENT_ID="TU_CLIENT_ID.apps.googleusercontent.com"
export GOOGLE_OAUTH_CLIENT_SECRET="TU_CLIENT_SECRET"
export GOOGLE_OAUTH_REDIRECT_URI="http://localhost:8501"
```

## Paso 6: Estructura del archivo secrets.toml

Ejemplo completo del archivo `.streamlit/secrets.toml`:

```toml
# Google OAuth para autenticación
[google_oauth]
client_id = "123456789-abc123def456.apps.googleusercontent.com"
client_secret = "GOCSPX-abc123def456xyz789"
redirect_uri = "http://localhost:8501"

# Configuración opcional de carpeta de Drive
[drive_config]
default_folder_id = ""  # Dejar vacío para buscar en todo el Drive
```

## Paso 7: Verificar Configuración

1. Ejecuta la aplicación: `streamlit run app.py`
2. Ve al tab "Buscar en Drive"
3. Haz clic en "Conectar con Google Drive"
4. Autoriza la aplicación en la ventana emergente
5. Si todo está correcto, verás el mensaje "Conectado exitosamente"

## Permisos Requeridos

La aplicación solicita los siguientes permisos:

- **Ver archivos de Google Drive**: Para buscar PDFs
- **Descargar archivos**: Para descargar los PDFs encontrados

## Solución de Problemas

### Error: "redirect_uri_mismatch"

**Solución**: Verifica que las URIs autorizadas en Google Cloud Console coincidan exactamente con las configuradas en secrets.toml

### Error: "invalid_client"

**Solución**: Verifica que el client_id y client_secret sean correctos

### Error: "access_denied"

**Solución**: Verifica que el usuario tenga acceso al proyecto y que la pantalla de consentimiento esté configurada correctamente

### La autenticación no funciona en localhost

**Solución**: Asegúrate de que las siguientes URIs estén autorizadas:
- `http://localhost:8501`
- `http://localhost:8501/component/streamlit_google_auth.login_button/`

## Seguridad

⚠️ **IMPORTANTE**:
- **NUNCA** subas el archivo `secrets.toml` a Git
- Agrega `.streamlit/secrets.toml` al archivo `.gitignore`
- Para producción, usa variables de entorno o servicios de gestión de secretos

## Notas Adicionales

- Las credenciales OAuth solo funcionan con los dominios/URIs autorizados
- Para uso en producción, actualiza las URIs autorizadas con tu dominio real
- Los tokens de acceso expiran después de cierto tiempo y se renuevan automáticamente
