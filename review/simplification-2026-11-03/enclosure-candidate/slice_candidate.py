#!/usr/bin/env python3
"""One-plate R12 integrated-ceiling local print candidate, never printer send."""
from pathlib import Path
import importlib.util,json,subprocess,hashlib
import trimesh
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
BASE=ROOT/'print/bambu-R11-PLA-click-2026-11-03'

def main():
    for name in ['profiles','source','source-mm','STL-print-oriented','runtime','validation']:(HERE/name).mkdir(exist_ok=True)
    for p in (BASE/'profiles').glob('*.json'):(HERE/'profiles'/p.name).write_bytes(p.read_bytes())
    spec=importlib.util.spec_from_file_location('project_builder',BASE/'source/build_project.py')
    b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
    b.OUT=HERE;b.BASE='R12_integrated_ceiling_LOCAL_CANDIDATE';b.PREVIOUS=BASE
    raw=HERE/'P01_integrated_ceiling_assembly.stl';clean=HERE/'P01_integrated_ceiling_local_slice.stl'
    m=trimesh.load_mesh(raw);before=float(m.volume);faces=len(m.faces)
    # OCP binary STL tessellation can retain mathematically zero-area facets at
    # tangent seams. Drop only those collapsed facets, never fill/remesh holes.
    m.update_faces(m.nondegenerate_faces());m.remove_unreferenced_vertices()
    assert m.is_volume and m.is_watertight and m.body_count==1
    assert abs(m.volume-before)<1e-8
    m.export(clean)
    (HERE/'local-tessellation.json').write_text(json.dumps(dict(raw_sha256=hashlib.sha256(raw.read_bytes()).hexdigest(),
        slice_stl_sha256=hashlib.sha256(clean.read_bytes()).hexdigest(),collapsed_triangles_removed=faces-len(m.faces),
        volume_change_mm3=float(m.volume)-before,scope='Local CSG candidate only; no mesh hole filling or surface remesh. Native release must export and validate independently.'),indent=2)+'\n')
    b.build(clean,ROOT/'fingerworker_mvp.fs','LOCAL_CSG_CANDIDATE_NOT_NATIVE',candidate=True)
    layout=json.loads((HERE/'candidate-flat-layout.json').read_text())
    CLI='/tmp/fingerworker-bambu-r8-runtime/BambuStudio.app/Contents/MacOS/BambuStudio'
    common=[CLI,'--datadir','/tmp/fingerworker-r12-enclosure-data','--arrange','0','--orient','0','--ensure-on-bed','--debug','2']
    native=HERE/layout['native_project'];sliced=HERE/'validation/integrated_ceiling_verification.gcode.3mf'
    cmds=[common+['--load-settings',str(HERE/'profiles/H2D_machine.json')+';'+str(HERE/'profiles/H2D_process.json'),'--load-filaments',str(HERE/'profiles/H2D_PLA.json'),'--outputdir',str(HERE),'--export-3mf',native.name,str(HERE/layout['seed_path'])],
          common+['--slice','0','--outputdir',str(sliced.parent),'--export-3mf',sliced.name,str(native)]]
    out=[]
    for i,cmd in enumerate(cmds):
        with (HERE/'runtime'/f'slice-{i}.log').open('w') as f:r=subprocess.run(cmd,cwd=HERE,stdout=f,stderr=subprocess.STDOUT)
        out.append(dict(command=cmd,exit_code=r.returncode));assert r.returncode==0
    report=dict(status='SLICED_LOCAL_CSG_CANDIDATE',no_printer_transmission=True,commands=out,
        slice_sha256=hashlib.sha256(sliced.read_bytes()).hexdigest(),
        scope='Local OCP proposal, not native manufacturing release. Builder inherited R11 label is superseded by this explicit candidate record.')
    (HERE/'slice-result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

if __name__=='__main__':main()
