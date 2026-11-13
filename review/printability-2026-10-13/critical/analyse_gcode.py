"""Read extrusion paths; reports labels from explicit object-start G-code markers."""
from pathlib import Path
from zipfile import ZipFile
from collections import defaultdict
import re,json,sys,math
OUT=Path(__file__).resolve().parent
def segments(text):
    pos={'X':0.,'Y':0.,'Z':0.,'E':0.};relative=True;feature=None;label=None
    result=[]
    for line in text.splitlines():
        if line.startswith('; FEATURE: '):feature=line[11:].strip()
        if '; start printing object, unique label id:' in line:label=int(line.rsplit(':',1)[1])
        if '; stop printing object, unique label id:' in line:label=None
        code=line.split(';')[0]
        if code.startswith('M83'):relative=True
        if code.startswith('M82'):relative=False
        if re.match(r'G92\s',code):
            for k,v in re.findall(r'([XYZE])(-?\d*\.?\d+)',code):pos[k]=float(v)
        if not re.match(r'G[01]\s',code):continue
        fields={k:float(v) for k,v in re.findall(r'([XYZE])(-?\d*\.?\d+)',code)}
        start=[pos['X'],pos['Y'],pos['Z']]
        move=any(k in fields for k in ['X','Y'])
        e=fields.get('E',0.) if relative else fields.get('E',pos['E'])-pos['E']
        for k in ['X','Y','Z']:
            if k in fields:pos[k]=fields[k]
        if 'E' in fields:pos['E']=pos['E']+fields['E'] if relative else fields['E']
        if move and e>0:
            end=[pos['X'],pos['Y'],pos['Z']]
            result.append(dict(label=label,feature=feature,start=start,end=end,length=math.dist(start,end),e=e))
    return result
def summary(segs):
    d=defaultdict(list)
    for s in segs:d[(s['label'],s['feature'])].append(s)
    return [dict(label=k[0],feature=k[1],segments=len(ss),total_length_mm=sum(s['length'] for s in ss),max_segment_mm=max(s['length'] for s in ss),z_min_mm=min(s['end'][2] for s in ss),z_max_mm=max(s['end'][2] for s in ss)) for k,ss in d.items() if k[1] in ['Bridge','Overhang wall','Support','Support interface']]
if __name__=='__main__':
    archive=Path(sys.argv[1])
    with ZipFile(archive) as z:
        results={n:summary(segments(z.read(n).decode())) for n in z.namelist() if n.endswith('.gcode')}
    target=OUT/(archive.stem+'-features.json');target.write_text(json.dumps(results,indent=2))
    print(json.dumps(results,indent=2))
