"""Check the USB-roof support location in the final shared plate (not only a trial)."""
from pathlib import Path
import json,zipfile,re
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
placement=next(r for r in json.loads((ROOT/'print/bambu-2026-10-13-RevF/plate-layout.json').read_text())['placements'] if r['part']=='P08')
# Sliced G-code uses bed-local coordinates; 3MF storage uses the plate grid.
p=placement['plate']-1;ox,oy=placement['xy_mm']
# USB roof in normalized tray coordinates: x4.35..17.35, y7..8, z7.6.
pos={'X':0.,'Y':0.,'Z':0.};obj=None;feature='';hits=[]
z=zipfile.ZipFile(OUT/'H2D-RevF-verification.gcode.3mf')
for line in z.read(f'Metadata/plate_{p+1}.gcode').decode().splitlines():
    if line.startswith('; start printing object, unique label id: '):obj=int(line.split(':')[1])
    elif line.startswith('; stop printing object'):obj=None
    elif line.startswith('; FEATURE: '):feature=line[11:]
    elif re.match(r'^G[0123] ',line):
        vals={k:float(v) for k,v in re.findall(r'([XYZE])(-?\d*\.?\d+)',line.split(';')[0])}
        new={k:vals.get(k,pos[k]) for k in pos};cx=(new['X']+pos['X'])/2-ox;cy=(new['Y']+pos['Y'])/2-oy
        if obj==11 and feature.startswith('Support') and vals.get('E',0)>0 and 4.35<=cx<=17.35 and 7<=cy<=8 and 6.2<=new['Z']<=7.6:
            hits.append(dict(feature=feature,z_mm=new['Z'],local_midpoint=[cx,cy]))
        pos=new
assert len(hits)>20 and any(h['feature']=='Support interface' for h in hits)
report=dict(status='PASS',USB_roof_support_segments=len(hits),support_interface_z_mm=sorted(set(h['z_mm'] for h in hits if h['feature']=='Support interface')),
            local_USB_roof_bounds_mm=[4.35,17.35,7,8,7.6],access='Removable from open tray and USB opening',
            other_support_access='P04 open finger pocket and shallow guide relief; P05 bed-only shoulder supports; H12 open sensor recess; H02 external shoulder. See reviewed geometry reports.')
(OUT/'final-support-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS: final P08 has',len(hits),'support segments beneath USB roof, including interface')
