"""Script para quitar 4 espacios de indentación desde línea 1536"""

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

fixed_lines = []
for i, line in enumerate(lines):
    line_num = i + 1

    # Desde línea 1536 en adelante, reducir 4 espacios
    if line_num >= 1536:
        if line.strip():  # Solo si no es línea vacía
            stripped = line.lstrip(' ')
            spaces = len(line) - len(stripped)

            # Reducir en 4 espacios
            if spaces >= 4:
                line = ' ' * (spaces - 4) + stripped

    fixed_lines.append(line)

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print("✅ Indentación de sección PDF corregida")
