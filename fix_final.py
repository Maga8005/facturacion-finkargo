"""Script para arreglar indentación del bloque de filtros"""

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

fixed_lines = []
for i, line in enumerate(lines):
    line_num = i + 1

    # Desde línea 1158 en adelante, reducir indentación en 4 espacios
    # hasta el final del archivo o hasta encontrar otro bloque con indentación menor
    if line_num >= 1158:
        stripped = line.lstrip(' ')
        if stripped:  # Si no es línea vacía
            spaces = len(line) - len(stripped)
            # Si tiene 12 o más espacios (dentro del bloque), reducir a 8
            if spaces >= 12:
                line = ' ' * 8 + stripped
            elif spaces == 8:
                # Mantener 8 espacios
                line = ' ' * 8 + stripped
            # Si tiene menos de 8, dejarlo como está (son líneas de nivel superior)

    fixed_lines.append(line)

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print("Indentación corregida")
