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

# 3. Parse lib_symbols
# Find the lib_symbols section
lib_start = text.find('(lib_symbols')
lib_end = text.find('\n\t(junction')
lib_text = text[lib_start:lib_end]

# Each symbol in lib_symbols starts with \t\t(symbol "lib_id"
# We can find each top level symbol by matching \n\t\t\(symbol "([^"]+)"
sym_splits = list(re.finditer(r'\n\t\t\(symbol\s+"([^"]+)"', lib_text))
lib_symbol_pins = defaultdict(list)

for i in range(len(sym_splits)):
    sname = sym_splits[i].group(1)
    st_idx = sym_splits[i].start()
    end_idx = sym_splits[i+1].start() if i+1 < len(sym_splits) else len(lib_text)
    sblock = lib_text[st_idx:end_idx]
    
    # find all pins in this block
    # (pin <type> <shape> (at X Y R) ... (name "...") (number "..."))
    for pm in re.finditer(r'\(pin\s+\w+\s+\w+\s+\(at\s+([-0-9.]+)\s+([-0-9.]+)\s+([-0-9.]+)\).*?\(name\s+"([^"]*)".*?\(number\s+"([^"]*)"', sblock, re.DOTALL):
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

print("Lib symbol pins found:")
for k, v in lib_symbol_pins.items():
    print(f"  {k}: {len(v)} pins")

# 4. Parse instances
pos = text.find('\n\t(junction')
symbol_blocks = []
sym_starts = [m.start() for m in re.finditer(r'\n\t\(symbol\b', text[pos:])]
for s in sym_starts:
    actual_start = pos + s + 2
    count = 0
    idx = actual_start
    while idx < len(text):
        if text[idx] == '(':
            count += 1
        elif text[idx] == ')':
            count -= 1
            if count == 0:
                symbol_blocks.append(text[actual_start:idx+1])
                break
        elif text[idx] == '"':
            idx += 1
            while idx < len(text):
                if text[idx] == '\\':
                    idx += 2
                    continue
                if text[idx] == '"':
                    break
                idx += 1
        idx += 1

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

print("\n=== DETAILED PIN NETS ===")
for s in sorted(symbols, key=lambda x: x['ref']):
    if s['ref'].startswith('#'): continue
    ref = s['ref']
    val = s['val']
    lib_id = s['lib_id']
    pins_def = lib_symbol_pins.get(lib_id, [])
    pin_connections = []
    for pd in pins_def:
        pnum = pd['num']
        pname = pd['name']
        found_net = None
        # In KiCad eeschema:
        # rotation angle θ is counter-clockwise (or clockwise in screen coordinates where +y is down)
        # Let's test standard rotations:
        for flip_y in [-1, 1]:
            for flip_x in [1, -1]:
                for r in [0, 90, 180, 270]:
                    import math
                    rad = math.radians(s['rot'])
                    # Let's test angle formula
                    px, py = pd['pos'][0] * flip_x, pd['pos'][1] * flip_y
                    # rotation matrix in screen coords
                    # (x, y) rotated by rot:
                    c = round(math.cos(rad))
                    si = round(math.sin(rad))
                    rx = px * c - py * si
                    ry = px * si + py * c
                    cand = (round(s['at'][0] + rx, 2), round(s['at'][1] + ry, 2))
                    for pt in point_to_net:
                        if abs(pt[0] - cand[0]) < 0.05 and abs(pt[1] - cand[1]) < 0.05:
                            found_net = (get_net_name(point_to_net[pt]), cand)
                            break
                    if found_net: break
                if found_net: break
            if found_net: break
        
        if found_net:
            pin_connections.append(f"pin {pnum} ({pname}): {found_net[0]} at {found_net[1]}")
        else:
            pin_connections.append(f"pin {pnum} ({pname}): NC")
    
    print(f"\n{ref} ({val}, {lib_id}) at {s['at']}, rot={s['rot']}:")
    for pc in pin_connections:
        print(f"   {pc}")
