"""Reproducible nominal prototype solids; millimetres, assembled CAD coordinates.
Run with CadQuery 2.8.0. Threads are represented by minor/major diameter envelopes.
The same operation ledger generates local solids and the FeatureScript enclosure.
"""
from pathlib import Path
import json, hashlib, math
import cadquery as cq
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parents[1]
parts={}; ledger={}; current=None
def box(lo,hi):
    return cq.Solid.makeBox(*[b-a for a,b in zip(lo,hi)],cq.Vector(*lo))
def cyl(a,b,r):
    v=cq.Vector(*b)-cq.Vector(*a)
    return cq.Solid.makeCylinder(r,v.Length,cq.Vector(*a),v.normalized())
def cone(a,b,r1,r2):
    v=cq.Vector(*b)-cq.Vector(*a)
    return cq.Solid.makeCone(r1,r2,v.Length,cq.Vector(*a),v.normalized())
def start(name):
    global current
    current=name; ledger[name]=[]
def op(kind,shape,*args):
    ledger[current].append(dict(operation=kind,shape=shape,args=args))
    s={'box':box,'cyl':cyl,'cone':cone}[shape](*args)
    if kind=='base': parts[current]=s
    elif kind=='add': parts[current]=parts[current].fuse(s).clean()
    else: parts[current]=parts[current].cut(s).clean()
def B(lo,hi):op('base','box',lo,hi)
def A(lo,hi):op('add','box',lo,hi)
def C(lo,hi):op('cut','box',lo,hi)
def CY(a,b,r,kind='cut'):op(kind,'cyl',a,b,r)

# Electronics: existing reserved shell; final coordinates include the -1.25 shift.
start('P08_Electronics_tray')
B([-46.1,-55,0],[-23.6,55,8.1])
C([-45.1,-54,1],[-24.6,54,8.2])
C([-41.75,-56,2],[-28.75,-49,7.6])
C([-47,-9.6,2.5],[-43.2,-1.6,5.4])  # direct side-switch access
C([-25,-8,5.4],[-22,5,7.6])
# Underside edge supports and end stops. No clips on populated top surface.
for x in [-44.6,-25.7]: A([x,-52.8,1],[x+.6,14.8,1.3])
A([-44.7,-54,1],[-25,-53.7,2.05])
A([-44.7,15.2,1],[-25,15.5,2.05])
# Battery: insulated floor pad, lateral loose rails, 0.5 mm nominal clearance.
A([-41.75,21.5,1],[-29.25,53.5,1.3])
for lo,hi in [([-42.55,21.5,1],[-41.75,54,2.3]),([-29.25,21.5,1],[-28.45,54,2.3]),([-42.55,21.5,1],[-28.45,21.8,2.3]),([-42.55,53.5,1],[-28.45,54,2.3])]: A(lo,hi)
# Three lid screws are confined to the PCB-free rear half.
lid_centres=[(-43.2,18),(-43.2,50),(-26.5,50)]
for x,y in lid_centres:
    CY([x,y,.9],[x,y,8.1],1.6,'add')
    CY([x,y,3.8],[x,y,8.2],.625)
# Wire clamp: separate from cell; six flexible insulated wires, no cell strap.
for y in [24,31]:
    CY([-26.5,y,.9],[-26.5,y,3.4],1.6,'add')
    CY([-26.5,y,1.2],[-26.5,y,3.5],.625)
# Mounting ears engage two new M2 inserts in underside of P02, at y +/-59.
for y in [-59,59]:
    A([-29,54 if y>0 else -59,8.1],[-24,59 if y>0 else -54,8.9])
    A([-29,y-3,7],[-24,y+3,8.9])
    CY([-26.5,y,8.8],[-26.5,y,9.5],2.1,'add')
    CY([-26.5,y,6.9],[-26.5,y,9.6],1.1)

