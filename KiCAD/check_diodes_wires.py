import parse_schematic3 as ps

print("=== CHECKING D4-D9 PINS AND WIRES ===")
# Let's inspect D4-D9 symbol coordinates and any wires touching them
for i in range(4, 10):
    ref = f"D{i}"
    s = next(x for x in ps.symbols if x['ref'] == ref)
    print(f"\n{ref} at {s['at']}:")
    # let's look at all wires with endpoints near s['at']
    for w in ps.wires:
        p1, p2 = w
        d1 = ((p1[0] - s['at'][0])**2 + (p1[1] - s['at'][1])**2)**0.5
        d2 = ((p2[0] - s['at'][0])**2 + (p2[1] - s['at'][1])**2)**0.5
        if d1 < 10 or d2 < 10:
            print(f"   Wire: {p1} -> {p2}")
