# 🔧 Troubleshooting - Render Deploy

## Problemas Comunes y Soluciones

### ❌ Error: "can't encode character" o UnicodeEncodeError

**Síntoma:**
```
UnicodeEncodeError: 'charmap' codec can't encode character
```

**Causa:** Emojis en código Python ejecutándose en Windows

**Solución:**
Agregar al inicio del archivo Python:
```python
import io
import sys

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
```

---

### ❌ Error: "KeyError: 'users'" o "st.secrets['users']"

**Síntoma:**
```
File "modules/simple_auth.py", line 22, in __init__
    self.users = dict(st.secrets["users"])
KeyError: 'users'
```

**Causa:** El código intenta leer `st.secrets` pero en producción las variables están en environment variables.

**Solución:**
1. Usar el helper `config_helper.py`:
```python
from modules.config_helper import get_users

# En lugar de:
self.users = dict(st.secrets["users"])

# Usar:
self.users = get_users()
```

2. Verificar que la variable `USERS_JSON` esté configurada en Render Dashboard → Environment

---

### ❌ Error: "FileNotFoundError: service_account.json"

**Síntoma:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'config/service_account.json'
```

**Causa:** El código busca un archivo local que no existe en producción.

**Solución:**
1. Usar el helper `config_helper.py`:
```python
from modules.config_helper import get_service_account_info

# En lugar de:
with open('config/service_account.json', 'r') as f:
    service_account = json.load(f)

# Usar:
service_account = get_service_account_info()
```

2. Verificar que `SERVICE_ACCOUNT_JSON` esté configurada en Render con el JSON completo

---

### ❌ Render no detecta cambios después de push

**Síntoma:**
- Hiciste push a GitHub
- Render no inicia deploy automático
- El código en producción es viejo

**Causa:** Render puede no estar detectando el webhook de GitHub

**Solución:**

**Opción 1 - Manual Deploy:**
1. Ve a Render Dashboard → Tu servicio
2. Clic en **"Manual Deploy"** → **"Clear build cache & deploy"**

**Opción 2 - Verificar rama:**
1. Render Dashboard → Settings → Branch
2. Verifica que esté configurado en `main` (o la rama correcta)
3. Verifica que los cambios estén en esa rama en GitHub

**Opción 3 - Reconectar GitHub:**
1. Render Dashboard → Settings
2. Scroll hasta "Repository"
3. Clic en "Disconnect" y vuelve a conectar

---

### ❌ Error: "Authentication failed" con Google Drive

**Síntoma:**
```
Error al autenticar con cuenta de servicio
```

**Causa:** Variable `SERVICE_ACCOUNT_JSON` mal formateada

**Solución:**
1. Verifica que el JSON esté completo (incluyendo `{` y `}`)
2. Verifica que el `private_key` tenga los `\n` literales:
```json
"private_key": "-----BEGIN PRIVATE KEY-----\nMIIE...\n-----END PRIVATE KEY-----\n"
```
3. NO agregues comillas extra alrededor del JSON
4. Render acepta JSON multilínea, copia y pega tal cual

**Verificar formato:**
```bash
# El JSON debe verse así en la variable de entorno:
{
  "type": "service_account",
  "project_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  ...
}
```

---

### ⚠️ App muy lenta o "sleeping"

**Síntoma:**
- Primera visita después de inactividad tarda 1-2 minutos
- App se "duerme"

**Causa:** Plan gratuito de Render se duerme después de 15 min sin uso

**Solución:**

**Opción 1 - Aceptar el comportamiento (gratis):**
- Avisar a usuarios que primera carga puede tardar
- Suficiente para uso interno ocasional

**Opción 2 - Keep-alive service (gratis):**
- Usa un servicio como UptimeRobot o Cron-job.org
- Ping cada 10 minutos a tu URL

**Opción 3 - Upgrade a plan pagado:**
- Plan Starter: $7/mes
- No se duerme
- Más RAM y CPU

---

### ❌ Error: "Module not found" o ImportError

**Síntoma:**
```
ModuleNotFoundError: No module named 'pandas'
```

**Causa:** Falta dependencia en `requirements.txt`

**Solución:**
1. Agregar la dependencia a `requirements.txt`
2. Commit y push
3. Render redesplegará automáticamente

**Verificar dependencias locales:**
```bash
pip freeze > requirements_temp.txt
# Comparar con requirements.txt
```

---

### 🔐 Error: "No se encontraron usuarios configurados"

**Síntoma:**
Mensaje en la app: "❌ No se encontraron usuarios configurados"

**Causa:** Variable `USERS_JSON` no configurada o mal formateada

**Solución:**
1. Ve a Render Dashboard → Environment
2. Verifica que existe la variable `USERS_JSON`
3. Formato correcto:
```json
{"maria.gaitan": "facturacion2024", "maleja": "facturacion2024"}
```
4. SIN comillas externas, solo el objeto JSON

---

### 📊 Ver logs detallados en Render

**Para debugging:**

1. **Logs en tiempo real:**
   - Render Dashboard → Tu servicio → **Logs**
   - Se actualiza automáticamente

2. **Logs de deploy:**
   - Render Dashboard → Tu servicio → **Events**
   - Ver cada deploy con su salida completa

3. **Logs de errores:**
   - Los errores de Python aparecen con stack trace completo
   - Buscar línea específica del error

---

### 🔄 Rollback a versión anterior

**Si un deploy rompe la app:**

**Opción 1 - Desde Render:**
1. Render Dashboard → Events
2. Encuentra el deploy que funcionaba
3. Clic en **"Rollback to this deploy"**

**Opción 2 - Desde Git:**
```bash
# Ver commits recientes
git log --oneline -5

