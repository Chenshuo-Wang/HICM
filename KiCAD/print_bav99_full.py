with open(r'C:\Users\Chens\Desktop\Microphone\KiCAD\PowerSupply.kicad_sch', 'r', encoding='utf-8') as f:
    text = f.read()

start = text.find('(symbol "Diode:BAV99"')
end = text.find('(symbol "GM1200:GM1200"', start)
print(text[start:end])
