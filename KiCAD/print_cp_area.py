sch_path = r'C:\Users\Chens\Desktop\Microphone\KiCAD\PowerSupply.kicad_sch'
with open(sch_path, 'r', encoding='utf-8') as f:
    text = f.read()

import re
start = text.find('(symbol "Device:C_Small"')
print(text[start:start+1200])

print("\n--- ALL WIRES IN CP AREA (x > 125, y < 55) ---")
wire_blocks = re.findall(r'\(wire\s+\(pts\s+(.*?)\)\s+\(stroke', text, re.DOTALL)
for wb in wire_blocks:
    pts = re.findall(r'\(xy\s+([-0-9.]+)\s+([-0-9.]+)\)', wb)
    pts = [(round(float(x), 2), round(float(y), 2)) for x, y in pts]
    p1, p2 = pts[0], pts[1]
    if (p1[0] > 125 or p2[0] > 125) and (p1[1] < 55 and p2[1] < 55):
        print(f"  {p1} -> {p2}")
