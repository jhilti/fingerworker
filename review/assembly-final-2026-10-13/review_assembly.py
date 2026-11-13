"""Staged rigid assembly review of current print geometry, mm, no load rating."""
from pathlib import Path
from io import BytesIO
import zipfile,json,re,hashlib
import numpy as np
import trimesh as tm
import manifold3d as mf
import cadquery as cq
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
models={}
with zipfile.ZipFile(ROOT/'review/rear-tether-2026-09-29/Onshape_open_all_parts.zip') as z:
    for name in z.namelist():
        match=re.search(r' - (\w+)\b',name)
        if match and name.endswith('.stl'):models[match[1]]=tm.load_mesh(BytesIO(z.read(name)),file_type='stl')
for key,name in [('P01','P01_base_6mm_AssemblyClear_RevB_2026-10-13'),('P060','P060_rear_retainer_left_RevC_2026-10-13'),('P061','P061_rear_retainer_right_RevC_2026-10-13')]:
    models[key]=tm.load_mesh((ROOT/'review/assembly-clear-2026-10-13' if key=='P01' else OUT)/(name+'_Onshape_original.stl'))
for key,name in [('P02','P02_Palm_mount_RevA'),('P08','P08_Electronics_tray'),('P09','P09_Electronics_lid'),('P10','P10_Wire_clamp')]:
    solid=cq.importers.importStep(str(ROOT/'mechanical/manufacturing-2026-10-11/step'/(name+'.step'))).val()
    dest=OUT/(key+'_reference.stl');cq.exporters.export(solid,str(dest),tolerance=.025,angularTolerance=.08)
    models[key]=tm.load_mesh(dest)
for key,name in [('P03a','P03a_Palm_shell_left_PETG_MOCKUP'),('P03b','P03b_Palm_shell_right_PETG_MOCKUP')]:
    solid=cq.importers.importStep(str(ROOT/'print/rigid-palm-2026-10-13/step'/(name+'.step'))).val()
    dest=OUT/(key+'_reference.stl');cq.exporters.export(solid,str(dest),tolerance=.025,angularTolerance=.08)
    models[key]=tm.load_mesh(dest)
def M(mesh):return mf.Manifold(mf.Mesh(np.asarray(mesh.vertices,dtype=np.float32),np.asarray(mesh.faces,dtype=np.uint32)))
def union(keys):return mf.Manifold.batch_boolean([M(models[k]) for k in keys],mf.OpType.Add)
results=[]
def path(label,part,fixed,axis,offsets):
    solid=M(models[part]);obstacles=union(fixed);checks=[]
    for amount in offsets:
        shift=np.zeros(3);shift[axis]=amount
        vol=(solid.translate(shift.tolist()) ^ obstacles).volume()
        assert vol<.001,(label,amount,vol)
        checks.append(dict(offset_mm=float(amount),intersection_mm3=vol))
    results.append(dict(stage=label,moving_part=part,installed_parts=fixed,axis='XYZ'[axis],checks=checks))
# No rear caps/rods/springs/stop screws during carriage insertion. These are
# assembly states, separate from the three qualified nominal operating poses.
front=['P01','P02','P03a','P03b','H11','H15']
path('Griff von hinten einschieben','P04',front,0,list(np.arange(0,181,2)))
sweep=M(models['P04']).minkowski_sum(mf.Manifold.cube([180,.0002,.0002]).translate([0,-.0001,-.0001]))
volume=(sweep ^ union(front)).volume();assert volume<.001
results[-1]['continuous_sweep_intersection_mm3']=volume
path('Handballenauflage von oben aufsetzen','P02',['P01','P04','P05'],2,[0,.5,1,2,5,10,20,40,80])
path('Linke starre Halbschale seitlich an die noch unmontierte Auflage setzen','P03a',['P02'],0,[0,-.5,-1,-2,-5,-10,-20,-40,-80])
path('Rechte starre Halbschale seitlich an die noch unmontierte Auflage setzen','P03b',['P02','P03a'],0,[0,.5,1,2,5,10,20,40,80])
models['P02_with_shells']=tm.util.concatenate([models['P02'],models['P03a'],models['P03b']])
path('Vormontierte Handballenauflage mit Halbschalen von oben aufsetzen','P02_with_shells',['P01','P04','P05'],2,[0,.5,1,2,5,10,20,40,80])
path('Vorspannungsmutter vor der Kassette von vorne einsetzen','H11',['P01'],0,[0,.5,1,2,5,10,20,40,80])
path('Halteplatte von hinten in die Vertiefung setzen','H15',['P01','H11'],0,[0,-.5,-1,-2,-5,-10,-20,-40,-80])
path('Sensorkassette von oben einsetzen, seitliche Schrauben danach','H12',['P01','H11','H15'],2,[0,.5,1,2,5,10,20,40,80])
models['P05_with_pusher']=tm.util.concatenate([models['P05'],models['H02']])
models['P05_offset_6']=models['P05_with_pusher'].copy();models['P05_offset_6'].apply_translation([6,0,0])
sensor=['H12','H01','H01a','H01b','H01c','H01d']
path('Federjoch mit vormontiertem Druckstift um 6 mm nach vorne versetzt absenken','P05_offset_6',['P01','P04',*sensor],2,[0,.5,1,2,5,10,20,40,80])
path('Abgesenktes Federjoch waagrecht 6 mm nach hinten an den Sensor schieben','P05_with_pusher',['P01','P04',*sensor],0,list(np.arange(0,6.01,.25)))
for rod in ['H040','H041']:
    path('Stab von hinten durch Griff und Joch in vorderen Sackloch-Sockel schieben',rod,['P01','P04','P05'],0,[0,.5,1,2,5,10,20,40,80,160])
