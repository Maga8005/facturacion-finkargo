"""Script para reducir indentación desde línea 1160"""

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

fixed_lines = []
for i, line in enumerate(lines):
    line_num = i + 1

    # Desde línea 1160 en adelante, reducir indentación en 4 espacios
    if line_num >= 1160:
        # No modificar líneas vacías ni comentarios de nivel superior
        if line.strip():
            stripped = line.lstrip(' ')
            spaces = len(line) - len(stripped)

            # Reducir en 4 espacios
            if spaces >= 4:
                line = ' ' * (spaces - 4) + stripped

    fixed_lines.append(line)

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print("Indentación final corregida")
