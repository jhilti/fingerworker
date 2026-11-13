#!/usr/bin/env python3
"""Compose peer-reviewed mechanical edits and genuine-sensor native query integration."""
from pathlib import Path
import json,hashlib,struct,re
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
BASE=ROOT/'review/onshape-flat132-2026-10-19/fingerworker_flat132.fs'
EXPECTED='3e5de8f56211cf2ed063b6b4294da5f77fea4c3fb881fa0c13b1288eca7932cc'
assert hashlib.sha256(BASE.read_bytes()).hexdigest()==EXPECTED
source=(HERE/'mount-proposal.fs').read_text()
records=[]
def change(label,old,new,count=1):
    global source
    actual=source.count(old)
    assert actual==count,(label,actual,count)
    source=source.replace(old,new)
    records.append(dict(label=label,old=old,new=new,count=count))
patch=json.loads((HERE/'comfort-roof-patch.json').read_text())
for item in (patch if isinstance(patch,list) else patch['replacements']):
    change(item.get('label',item.get('name','comfort/roof')),item['old'],item['new'],item.get('count',1))
change('reinforce closed preload slot ends',
    '            makeBox(context,id + ("cassetteGuide"~t),vector(-16.2,lo,3.8)*mm,vector(-8,lo+3,29)*mm);',
    '''            makeBox(context,id + ("cassetteGuide"~t),vector(-16.2,lo,3.8)*mm,vector(-8,lo+3,29)*mm);
            // Retain 2.3 mm at the closed slot end; this cap stays below the lead.
            makeBox(context,id + ("cassetteGuideEndCap"~t),vector(-8.1,lo,3.8)*mm,
                vector(-6.5,lo+3,11.7)*mm);
            join(context,id + ("cassetteGuideEndCapJoin"~t),
                [body(id + ("cassetteGuide"~t)),body(id + ("cassetteGuideEndCap"~t))]);''')
change('clear strengthened preload slot caps from yoke',
    '        cut(context,id + "yokeRelief",body(id + "springAnchor"),qUnion([body(id + "yokeSensorTool"),body(id + "yokeCableTool")]));',
    '''        cut(context,id + "yokeRelief",body(id + "springAnchor"),qUnion([body(id + "yokeSensorTool"),body(id + "yokeCableTool")]));
        for (var side in [-1,1])
        {
            const t=side == -1 ? "0" : "1";
            const loY=side == -1 ? -19 : 15;
            makeBox(context,id + ("yokeGuideCapTool"~t),vector(-8.2,loY,3.3)*mm,
                vector(-6.0,loY+4,12.2)*mm);
            cut(context,id + ("yokeGuideCapClearance"~t),body(id + "springAnchor"),
                body(id + ("yokeGuideCapTool"~t)));
        }''')
change('manufacturing M3 tap-drill rather than smooth clearance envelope',
       'vector(-12.8,side*11.9,8.5)*mm,vector(-12.8,side*15.2,8.5)*mm,1.55*mm',
       'vector(-12.8,side*11.9,8.5)*mm,vector(-12.8,side*15.2,8.5)*mm,1.25*mm')
change('explicit final thread callout',
       '// Flat-bottom blind M3 bore to |Y|11.9; 2 mm engaged from |Y|13..15',
       '// Flat-bottom blind pilot dia2.5, TAP M3x0.5 to |Y|11.9; 2 mm engaged from |Y|13..15')
change('actual sensor query', '    precondition\n    {\n', '''    precondition
    {
        annotation { "Name" : "Aligned official TE FX1901 solid (derive before this feature)",
            "Filter" : EntityType.BODY && BodyType.SOLID, "MaxNumberOfPicks" : 1 }
        definition.actualSensor is Query;
''')
change('require real input', '        const mm = millimeter;\n        const preload = definition.preloadAdjustment;', '''        const mm = millimeter;
        if (size(evaluateQuery(context,definition.actualSensor)) != 1)
            throw regenError("Select the aligned, unmodified official TE FX1901 manufacturer solid.",["actualSensor"]);
        const sensorBox = evBox3d(context,{"topology":definition.actualSensor,"tight":true});
        if (norm(sensorBox.minCorner-vector(-9.85,-12.5,5.5)*mm)>0.05*mm ||
            norm(sensorBox.maxCorner-vector(-1.9,27,30.5)*mm)>0.05*mm)
            throw regenError("Use the apex-aligned official STEP at its base origin; do not rescale or offset it.",["actualSensor"]);
        nameBody(context,definition.actualSensor,"H01 ACTUAL TE FX1901-0001-0200-L manufacturer STEP rev F");
        finishBody(context,definition.actualSensor,color(0.75,0.76,0.77));
        const preload = definition.preloadAdjustment;''')
