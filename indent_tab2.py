"""Script para agregar 4 espacios de indentación al contenido de tab2"""

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

fixed_lines = []
for i, line in enumerate(lines):
    line_num = i + 1

    # Desde línea 1067 hasta 1751 (antes del footer), agregar 4 espacios
    # Excepto líneas vacías
    if 1067 <= line_num <= 1751:
        if line.strip():  # Solo si no es línea vacía
            line = '    ' + line

    fixed_lines.append(line)

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print("Indentacion agregada al contenido de tab2")