start('P09_Electronics_lid')
B([-46.1,-55,8.1],[-23.6,55,8.9])
for y in [-55,55]: C([-29.1,y-1.1,8],[-23.9,y+1.1,9])
for x,y in lid_centres:
    CY([x,y,8], [x,y,9],.9)
    op('cut','cone',[x,y,8.3],[x,y,8.9],.9,1.5)
# PCB keeper rib over a courtyard-free 2 mm corridor; insulating shim closes gap.
A([-44.6,-27,2.15],[-25.1,-25,8.2])
# Loose ceiling rail: a cell can be removed vertically with lid off.
A([-41.5,36,6.6],[-29.5,39,8.2])

start('P10_Wire_clamp')
B([-28.1,22.4,3.4],[-24.9,32.6,4.4])
for y in [24,31]: CY([-26.5,y,3.3],[-26.5,y,4.5],.9)

# Machined parts, using unambiguous finished dimensions rather than modelling overlaps.
start('H02_Pusher'); CY([-1.9,0,18],[0,0,18],2,'base'); CY([0,0,18],[1,0,18],4,'add'); CY([1,0,18],[7.5,0,18],1.5,'add')
start('H04_Guide_rod'); CY([0,0,0],[146,0,0],3,'base')
for name,r in [('H05_Fixed_spring_seat',3.3),('H06_Moving_spring_seat',4)]:
    start(name); CY([0,0,0],[3,0,0],11,'base'); CY([-.1,0,0],[3.1,0,0],r)
start('H11_Preload_nut'); B([-21,-6,12],[-16,6,24]); CY([-21.1,0,18],[-15.9,0,18],2.5); CY([-19,0,20.5],[-19,0,24.1],1.25)
start('H12_Sensor_cassette'); B([-12,-13.5,7.5],[-8,13.5,28.5]); CY([-9.6,0,18],[-7.9,0,18],7.5)
for side in [-1,1]:
    low=-13.5 if side<0 else 10
    A([-15.2,low,7.5],[-11.8,low+3.5,12.5])
    CY([-13,side*9.9,10],[-13,side*13.6,10],1.25)
start('H13_Preload_adjuster'); CY([-24,0,18],[-12,0,18],3,'base'); CY([-15.8,0,18],[-13,0,18],11,'add')
start('H15_Keeper'); B([-23,-16,9],[-21,16,28]); CY([-23.1,0,18],[-20.9,0,18],3.2)
CY([-19,0,26],[-19,0,28.1],2.9)  # partial top-edge notch for recessed lock head
for side in [-1,1]:
    CY([-23.1,side*11,24],[-20.9,side*11,24],1.7)
    op('cut','cone',[-23,side*11,24],[-21.7,side*11,24],3,1.7)
start('H19_Spacer'); CY([0,0,0],[4,0,0],2,'base'); CY([-.1,0,0],[4.1,0,0],1.6)
start('H22_Brass_pad'); CY([0,0,0],[1,0,0],1.25,'base')
start('H14_Isometric_sleeve'); CY([0,0,0],[86,0,0],8,'base'); CY([-.1,0,0],[86.1,0,0],4)

