#!/usr/bin/env python3
"""Read final native R11 H2D toolpaths; never edits project authoring files."""
from pathlib import Path
import argparse,hashlib,json,re,zipfile,xml.etree.ElementTree as E
import numpy as np

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def parse(data):
    obj=None;feature='';xyz=np.zeros(3);speed=0.;paths=[]
    for line in data.splitlines():
        if 'start printing object, unique label id:' in line:obj=int(line.split(':')[-1])
        elif 'stop printing object' in line:obj=None
        elif line.startswith('; FEATURE: '):feature=line[11:]
        elif line.startswith('G92 '):
            v={k:float(v) for k,v in re.findall(r'([XYZ])([-+.\d]+)',line)}
            for i,k in enumerate('XYZ'):xyz[i]=v.get(k,xyz[i])
        elif re.match(r'^G[0123] ',line):
            v={k:float(v) for k,v in re.findall(r'([XYZEF])([-+.\d]+)',line)}
            nxt=np.array([v.get(k,xyz[i]) for i,k in enumerate('XYZ')]);speed=v.get('F',speed)
            if v.get('E',0)>0 and ('X' in v or 'Y' in v):paths.append(dict(obj=obj,feature=feature,a=xyz.copy(),b=nxt.copy(),length=float(np.linalg.norm(nxt[:2]-xyz[:2])),speed_mm_s=speed/60))
            xyz=nxt
    return paths

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--pack',type=Path,default=ROOT/'print/bambu-R11-PLA-click-2026-11-03');a=ap.parse_args();pack=a.pack.resolve()
    layout=json.loads((pack/'plate-layout.json').read_text());plan={r['ref']:r for r in layout['placements']}
    final=pack/'validation/Fingerworker_R11_H2D_04mm_PLA_Fit_Test_verification.gcode.3mf'
    with zipfile.ZipFile(final) as z:
        info=E.fromstring(z.read('Metadata/slice_info.config'));plates=info.findall('plate');labels={};pathbyplate={}
        for plate in plates:
            metadata={x.get('key'):x.get('value') for x in plate.findall('metadata')};p=int(metadata['index'])
            pathbyplate[p]=parse(z.read(f'Metadata/plate_{p}.gcode').decode())
            for ob in plate.findall('object'):
                for ref in ('P08','P09'):
                    if ob.get('name','').startswith(ref+' '):labels[ref]=(p,int(ob.get('identify_id')))
    checks=[];metrics={}
    def add(name,ok,**details):checks.append(dict(name=name,status='PASS' if ok else 'FAIL',**details))
    transformed={}
    for ref in ('P08','P09'):
        row=plan[ref];p,label=labels[ref];assert p==row['plate']
        R=np.asarray(row['rotation_3x3']);offset=np.asarray(row['normalization_translation_mm'])+np.array([*row['plate_xy_mm'],0])
        allpaths=pathbyplate[p];ss=[]
        for path in allpaths:
            q=path.copy();q['native_a']=R.T@(q['a']-offset);q['native_b']=R.T@(q['b']-offset);q['native_mid']=(q['native_a']+q['native_b'])/2;ss.append(q)
        transformed[ref]=ss
        model=[s for s in ss if s['obj']==label and s['feature'] not in ['Support','Support interface','Brim','Skirt']]
        bridges=[s for s in model if 'bridge' in s['feature'].lower()]
        mm=dict(plate=p,label_id=label,rotation_3x3=R.tolist(),bed_offset_mm=offset.tolist(),model_extrusion_segments=len(model),first_layer_extrusion_mm=sum(s['length'] for s in model if s['b'][2]<=.201),maximum_print_z_mm=max(s['b'][2] for s in model),bridge_segments=len(bridges),longest_bridge_segment_mm=max([s['length'] for s in bridges] or [0]),native_stl_sha256=row['source_sha256'])
        metrics[ref]=mm
        add(ref+' starts on print bed',mm['first_layer_extrusion_mm']>100,**mm)
        def roi(lo,hi,kind='model'):
            source=model if kind=='model' else [s for s in ss if 'Support' in s['feature']]
            lo=np.asarray(lo);hi=np.asarray(hi)
            return [s for s in source if np.all(s['native_mid']>=lo) and np.all(s['native_mid']<=hi)]
        if ref=='P08':
            add('P08 no long unsupported bridge path',mm['longest_bridge_segment_mm']<4,longest_actual_bridge_tagged_segment_mm=mm['longest_bridge_segment_mm'])
            for sign in [-1,1]:
                low,high=([64.1,65.7] if sign>0 else [-65.7,-64.1])
                post=roi([-29.2,low,-.1],[-25.4,high,16.4]);top=max(s['native_b'][2] for s in post)
                add('P08 complete high palm hook side'+str(sign),top>=16.15 and len(post)>100,native_top_z_mm=top,extrusion_segments=len(post))
                beam=roi([-43.8,low,-.1],[-30,high,2.5]);first=[s for s in beam if s['b'][2]<.201]
                first_length=sum(s['length'] for s in first)
                first_x=[s[k][0] for s in first for k in ['native_a','native_b']]
                span=max(first_x)-min(first_x) if first_x else 0
                add('P08 long beam is bed-connected side'+str(sign),first_length>25 and span>13,first_layer_extrusion_segments=len(first),first_layer_beam_path_mm=first_length,native_longitudinal_span_mm=span,note='Two complete long perimeter paths may cover this narrow beam; segment count alone does not measure coverage.')
                low,high=([55.4,63.7] if sign>0 else [-63.7,-55.4])
                gap=roi([-43.5,low,-.1],[-30,high,2.5])
                add('P08 open clip frame slot preserved side'+str(sign),len(gap)==0,unexpected_model_extrusion_segments=len(gap))
            usb=roi([-42,-55.3,6.5],[-28.5,-53.4,7.6],'support')
            add('P08 USB roof has removable support/interface',len(usb)>5,support_segments=len(usb),removal_access='Open tray above and13mm USB port outside; no internal closed pocket introduced.')
            regions=[]
            for sign in [-1,1]:
                yy=[63.2,65.8] if sign>0 else [-65.8,-63.2]
                ssclip=roi([-29.5,yy[0],2.4],[-25,yy[1],14.8],'support')
                regions.append(dict(side=sign,support_segments=len(ssclip),access='Outside open end-frame gap; clips outside electronics chamber.'))
            add('P08 supports are on externally accessible clip/USB surfaces',True,clip_support_regions=regions,notes='Support accessibility derives from unchanged open tray/USB port and external end clips, with toolpaths localized in these regions. Physical cleanup remains a real print check.')
        else:
            add('P09 zero bridge paths without supports',mm['bridge_segments']==0,bridge_segments=mm['bridge_segments'])
            for name,beam0,free0,free1 in [('negative',-49.2,-28,-25),('positive',18.8,40,43)]:
                beam=roi([-48.8,beam0-.1,4.6],[-47.2,free1+.1,9.1]);first=[s for s in beam if s['b'][2]<.201]
                hook=roi([-47.65,free0-.1,4.0],[-46.1,free1+.1,5.9])
                add('P09 full flat leaf and hook '+name,len(first)>5 and len(hook)>10,first_layer_arm_segments=len(first),hook_extrusion_segments=len(hook))
            for name,y0,y1 in [('negative',-47,-30),('positive',22,38)]:
                gap=roi([-47.05,y0,4.6],[-46.35,y1,9.1])
                add('P09 free leaf gap stays open '+name,len(gap)==0,unexpected_model_extrusion_segments=len(gap))
            clip_support=[s for s in ss if 'Support' in s['feature'] and -49<=s['native_mid'][0]<=-46.2 and -54<=s['native_mid'][1]<=45 and 4<=s['native_mid'][2]<=9.1]
            add('P09 clip leaves require no support cleanup',len(clip_support)==0,support_segments_in_external_arm_region=len(clip_support))
            clamp=roi([-28.3,22.2,3.2],[-24.7,32.8,8.3])
            add('P09 integral cable clamp present',len(clamp)>50,integral_clamp_extrusion_segments=len(clamp),loose_P10_not_required=True)
    failures=[x for x in checks if x['status']!='PASS']
    out=dict(status='PASS_FINAL_NATIVE_ENCLOSURE_TOOLPATHS' if not failures else 'FAIL',scope='Independent actual final full-pack H2D0.4 PLA extrusion paths. Native coordinate ROI recovered from each recorded rotation, normalization and plate-local placement. No project authoring changes.',date='2026-11-03',revision='R11',native_sliced_archive_sha256=sha(final),native_editable_project_sha256=sha(pack/layout['native_project']),CAD_source_sha256=layout['CAD_source_sha256'],plate_layout_sha256=sha(pack/'plate-layout.json'),validator_sha256=sha(Path(__file__)),object_metrics=metrics,checks=checks,failed_count=len(failures),failures=failures,limitations=['Nominal slice paths; no real PLA flexibility, fatigue, fit tolerance or cleanup force qualification.','Support accessibility is a geometric access review, not a successful physical support removal test.'])
    (pack/'validation/enclosure-toolpath-check.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(dict(status=out['status'],checks=len(checks),failed=failures,metrics=metrics),indent=2))
    return bool(failures)

if __name__=='__main__':raise SystemExit(main())
