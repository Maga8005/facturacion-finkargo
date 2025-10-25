"""Script para arreglar la indentación del app.py"""

def fix_indentation():
    with open('app.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    fixed_lines = []
    in_tab1 = False
    in_tab2 = False
    in_main_tab2 = False

    for i, line in enumerate(lines):
        line_num = i + 1

        # Detectar inicio de tab1
        if '# ==================== SUB-TAB 1: CARGA DE ARCHIVOS ====================' in line:
            in_tab1 = True
            fixed_lines.append(line)
            continue

        # Detectar inicio de tab2
        if '# ==================== TAB 3: GENERAR REPORTE ====================' in line or \
           '# ==================== SUB-TAB 2: GENERAR REPORTE ====================' in line:
            in_tab1 = False
            in_tab2 = True
            fixed_lines.append(line)
            continue

        # Detectar inicio de main_tab2
        if '# ==================== MAIN TAB 2: REPORTES DESDE MASTER ====================' in line:
            in_tab1 = False
            in_tab2 = False
            in_main_tab2 = True
            fixed_lines.append(line)
            continue

        # Detectar fin del archivo
        if '# Footer compacto' in line:
            in_main_tab2 = False

        # Aplicar indentación
        if in_tab1:
            # Contenido de tab1 necesita 8 espacios adicionales (within main_tab1 and tab1)
            if line.strip() and not line.startswith(' ' * 8):
                # Contar espacios actuales
                current_indent = len(line) - len(line.lstrip())
                if current_indent == 0:
                    # Sin indentación, agregar 8
                    line = ' ' * 8 + line
                elif current_indent == 4:
                    # Ya tiene 4, agregar 8 más = 12 total
                    line = ' ' * 8 + line

        fixed_lines.append(line)

    with open('app.py', 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)

    print("Indentación arreglada")

if __name__ == '__main__':
    fix_indentation()
