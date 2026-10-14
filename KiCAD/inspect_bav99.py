sch_path = r'C:\Users\Chens\Desktop\Microphone\KiCAD\PowerSupply.kicad_sch'
with open(sch_path, 'r', encoding='utf-8') as f:
    text = f.read()

start = text.find('(symbol "Diode:BAV99"')
print(text[start+3000:start+4200])
