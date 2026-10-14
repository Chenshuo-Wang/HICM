# Let's inspect the exact lines of Diode:BAV99 pins in the schematic lib_symbols
with open(r'C:\Users\Chens\Desktop\Microphone\KiCAD\PowerSupply.kicad_sch', 'r', encoding='utf-8') as f:
    text = f.read()

import re

# Find BAV99 pin 3 definition
bav_start = text.find('(symbol "Diode:BAV99"')
bav_end = text.find('\n\t\t(symbol "GM1200', bav_start)
bav_block = text[bav_start:bav_end]

pins = re.findall(r'\(pin\s+([^\)]+)\)', bav_block)
for p in pins:
    print("(pin " + p.replace('\n', ' ') + ")")

# Also check D4 instance
d4_pos = text.find('"D4"')
d4_block = text[text.rfind('\n\t(symbol', 0, d4_pos):text.find('\n\t(symbol', d4_pos)]
print("\nD4 instance:")
print(d4_block[:400])

# Also check C41 instance
c41_pos = text.find('"C41"')
c41_block = text[text.rfind('\n\t(symbol', 0, c41_pos):text.find('\n\t(symbol', c41_pos)]
print("\nC41 instance:")
print(c41_block[:400])
