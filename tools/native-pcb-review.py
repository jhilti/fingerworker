"""Read-only geometry evidence; run with KiCad bundled Python 3.9."""
from pathlib import Path
import sys, json, hashlib, math, collections
import pcbnew as p

path = Path(sys.argv[1]).resolve()
before = hashlib.sha256(path.read_bytes()).hexdigest()
b = p.LoadBoard(str(path))
mm = p.ToMM
def xy(v): return [mm(v.x), mm(v.y)]
def distance(a, c): return math.hypot(mm(a.x-c.x), mm(a.y-c.y))
tracks = [t for t in b.GetTracks() if not isinstance(t, p.PCB_VIA)]
vias = [t for t in b.GetTracks() if isinstance(t, p.PCB_VIA)]
by_net = collections.defaultdict(list)
for t in tracks: by_net[t.GetNetname()].append(t)
fps = {f.GetReference():f for f in b.GetFootprints()}
pads = {(ref,pad.GetNumber()):pad for ref,f in fps.items() for pad in f.Pads()}
bbox = b.GetBoardEdgesBoundingBox()
edges = [x for x in b.GetDrawings() if x.GetLayer()==p.Edge_Cuts]
points = [v for x in edges for v in (x.GetStart(),x.GetEnd())]
outline = [mm(max(v.x for v in points)-min(v.x for v in points)),
           mm(max(v.y for v in points)-min(v.y for v in points))] if points and all(x.GetShape()==p.S_SEGMENT for x in edges) else None
result = {'pcb_path':str(path), 'sha256':before, 'kicad_version':p.GetBuildVersion(),
 'outline_centerline_dimensions_mm':outline,
 'edge_stroke_bounding_box_dimensions_mm':[mm(bbox.GetWidth()),mm(bbox.GetHeight())],
 'thickness_mm':mm(b.GetDesignSettings().GetBoardThickness()),
 'footprint_count':len(fps),'track_count':len(tracks),'via_count':len(vias),
 'tracks_by_layer':dict(collections.Counter(b.GetLayerName(t.GetLayer()) for t in tracks)),
 'nets':{n:{'total_segment_length_mm':sum(mm(t.GetLength()) for t in ts), 'segments':len(ts),
 'min_width_mm':min(mm(t.GetWidth()) for t in ts),'max_width_mm':max(mm(t.GetWidth()) for t in ts),
 'layers':sorted({b.GetLayerName(t.GetLayer()) for t in ts}),'vias':sum(v.GetNetname()==n for v in vias)} for n,ts in sorted(by_net.items())},
 'footprints':{ref:{'value':f.GetValue(),'position_mm':xy(f.GetPosition()),'rotation_degrees':f.GetOrientationDegrees(),
 'pads':{pad.GetNumber():{'net':pad.GetNetname(),'position_mm':xy(pad.GetPosition()),'size_mm':xy(pad.GetSize())} for pad in f.Pads()}} for ref,f in sorted(fps.items())},
 'zones':[], 'decoupling_pad_center_distances_mm':{},'gnd_pad_nearest_via_mm':{},'via_in_pad':[]}
for z in b.Zones():
 result['zones'].append({'name':z.GetZoneName(),'net':z.GetNetname(),'rule_area':z.GetIsRuleArea(),
 'layers':[b.GetLayerName(l) for l in z.GetLayerSet().CuStack()],
 'filled_islands':0 if z.GetIsRuleArea() else z.GetFilledPolysList(z.GetLayer()).OutlineCount()})
for a,c in [(('U4','12'),('C12','1')),(('U4','13'),('C14','1')),(('U4','12'),('C13','1')),
            (('U3','5'),('C7','1')),(('U3','1'),('C6','1')),(('U2','5'),('C3','1'))]:
 result['decoupling_pad_center_distances_mm']['.'.join(a)+' to '+'.'.join(c)] = distance(pads[a].GetPosition(),pads[c].GetPosition())
for (ref,num),pad in pads.items():
 if ref in ['U2','U3','U4','C3','C4','C7','C12','C14'] and pad.GetNetname()=='GND':
  gv=[v for v in vias if v.GetNetname()=='GND']
  result['gnd_pad_nearest_via_mm'][ref+'.'+num]=min(distance(pad.GetPosition(),v.GetPosition()) for v in gv)
 for v in vias:
  if pad.GetNumber() and pad.IsOnLayer(p.F_Cu) and pad.HitTest(v.GetPosition()):
   result['via_in_pad'].append({'ref':ref,'pad':num,'net':v.GetNetname(),'position_mm':xy(v.GetPosition())})
assert before==hashlib.sha256(path.read_bytes()).hexdigest(),'Input changed during review'
print(json.dumps(result,indent=2))
