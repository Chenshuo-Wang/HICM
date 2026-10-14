with open(r'C:\Users\Chens\Desktop\Microphone\KiCAD\full_netlist.net', 'r', encoding='utf-8') as f:
    text = f.read()

lines = text.splitlines()
for i, line in enumerate(lines):
    if '(ref "D4")' in line:
        for j in range(max(0, i-5), min(len(lines), i+6)):
            print(f"{j}: {lines[j]}")
        print("="*40)
