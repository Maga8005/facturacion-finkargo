"""
Script rápido para verificar acceso de la cuenta de servicio
"""

from google.oauth2 import service_account
from googleapiclient.discovery import build

# Configuración
SERVICE_ACCOUNT_FILE = 'config/service_account.json'
FOLDER_ID = '1l3zOaD7Qt-KOHz97FLib4HwSEQqwjN2y'
SCOPES = ['https://www.googleapis.com/auth/drive']

print("=" * 60)
print("Verificando acceso a la carpeta Facturacion")
print("=" * 60)

try:
    # Cargar credenciales
    print("\n1. Cargando credenciales...")
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES
    )
    print(f"✅ Cuenta de servicio: {creds.service_account_email}")

    # Construir servicio
    print("\n2. Conectando a Google Drive...")
    service = build('drive', 'v3', credentials=creds)
    print("✅ Conectado")

    # Intentar acceder a la carpeta
    print(f"\n3. Intentando acceder a la carpeta...")
    print(f"   Folder ID: {FOLDER_ID}")

    folder_info = service.files().get(
        fileId=FOLDER_ID,
        fields='id, name, mimeType, capabilities'
    ).execute()

    print("\n✅ ¡ACCESO EXITOSO!")
    print(f"   Nombre: {folder_info.get('name')}")
    print(f"   Tipo: {folder_info.get('mimeType')}")

    capabilities = folder_info.get('capabilities', {})
    print(f"\n   Permisos:")
    print(f"   • Puede leer: {capabilities.get('canListChildren', False)}")
    print(f"   • Puede editar: {capabilities.get('canEdit', False)}")
    print(f"   • Puede crear archivos: {capabilities.get('canAddChildren', False)}")

    # Listar contenido
    print(f"\n4. Listando contenido...")
    results = service.files().list(
        q=f"'{FOLDER_ID}' in parents and trashed=false",
        pageSize=20,
        fields="files(id, name, mimeType)"
    ).execute()

    items = results.get('files', [])
    print(f"   Encontrados: {len(items)} elementos")

    if items:
        for item in items[:10]:
            tipo = "📁" if 'folder' in item['mimeType'] else "📄"
            print(f"   {tipo} {item['name']}")

    print("\n" + "=" * 60)
    print("✅ TODO FUNCIONA CORRECTAMENTE")
    print("=" * 60)

except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    print("\n" + "=" * 60)
    print("SOLUCIÓN:")
    print("=" * 60)
    print("\nLa carpeta NO está compartida con la cuenta de servicio.")
    print("\nPasos para compartir:")
    print("1. Abre Google Drive en el navegador")
    print("2. Busca la carpeta 'Facturacion'")
    print("3. Haz clic derecho → Compartir")
    print("4. Agrega este email:")
    print(f"   {creds.service_account_email}")
    print("5. Rol: Editor")
    print("6. Clic en 'Compartir'\n")
