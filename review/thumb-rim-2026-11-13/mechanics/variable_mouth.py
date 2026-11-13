from pathlib import Path
import sys,re,hashlib,json
sys.path.insert(0,str(Path(__file__).parent));import thumb_rim as m

def source():
 s=m.BASE_SOURCE.read_text();start=s.index('        opFillet(context,id + "R17ThumbSideMouthRound"');end=s.index('        // R18:',start)
 old=s[start:end];q=old.split('"entities":',1)[1].split(',"radius":',1)[0]
 patch='''        // R19: smoothly varying mouth radii retain the thin lower lip.
        const R19RawMouthEdges='''+q+''';
        println({"R19RawMouthEdgeCount":size(evaluateQuery(context,R19RawMouthEdges))});
        var R19VertexSettings=[];
        for (var vertex in evaluateQuery(context,qAdjacent(R19RawMouthEdges,AdjacencyType.VERTEX,EntityType.VERTEX)))
        {
            const p=evVertexPoint(context,{"vertex":vertex});
            var r=0.4*mm;
            if (p[0] < -27.5*mm && p[2] > 27.9*mm) r=1*mm;
            if (p[2] > 32*mm) r=2*mm;
            R19VertexSettings=append(R19VertexSettings,{"vertex":vertex,"vertexRadius":r});
        }
        opFillet(context,id + "R17ThumbSideMouthRound",{
            "entities":R19RawMouthEdges,"radius":0.4*mm,"tangentPropagation":true,
            "isVariable":true,"smoothTransition":true,"vertexSettings":R19VertexSettings,
            "pointOnEdgeSettings":[
                {"edge":qContainsPoint(qOwnedByBody(body(id + "base"),EntityType.EDGE),vector(-28.4530059123,-61.727067455,24.75)*mm),"edgeParameter":0.5,"pointOnEdgeRadius":1*mm},
                {"edge":qContainsPoint(qOwnedByBody(body(id + "base"),EntityType.EDGE),vector(-28.4530059123,61.727067455,24.75)*mm),"edgeParameter":0.5,"pointOnEdgeRadius":1*mm}] });
'''
 s=s[:start]+patch+s[end:];s=s.replace('Flat132 R18 - organic palm bolster and side thumb seats','Flat132 R19 - softly rounded thumb mouths and organic palm')
 return s
if __name__=='__main__':
 p=m.STUDY/'fingerworker_R19_variable_trial.fs';p.write_text(source());Path('/tmp/r19-variable-source-info').write_text(str(p.resolve())+'\n'+m.sha(p))
