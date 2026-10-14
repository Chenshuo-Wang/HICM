import parse_schematic3 as ps

print("=== NET CONNECTIVITY FOR CHARGE PUMP & ADP5070 ===")

# Build net to component map
net_to_comp = ps.defaultdict(list)

# Re-run pin connection logic to collect (comp, pin_name, pin_num, net)
for s in ps.symbols:
    ref = s['ref']
    if ref.startswith('#'): continue
    val = s['val']
    lib_id = s['lib_id']
    pins_def = ps.lib_symbol_pins.get(lib_id, [])
    for pd in pins_def:
        pnum = pd['num']
        pname = pd['name']
        for flip_y in [-1, 1]:
            for flip_x in [1, -1]:
                for r in [0, 90, 180, 270]:
                    import math
                    rad = math.radians(s['rot'])
                    px, py = pd['pos'][0] * flip_x, pd['pos'][1] * flip_y
                    c = round(math.cos(rad))
                    si = round(math.sin(rad))
                    rx = px * c - py * si
                    ry = px * si + py * c
                    cand = (round(s['at'][0] + rx, 2), round(s['at'][1] + ry, 2))
                    found_net = None
                    for pt in ps.point_to_net:
                        if abs(pt[0] - cand[0]) < 0.05 and abs(pt[1] - cand[1]) < 0.05:
                            found_net = ps.get_net_name(ps.point_to_net[pt])
                            break
                    if found_net: break
                if found_net: break
            if found_net: break
        if found_net:
            net_to_comp[found_net].append((ref, val, pnum, pname))

for net in sorted(net_to_comp.keys()):
    comps = net_to_comp[net]
    print(f"\nNet: {net}")
    for ref, val, pnum, pname in sorted(comps):
        print(f"   {ref} ({val}) pin {pnum} [{pname}]")
