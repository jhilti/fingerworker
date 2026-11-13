"""Combine the two final native Bambu thumbnails for the package overview."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parents[1]/'preview'
f=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',24)
f2=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',18)
canvas=Image.new('RGB',(1056,584),'#f5f7f9');d=ImageDraw.Draw(canvas)
for i,caption in [(1,'Platte 1: P01 mit integrierter Auflage'),(2,'Platte 2: 17 vorhandene R9-Teile')]:
    im=Image.open(P/f'plate_{i}.png').convert('RGBA');base=Image.new('RGBA',im.size,'#f5f7f9');base.alpha_composite(im)
    canvas.paste(base.convert('RGB'),((i-1)*528+8,56));d.text(((i-1)*528+18,18),caption,font=f,fill='#1c3040')
d.text((18,556),'H2D / 0,4 mm / PLA / 100 % — Stützen und Brims sind im Projekt gespeichert.',font=f2,fill='#334958')
canvas.save(P/'R10-Druckplatten.png')
print('Final native two-plate preview saved')
