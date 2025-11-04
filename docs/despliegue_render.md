# 🚀 Guía de Despliegue en Render

## 📋 Pre-requisitos

- ✅ Cuenta de GitHub con el repositorio
- ✅ Cuenta gratuita en [Render](https://render.com/)
- ✅ Archivo `service_account.json` de Google Cloud
- ✅ Usuarios y contraseñas para autenticación

---

## 🔧 Paso 1: Preparar el Repositorio

### 1.1 Verificar archivos necesarios

Asegúrate de que tu repositorio tiene:
- ✅ `requirements.txt`
- ✅ `render.yaml` (ya creado)
- ✅ `.gitignore` (archivos sensibles NO deben estar en GitHub)
- ✅ `.env.example` (template de variables de entorno)

### 1.2 Subir cambios a GitHub

```bash
# Agregar todos los archivos nuevos
git add .

# Commit
git commit -m "Preparación para despliegue en Render

- Agregado render.yaml con configuración
- Agregado .env.example con template de variables
- Documentación de despliegue completa

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Push a GitHub
git push origin feature/login-drive-facturacion

# O si ya hiciste merge a main:
git push origin main
```

---

## 🌐 Paso 2: Crear Web Service en Render

### 2.1 Conectar GitHub

1. Ve a https://dashboard.render.com/
2. Haz clic en **"New +"** → **"Web Service"**
3. Selecciona **"Build and deploy from a Git repository"**
4. Si es la primera vez, autoriza a Render a acceder a tu GitHub
5. Selecciona tu repositorio: `facturacion-finkargo`

### 2.2 Configuración Básica

En la pantalla de configuración, llena:

**Name (Nombre del servicio):**
```
facturacion-finkargo
```

**Region (Región):**
```
Oregon (US West) o la más cercana a Colombia
```

**Branch (Rama):**
```
main
```
(o `feature/login-drive-facturacion` si aún no has hecho merge)

**Root Directory (Directorio raíz):**
```
(dejar vacío - el proyecto está en la raíz)
```

**Runtime (Entorno):**
```
Python 3
```

**Build Command (Comando de construcción):**
```
pip install -r requirements.txt
```

**Start Command (Comando de inicio):**
```
streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true
```

**Instance Type (Tipo de instancia):**
```
Free (Gratis)
```

---

## 🔐 Paso 3: Configurar Variables de Entorno

### 3.1 Agregar Variables de Entorno

En la misma pantalla de configuración, baja hasta la sección **"Environment Variables"** y agrega:

#### Variable 1: drive_folder_id
```
Key:   drive_folder_id
Value: 1l3zOaD7Qt-KOHz97FLib4HwSEQqwjN2y
```

#### Variable 2: SERVICE_ACCOUNT_JSON
```
Key:   SERVICE_ACCOUNT_JSON
Value: (pegar el contenido COMPLETO del archivo config/service_account.json)
```

**⚠️ IMPORTANTE:**
- Abre tu archivo `config/service_account.json` local
- Copia TODO el contenido (incluyendo las llaves `{` `}`)
- Pégalo tal cual en el campo Value
- Render maneja correctamente JSON multilínea

Ejemplo de formato:
```json
{
  "type": "service_account",
  "project_id": "api-producto-476819",
  "private_key_id": "abc123...",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIE...\n-----END PRIVATE KEY-----\n",
  "client_email": "drive-and-sheets-access-sa@api-producto-476819.iam.gserviceaccount.com",
  ...
}
```

#### Variable 3: USERS (para autenticación)

Tienes dos opciones:

**Opción A - Variable JSON:**
```
Key:   USERS_JSON
Value: {"maria.gaitan": "facturacion2024", "maleja": "facturacion2024"}
```

**Opción B - Variables separadas** (si prefieres más seguridad):
```
Key:   USER_MARIA
Value: facturacion2024

Key:   USER_MALEJA
Value: facturacion2024
```

> **Nota:** Si usas Opción B, deberás modificar `modules/simple_auth.py` para leer estas variables en lugar del archivo secrets.toml

### 3.2 Variables Opcionales (para optimización)

```
Key:   PYTHON_VERSION
Value: 3.11.0

Key:   STREAMLIT_SERVER_MAX_UPLOAD_SIZE
Value: 200

Key:   STREAMLIT_SERVER_ENABLE_CORS
Value: false
```

---

## 🚀 Paso 4: Desplegar

1. **Revisa toda la configuración**
2. Haz clic en **"Create Web Service"**
3. Render comenzará a:
   - ✅ Clonar tu repositorio
   - ✅ Instalar dependencias (`requirements.txt`)
   - ✅ Ejecutar el comando de inicio
   - ✅ Asignar una URL pública

### 4.1 Monitorear el Deploy

En la consola verás logs como:
```
==> Cloning from https://github.com/tu-usuario/facturacion-finkargo...
==> Running build command: pip install -r requirements.txt
==> Installing streamlit...
==> Build successful 🎉
==> Starting service with: streamlit run app.py...
==> Your service is live at https://facturacion-finkargo.onrender.com
```

**⏱️ Tiempo estimado:** 3-5 minutos

---

## ✅ Paso 5: Verificar el Despliegue

### 5.1 Acceder a la Aplicación

Tu app estará disponible en:
```
https://facturacion-finkargo.onrender.com
```
(Render te proporcionará la URL exacta)

### 5.2 Checklist de Verificación

- [ ] La página carga correctamente
- [ ] El login funciona con tus credenciales
- [ ] Puedes conectar con Google Drive
- [ ] Puedes cargar archivos Excel
- [ ] El procesamiento de archivos funciona
- [ ] La búsqueda de PDFs funciona
- [ ] Los reportes se generan correctamente

---

## 🔧 Paso 6: Actualizar Secrets de Streamlit (Código)

Si tu código aún usa `st.secrets` para leer variables, necesitas actualizarlo para leer de variables de entorno en producción.

### 6.1 Modificar `modules/drive_manager.py`

Encuentra donde se lee el service account y cambia a:

```python
import os
import json

def get_service_account_credentials():
    """Obtiene las credenciales de Service Account"""
    # En producción (Render) lee de variable de entorno
    if os.getenv('SERVICE_ACCOUNT_JSON'):
        service_account_info = json.loads(os.getenv('SERVICE_ACCOUNT_JSON'))
        return service_account_info
    # En desarrollo lee del archivo
    else:
        with open('config/service_account.json', 'r') as f:
            return json.load(f)
```

### 6.2 Modificar lectura de drive_folder_id

```python
import os
import streamlit as st

# Leer de variable de entorno o secrets
drive_folder_id = os.getenv('drive_folder_id') or st.secrets.get("drive_folder_id", "")
```

### 6.3 Modificar autenticación de usuarios

En `modules/simple_auth.py`:

```python
import os
import streamlit as st
import json

def get_users():
    """Obtiene usuarios de entorno o secrets"""
    # Opción 1: Leer de variable JSON
    if os.getenv('USERS_JSON'):
        return json.loads(os.getenv('USERS_JSON'))
    # Opción 2: Leer de secrets.toml (desarrollo)
    elif 'users' in st.secrets:
        return dict(st.secrets.users)
    else:
        return {}
```

---

## ⚠️ Limitaciones del Plan Gratuito de Render

### Restricciones importantes:

1. **Sleep después de inactividad:**
   - La app se "duerme" después de 15 minutos sin uso
   - Primera visita después del sleep tarda ~1-2 minutos en despertar
   - **Solución:** Usa un servicio de "keep-alive" o actualiza a plan pagado

2. **Límite de horas mensuales:**
   - 750 horas de servicio gratis al mes
   - Suficiente para un servicio que corra 24/7

3. **Recursos limitados:**
   - 512 MB RAM
   - CPU compartida
   - Puede ser lento con archivos Excel muy grandes

4. **No hay dominio personalizado:**
   - URL será `*.onrender.com`
   - Dominio custom requiere plan pagado

---

## 🐛 Troubleshooting (Solución de Problemas)

### Error: "Application failed to respond"

**Causa:** Streamlit no arrancó correctamente

**Solución:**
1. Revisa los logs en Render Dashboard
2. Verifica que el Start Command sea correcto:
   ```
   streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true
   ```

### Error: "Module not found"

**Causa:** Falta una dependencia en `requirements.txt`

**Solución:**
1. Agrega la dependencia faltante a `requirements.txt`
2. Haz commit y push
3. Render redesplegará automáticamente

### Error: "FileNotFoundError: service_account.json"

**Causa:** El código busca el archivo en vez de la variable de entorno

**Solución:**
1. Implementa la lectura de variable de entorno (ver Paso 6)
2. O sube el archivo (NO recomendado por seguridad)

### Error de autenticación con Google Drive

**Causa:** Variable SERVICE_ACCOUNT_JSON mal formateada

**Solución:**
1. Verifica que copiaste el JSON completo
2. Asegúrate de que el `private_key` mantenga los `\n`
3. Verifica que no haya espacios extras al inicio/final

### La aplicación está muy lenta

**Causa:** Plan gratuito con recursos limitados

**Solución:**
1. Optimiza el código (caché, lazy loading)
2. Reduce el tamaño de archivos procesados
3. Considera upgrade a plan pagado ($7/mes)

---

## 🔄 Actualizar la Aplicación (CI/CD Automático)

Render tiene **despliegue automático** configurado por defecto:

1. Haz cambios en tu código local
2. Commit y push a GitHub:
   ```bash
   git add .
   git commit -m "Actualización de features"
   git push origin main
   ```
3. Render detecta el cambio automáticamente
4. Redespliega en ~3-5 minutos
5. Tu app se actualiza automáticamente

**Ver progreso:**
- Ve a Render Dashboard → Tu servicio → Pestaña "Events"

---

## 🎯 Checklist Final de Despliegue

### Antes de desplegar:
- [ ] `.gitignore` protege archivos sensibles
- [ ] `requirements.txt` está actualizado
- [ ] `render.yaml` está configurado
- [ ] Código lee variables de entorno en producción
- [ ] Todos los cambios están en GitHub

### Durante el despliegue:
- [ ] Render conectado a GitHub
- [ ] Variables de entorno configuradas
- [ ] SERVICE_ACCOUNT_JSON pegado correctamente
- [ ] Build command correcto
- [ ] Start command correcto

### Después del despliegue:
- [ ] App carga sin errores
- [ ] Login funciona
- [ ] Conexión a Drive funciona
- [ ] Funcionalidades principales funcionan
- [ ] URL compartida con usuarios

---

## 📞 Soporte

**Documentación de Render:**
- https://render.com/docs/web-services

**Documentación de Streamlit:**
- https://docs.streamlit.io/deploy

**Issues del proyecto:**
- Crear issue en el repositorio de GitHub

---

## 🎉 ¡Listo!

Tu aplicación ahora está desplegada y accesible desde cualquier lugar con:
- ✅ HTTPS automático
- ✅ Despliegue continuo desde GitHub
- ✅ Variables de entorno seguras
- ✅ Monitoreo de logs
- ✅ URL pública compartible

**URL de tu app:**
```
https://facturacion-finkargo.onrender.com
```

---

**Fecha:** 04 Enero 2025
**Plataforma:** Render (Free Tier)
**Versión:** 1.1.0
