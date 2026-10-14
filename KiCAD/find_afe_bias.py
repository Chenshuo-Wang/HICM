with open(r'C:\Users\Chens\Desktop\Microphone\KiCAD\AFE.kicad_sch', 'r', encoding='utf-8') as f:
    text = f.read()

import re

# find all symbols
pos = text.find('\n\t(junction')
matches = re.findall(r'\(symbol\s+\(lib_id\s+"([^"]+)".*?\(at\s+([-0-9.]+)\s+([-0-9.]+)(?:\s+[-0-9.]+)?\).*?\(property\s+"Reference"\s+"([^"]+)".*?\(property\s+"Value"\s+"([^"]+)"', text[pos:], re.DOTALL)
for lib, x, y, ref, val in matches:
    x, y = float(x), float(y)
    if abs(x - 40.64) < 15 and 60 <= y <= 120:
        print(f'{ref} ({val}, {lib}) at ({x}, {y})')
