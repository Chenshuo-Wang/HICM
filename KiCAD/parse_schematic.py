import re
from collections import defaultdict

sch_path = r'C:\Users\Chens\Desktop\Microphone\KiCAD\PowerSupply.kicad_sch'

with open(sch_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Parse wires
# pts can have two or more xy
wires = []
# Find all (wire (pts ...))
wire_blocks = re.findall(r'\(wire\s+\(pts\s+(.*?)\)\s+\(stroke', text, re.DOTALL)
for wb in wire_blocks:
    pts = re.findall(r'\(xy\s+([-0-9.]+)\s+([-0-9.]+)\)', wb)
    pts = [(round(float(x), 2), round(float(y), 2)) for x, y in pts]
    for i in range(len(pts) - 1):
        wires.append((pts[i], pts[i+1]))

print(f"Total wire segments parsed: {len(wires)}")

# 2. Parse labels
labels = []
for m in re.finditer(r'\((global_label|hierarchical_label|label)\s+"([^"]+)"\s*(?:\([^\)]*\)\s*)*\(at\s+([-0-9.]+)\s+([-0-9.]+)', text):
    ltype, lname, lx, ly = m.group(1), m.group(2), round(float(m.group(3)), 2), round(float(m.group(4)), 2)
    labels.append((ltype, lname, (lx, ly)))
print(f"Total labels parsed: {len(labels)}")
for l in labels:
    print(f"  {l[0]}: {l[1]} at {l[2]}")

# 3. Parse power symbols
power_syms = []
# In KiCad, power symbols are (symbol (lib_id "power:...") (at X Y R) ... (property "Value" "...") ...)
# Let's find all symbols in the file
symbol_blocks = []
# symbols start at \n\t(symbol\n
pos = text.find('(lib_symbols')
# skip lib_symbols
# Find end of lib_symbols
pos = text.find('\n\t(junction') # junctions come right after lib_symbols
sym_starts = [m.start() for m in re.finditer(r'\n\t\(symbol\b', text[pos:])]
for s in sym_starts:
    actual_start = pos + s + 2 # skip \n\t
    # find matching paren
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

print(f"Total symbol blocks: {len(symbol_blocks)}")

# Let's extract symbol info
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

print(f"Parsed {len(symbols)} symbols")

# Now build nets from wires
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

print(f"Total connected net components: {len(net_list)}")

# Associate labels with nets
net_names = {}
for ltype, lname, lpos in labels:
    if lpos in point_to_net:
        net_names[point_to_net[lpos]] = lname
    else:
        # Check nearby (within 0.1)
        for p in point_to_net:
            if abs(p[0] - lpos[0]) < 0.1 and abs(p[1] - lpos[1]) < 0.1:
                net_names[point_to_net[p]] = lname
                break

# Also power symbols:
for s in symbols:
    if s['lib_id'].startswith('power:'):
        pos = s['at']
        pname = s['val']
        if pos in point_to_net:
            net_names[point_to_net[pos]] = pname
        else:
            for p in point_to_net:
                if abs(p[0] - pos[0]) < 0.1 and abs(p[1] - pos[1]) < 0.1:
                    net_names[point_to_net[p]] = pname
                    break

print("Named nets:")
for k, v in net_names.items():
    print(f"  Net {k}: {v} (size {len(net_list[k])})")
