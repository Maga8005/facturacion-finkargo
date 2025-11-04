# Actualización del Sistema de Autenticación

## Resumen de Cambios

Se ha reemplazado el sistema de autenticación OAuth por un sistema más simple y se configuró el acceso a Google Drive mediante cuenta de servicio.

## 🔄 Cambios Implementados

### 1. **Nuevo Sistema de Autenticación**

**Antes**: OAuth con Google (usuarios de Google)
**Ahora**: Login simple con usuario/contraseña

**Archivo**: `modules/simple_auth.py`

- Login con formulario de usuario y contraseña
- Usuarios configurados en `.streamlit/secrets.toml`
- Contraseñas en texto plano (para desarrollo) o SHA256 hash
- Sesión persistente durante el uso

### 2. **Acceso a Google Drive con Cuenta de Servicio**

**Antes**: OAuth individual (cada usuario autoriza)
**Ahora**: Cuenta de servicio única con permisos permanentes

**Cuenta de servicio**: `drive-and-sheets-access-sa@api-producto-476819.iam.gserviceaccount.com`

**Archivo de credenciales**: `config/service_account.json`

**Ventajas**:
- No requiere autorización manual cada vez
- Acceso automático al Drive compartido
- Sin conflictos de scopes
- Más simple de mantener

### 3. **Archivos Modificados**

```
✅ modules/simple_auth.py (NUEVO)
   - Sistema de autenticación simple

✅ modules/drive_manager.py (ACTUALIZADO)
   - Ahora usa cuenta de servicio
   - Método _authenticate_with_service_account()

✅ app.py (ACTUALIZADO)
   - Usa SimpleAuthManager en lugar de AuthManager
   - Login simplificado

✅ config/service_account.json (NUEVO)
   - Credenciales de la cuenta de servicio
   - ⚠️ En .gitignore (no se versiona)

✅ .streamlit/secrets.toml (ACTUALIZADO)
   - Configuración de usuarios autorizados
   - Eliminadas credenciales OAuth antiguas

✅ .gitignore (ACTUALIZADO)
   - Agregado config/service_account.json
```

## 📋 Configuración de Usuarios

### Agregar un Usuario

Edita `.streamlit/secrets.toml`:

```toml
[users]
"nombre.usuario" = "contraseña123"
"maria.gaitan" = "facturacion2024"
"maleja" = "facturacion2024"
```

### Cambiar Contraseña

Simplemente edita el valor en `secrets.toml`:

```toml
[users]
"maria.gaitan" = "nueva_contraseña_segura"
```

### Usar Contraseñas Hasheadas (Recomendado para Producción)

```python
import hashlib
password = "mi_contraseña"
hash_pass = hashlib.sha256(password.encode()).hexdigest()
print(hash_pass)
```

Luego en `secrets.toml`:

```toml
[users]
"usuario" = "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"  # hash de "password"
```

## 🔐 Configuración de Google Drive

### Cuenta de Servicio

La aplicación ahora usa una cuenta de servicio que tiene:

- **Email**: drive-and-sheets-access-sa@api-producto-476819.iam.gserviceaccount.com
- **Permisos**: Editor en la carpeta compartida de Drive
- **Scopes**: `https://www.googleapis.com/auth/drive`

### Folder ID

Configurado en `.streamlit/secrets.toml`:

```toml
drive_folder_id = "1PMdI6oYpPO3_79Lz5eJpWvdIZCgrrka7"
```

## 🚀 Uso de la Aplicación

### 1. Iniciar Sesión

1. Abre la aplicación: `streamlit run app.py`
2. Ingresa tu usuario (ej: "maria.gaitan")
3. Ingresa tu contraseña (ej: "facturacion2024")
4. Haz clic en "Iniciar Sesión"

### 2. Cerrar Sesión

- Usa el botón "🚪 Cerrar Sesión" en el sidebar
- O usa el botón "🚪 Salir" en la esquina superior derecha

## ⚠️ Seguridad

### Archivos Sensibles (NO versionados en Git)

```
✓ .streamlit/secrets.toml        → Usuarios y contraseñas
✓ config/service_account.json    → Credenciales de Google
✓ token.json                      → (Ya no se usa)
```

### Para Producción

1. **Cambiar todas las contraseñas** de las de prueba
2. **Usar contraseñas hasheadas** en lugar de texto plano
3. **Configurar secrets en Streamlit Cloud**:
   - Ve a App Settings → Secrets
   - Copia el contenido de `.streamlit/secrets.toml`
   - Pega en el editor de secrets

## 📝 Archivos Ya No Necesarios

Los siguientes archivos/módulos ya no se usan:

- `modules/auth.py` (OAuth - puede eliminarse)
- `config/google_credentials.json` (OAuth - puede eliminarse)
- `token.json` (OAuth - ya eliminado)

## 🔧 Troubleshooting

### Error: "No se encontró el archivo de cuenta de servicio"

**Solución**: Verifica que existe `config/service_account.json`

### Error: "Error al autenticar con cuenta de servicio"

**Solución**:
1. Verifica que el JSON de credenciales sea válido
2. Verifica que la cuenta de servicio tenga permisos en la carpeta de Drive

### Error: "Usuario o contraseña incorrectos"

**Solución**:
1. Verifica que el usuario existe en `[users]` en secrets.toml
2. Verifica que la contraseña sea correcta
3. Si usas hash, verifica que el hash sea correcto

## 📊 Estado del Proyecto

```
✅ Autenticación simple implementada
✅ Acceso a Drive con cuenta de servicio configurado
✅ Login funcional
✅ Logout funcional
✅ Documentación actualizada
⏳ Pendiente: Pruebas de acceso al Drive compartido
```

---

**Fecha**: Octubre 2024
**Versión**: 2.0 - Sistema de autenticación simple con cuenta de servicio
