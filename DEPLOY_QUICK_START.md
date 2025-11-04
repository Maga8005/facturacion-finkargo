# 🚀 Inicio Rápido - Despliegue en Render

## ⚡ Resumen en 5 minutos

### 1️⃣ Verificar que todo esté listo
```bash
python verify_deploy.py
```

### 2️⃣ Subir a GitHub
```bash
git add .
git commit -m "Preparación para despliegue en Render"
git push origin main
```

### 3️⃣ Crear servicio en Render
1. Ve a https://dashboard.render.com/
2. **New +** → **Web Service**
3. Conecta tu repositorio GitHub
4. Configura:
   - **Name:** `facturacion-finkargo`
   - **Branch:** `main`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true`
   - **Instance Type:** Free

### 4️⃣ Agregar Variables de Entorno

En la sección "Environment Variables":

```
drive_folder_id = 1l3zOaD7Qt-KOHz97FLib4HwSEQqwjN2y
```

```
SERVICE_ACCOUNT_JSON = {
  "type": "service_account",
  ...
  (pegar COMPLETO el contenido de config/service_account.json)
}
```

```
USERS_JSON = {"maria.gaitan": "facturacion2024", "maleja": "facturacion2024"}
```

### 5️⃣ Desplegar
- Haz clic en **"Create Web Service"**
- Espera 3-5 minutos
- ¡Listo! Tu app estará en `https://facturacion-finkargo.onrender.com`

---

## 📚 Documentación Completa
Para instrucciones detalladas, ver: **[docs/despliegue_render.md](docs/despliegue_render.md)**

## ⚠️ Importante
- El plan gratuito se "duerme" después de 15 min de inactividad
- Primera visita después del sleep tarda ~1-2 min en cargar
- NO subas archivos sensibles a GitHub (`.gitignore` los protege)

## 🆘 ¿Problemas?
Ver sección "Troubleshooting" en `docs/despliegue_render.md`
