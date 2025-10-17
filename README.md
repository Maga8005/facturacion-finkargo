# Sistema de Consolidación de Facturas - Finkargo

Sistema automatizado para consolidar y procesar facturas de NUVA y Netsuite, generando reportes consolidados para el análisis de facturación.

## Descripción

Este sistema permite:
- Cargar múltiples archivos Excel (2 de NUVA + 1 de Netsuite)
- Consolidar y clasificar conceptos de facturación
- Validar datos automáticamente
- Generar reportes personalizados
- Exportar a Excel, CSV o Google Sheets

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

### Ejecutar la aplicación

```bash
streamlit run app.py
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`

### Flujo de trabajo

1. **Carga de Archivos**: Sube los 3 archivos Excel requeridos
2. **Dashboard**: Visualiza métricas y estadísticas consolidadas
3. **Generar Reporte**: Aplica filtros y exporta reportes personalizados

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

## Próximos Pasos

1. Implementar lógica de procesamiento de archivos
2. Configurar mapeo de columnas en `column_mapping.json`
3. Definir reglas de clasificación en `classification_rules.json`
4. Configurar conexión a Google Sheets (opcional)
5. Agregar tests unitarios

## Soporte

Para preguntas o problemas, contactar a:
- **Usuario principal**: Alejandro (Analista de Facturación)
- **Equipo de desarrollo**: [Tu equipo]

## Licencia

Propiedad de Finkargo - Uso interno exclusivo

---

**Versión**: 1.0
**Última actualización**: 2024
