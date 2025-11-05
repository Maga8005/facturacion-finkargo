# Sistema de Consolidación de Facturas - Finkargo

Sistema automatizado para consolidar y procesar facturas, generando reportes consolidados para el análisis de facturación con integración a Google Drive.

## 🌐 Acceso a Producción

**URL:** `https://facturacion-finkargo.onrender.com`

**Usuarios autorizados:**
- maria.gaitan
- maleja
- Alejo

⚠️ **Nota:** Primera carga puede tardar 1-2 minutos (plan gratuito de Render)

## Descripción

Este sistema permite:
- Cargar archivo maestro desde Google Drive
- Buscar y descargar PDFs de facturas automáticamente
- Consolidar y clasificar conceptos de facturación
- Validar datos automáticamente
- Generar reportes personalizados en Excel
- Subir reportes generados a Google Drive

## Tecnologías

- **Python**: 3.11+
- **Streamlit**: Framework web para la interfaz
- **Pandas**: Procesamiento de datos
- **Google Sheets API**: Integración con Google Sheets
- **Plotly**: Visualizaciones interactivas

## Estructura del Proyecto

```
facturacion-finkargo/
├── .streamlit/              # Configuración de Streamlit
├── config/                  # Archivos de configuración
│   ├── column_mapping.json
│   ├── classification_rules.json
│   └── sheets_config.json
├── modules/                 # Módulos principales
│   ├── file_processor.py    # Procesamiento de archivos
│   ├── classifier.py        # Clasificación de conceptos
│   ├── validator.py         # Validación de datos
│   ├── sheets_manager.py    # Gestión Google Sheets
│   └── report_generator.py  # Generación de reportes
├── utils/                   # Utilidades
│   └── helpers.py
├── data/                    # Datos y logs
│   └── logs/
├── tests/                   # Tests unitarios
├── app.py                   # Aplicación principal
├── requirements.txt         # Dependencias
└── README.md
```

## Instalación

### 1. Clonar o descargar el proyecto

```bash
cd facturacion-finkargo
```

### 2. Crear entorno virtual

**Windows (PowerShell):**
```powershell
python -m venv venv
```

**Linux/Mac:**
```bash
python3 -m venv venv
```

### 3. Activar entorno virtual

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

## Configuración

### Google Sheets (Opcional)

Si deseas usar la integración con Google Sheets:

1. Crear un proyecto en [Google Cloud Console](https://console.cloud.google.com/)
2. Habilitar Google Sheets API
3. Crear credenciales (Service Account)
4. Descargar el archivo JSON de credenciales
5. Guardar como `.streamlit/secrets.toml`:

```toml
[gcp_service_account]
type = "service_account"
project_id = "tu-proyecto"
private_key_id = "..."
private_key = "..."
client_email = "..."
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "..."
```

## Uso

### Ejecutar la aplicación localmente

```bash
streamlit run app.py
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`

### Flujo de trabajo

1. **Login**: Inicia sesión con tu usuario autorizado
2. **Cargar Master desde Drive**: Carga el archivo maestro de facturación desde Google Drive
3. **Buscar PDFs en Drive**: Busca automáticamente PDFs de facturas en Drive
4. **Generar Reporte Maestro**: Genera reporte consolidado en Excel

## 🚀 Deploy a Producción

### Deploy en Render

El sistema está desplegado en Render (https://render.com). Para actualizar o redesplegar:

**Guía rápida:**
- Ver: [`DEPLOY_QUICK_START.md`](DEPLOY_QUICK_START.md)

**Documentación completa:**
- Deploy paso a paso: [`docs/despliegue_render.md`](docs/despliegue_render.md)
- Troubleshooting: [`docs/troubleshooting_render.md`](docs/troubleshooting_render.md)
- Post-deploy checklist: [`docs/post_deploy_checklist.md`](docs/post_deploy_checklist.md)

**Deploy automático:**
Cada vez que se hace push a `main`, Render redespliega automáticamente en 3-5 minutos.

**Variables de entorno requeridas:**
- `drive_folder_id` - ID de la carpeta de Google Drive
- `SERVICE_ACCOUNT_JSON` - Credenciales de Service Account (JSON completo)
- `USERS_JSON` - Diccionario de usuarios autorizados

Ver `.env.example` para el formato completo.

## Desarrollo

### Ejecutar tests

```bash
pytest tests/
```

### Estructura de módulos

- `file_processor.py`: Lectura y normalización de archivos Excel
- `classifier.py`: Clasificación automática de conceptos
- `validator.py`: Validación de datos y detección de errores
- `sheets_manager.py`: Sincronización con Google Sheets
- `report_generator.py`: Generación de reportes finales

## 📁 Archivos de Configuración

- `config/service_account.json` - Credenciales de Google Cloud (NO subir a Git)
- `.streamlit/secrets.toml` - Secretos locales para desarrollo (NO subir a Git)
- `.env.example` - Template de variables de entorno para producción
- `render.yaml` - Configuración de deploy en Render

## 🔒 Seguridad

**Archivos protegidos por `.gitignore`:**
- `config/service_account.json` - Credenciales de Google
- `.streamlit/secrets.toml` - Secretos locales
- `token.json` - Tokens de autenticación
- `.env` - Variables de entorno

**NUNCA** subir estos archivos a GitHub. Usar variables de entorno en producción.

## 📚 Documentación

- [`DEPLOY_QUICK_START.md`](DEPLOY_QUICK_START.md) - Inicio rápido de deploy
- [`docs/despliegue_render.md`](docs/despliegue_render.md) - Guía completa de deploy
- [`docs/troubleshooting_render.md`](docs/troubleshooting_render.md) - Solución de problemas
- [`docs/post_deploy_checklist.md`](docs/post_deploy_checklist.md) - Verificación post-deploy

## Soporte

**Problemas técnicos:**
- Ver documentación de troubleshooting
- Revisar logs en Render Dashboard
- Crear issue en GitHub

**Usuarios:**
- maria.gaitan
- maleja

## Licencia

Propiedad de Finkargo - Uso interno exclusivo

---

**Versión**: 1.1.0
**Última actualización**: 04 Enero 2025
**Status**: ✅ En Producción
**URL**: https://facturacion-finkargo.onrender.com
