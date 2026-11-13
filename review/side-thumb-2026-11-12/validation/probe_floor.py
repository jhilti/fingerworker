#!/usr/bin/env python3
"""Exact section evidence for the R17 floor; no geometry/source mutations."""
from pathlib import Path
import importlib.util,json,math
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from OCP.TopAbs import TopAbs_EDGE
from OCP.TopExp import TopExp_Explorer
from OCP.gp import gp_Pnt
HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('audit',HERE/'audit_thumb_integration.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a)

def sections(frame):
    rows=[]
    for sign in [-1,1]:
        for x in [-23.9,-23.5,-23,-22.5,-22,-21,-20,-19,-18,-17]:
            for y in [63,63.5,64,64.5,64.9,64.99]:
                # The central R12 disk is conservatively inside the planar
                # Z20 floor for either contemplated R1.5 or R2 bottom blend.
                if math.hypot(x+24,y-75)>=12:continue
                line=BRepBuilderAPI_MakeEdge(gp_Pnt(x,sign*y,0),gp_Pnt(x,sign*y,35)).Edge()
                cut=a.b.common(frame,line);ex=TopExp_Explorer(cut,TopAbs_EDGE);intervals=[]
                while ex.More():
                    bb=a.b.bounds(ex.Current());intervals.append([float(bb[0,2]),float(bb[1,2])]);ex.Next()
                intervals.sort()
                if not intervals:continue # rounded outside end beyond the actual solid
                # Mouth blends can propagate around the continuous outer
                # contour and lower the floor's rounded free edge slightly.
                low=[z for z in intervals if 16.5<z[1]<23.5]
                if low:
                    z0,z1=low[0];rows.append(dict(x_mm=x,y_mm=sign*y,material_z_mm=[z0,z1],floor_thickness_mm=z1-z0))
    return rows

def main():
    old,_,_=a.baseline();c=a.module('candidate_floor',a.STUDY/'mechanics/side_thumb.py');frame=c.expected(old)['P01']
    rows=sections(frame)
    result=dict(status='MEASURED_LOCAL_FLOOR_SECTIONS',source_sha256=a.sha(a.SOURCE),generator_sha256=a.sha(a.STUDY/'mechanics/side_thumb.py'),minimum_sampled_floor_thickness_mm=min(q['floor_thickness_mm'] for q in rows),checks=rows,scope='Exact vertical line/solid sections at declared XY samples in the Z20 floor region, including its rounded free edge. Not a global minimum-thickness or strength qualification.')
    (HERE/'local-floor-sections.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='checks'},indent=2))
if __name__=='__main__':main()
