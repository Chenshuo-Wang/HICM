with open(r'C:\Users\Chens\Desktop\Microphone\KiCAD\full_netlist.net', 'r', encoding='utf-8') as f:
    text = f.read()

import re

# Find each net
nets = re.findall(r'\(net\s+\(code\s+"([^"]+)"\)\s+\(name\s+"([^"]+)"\)(.*?)\n\t\t\)', text, re.DOTALL)

target_refs = set([f"D{i}" for i in range(4, 10)] + [f"C{i}" for i in range(41, 64)] + [f"R{i}" for i in [52, 54]] + ["U7"])

for code, name, body in nets:
    nodes = re.findall(r'\(node\s+\(ref\s+"([^"]+)"\)\s+\(pin\s+"([^"]+)"\)\s*(?:\(pinfunction\s+"([^"]+)"\))?', body)
    matched_nodes = [f"{r}.{p}({fn})" for r, p, fn in nodes if r in target_refs]
    if matched_nodes:
        all_nodes = [f"{r}.{p}" for r, p, fn in nodes]
        print(f"Net '{name}': {', '.join(all_nodes)}")
