with open(r'C:\Users\Chens\Desktop\Microphone\KiCAD\full_netlist.net', 'r', encoding='utf-8') as f:
    text = f.read()

for line in text.splitlines():
    if '"D4"' in line:
        print(line)
