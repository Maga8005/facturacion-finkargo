# Sistema de Autenticación - Facturación Finkargo

## Descripción General

El sistema de facturación implementa autenticación OAuth con Google para garantizar que solo el equipo de facturación autorizado pueda acceder a la aplicación.

## Características

- ✅ Autenticación con Google OAuth 2.0
- ✅ Lista blanca de usuarios autorizados
- ✅ Interfaz de login personalizada
- ✅ Cierre de sesión seguro
- ✅ Validación de permisos en tiempo real

## Arquitectura

### Componentes

1. **AuthManager** (`modules/auth.py`): Gestiona toda la lógica de autenticación
2. **Configuración** (`.streamlit/secrets.toml`): Almacena credenciales y lista de usuarios
3. **Integración** (`app.py`): Protege la aplicación principal

### Flujo de Autenticación

```
Usuario accede → Login con Google → Validación de email → Acceso permitido/denegado
```

## Configuración

### 1. Credenciales OAuth

Las credenciales de Google OAuth se configuran en dos lugares:

**A) Archivo de credenciales JSON** (`config/google_credentials.json`):

1. Copia el archivo de ejemplo:
   ```bash
   cp config/google_credentials.json.example config/google_credentials.json
   ```

2. Edita `config/google_credentials.json` con tus credenciales:
   ```json
   {
     "web": {
       "client_id": "tu-client-id.apps.googleusercontent.com",
       "client_secret": "tu-client-secret",
       "redirect_uris": ["http://localhost:8501"],
       "auth_uri": "https://accounts.google.com/o/oauth2/auth",
       "token_uri": "https://oauth2.googleapis.com/token",
       "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs"
     }
   }
   ```

**B) Configuración en secrets.toml** (`.streamlit/secrets.toml`):

```toml
redirect_uri = "http://localhost:8501"
```

### 2. Usuarios Autorizados

Para agregar o quitar usuarios del equipo de facturación, edita `.streamlit/secrets.toml`:

```toml
[authorized_users]
emails = [
    "usuario1@finkargo.com",
    "usuario2@finkargo.com",
    "usuario3@finkargo.com",
]
```

**Importante**:
- Los emails deben ser exactos (incluyendo mayúsculas/minúsculas)
- Cada email debe estar entre comillas
- Separar emails con comas
- Pueden ser cuentas de cualquier dominio (@finkargo.com, @gmail.com, etc.)

## Gestión de Usuarios

### Agregar un Usuario

1. Abre `.streamlit/secrets.toml`
2. Añade el email a la lista `authorized_users.emails`
3. Guarda el archivo
4. Reinicia la aplicación con `streamlit run app.py`

Ejemplo:
```toml
[authorized_users]
emails = [
    "usuario1@finkargo.com",
    "usuario2@finkargo.com",
    "nuevousuario@finkargo.com",  # Usuario nuevo
]
```

### Remover un Usuario

1. Abre `.streamlit/secrets.toml`
2. Elimina o comenta (con `#`) el email del usuario
3. Guarda el archivo
4. Reinicia la aplicación

Ejemplo:
```toml
[authorized_users]
emails = [
    "usuario1@finkargo.com",
    # "usuarioremovido@finkargo.com",  # Usuario deshabilitado
    "usuario3@finkargo.com",
]
```

## Uso

### Para Usuarios Finales

1. **Acceder a la aplicación**: Navega a la URL de la aplicación
2. **Iniciar sesión**: Haz clic en el botón "Login with Google"
3. **Seleccionar cuenta**: Elige tu cuenta de Google autorizada
4. **Usar la aplicación**: Una vez autenticado, accede a todas las funcionalidades
5. **Cerrar sesión**: Usa el botón "🚪 Cerrar Sesión" en el sidebar

### Para Administradores

#### Verificar Usuario Autenticado

La información del usuario se muestra en el sidebar:
- Nombre del usuario
- Email de la cuenta
- Botón de cierre de sesión

#### Solucionar Problemas de Acceso

Si un usuario autorizado no puede acceder:

1. Verificar que el email esté correctamente escrito en `secrets.toml`
2. Confirmar que las credenciales OAuth estén activas
3. Verificar que el usuario esté usando la cuenta de Google correcta
4. Reiniciar la aplicación

## Seguridad

### Mejores Prácticas

1. **No compartir credenciales**: Las credenciales OAuth en `secrets.toml` son sensibles
2. **Mantener actualizada la lista**: Remover usuarios que ya no forman parte del equipo
3. **Revisar accesos periódicamente**: Auditar la lista de usuarios autorizados
4. **Usar HTTPS en producción**: Para conexiones seguras
5. **No versionar secrets.toml**: Está en `.gitignore` por seguridad

### Archivo secrets.toml en .gitignore

El archivo `.streamlit/secrets.toml` está excluido del control de versiones para proteger las credenciales. **Nunca** lo subas al repositorio.

## Estructura del Código

### AuthManager (modules/auth.py)

```python
class AuthManager:
    def __init__()              # Inicializa con credenciales
    def login()                 # Maneja el proceso de login
    def is_authenticated()      # Verifica autenticación y autorización
    def is_authorized(email)    # Verifica si email está autorizado
    def logout()                # Cierra sesión
    def get_user_info()         # Obtiene info del usuario
```

### Integración en app.py

```python
# Inicializar autenticación
auth_manager = AuthManager()

# Verificar acceso
if not auth_manager.login():
    st.stop()  # Detener si no autorizado

# Mostrar info del usuario
auth_manager.show_user_info_sidebar()
```

## Troubleshooting

### Error: "Falta la clave en secrets.toml"

**Causa**: Configuración incompleta en secrets.toml

**Solución**: Verificar que existan todas las claves requeridas:
- `client_id`
- `client_secret`
- `redirect_uri`
- `authorized_users.emails`

### Error: "Acceso No Autorizado"

**Causa**: El email del usuario no está en la lista de autorizados

**Solución**:
1. Agregar el email a `authorized_users.emails` en secrets.toml
2. Reiniciar la aplicación

### El botón de login no aparece

**Causa**: Error en la carga de streamlit-google-auth

**Solución**:
```bash
pip install --upgrade streamlit-google-auth
```

## Deployment en Producción

Para desplegar en Streamlit Cloud:

1. **Configurar Secrets en Streamlit Cloud**:
   - Ve a App Settings → Secrets
   - Copia el contenido de `.streamlit/secrets.toml`
   - Pega en el editor de secrets

2. **Actualizar redirect_uri**:
   ```toml
   redirect_uri = "https://tu-app.streamlit.app"
   ```

3. **Configurar OAuth en Google Cloud**:
   - Agregar la URL de producción a las URIs autorizadas
   - Actualizar el origen autorizado

## Soporte

Para problemas o consultas sobre el sistema de autenticación:
- Revisar esta documentación
- Consultar logs de la aplicación
- Contactar al administrador del sistema

---

**Última actualización**: Octubre 2024
**Versión**: 1.0
