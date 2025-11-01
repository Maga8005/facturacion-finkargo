"""
Script de prueba para verificar acceso a Google Drive con cuenta de servicio
Estructura esperada:
- Facturacion (carpeta raíz)
  ├── Reportes Facturación
  ├── Año 2025
  ├── Año 2024
  ├── Año 2023
  ├── Año 2022
  └── Archivo control facturacion mensual Finkargo Def.xlsx
"""

from google.oauth2 import service_account
from googleapiclient.discovery import build
import os

def test_drive_access():
    """Prueba el acceso al Drive con la cuenta de servicio"""

    print("=" * 70)
    print("PRUEBA DE ACCESO A GOOGLE DRIVE - CARPETA FACTURACION")
    print("=" * 70)

    # Configuración
    SCOPES = ['https://www.googleapis.com/auth/drive']
    SERVICE_ACCOUNT_FILE = 'config/service_account.json'
    FOLDER_ID = '1PMdI6oYpPO3_79Lz5eJpWvdIZCgrrka7'  # ID de carpeta "Facturacion"

    try:
        # 1. Verificar que el archivo de credenciales existe
        print("\n1️⃣  Verificando archivo de credenciales...")
        if not os.path.exists(SERVICE_ACCOUNT_FILE):
            print(f"   ❌ ERROR: No se encontró {SERVICE_ACCOUNT_FILE}")
            return False
        print(f"   ✅ Archivo encontrado: {SERVICE_ACCOUNT_FILE}")

        # 2. Cargar credenciales
        print("\n2️⃣  Cargando credenciales de cuenta de servicio...")
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE,
            scopes=SCOPES
        )
        print(f"   ✅ Credenciales cargadas")
        print(f"   📧 Email: {creds.service_account_email}")

        # 3. Construir servicio de Drive
        print("\n3️⃣  Construyendo servicio de Google Drive...")
        service = build('drive', 'v3', credentials=creds)
        print("   ✅ Servicio de Drive construido")

        # 4. Probar acceso a carpeta "Facturacion"
        print(f"\n4️⃣  Accediendo a la carpeta 'Facturacion'...")
        print(f"   📂 Folder ID: {FOLDER_ID}")

        # Obtener información de la carpeta
        folder_info = service.files().get(
            fileId=FOLDER_ID,
            fields='id, name, mimeType, owners, capabilities'
        ).execute()

        print(f"   ✅ Acceso exitoso!")
        print(f"   📁 Nombre: {folder_info.get('name')}")
        print(f"   🔧 Tipo: {folder_info.get('mimeType')}")

        # Verificar permisos
        capabilities = folder_info.get('capabilities', {})
        print(f"   📝 Puede editar: {capabilities.get('canEdit', False)}")
        print(f"   📄 Puede crear archivos: {capabilities.get('canAddChildren', False)}")

        # 5. Listar contenido de la carpeta "Facturacion"
        print(f"\n5️⃣  Listando contenido de la carpeta 'Facturacion'...")
        results = service.files().list(
            q=f"'{FOLDER_ID}' in parents and trashed=false",
            pageSize=50,
            fields="files(id, name, mimeType, modifiedTime, size)",
            orderBy="name"
        ).execute()

        items = results.get('files', [])

        if not items:
            print("   ⚠️  La carpeta está vacía")
        else:
            print(f"   ✅ Encontrados {len(items)} elementos:\n")
            for i, item in enumerate(items, 1):
                if item['mimeType'] == 'application/vnd.google-apps.folder':
                    tipo = "📁 CARPETA"
                elif item['mimeType'] == 'application/vnd.google-apps.spreadsheet':
                    tipo = "📊 HOJA DE CÁLCULO"
                else:
                    tipo = "📄 ARCHIVO"

                print(f"   {i}. {tipo}")
                print(f"      Nombre: {item['name']}")
                print(f"      ID: {item['id']}")
                print()

        # 6. Buscar carpetas y archivos específicos
        print(f"6️⃣  Buscando elementos específicos del sistema...\n")
        elementos_esperados = [
            "Reportes Facturación",
            "Año 2025",
            "Año 2024",
            "Año 2023",
            "Año 2022",
            "Archivo control facturacion mensual Finkargo Def"
        ]

        encontrados_count = 0
        for nombre in elementos_esperados:
            # Buscar por nombre que contenga el texto
            query = f"name contains '{nombre}' and '{FOLDER_ID}' in parents and trashed=false"
            results = service.files().list(
                q=query,
                pageSize=5,
                fields="files(id, name, mimeType)"
            ).execute()

            encontrados = results.get('files', [])
            if encontrados:
                encontrados_count += 1
                item = encontrados[0]
                emoji = "📁" if 'folder' in item['mimeType'] else "📄"
                print(f"   ✅ {emoji} '{nombre}'")
                print(f"      → Nombre completo: {item['name']}")
                print(f"      → ID: {item['id']}")
            else:
                print(f"   ⚠️  '{nombre}': No encontrado")
            print()

        # 7. Resumen final
        print("=" * 70)
        print("✅ PRUEBA COMPLETADA")
        print("=" * 70)
        print(f"\n📊 Resumen:")
        print(f"   • Carpeta 'Facturacion': ✅ Accesible")
        print(f"   • Total de elementos: {len(items)}")
        print(f"   • Elementos esperados encontrados: {encontrados_count}/{len(elementos_esperados)}")
        print(f"   • Permisos de escritura: {'✅' if capabilities.get('canAddChildren') else '❌'}")

        print(f"\n🎯 Estado del acceso a Drive:")
        if len(items) > 0 and encontrados_count >= 3:
            print("   ✅ EXITOSO - La aplicación puede acceder al Drive correctamente")
        elif len(items) > 0:
            print("   ⚠️  PARCIAL - Hay acceso pero faltan algunos elementos esperados")
        else:
            print("   ❌ FALLIDO - No se puede acceder al contenido")

        return True

    except Exception as e:
        print(f"\n❌ ERROR durante la prueba:")
        print(f"   {str(e)}")
        print("\n" + "=" * 70)
        print("❌ PRUEBA FALLIDA")
        print("=" * 70)

        print("\n🔧 Posibles soluciones:")
        print("   1. Verifica que la carpeta 'Facturacion' esté compartida con:")
        print("      drive-and-sheets-access-sa@api-producto-476819.iam.gserviceaccount.com")
        print("   2. Verifica que el FOLDER_ID sea correcto")
        print("   3. Verifica que el archivo config/service_account.json sea válido")
        print("   4. Dale permisos de 'Editor' a la cuenta de servicio en Drive")

        return False

if __name__ == "__main__":
    test_drive_access()
