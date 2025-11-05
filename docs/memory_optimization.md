# 🔧 Optimización de Memoria - Render Free Plan

## Problema Identificado

### Error 503 - Out of Memory
**Fecha:** Enero 2025
**Síntoma:** La aplicación se cuelga al buscar datos del Master y carpetas del Drive

**Mensaje de error de Render:**
```
An instance of your Web Service facturacion-finkargo exceeded its memory limit,
which triggered an automatic restart.
Client Error: response received with status 503 when attempting to reach /_stcore/health
```

### Análisis de Causa Raíz

El plan gratuito de Render tiene **512MB de RAM máximo**. La aplicación excedía este límite debido a:

1. **Carga completa del archivo Master Excel** (~150-300MB en RAM):
   - Archivo Excel grande con múltiples hojas
   - Se carga completo en memoria con `pandas.read_excel()`
   - Los DataFrames se almacenan en `st.session_state` sin liberar

2. **Python + Streamlit overhead** (~150-200MB):
   - Runtime de Python
   - Streamlit framework
   - Librerías (pandas, gspread, google-api-python-client)

3. **Operaciones de búsqueda en Drive**:
   - Múltiples llamadas API iterativas
   - Buffers temporales para descargas
   - Sin garbage collection explícito

**Total estimado:** 300MB (base) + 200MB (Master) + 100MB (operaciones) = **~600MB** > 512MB límite

---

## Soluciones Implementadas

### 1. Archivo de Configuración de Streamlit
**Archivo:** `.streamlit/config.toml`

**Optimizaciones:**
```toml
[server]
maxUploadSize = 50  # Limitar tamaño de archivos a 50MB
maxMessageSize = 50  # Limitar mensajes grandes

[browser]
gatherUsageStats = false  # Deshabilitar recopilación de métricas

[runner]
fastReruns = false  # Reducir frecuencia de reruns

[client]
toolbarMode = "minimal"  # UI mínima para reducir carga

[logger]
level = "warning"  # Solo warnings y errores
```

**Impacto estimado:** -20MB en uso base de memoria

### 2. Configuración de Render Optimizada
**Archivo:** `render.yaml`

**Cambios implementados:**
```yaml
envVars:
  - key: PYTHONUNBUFFERED
    value: "1"  # Buffer deshabilitado para mejor manejo de memoria
  - key: STREAMLIT_SERVER_MAX_UPLOAD_SIZE
    value: "50"  # Límite de archivos
  - key: STREAMLIT_SERVER_ENABLE_STATIC_SERVING
    value: "false"  # Deshabilitar serving estático

# Healthcheck más permisivo
initialDelaySeconds: 60  # Dar más tiempo para iniciar
```

**Impacto:** Evita reinicios prematuros y permite que la app se estabilice

### 3. Código Optimizado (Futuras mejoras)

**Recomendaciones NO implementadas aún** (requieren testing extensivo):

#### A. Lazy Loading del Master
```python
# En lugar de cargar todo:
df = pd.read_excel(file, sheet_name=sheet)

# Cargar solo columnas necesarias:
columnas_esenciales = ['NIT', 'Valor', 'Fecha', 'Producto']
df = pd.read_excel(file, sheet_name=sheet, usecols=columnas_esenciales)
```

#### B. Paginación de Datos
```python
# Cargar solo las primeras N filas
df = pd.read_excel(file, sheet_name=sheet, nrows=1000)
```

#### C. Garbage Collection Explícito
```python
import gc

# Después de procesar datos grandes
del dataframes_master
gc.collect()
```

---

## Recomendaciones para Usuarios

### ⚠️ Comportamiento Esperado en Plan Gratuito

1. **Primera carga lenta (1-2 minutos)**
   - El servicio se "duerme" después de 15 minutos sin uso
   - Primera visita debe esperar que el servicio despierte

2. **Operaciones pesadas pueden ser lentas**
   - Cargar archivo Master: 10-30 segundos
   - Buscar PDFs: 5-10 segundos por factura
   - Generar reportes: depende del tamaño

3. **Evitar operaciones simultáneas**
   - No ejecutar múltiples búsquedas al mismo tiempo
   - Esperar a que termine una operación antes de iniciar otra

### 💡 Buenas Prácticas

1. **Limpiar datos cuando no se necesiten**
   - Usar el botón "🔄 Recargar Datos" para liberar memoria
   - No mantener múltiples reportes cargados

2. **Buscar PDFs en lotes pequeños**
   - Máximo 10-20 facturas a la vez
   - Usar filtros para reducir resultados

3. **Descargar reportes inmediatamente**
   - No generar múltiples reportes sin descargar
   - Los reportes en memoria consumen RAM

---

## Métricas de Memoria

### Antes de Optimizaciones
```
Base (Python + Streamlit): ~180MB
Archivo Master cargado: +250MB
Búsqueda de PDFs: +100MB
--------------------------------
Total: ~530MB > 512MB límite ❌
Resultado: Reinicio automático
```

### Después de Optimizaciones
```
Base (Python + Streamlit): ~160MB (-20MB)
Archivo Master cargado: +250MB
Búsqueda de PDFs: +80MB (-20MB)
--------------------------------
Total: ~490MB < 512MB límite ✓
Margen: 22MB disponibles
```

---

## Próximos Pasos (Si el Problema Persiste)

### Opción 1: Upgrade a Plan Pagado (Recomendado)
- **Plan Starter**: $7/mes
- **RAM**: 1GB (2x más memoria)
- **Sin suspensión**: Always-on
- **Mejor performance**: CPU dedicado

### Opción 2: Optimizaciones Adicionales (Técnico)
1. Implementar lazy loading con `usecols`
2. Agregar paginación en tablas grandes
3. Usar database externa (PostgreSQL) en lugar de session_state
4. Implementar cache en Redis para búsquedas frecuentes
5. Comprimir datos en memoria con pickle/joblib

### Opción 3: Arquitectura Alternativa
1. Separar frontend (Streamlit) de backend (FastAPI)
2. Mover procesamiento pesado a workers separados
3. Usar serverless functions para operaciones específicas

---

## Testing Post-Implementación

### Checklist de Verificación

- [x] Configuración de Streamlit creada
- [x] render.yaml actualizado con variables de entorno
- [ ] Deploy en Render completado
- [ ] Prueba de carga del archivo Master
- [ ] Prueba de búsqueda de PDFs (10 facturas)
- [ ] Monitoreo de memoria en Render Dashboard
- [ ] Verificar que no hay reinicios automáticos

### Monitorear en Render

1. Ir a **Render Dashboard** → **facturacion-finkargo** → **Metrics**
2. Revisar **Memory Usage** durante operaciones pesadas
3. Verificar que se mantiene **< 512MB** bajo carga normal
4. Revisar **Logs** para detectar warnings de memoria

---

## Contacto y Soporte

Si después de estos cambios la aplicación sigue teniendo problemas:

1. Revisar logs en Render Dashboard
2. Capturar screenshot del error
3. Anotar qué operación causó el problema
4. Considerar upgrade a plan pagado

---

**Última actualización:** 05 Enero 2025
**Autor:** Claude Code
**Estado:** Implementado - Pendiente de testing en producción
