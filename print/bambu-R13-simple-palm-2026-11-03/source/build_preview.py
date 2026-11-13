"""Combine the three native Bambu plate thumbnails without modifying them."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parents[1]/'preview'
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',22)
small=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',18)
canvas=Image.new('RGB',(1584,584),'#f5f7f9');draw=ImageDraw.Draw(canvas)
for i,caption in [(1,'Platte 1: Rahmen mit Rastgegenhaltern'),(2,'Platte 2: Traverse, Gehäuse, Passhilfen'),(3,'Platte 3: Fingerfläche nach oben')]:
    im=Image.open(P/f'plate_{i}.png').convert('RGBA')
    bg=Image.new('RGBA',im.size,'#f5f7f9');bg.alpha_composite(im)
    canvas.paste(bg.convert('RGB'),((i-1)*528+8,56))
    draw.text(((i-1)*528+18,18),caption,font=font,fill='#1c3040')
draw.text((18,556),'R13 · H2D · 0,4 mm · PLA · 100 % · 10 Stücke · Drucklagen und Stützen im Projekt gespeichert',font=small,fill='#334958')
canvas.save(P/'R13-Druckplatten.png')