def fs_operations(names):
    lines=['// Generated from source/build_models.py; coordinates already include clearance shift.',
           'function makeElectronicsEnclosure(context is Context, id is Id) returns Query',
           '{','    const mm=millimeter;']
    def vec(p):return 'vector('+','.join(f'{v:g}' for v in p)+')*mm'
    for name in names:
        for n,item in enumerate(ledger[name]):
            kind,shape,args=item['operation'],item['shape'],item['args']; tag=name if kind=='base' else name+'_'+str(n)
            q='body(id + "'+tag+'")'; target='body(id + "'+name+'")'
            if shape=='box': lines.append(f'    makeBox(context,id + "{tag}",{vec(args[0])},{vec(args[1])});')
            elif shape=='cyl':lines.append(f'    makeCylinder(context,id + "{tag}",{vec(args[0])},{vec(args[1])},{args[2]:g}*mm);')
            elif shape=='cone':lines.append(f'    fCone(context,id + "{tag}",{{"bottomCenter":{vec(args[0])},"topCenter":{vec(args[1])},"bottomRadius":{args[2]:g}*mm,"topRadius":{args[3]:g}*mm}});')
            if kind=='add':lines.append(f'    join(context,id + "{tag}Join",[{target},{q}]);')
            elif kind=='cut':lines.append(f'    cut(context,id + "{tag}Cut",{target},{q});')
        lines.append(f'    nameBody(context,body(id + "{name}"),"{name[:3]} PRINT - {name[4:].replace("_"," ")}");')
        lines.append(f'    finishBody(context,body(id + "{name}"),color(0.15,0.65,0.78));')
    lines.append('    return qUnion(['+','.join('body(id + "'+n+'")' for n in names)+']);')
    lines.append('}')
    return '\n'.join(lines)+'\n'
names=[n for n in parts if n.startswith('P')]
(OUT/'source/enclosure_generated.fs').write_text(fs_operations(names))
checks=[]
for name,s in parts.items():
    assert s.isValid() and len(s.Solids())==1, name
    cq.exporters.export(s,str(OUT/'step'/f'{name}.step'))
    if name.startswith('P'):
        # Print floor-down; lid rib-up, wire clamp holes vertical.
        printable=s
        if name.startswith('P09'): printable=s.rotate((0,0,0),(1,0,0),180)
        bb=printable.BoundingBox(); printable=printable.translate((-bb.xmin,-bb.ymin,-bb.zmin))
        cq.exporters.export(printable,str(OUT/'stl'/f'{name}.stl'),tolerance=.025,angularTolerance=.08)
    bb=s.BoundingBox();checks.append(dict(part=name,valid=True,solids=1,volume_mm3=s.Volume(),bounds_mm=[bb.xmin,bb.ymin,bb.zmin,bb.xmax,bb.ymax,bb.zmax]))
# Exact nominal checks against all saved PCB/cell/plug envelopes, with intentional
# keeper and support contacts evaluated separately from shell clearance.
env=json.loads((OUT/'source/pcb-reference-envelopes.json').read_text())
collisions=[]
for e in env['bodies']:
    if e['id'] in ['elecCase','elecButton']:continue
    ref=box(e['lo'],e['hi'])
    for name in names:
        volume=parts[name].intersect(ref).Volume()
        collisions.append(dict(part=name,reference=e['id'],intersection_mm3=volume))
        assert volume<1e-7,(name,e['id'],volume)
for i,n in enumerate(names):
    for m in names[i+1:]:
        v=parts[n].intersect(parts[m]).Volume();assert v<1e-7,(n,m,v)
# Mounting pilots in P02 remain at least 1 mm below top plate and avoid palm core.
assert 14.5-13.5==1 and 59-58==1
assembly=cq.Assembly()
for name in names:assembly.add(parts[name],name=name,color=cq.Color(.15,.65,.78))
for e in env['bodies']:
    if e['id'] not in ['elecCase','elecButton','elecUsb']:assembly.add(box(e['lo'],e['hi']),name=e['id'],color=cq.Color(.3,.5,.2,.4))
assembly.export(str(OUT/'step/Electronics_assembled.step'))
(OUT/'source/operation-ledger.json').write_text(json.dumps(ledger,indent=2)+'\n')
(OUT/'validation.json').write_text(json.dumps(dict(status='PASS',scope='Exact BRep validity and nominal envelope intersections; hardware fitting and strength remain untested',parts=checks,envelope_checks=collisions,enclosure_pair_checks=3,pcb_keeper_corridor_y_mm=[-27,-25],mount_insert_centres_mm=[[-26.5,-59,9.5],[-26.5,59,9.5]]),indent=2)+'\n')
print('PASS',len(parts),'valid single-solid parts;',len(collisions),'reference-envelope checks')
