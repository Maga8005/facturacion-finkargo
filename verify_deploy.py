"""
Script de verificación pre-despliegue
Verifica que todos los archivos y configuraciones estén listos para Render
"""

import os
import sys
import json
import io

# Configurar la codificación de salida para Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def check_file(filepath, description):
    """Verifica que un archivo exista"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} NO ENCONTRADO")
        return False


def check_gitignore():
    """Verifica que archivos sensibles estén en .gitignore"""
    print("\n📋 Verificando .gitignore...")

    if not os.path.exists('.gitignore'):
        print("❌ .gitignore no encontrado")
        return False

    with open('.gitignore', 'r') as f:
        content = f.read()

    required_entries = [
        '.streamlit/secrets.toml',
        'config/service_account.json',
        'token.json',
        '.env'
    ]

    all_good = True
    for entry in required_entries:
        if entry in content:
            print(f"✅ '{entry}' está en .gitignore")
        else:
            print(f"❌ '{entry}' NO está en .gitignore - ¡PELIGRO!")
            all_good = False

    return all_good


def check_requirements():
    """Verifica requirements.txt"""
    print("\n📦 Verificando requirements.txt...")

    if not os.path.exists('requirements.txt'):
        print("❌ requirements.txt no encontrado")
        return False

    with open('requirements.txt', 'r') as f:
        content = f.read()

    required_packages = [
        'streamlit',
        'pandas',
        'openpyxl',
        'google-auth',
        'google-api-python-client'
    ]

    all_good = True
    for package in required_packages:
        if package in content:
            print(f"✅ {package} está en requirements.txt")
        else:
            print(f"⚠️  {package} NO está en requirements.txt")
            all_good = False

    return all_good


def check_service_account():
    """Verifica que exista el service account (pero no lo muestra por seguridad)"""
    print("\n🔐 Verificando Service Account...")

    filepath = 'config/service_account.json'
    if not os.path.exists(filepath):
        print(f"❌ {filepath} NO encontrado")
        print("   Necesitarás configurar SERVICE_ACCOUNT_JSON en Render")
        return False

    try:
        with open(filepath, 'r') as f:
            data = json.load(f)

        required_fields = [
            'type',
            'project_id',
            'private_key',
            'client_email'
        ]

        all_good = True
        for field in required_fields:
            if field in data:
                print(f"✅ Campo '{field}' presente")
            else:
                print(f"❌ Campo '{field}' faltante")
                all_good = False

        if all_good:
            print(f"✅ Service Account JSON es válido")
            print(f"   Email: {data.get('client_email', 'N/A')}")

        return all_good

    except json.JSONDecodeError:
        print(f"❌ {filepath} no es un JSON válido")
        return False


def check_secrets():
    """Verifica secrets.toml"""
    print("\n🔒 Verificando .streamlit/secrets.toml...")

    filepath = '.streamlit/secrets.toml'
    if not os.path.exists(filepath):
        print(f"⚠️  {filepath} NO encontrado (OK si solo despliegas)")
        return True

    with open(filepath, 'r') as f:
        content = f.read()

    if 'drive_folder_id' in content:
        print("✅ drive_folder_id configurado")
    else:
        print("⚠️  drive_folder_id no configurado")

    if '[users]' in content:
        print("✅ Usuarios configurados")
    else:
        print("⚠️  Usuarios no configurados")

    print("ℹ️  Recuerda: estos valores deberán ir como variables de entorno en Render")
    return True


def main():
    """Ejecuta todas las verificaciones"""
    print("=" * 60)
    print("🔍 VERIFICACIÓN PRE-DESPLIEGUE A RENDER")
    print("=" * 60)

    checks = {
        'Archivos esenciales': [
            check_file('app.py', 'Archivo principal'),
            check_file('requirements.txt', 'Dependencias'),
            check_file('render.yaml', 'Configuración de Render'),
            check_file('.env.example', 'Template de variables'),
        ],
        'Configuración': [
            check_gitignore(),
            check_requirements(),
            check_service_account(),
            check_secrets(),
        ]
    }

    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN")
    print("=" * 60)

    total_checks = sum(len(checks_list) for checks_list in checks.values())
    passed_checks = sum(
        sum(1 for check in checks_list if check)
        for checks_list in checks.values()
    )

    print(f"\nVerificaciones pasadas: {passed_checks}/{total_checks}")

    if passed_checks == total_checks:
        print("\n✅ ¡TODO LISTO PARA DESPLEGAR!")
        print("\n📝 PRÓXIMOS PASOS:")
        print("1. git add .")
        print("2. git commit -m 'Preparación para despliegue'")
        print("3. git push origin main")
        print("4. Ve a https://dashboard.render.com/")
        print("5. Sigue la guía en docs/despliegue_render.md")
        return 0
    else:
        print("\n⚠️  HAY PROBLEMAS QUE RESOLVER")
        print("Por favor, corrige los errores marcados con ❌")
        return 1


if __name__ == "__main__":
    sys.exit(main())
