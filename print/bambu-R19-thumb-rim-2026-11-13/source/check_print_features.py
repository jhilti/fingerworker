#!/usr/bin/env python3
"""Shared actual extrusion-path parsing and native-coordinate geometry helpers.

Retained from R16, without the obsolete standalone R15 validation entry point.
No geometry or project edits.
"""
from pathlib import Path
import argparse,hashlib,json,math,re,sys,zipfile,xml.etree.ElementTree as ET
from collections import Counter
import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
SUPPORT={'Support','Support interface','Support transition'}
NONMODEL=SUPPORT|{'Brim','Skirt','Custom'}
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def parse(data,single_object=None):
    obj=None;feature='';xyz=np.zeros(3);width=.4;height=.2;speed=0.;relative=True;eold=0.;paths=[];path_break=True
    for line in data.splitlines():
        if 'start printing object, unique label id:' in line:obj=int(line.split(':')[-1]);path_break=True
        elif line.startswith('; OBJECT_ID: ') and single_object is not None:obj=single_object;path_break=True
        elif 'stop printing object' in line:obj=None;path_break=True
        elif line.startswith('; FEATURE: '):
            feature=line[11:].strip()
            path_break=True
            if feature=='Custom':obj=None
        elif line.startswith('; LINE_WIDTH: '):width=float(line.split(':')[1])
        elif line.startswith('; LAYER_HEIGHT: '):height=float(line.split(':')[1])
        elif line.startswith('M83'):relative=True
        elif line.startswith('M82'):relative=False
        elif line.startswith('G92 '):
            v={k:float(n) for k,n in re.findall(r'([XYZE])([-+.\d]+)',line)}
            for i,k in enumerate('XYZ'):xyz[i]=v.get(k,xyz[i])
            eold=v.get('E',eold)
        elif re.match(r'^G[0123] ',line):
            v={k:float(n) for k,n in re.findall(r'([XYZEFIJ])([-+.\d]+)',line.split(';')[0])}
            nxt=np.array([v.get(k,xyz[i]) for i,k in enumerate('XYZ')]);speed=v.get('F',speed)
            de=v.get('E',0) if relative else v.get('E',eold)-eold
            if 'E' in v:eold=eold+v['E'] if relative else v['E']
            points=[xyz.copy(),nxt.copy()];length=float(np.linalg.norm(nxt[:2]-xyz[:2]));arc=None
            if line.startswith(('G2 ','G3 ')):
                center=xyz[:2]+[v.get('I',0),v.get('J',0)];radius=float(np.linalg.norm(xyz[:2]-center))
                a1=math.atan2(*(xyz[:2]-center)[::-1]);a2=math.atan2(*(nxt[:2]-center)[::-1]);ccw=line.startswith('G3 ')
                angle=((a2-a1) if ccw else (a1-a2))%(2*math.pi)
                if angle<1e-10 and np.linalg.norm(nxt[:2]-xyz[:2])<1e-7 and radius>1e-5:angle=2*math.pi
                length=radius*angle
                arc=dict(center=np.array([*center,nxt[2]]),radius=radius,sweep=angle,ccw=ccw)
                for theta in (0,math.pi/2,math.pi,3*math.pi/2):
                    d=((theta-a1) if ccw else (a1-theta))%(2*math.pi)
                    if d<=angle+1e-9:points.append(np.array([center[0]+radius*math.cos(theta),center[1]+radius*math.sin(theta),nxt[2]]))
            if de>1e-8 and length>1e-6 and ('X' in v or 'Y' in v):
                paths.append(dict(obj=obj,feature=feature,a=xyz.copy(),b=nxt.copy(),points=np.array(points),length=length,
                    width=width,height=height,speed_mm_s=speed/60,arc=arc,path_break_before=path_break))
                path_break=False
            elif de < -1e-8 or np.linalg.norm(nxt-xyz)>1e-6:path_break=True
            xyz=nxt
    return paths

def native_paths(paths,row):
    R=np.asarray(row['rotation_3x3']);offset=np.asarray(row['normalization_translation_mm'])+[*row['plate_xy_mm'],0]
    result=[]
    for s in paths:
        n=dict(s)
        for k in ('a','b'):n['native_'+k]=R.T@(s[k]-offset)
        n['native_mid']=(n['native_a']+n['native_b'])/2
        n['native_points']=(s['points']-offset)@R
        if s['arc'] is not None:n['native_arc_center']=R.T@(s['arc']['center']-offset)
        result.append(n)
    return result

def roi(paths,lo,hi):
    lo=np.asarray(lo);hi=np.asarray(hi)
    return [s for s in paths if np.all(s['native_mid']>=lo) and np.all(s['native_mid']<=hi)]

def xy_path_distance(s,point):
    """Exact line/circular-arc centerline distance in native XY (no tilt)."""
    point=np.asarray(point);a=s['native_a'][:2];c=s['native_b'][:2]
    if s['arc'] is None:
        d=c-a;u=np.clip(np.dot(point-a,d)/max(np.dot(d,d),1e-20),0,1)
        return float(np.linalg.norm(point-(a+u*d)))
    center=s['native_arc_center'][:2];arc=s['arc'];start=math.atan2(*(a-center)[::-1])
    theta=math.atan2(*(point-center)[::-1]);sweep=((theta-start) if arc['ccw'] else (start-theta))%(2*math.pi)
    if sweep<=arc['sweep']+1e-9:return abs(float(np.linalg.norm(point-center))-arc['radius'])
    return min(float(np.linalg.norm(point-a)),float(np.linalg.norm(point-c)))

def xy_line(s):
    from shapely.geometry import LineString
    if s['arc'] is None:return LineString([s['native_a'][:2],s['native_b'][:2]])
    arc=s['arc'];center=s['native_arc_center'][:2]
    start=math.atan2(*(s['native_a'][:2]-center)[::-1]);sign=1 if arc['ccw'] else -1
    angles=start+sign*np.linspace(0,arc['sweep'],max(2,math.ceil(s['length']/.05)+1))
    points=center+arc['radius']*np.column_stack([np.cos(angles),np.sin(angles)])
    return LineString(points)

def free_bridge_spans(bridges,model):
    """Bridge-tagged segments include supported anchors; measure actual air gap."""
    from shapely.ops import unary_union
    results=[]
    for z in sorted({round(s['native_b'][2],5) for s in bridges}):
        current=[s for s in bridges if abs(s['native_b'][2]-z)<1e-4]
        points=np.concatenate([s['native_points'] for s in current]);lo=points[:,:2].min(0)-.6;hi=points[:,:2].max(0)+.6
        height=max(s['height'] for s in current)
        prior=[s for s in model if abs(s['native_b'][2]-(z-height))<.002
            and np.all(s['native_points'][:,:2].max(0)>=lo) and np.all(s['native_points'][:,:2].min(0)<=hi)]
        footprint=unary_union([xy_line(s).buffer(s['width']/2,quad_segs=12) for s in prior])
        maximum=0.
        for s in current:
            unsupported=xy_line(s).difference(footprint)
            lengths=[g.length for g in unsupported.geoms] if hasattr(unsupported,'geoms') else [unsupported.length]
            maximum=max(maximum,max(lengths,default=0.))
        results.append(dict(native_top_z_mm=z,prior_layer_model_segments=len(prior),longest_actual_unbacked_centerline_mm=maximum))
    return results

if __name__=='__main__':
    raise SystemExit('Path parsing library. Run check_actual_print.py or the contact-specific validators.')
