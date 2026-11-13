"""Update optional FeatureScript reference envelopes from actual PCB placement; no manufacturing claim."""
from pathlib import Path
import json
R=Path(__file__).resolve().parent;root=R.parents[1];pl=json.loads((R/'routing/placement-routing.json').read_text());F={x['ref']:x for x in pl}
base=(-43.35,-53.5,2.1);bodies=[];spec=[];code=[]
def box(suffix,name,lo,hi,c):
 def vec(p):return 'vector('+','.join(f'{t:g}' for t in p)+')*mm'
 code.append(f'    makeBox(context,id + "{suffix}",{vec(lo)},{vec(hi)});')
 code.append(f'    nameBody(context,body(id + "{suffix}"),"{name}");')
 code.append(f'    finishBody(context,body(id + "{suffix}"),color({c}));')
 spec.append({'id':suffix,'name':name,'lo':lo,'hi':hi})
box('elecCase','REF E00 - housing study 22.5 x 110 x 8.9 - not for printing',[-44.85,-55,0],[-22.35,55,8.9],'0.15,0.65,0.78,0.20')
# Holes are retained as cuts, not additional solids.
code.extend(['    makeBox(context,id + "elecVoid",vector(-43.85,-54,1)*mm,vector(-23.35,54,8.1)*mm);',
 '    makeBox(context,id + "elecPortCut",vector(-40.5,-56,2)*mm,vector(-27.5,-49,7.6)*mm);',
 '    makeBox(context,id + "elecButtonCut",vector(-46,-7.6,2.5)*mm,vector(-42,-3.6,5.4)*mm);',
 '    makeBox(context,id + "elecWireCut",vector(-25,-8,5.4)*mm,vector(-21.5,5,7.6)*mm);',
 '    cut(context,id + "elecHollow",body(id + "elecCase"),qUnion([body(id + "elecVoid"),body(id + "elecPortCut"),body(id + "elecButtonCut"),body(id + "elecWireCut")]));'])
box('elecCarrier','REF E01 - KiCad PCB 19.5 x 68.5 x 0.8',[-43.35,-53.5,1.3],[-23.85,15,2.1],'0.10,0.42,0.27')
# Courtyards deliberately overbound physical XY dimensions; heights include solder allowance.
for row in pl:
 ref=row['ref'];a,b,c,d=row['courtyard_mm'];lo=[base[0]+a,base[1]+b,base[2]]
 h=1.65 if ref[0] in 'RCDQL' else 1.65
 if ref=='U1':h=5
 if ref=='J1':h=5.65
 if ref=='SW2':h=2.5
 if ref in ['J2','J3']:h=2.3
 hi=[base[0]+c,base[1]+d,base[2]+h];s='elecPart'+ref;bodies.append(s)
 box(s,f'REF PCB {ref} - courtyard and height envelope',lo,hi,'0.15,0.40,0.90' if ref=='U1' else ('0.86,0.86,0.82' if ref=='J1' else '0.20,0.70,0.48'))
box('elecBattery','REF E05 - 100mAh LiPo nominal 11.5 x 31 x 3.8',[-40,19,1.5],[-28.5,50,5.3],'0.92,0.68,0.16')
box('elecUsb','REF E06 - USB approach clearance',[-39.5,-74,2.4],[-28.5,-54,7.3],'0.66,0.40,0.90,0.35')
# Reserve protruding portion of the mating housing plus an initial straight wire lead.
# 6 mm extension is an allowance, not a manufacturer-certified mated stack length.
box('elecMate','REF E07 - battery mating plug and lead allowance',[-35.85,14.7,2.45],[-27.85,20.7,7.75],'0.85,0.75,0.55,0.4')
# Move the cell 3 mm away from the plug allowance. Nominal end clearance becomes 1 mm.
for item in spec:
 if item['id']=='elecBattery':item['lo'][1]=22;item['hi'][1]=53
code=[s.replace('vector(-40,19,1.5)','vector(-40,22,1.5)').replace('vector(-28.5,50,5.3)','vector(-28.5,53,5.3)') for s in code]
# Side button travel envelope reaches the shell opening; no force transmitted to the PCB housing.
box('elecButton','REF E08 - side-button actuator travel envelope',[-45.25,-7.1,2.8],[-42.55,-4.1,5.1],'0.90,0.45,0.16,0.35')
code.extend(['    const housing=body(id + "elecCase");', '    const carrier=body(id + "elecCarrier");','    const battery=body(id + "elecBattery");',
 '    const populated=qUnion(['+','.join('body(id + "'+s+'")' for s in bodies)+']);',
 '    const cable=body(id + "elecMate");','    const actuator=body(id + "elecButton");',
 '    const components=qUnion([carrier,populated,battery,cable,actuator]);','    const usb=body(id + "elecUsb");',
 '    const electronics=qUnion([housing,components,usb]);',
 '    opTransform(context,id + "electronicsClearanceShift",{"bodies":electronics,"transform":transform(vector(-1.25,0,0)*mm)});','    const hand=body(id + "handReference");',
 '    const mechanism=qSubtraction(qBodyType(body(id),BodyType.SOLID),qUnion([electronics,hand]));',
 '    return [',
 '        auditSolidPair(context,"Electronics housing / mechanism",housing,mechanism,false),',
 '        auditSolidPair(context,"Electronics components / mechanism",components,mechanism,false),',
 '        auditSolidPair(context,"Electronics components / housing",components,housing,false),',
 '        auditSolidPair(context,"Battery / populated carrier and plug",battery,qUnion([carrier,populated,cable]),false),',
 '        auditSolidPair(context,"USB approach / mechanism",usb,mechanism,false),',
 '        auditSolidPair(context,"USB approach / housing",usb,housing,false),',
 '        auditSolidPair(context,"Electronics study / hand",electronics,hand,false)',
 '    ];'])
s=(root/'fingerworker_mvp.fs').read_text();a=s.index('function makeElectronicsStudy(');b=s.index('\nannotation { "Feature Type Name"',a)
s=s[:a]+'function makeElectronicsStudy(context is Context, id is Id) returns array\n{\n    const mm = millimeter;\n'+'\n'.join(code)+'\n}\n'+s[b:];(root/'fingerworker_mvp.fs').write_text(s)
for item in spec:
 item['lo'][0]-=1.25;item['hi'][0]-=1.25
base=(base[0]-1.25,base[1],base[2])
(R/'mechanical-envelopes.json').write_text(json.dumps({'status':'local study; Onshape regeneration pending','pcb_origin_mm':base,'case_inner':{'lo':[-45.1,-54,1],'hi':[-24.6,54,8.1]},'bodies':spec},indent=2))
print('Updated local study:',len(spec),'reference envelopes')