# Revertir al commit anterior
git revert HEAD

# O reset (más agresivo)
git reset --hard COMMIT_ID
git push origin main --force
```

---

### ⚡ Build muy lento

**Síntoma:**
- Build tarda más de 5 minutos
- Timeout

**Solución:**
1. Optimizar `requirements.txt` - solo dependencias necesarias
2. Usar versiones específicas:
```
pandas==2.0.3
streamlit==1.28.1
```
3. Limpiar build cache:
   - Manual Deploy → **"Clear build cache & deploy"**

---

### 🌐 Variable de entorno no se actualiza

**Síntoma:**
- Cambias una variable en Render Dashboard
- La app sigue usando el valor viejo

**Causa:** Render no reinicia automáticamente al cambiar env vars

**Solución:**
1. Después de cambiar variables de entorno
2. Clic en **"Manual Deploy"** → **"Deploy latest commit"**
3. O reiniciar el servicio

---

### ❌ Error: 503 - Aplicación se cuelga al buscar Master o carpetas

**Síntoma:**
```
Error 503: Service Unavailable
Client Error: response received with status 503 when attempting to reach /_stcore/health
```

O mensaje de Render:
```
An instance of your Web Service exceeded its memory limit,
which triggered an automatic restart.
```

**Causa:** La aplicación excede el límite de memoria de 512MB del plan gratuito

**Soluciones implementadas:**

1. **Configuración de Streamlit optimizada** (`.streamlit/config.toml`)
   - Límites de tamaño de archivos reducidos
   - Logging mínimo
   - Stats deshabilitados

2. **Variables de entorno optimizadas** (en `render.yaml`)
   - `PYTHONUNBUFFERED=1`
   - Límites de upload configurados
   - Healthcheck con más timeout

3. **Buenas prácticas de uso:**
   - No ejecutar múltiples operaciones simultáneas
   - Limpiar datos cuando no se necesiten (botón "Recargar")
   - Buscar máximo 10-20 facturas a la vez

**Si el problema persiste:**

**Opción 1 - Monitorear memoria:**
1. Render Dashboard → Metrics
2. Verificar Memory Usage durante operaciones
3. Si consistentemente > 512MB, considerar upgrade

**Opción 2 - Upgrade a plan pagado:**
- Plan Starter: $7/mes
- 1GB RAM (2x más memoria)
- Sin suspensión automática
- Mejor performance

**Opción 3 - Optimizaciones adicionales:**
- Ver documentación completa en `docs/memory_optimization.md`
- Implementar lazy loading
- Usar paginación en datos grandes

---

## 📞 Contacto y Recursos

**Documentación oficial:**
- Render Web Services: https://render.com/docs/web-services
- Streamlit Deploy: https://docs.streamlit.io/deploy

**Logs y debugging:**
- Siempre revisa Render Dashboard → Logs primero
- Google el error específico si persiste

**Archivos clave:**
- `modules/config_helper.py` - Lee env vars
- `render.yaml` - Configuración de servicio
- `.env.example` - Template de variables

---

**Última actualización:** 05 Enero 2025
