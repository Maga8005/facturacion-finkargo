"""Script para crear la versión final correcta del app.py"""

# Restaurar desde backup
with open('app.py.backup', 'r', encoding='utf-8') as f:
    lines = f.readlines()

final_lines = []

# Copiar hasta línea 337 (inclusive)
for i in range(338):  # 0-337
    final_lines.append(lines[i])

# Agregar estructura de tabs
final_lines.append('\n')
final_lines.append('# ==================== TABS PRINCIPALES (NIVEL 1) ====================\n')
final_lines.append('main_tab1, main_tab2 = st.tabs(["📝 Generar Reporte", "📊 Reportes desde Master"])\n')
final_lines.append('\n')
final_lines.append('# ==================== MAIN TAB 1: GENERAR REPORTE ====================\n')
final_lines.append('with main_tab1:\n')
final_lines.append('    # Sub-tabs (Nivel 2)\n')
final_lines.append('    tab1, tab2 = st.tabs(["📁 Carga de Archivos", "📋 Generar Reporte"])\n')
final_lines.append('\n')
final_lines.append('    # ==================== SUB-TAB 1: CARGA DE ARCHIVOS ====================\n')
final_lines.append('    with tab1:\n')

# Saltar la función render_file_upload_section y copiar su contenido indentado
# Saltar líneas 339-342 (comentario y def)
i = 342  # Siguiente línea después de "def render_file_upload_section():"

# Encontrar dónde termina la sección de carga de archivos (buscar where starts tab3 or main_tab2)
while i < len(lines):
    line = lines[i]

    # Si encontramos el inicio de tab3 o main_tab2, paramos
    if 'with tab3:' in line or 'with main_tab2:' in line or '# ==================== MAIN TAB 2' in line:
        break

    # Si la línea no está vacía y no tiene indentación (empieza en columna 0 excepto comentarios), paramos
    if line.strip() and not line.startswith(' ') and not line.startswith('#'):
        # Verificar que no sea parte del código de la función
        if not line.startswith('def ') and not line.startswith('class '):
            break

    # Agregar la línea con indentación adicional (8 espacios = 2 niveles de tabs)
    if line.strip():  # Solo si no es línea vacía
        # Contar indentación actual
        current_indent = len(line) - len(line.lstrip())
        # Agregar 8 espacios más
        final_lines.append(' ' * 8 + line.lstrip())
    else:
        final_lines.append(line)

    i += 1

# Agregar tab2
final_lines.append('\n')
final_lines.append('    # ==================== SUB-TAB 2: GENERAR REPORTE ====================\n')
final_lines.append('    with tab2:\n')

# Continuar con el resto del archivo desde donde paramos
# pero ajustando las referencias a tab3 -> tab2
while i < len(lines):
    line = lines[i]

    # Reemplazar tab3 por tab2
    if 'with tab3:' in line:
        line = line.replace('tab3', 'tab2')

    # Si encontramos main_tab2, copiar el resto sin modificar
    if 'with main_tab2:' in line or '# ==================== MAIN TAB 2' in line:
        # Copiar el resto del archivo tal cual
        while i < len(lines):
            final_lines.append(lines[i])
            i += 1
        break

    final_lines.append(line)
    i += 1

# Escribir el archivo final
with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(final_lines)

print("Archivo creado exitosamente")