for cap,rod in [('P060','H040'),('P061','H041')]:
    path('Hinteren Halter von hinten auf Stabende schieben und danach verschrauben',cap,['P01','P04',rod],0,[0,.5,1,2,5,10,20,40,80])
path('Geschlossene Elektronikwanne von unten montieren','P08',['P01','P02','P03a','P03b'],2,[0,-.5,-1,-2,-5,-10,-20,-40,-80])
# Nominal bolt/counterbore fit is checked explicitly, rather than assuming that
# a collision-free operating model proves fasteners can be assembled.
fasteners=[]
for y in [-83,-67,67,83]:
    cap='P060' if y<0 else 'P061'
    shaft=tm.creation.cylinder(radius=1.5,height=8,sections=48);shaft.apply_translation([129.5,y,6])
    head=tm.creation.cylinder(radius=2.75,height=3,sections=48);head.apply_translation([129.5,y,11.5])
    # Thread engagement into the pilot is intentional; check cap clearance only.
    vol=((M(shaft)+M(head)) ^ M(models[cap])).volume();assert vol<.001
    fasteners.append(dict(type='rear M3x8, head Ø5.5x3',axis_mm=[129.5,y],cap_intersection_mm3=vol,nominal_insert_engagement_mm=2.5))
for y in [-56,-45,45,56]:
    shaft=tm.creation.cylinder(radius=2,height=10,sections=48);shaft.apply_translation([-15,y,8.5])
    head=tm.creation.cylinder(radius=3.5,height=4,sections=48);head.apply_translation([-15,y,15.5])
    vol=((M(shaft)+M(head)) ^ M(models['P02'])).volume();assert vol<.001
    fasteners.append(dict(type='palm M4x10, head Ø7x4',axis_mm=[-15,y],palm_intersection_mm3=vol,nominal_insert_engagement_mm=6))
source_sha=hashlib.sha256((ROOT/'fingerworker_mvp.fs').read_bytes()).hexdigest()
assert source_sha==json.loads((OUT/'caps-validation.json').read_text())['source_sha256']
assert hashlib.sha256((OUT/'before-cap-bore-fix.fs').read_bytes()).hexdigest()==json.loads((ROOT/'review/assembly-clear-2026-10-13/validation.json').read_text())['source_sha256']
report=dict(status='PASS',source_sha256=source_sha,stages=results,fasteners=fasteners,
    rigid_palm_source_sha256=hashlib.sha256((ROOT/'print/rigid-palm-2026-10-13/source/build_rigid_palm.py').read_bytes()).hexdigest(),
    rigid_palm_validation=json.loads((ROOT/'print/rigid-palm-2026-10-13/validation.json').read_text()),
    exclusions=['Rigid PETG/PLA shells are retained temporarily with tape; hard return-pad mockups provide no TPU damping',
    'No compressed-spring installation/load test; assessment build remains spring-free',
    'Printed metal mockups have plain envelopes/core holes, requiring purchased fasteners and thread finishing or metal parts for a functional build',
    'Real PCB, cell, cable bundle and insert-manufacturer dimensions still require fitting'],
    conclusion='Rear insertion, top-loaded rigid subassemblies, rod threading, rear caps and electronics approach are nominally assemblable in the documented sequence.')
(OUT/'validation.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
print('PASS',len(results),'assembly paths;',sum(len(r['checks']) for r in results),'poses;',len(fasteners),'bolt clearance checks')
