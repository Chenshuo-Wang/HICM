import parse_schematic3 as ps

print("Wires around x in [130, 160], y in [20, 50]:")
for w in ps.wires:
    (x1, y1), (x2, y2) = w
    if (130 <= x1 <= 160 or 130 <= x2 <= 160) and (20 <= y1 <= 50 or 20 <= y2 <= 50):
        print(f"  ({x1}, {y1}) -> ({x2}, {y2})")
