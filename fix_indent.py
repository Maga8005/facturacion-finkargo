"""Script para corregir indentación desde línea 1182"""

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

fixed_lines = []
for i, line in enumerate(lines):
    line_num = i + 1

    # Líneas 1182 en adelante que tienen 16 espacios deben tener 12
    if line_num >= 1182:
        # Contar espacios al inicio
        stripped = line.lstrip(' ')
        spaces = len(line) - len(stripped)

        # Si tiene 16 o más espacios, reducir en 4
        if spaces >= 16 and stripped:  # Solo si no es línea vacía
            line = ' ' * (spaces - 4) + stripped

    fixed_lines.append(line)

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print("Indentación corregida")
