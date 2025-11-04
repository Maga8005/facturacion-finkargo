# Cómo Conectarse a Google Drive

## 🎯 Ubicación del Botón de Conexión

El botón para conectarte a Google Drive está en:
**📊 Reportes desde Master** (pestaña principal)

## 📝 Pasos para Conectarse

### 1. Ve a la Pestaña "Reportes desde Master"
- Haz clic en la pestaña principal **"📊 Reportes desde Master"**
- Verás un banner amarillo que dice "🔐 Autenticación Requerida"

### 2. Inicia el Proceso de Autenticación
- Haz clic en el botón **"🔑 Conectar con Google Drive"**
- Se abrirá un panel con instrucciones

### 3. Genera la URL de Autorización
- Haz clic en **"🔑 Generar URL de autorización"**
- Se generará una URL larga

### 4. Autoriza en Google
- **Copia** la URL completa
- **Pégala** en una nueva pestaña del navegador
- **Inicia sesión** con la cuenta: `maleja8005@gmail.com`
- **Acepta** todos los permisos que solicita la aplicación

### 5. Copia el Código de Autorización
- Después de aceptar, verás un código de autorización
- **Copia** ese código

### 6. Completa la Conexión
- Vuelve a la aplicación Streamlit
- **Pega** el código en el campo "Código de autorización"
- Haz clic en **"✅ Conectar"**

### 7. ¡Listo!
- Si todo salió bien, verás: **"✅ ¡Conectado exitosamente!"**
- La página se recargará automáticamente
- Ya podrás acceder a los reportes master y buscar PDFs

## 🔍 Verificar Conexión

Una vez conectado, verás en el **sidebar izquierdo**:
- ✅ Credenciales configuradas
- 🔗 Conectado a Drive
- Botón para desconectar (si es necesario)

## ⚠️ Solución de Problemas

### Error: "Faltan credenciales en secrets.toml"
- Verifica que el archivo `.streamlit/secrets.toml` exista
- Debe contener:
  ```toml
  client_id = "tu-client-id"
  client_secret = "tu-client-secret"
  drive_folder_id = "id-de-carpeta-finkargo"
  ```

### Error: "Error al conectar con Drive"
- Verifica que copiaste el código completo
- Intenta generar una nueva URL de autorización
- Asegúrate de usar la cuenta correcta (maleja8005@gmail.com)

### La conexión se pierde al recargar
- La primera vez puede perderse
- Vuelve a conectar
- Se guardará un archivo `token.json` para mantener la sesión

## 📂 Estructura de Google Drive Esperada

La aplicación busca estas carpetas en tu Drive:
```
finkargo/
├── Facturación/
│   └── Master_Facturacion.xlsx
├── Reportes Facturación/
│   └── (Reportes generados)
└── Facturas PDF/
    └── (PDFs de facturas)
```

Si alguna carpeta no existe, la aplicación la creará automáticamente.
