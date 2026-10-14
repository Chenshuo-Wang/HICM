import parse_schematic3 as ps

print("=== ALL SEGMENTS OF Net_7 (SW1) ===")
net_7_pts = ps.net_list[ps.point_to_net[(101.6, 53.34)]]
for w in ps.wires:
    p1, p2 = w
    if p1 in net_7_pts or p2 in net_7_pts:
        print(f"  {p1} -> {p2}")

print("\n=== ALL SEGMENTS OF Net_5 (OUT1) ===")
net_5_pts = ps.net_list[ps.point_to_net[(121.92, 53.34)]]
for w in ps.wires:
    p1, p2 = w
    if p1 in net_5_pts or p2 in net_5_pts:
        print(f"  {p1} -> {p2}")
