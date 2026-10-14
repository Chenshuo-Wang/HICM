import parse_schematic3 as ps
import math

print("=== CHECKING ALL PINS OF CHARGE PUMP COMPONENTS ===")

cp_refs = [f"D{i}" for i in range(4, 10)] + [f"C{i}" for i in range(41, 64)] + ["R52", "R54"]

# Map all points in wires to their nets
pt_to_net = ps.point_to_net

for ref in cp_refs:
    s = next((x for x in ps.symbols if x['ref'] == ref), None)
    if not s: continue
    val = s['val']
    lib_id = s['lib_id']
    pins = ps.lib_symbol_pins[lib_id]
    print(f"\n{ref} ({val}) placed at {s['at']}, rot={s['rot']}:")
    for p in pins:
        pnum = p['num']
        pname = p['name']
        px, py, prot = p['pos']
        
        # In KiCad schematic:
        # local coords in symbol editor: (px, py).
        # KiCad eeschema screen: Y goes DOWN. In symbol editor, Y goes UP.
        # So symbol editor (px, py) maps to (px, -py) before rotation.
        # When rot = 0: x_sch = sym_x + px, y_sch = sym_y - py
        # When rot = 90: rotates 90 deg counter-clockwise in math (clockwise on screen)
        # Let's check rotation formula:
        rad = math.radians(s['rot'])
        # In KiCad screen coords:
        # A rotation of 90 deg counter-clockwise in symbol editor:
        # standard 2D rotation for (px, -py):
        # x' = px * cos(θ) + py * sin(θ) [depending on coordinate convention]
        # Let's test candidates:
        matched = None
        for sx in [1, -1]:
            for sy in [1, -1]:
                for swap in [False, True]:
                    x0 = px * sx
                    y0 = py * sy
                    if swap: x0, y0 = y0, x0
                    # rotate by s['rot']
                    r = math.radians(s['rot'])
                    rx = x0 * math.cos(r) - y0 * math.sin(r)
                    ry = x0 * math.sin(r) + y0 * math.cos(r)
                    cx = round(s['at'][0] + rx, 2)
                    cy = round(s['at'][1] + ry, 2)
                    if (cx, cy) in pt_to_net:
                        matched = ((cx, cy), ps.get_net_name(pt_to_net[(cx, cy)]))
                        break
                if matched: break
            if matched: break
        
        if matched:
            print(f"   Pin {pnum} [{pname}] connects at {matched[0]} to {matched[1]}")
        else:
            print(f"   Pin {pnum} [{pname}] -> NO CONNECTION FOUND (checked offsets from {px}, {py})")
