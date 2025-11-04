"""Script para quitar indentación de 4 espacios desde línea 1077"""

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

fixed_lines = []
for i, line in enumerate(lines):
    line_num = i + 1

    # Desde línea 1077 en adelante, reducir 4 espacios de indentación
    if line_num >= 1077:
        if line.strip():  # Solo si no es línea vacía
            stripped = line.lstrip(' ')
            spaces = len(line) - len(stripped)

            # Reducir en 4 espacios
            if spaces >= 4:
                line = ' ' * (spaces - 4) + stripped

    fixed_lines.append(line)

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print("Indentación reducida correctamente")
