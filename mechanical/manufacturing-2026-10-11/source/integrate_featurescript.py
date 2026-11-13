"""Integrate generated enclosure and P02 mounting pilot into main FeatureScript.
Idempotent; leaves electronics routing/order files unchanged.
"""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
p=ROOT/'fingerworker_mvp.fs';s=p.read_text()
generated=(Path(__file__).parent/'enclosure_generated.fs').read_text()
begin='// BEGIN GENERATED ENCLOSURE REV A\n';end='// END GENERATED ENCLOSURE REV A\n'
if begin in s:
    a=s.index(begin);b=s.index(end,a)+len(end);s=s[:a]+begin+generated+end+s[b:]
else:
    a=s.index('// Packaging study only:');s=s[:a]+begin+generated+end+'\n'+s[a:]
a=s.index('    makeBox(context,id + "elecCase"',s.index('function makeElectronicsStudy')) if '    makeBox(context,id + "elecCase"' in s else -1
if a>=0:
    b=s.index('    makeBox(context,id + "elecCarrier"',a)
    s=s[:a]+'    const enclosure=makeElectronicsEnclosure(context,id);\n'+s[b:]
s=s.replace('    const housing=body(id + "elecCase");','    const housing=enclosure;')
s=s.replace('    const electronics=qUnion([housing,components,usb]);\n    opTransform(context,id + "electronicsClearanceShift",{"bodies":electronics,"transform":transform(vector(-1.25,0,0)*mm)});','    opTransform(context,id + "electronicsClearanceShift",{"bodies":qUnion([components,usb]),"transform":transform(vector(-1.25,0,0)*mm)});\n    const electronics=qUnion([housing,components,usb]);')
s=s.replace('auditSolidPair(context,"Electronics housing / mechanism",housing,mechanism,false)','auditSolidPair(context,"Electronics housing / mechanism",housing,mechanism,true)')
s=s.replace('auditSolidPair(context,"Electronics components / housing",components,housing,false)','auditSolidPair(context,"Electronics components / housing",components,housing,true)')
s=s.replace('Show electronics packaging study (not manufacturing)','Show electronics enclosure and component references')
s=s.replace('// Packaging study only: nominal board/cell outlines plus reserved component\n// heights. No mounting, routed PCB, thermal or RF performance is implied.','// Printable Rev A enclosure plus nominal PCB/cell/plug envelopes.\n// Physical fitting, thermal and RF qualification remain hardware checks.')
marker='        // Electronics enclosure M2 insert pilots in underside of fixed palm.'
if marker not in s:
    a=s.index('        var insertTools=[];')
    code='''        // Electronics enclosure M2 insert pilots in underside of fixed palm.
        // Blind depth 4 mm; 1 mm remains to the flat plate top.
        for (var y in [-59,59])
        {
            const suffix=y < 0 ? "0" : "1";
            makeCylinder(context,id + ("enclosurePalmPilot"~suffix),
                vector(-26.5,y,9.4)*mm,vector(-26.5,y,13.5)*mm,1.6*mm);
            cut(context,id + ("enclosurePalmPilotCut"~suffix),
                body(id + "palmPad"),body(id + ("enclosurePalmPilot"~suffix)));
        }
'''
    s=s[:a]+code+s[a:]
p.write_text(s)
print('Integrated printable enclosure and P02 mounting pilots')
