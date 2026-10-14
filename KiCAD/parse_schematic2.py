import re
from collections import defaultdict

sch_path = r'C:\Users\Chens\Desktop\Microphone\KiCAD\PowerSupply.kicad_sch'

with open(sch_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Parse wires
wires = []
wire_blocks = re.findall(r'\(wire\s+\(pts\s+(.*?)\)\s+\(stroke', text, re.DOTALL)
for wb in wire_blocks:
    pts = re.findall(r'\(xy\s+([-0-9.]+)\s+([-0-9.]+)\)', wb)
    pts = [(round(float(x), 2), round(float(y), 2)) for x, y in pts]
    for i in range(len(pts) - 1):
        wires.append((pts[i], pts[i+1]))

# 2. Parse labels
labels = []
for m in re.finditer(r'\((global_label|hierarchical_label|label)\s+"([^"]+)"\s*(?:\([^\)]*\)\s*)*\(at\s+([-0-9.]+)\s+([-0-9.]+)', text):
    ltype, lname, lx, ly = m.group(1), m.group(2), round(float(m.group(3)), 2), round(float(m.group(4)), 2)
    labels.append((ltype, lname, (lx, ly)))

# 3. Parse lib_symbols to know pin definitions and their local positions
# A symbol in lib_symbols has sub-symbols with (pin <type> <shape> (at X Y R) ... (name "...") (number "..."))
lib_symbol_pins = defaultdict(list)
# Find each lib_symbol
for m in re.finditer(r'\(symbol\s+"([^"]+)"\s*(.*?)\n\t\t\)', text, re.DOTALL):
    sname = m.group(1)
    sbody = m.group(2)
    # search pins inside sbody
    # pin can be in sub-symbols
    for pm in re.finditer(r'\(pin\s+\w+\s+\w+\s+\(at\s+([-0-9.]+)\s+([-0-9.]+)\s+([-0-9.]+)\)[^\)]*\(length\s+[-0-9.]+\)[^\)]*\(name\s+"([^"]*)"[^\)]*\)\s*\(number\s+"([^"]*)"', sbody, re.DOTALL):
        px = round(float(pm.group(1)), 2)
        py = round(float(pm.group(2)), 2)
        prot = round(float(pm.group(3)), 2)
        pname = pm.group(4)
        pnum = pm.group(5)
        lib_symbol_pins[sname].append({
            'num': pnum,
            'name': pname,
            'pos': (px, py, prot)
        })

# 4. Parse schematic symbol instances
pos = text.find('\n\t(junction')
sym_starts = [m.start() for m in re.finditer(r'\n\t\(symbol\b', text[pos:])]
symbol_blocks = []
for s in sym_starts:
    actual_start = pos + s + 2
    count = 0
    i = actual_start
    while i < len(text):
        if text[i] == '(':
            count += 1
        elif text[i] == ')':
            count -= 1
            if count == 0:
                symbol_blocks.append(text[actual_start:i+1])
                break
        elif text[i] == '"':
            i += 1
            while i < len(text):
                if text[i] == '\\':
                    i += 2
                    continue
                if text[i] == '"':
                    break
                i += 1
        i += 1

symbols = []
for sb in symbol_blocks:
    lib_id_m = re.search(r'\(lib_id\s+"([^"]+)"\)', sb)
    at_m = re.search(r'\(at\s+([-0-9.]+)\s+([-0-9.]+)(?:\s+([-0-9.]+))?\)', sb)
    ref_m = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', sb)
    val_m = re.search(r'\(property\s+"Value"\s+"([^"]+)"', sb)
    if lib_id_m and at_m and ref_m and val_m:
        lib_id = lib_id_m.group(1)
        x = round(float(at_m.group(1)), 2)
        y = round(float(at_m.group(2)), 2)
        rot = round(float(at_m.group(3)), 2) if at_m.group(3) else 0.0
        ref = ref_m.group(1)
        val = val_m.group(1)
        
        # Check if symbol has pin UUID mappings or pins in instance:
        # KiCad 6+ stores: (pin "1" (uuid "..."))
        symbols.append({
            'lib_id': lib_id,
            'ref': ref,
            'val': val,
            'at': (x, y),
            'rot': rot,
            'raw': sb
        })

# Build net graph
adj = defaultdict(set)
for p1, p2 in wires:
    adj[p1].add(p2)
    adj[p2].add(p1)

visited = set()
net_list = []
point_to_net = {}
for pt in adj:
    if pt not in visited:
        comp = []
        q = [pt]
        visited.add(pt)
        while q:
            c = q.pop(0)
            comp.append(c)
            for n in adj[c]:
                if n not in visited:
                    visited.add(n)
                    q.append(n)
        net_idx = len(net_list)
        net_list.append(comp)
        for p in comp:
            point_to_net[p] = net_idx

# Label nets
net_names = {}
for ltype, lname, lpos in labels:
    if lpos in point_to_net:
        net_names[point_to_net[lpos]] = lname
    else:
        for p in point_to_net:
            if abs(p[0] - lpos[0]) < 0.2 and abs(p[1] - lpos[1]) < 0.2:
                net_names[point_to_net[p]] = lname
                break

for s in symbols:
    if s['lib_id'].startswith('power:'):
        pos = s['at']
        pname = s['val']
        if pos in point_to_net:
            net_names[point_to_net[pos]] = pname
        else:
            for p in point_to_net:
                if abs(p[0] - pos[0]) < 0.2 and abs(p[1] - pos[1]) < 0.2:
                    net_names[point_to_net[p]] = pname
                    break

def get_net_name(net_id):
    if net_id in net_names:
        return net_names[net_id]
    return f"Net_{net_id}"

# Function to transform pin coords
def transform_pin(px, py, sym_x, sym_y, rot):
    # In KiCad schematic, Y is downwards!
    # Symbol editor Y is upwards. So local py -> -py in schematic space if rot=0.
    # Let's verify rotation:
    import math
    rad = math.radians(rot)
    # in symbol editor: (px, py)
    # when placed at (sx, sy) with angle rot:
    # First reflect Y: (px, -py)
    # Then rotate by rot degrees (standard math: x' = x cos θ - y sin θ, y' = x sin θ + y cos θ)
    # But KiCad rotation in schematic is counter-clockwise?
    x_rel = px
    y_rel = -py
    rx = x_rel * math.cos(rad) - y_rel * math.sin(rad)
    ry = x_rel * math.sin(rad) + y_rel * math.cos(rad)
    return round(sym_x + rx, 2), round(sym_y + ry, 2)

# Let's find pins for each symbol by matching with net points
print("\n=== COMPONENT PIN CONNECTIONS ===")
for s in sorted(symbols, key=lambda x: x['ref']):
    if s['ref'].startswith('#'): continue
    ref = s['ref']
    val = s['val']
    lib_id = s['lib_id']
    pins_def = lib_symbol_pins.get(lib_id, [])
    # Let's see if we can find which nets are at each pin
    pin_connections = []
    for pd in pins_def:
        # try transform
        # KiCad angle might be 0, 90, 180, 270
        # Let's test standard transforms:
        pnum = pd['num']
        pname = pd['name']
        # Try both Y flip and no flip
        found_net = None
        for flip in [-1, 1]:
            for r_dir in [1, -1]:
                import math
                rad = math.radians(s['rot'] * r_dir)
                x_rel = pd['pos'][0]
                y_rel = pd['pos'][1] * flip
                rx = x_rel * math.cos(rad) - y_rel * math.sin(rad)
                ry = x_rel * math.sin(rad) + y_rel * math.cos(rad)
                cand = (round(s['at'][0] + rx, 2), round(s['at'][1] + ry, 2))
                for pt in point_to_net:
                    if abs(pt[0] - cand[0]) < 0.15 and abs(pt[1] - cand[1]) < 0.15:
                        found_net = get_net_name(point_to_net[pt])
                        break
                if found_net: break
            if found_net: break
        pin_connections.append(f"pin {pnum} ({pname}): {found_net if found_net else 'NC'}")
    
    print(f"\n{ref} ({val}, {lib_id}) at {s['at']}, rot={s['rot']}:")
    for pc in pin_connections:
        print(f"   {pc}")
