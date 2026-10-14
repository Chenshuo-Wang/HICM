with open(r'C:\Users\Chens\Desktop\Microphone\KiCAD\full_netlist.net', 'r', encoding='utf-8') as f:
    text = f.read()

import re

# Find nets containing D4, D5, D6, D7, D8, D9, C41, C43, U7
# In KiCad netlist format, nets are:
# (net (code "...") (name "...")
#   (node (ref "...") (pin "..."))
#   ...
# )

nets = re.findall(r'\(net\s+\(code\s+"[^"]+"\)\s+\(name\s+"([^"]+)"\)(.*?)\n\s*\)', text, re.DOTALL)
print(f"Total nets in exported netlist: {len(nets)}")

target_refs = [f"D{i}" for i in range(4, 10)] + [f"C{i}" for i in range(41, 64)] + ["U7"]

for nname, nbody in nets:
    nodes = re.findall(r'\(node\s+\(ref\s+"([^"]+)"\)\s+\(pin\s+"([^"]+)"\)', nbody)
    matching = [f"{r}.{p}" for r, p in nodes if r in target_refs]
    if matching:
        all_nodes = [f"{r}.{p}" for r, p in nodes]
        print(f"\nNet: {nname}")
        print(f"   Nodes: {', '.join(all_nodes)}")
