import parse_schematic3 as ps

caps = ["C41", "C42", "C43", "C47", "C48", "C49", "C50", "C51", "C53", "C56", "C57", "C60", "C61", "C63"]

print("=== CHECKING ALL CAPACITORS IN CHARGE PUMP ===")
for ref in caps:
    s = next(x for x in ps.symbols if x['ref'] == ref)
    # C_Small has pins at (0, -2.54) and (0, 2.54) relative to origin (at s['at'])
    p1 = (round(s['at'][0], 2), round(s['at'][1] - 2.54, 2))
    p2 = (round(s['at'][0], 2), round(s['at'][1] + 2.54, 2))
    w1 = [w for w in ps.wires if p1 in w]
    w2 = [w for w in ps.wires if p2 in w]
    print(f"\n{ref} ({s['val']}) at {s['at']}:")
    print(f"  Top pin ({p1}): {w1 if w1 else 'FLOATING / NOT CONNECTED!'}")
    print(f"  Bottom pin ({p2}): {w2 if w2 else 'FLOATING / NOT CONNECTED!'}")