start=source.index('        makeCylinder(context,id + "loadCell",')
end=source.index('        makeCylinder(context,id + "loadPusher",',start)
removed=source[start:end]
change('remove obsolete proxy generation',removed,'''        // H01 is the genuine STEP solid selected above, with its original shape.
        // The full flexible lead/connector is a routing requirement, not invented CAD.
''')
for suffix,name in [('loadCell','H01 TE FX1901-0001-0200-L compression cell'),('loadCellBoss','H01a Sensor force boss'),('loadCellOvermold','H01b Sensor cable overmold'),('loadCellCable','H01c Sensor cable'),('loadCellConnector','H01d Sensor connector')]:
    change('remove '+suffix+' proxy name',f'        nameBody(context,body(id + "{suffix}"),"{name}");\n','')
old='''body(id + "sensorCassette"),body(id + "loadCell"),body(id + "loadCellBoss"),
                    body(id + "loadCellOvermold"),body(id + "loadCellCable"),body(id + "loadCellConnector"),'''
change('genuine sensor follows synchronized preload',old,'body(id + "sensorCassette"),definition.actualSensor,')
change('native audit query parameter','export function auditFingerworkerCollisions(context is Context, id is Id) returns array','export function auditFingerworkerCollisions(context is Context, id is Id, sensor is Query) returns array')
change('remove proxy audit query','''    const sensor = qUnion([body(id + "loadCell"),body(id + "loadCellBoss"),
        body(id + "loadCellOvermold"),body(id + "loadCellCable"),body(id + "loadCellConnector")]);\n''','')
change('include manufacturer part in all-device audit','    const device = qBodyType(body(id), BodyType.SOLID);','    const device = qBodyType(qUnion([body(id),sensor]), BodyType.SOLID);')
change('pass actual sensor to collision checks','auditFingerworkerCollisions(context,id))','auditFingerworkerCollisions(context,id,definition.actualSensor))')
change('electronics audit query parameter','function makeElectronicsStudy(context is Context, id is Id) returns array','function makeElectronicsStudy(context is Context, id is Id, actualSensor is Query) returns array')
change('electronics audit includes manufacturer solid','const mechanism=qSubtraction(qBodyType(body(id),BodyType.SOLID),qUnion([electronics,hand]));','const mechanism=qSubtraction(qBodyType(qUnion([body(id),actualSensor]),BodyType.SOLID),qUnion([electronics,hand]));')
change('pass real sensor to electronics checks','makeElectronicsStudy(context,id))','makeElectronicsStudy(context,id,definition.actualSensor))')
change('accurate sensor-base audit','auditSolidPair(context,"Sensor / base",sensor,base,true)','auditSolidPair(context,"Sensor / base",sensor,base,false)')
# Scope statements follow the revised geometry rather than historic proxy dimensions.
source=source.replace('32 mm total height','35 mm nominal sensor-retainer envelope')
source=source.replace('Envelope180.1 x132 x32 including enclosure','Envelope180.1 x132 x35 including enclosure and captive sensor')
source=source.replace('"FingerworkerFlat132Study"','"FingerworkerFlat132ActualSensor"').replace('"Flat132 study 30 mm"','"Flat132 actual sensor - 30 mm travel"')
assert not re.search(r'body\(id \+ "loadCell(?:Boss|Overmold|Cable|Connector)?"\)',source)
OUT=HERE/'fingerworker_flat132_finished.fs'; OUT.write_text(source)
b=source.encode(); units=source.encode('utf-16-le'); fnv=2166136261
for (u,) in struct.iter_unpack('<H',units): fnv=((fnv^u)*16777619)&0xffffffff
identity={'file':str(OUT.relative_to(ROOT)),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'utf16_length':len(units)//2,'fnv1a32_utf16':f'{fnv:08x}','baseline_sha256':EXPECTED,'replacements':records}
(HERE/'source-build.json').write_text(json.dumps(identity,indent=2)+'\n')
print(json.dumps({k:v for k,v in identity.items() if k!='replacements'},indent=2))
