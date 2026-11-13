#!/usr/bin/env python3
"""Package the GUI-saved connected variant without changing generic release artifacts."""
from pathlib import Path
import argparse,hashlib,json,re,shutil,zipfile
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
PACK=ROOT/'print/bambu-R15-inboard-straps-2026-11-08'
BASE='Fingerworker_R15_H2D_04mm_PLA_Basic_Print_Ready';OUT=PACK/'connected-ready-package'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--audit',required=True);args=ap.parse_args()
 gui_path=PACK/'validation/connected-gui-check.json';gui=read(gui_path)
 project=PACK/(BASE+'.3mf');sliced=PACK/'validation'/(BASE+'_verification.gcode.3mf');audit_path=PACK/'validation'/args.audit;audit=read(audit_path)
 assert gui['status']=='PASS_CONNECTED_GUI_PRINT_READY' and not gui['printer_job_started']
 assert gui['connected_project_sha256']==sha(project) and gui['connected_sliced_archive_sha256']==sha(sliced)
 assert gui['baseline_project_sha256']==sha(PACK/'Fingerworker_R15_H2D_04mm_PLA_Inboard_Straps.3mf')
 assert gui['used_material']=='Bambu PLA Basic' and gui['used_nozzle']=='Left' and gui['mapped_AMS_slot']=='A3' and not gui['PETG_used']
 assert str(audit['status']).startswith('PASS') and not audit.get('failures') and not audit.get('failed') and not audit.get('failed_checks',audit.get('failed_count',0))
 # Exact connected project and slice hashes must be present in the completed audit.
 encoded=json.dumps(audit);assert sha(project) in encoded and sha(sliced) in encoded
 generic=read(PACK/'delivery-specification.json')
 for name,h in generic['files_sha256'].items():assert sha(ROOT/name)==h,name
 version=read(HERE/'onshape-version.json');assert version['source_sha256']==generic['CAD_source_sha256']
 OUT.mkdir(exist_ok=True)
 copied=[]
 def copy(src,rel):
  dst=OUT/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst);copied.append(dst)
 copy(project,project.name)
 for ref in ['P01','P04','P05','P06','P11','Q01']:copy(PACK/'STL-print-oriented'/(ref+'.stl'),'STL-print-oriented/'+ref+'.stl')
 for name in ['MONTAGE.md','Druckliste.csv','Druckliste.json','BOM_Aenderungen.csv']:copy(PACK/name,name)
 for name in ['strap-routing.svg','strap-routing-preview.png','strap-routing-provenance.json']:copy(PACK/'preview'/name,'preview/'+name)
 for name in ['native-geometry.json','native-motion.json','service-native.json','fixture-q01-check.json','independent-strap-native.json']:
  copy(PACK/'validation'/('cad-R15-'+name),'validation/cad-R15-'+name)
 copy(gui_path,'validation/connected-gui-check.json');copy(audit_path,'validation/'+audit_path.name)
 geometry=PACK/'validation/connected-geometry-settings-check.json';g=read(geometry)
 assert g['status']=='PASS_CONNECTED_GEOMETRY_AND_SETTINGS' and not g['failures']
 assert g['connected_project_sha256']==sha(project) and g['connected_sliced_archive_sha256']==sha(sliced)
 copy(geometry,'validation/connected-geometry-settings-check.json')
 for name in ['connected-p04-support-check.json','connected-actual-path-check.json','connected-flow-check.json']:
  p=PACK/'validation'/name;d=read(p)
  assert str(d['status']).startswith('PASS') and not d.get('failures') and not d.get('issues') and not d.get('failed_checks',d.get('failed_count',0)),name
  assert sha(sliced) in json.dumps(d),name
  copy(p,'validation/'+name)
 copy(HERE/'fingerworker_R15_inboard_straps.fs','source/fingerworker_R15_inboard_straps.fs')
 copy(HERE/'mechanics/design-specification.json','source/design-specification.json')
 copy(HERE/'onshape-version.json','source/onshape-version.json')
 text=f'''# Fingerworker R15 – am H2D vorbereitete PLA-Basic-Druckplatte

`{project.name}` als **Projekt** in Bambu Studio öffnen. Es enthält **sechs Druckstücke auf einer Platte**: P01/P04/P05/P06/P11 und die federfreie Passhilfe Q01. Die sechs Dateien in `STL-print-oriented` sind dieselben Teile als einzelne STLs; nicht zusätzlich zum Projekt drucken. Vorhandene echte Führungsstangen verwenden. Elektronikgehäuse, gedruckte Stangen, Schrauben und Muttern gehören nicht zu diesem Auftrag.

Diese Variante wurde in der verbundenen Bambu-Studio-Sitzung vorbereitet und gesliced. Anzeige: **{gui['displayed_estimate']} / {gui['displayed_filament_g']:.2f} g PLA**. Drucker **{gui['printer']}**, H2D mit **linker 0,4-mm-Standarddüse**, strukturierte PEI-Platte. Projektfilament 1 **Bambu PLA Basic** war **AMS A3** zugeordnet; die rechte Düse ist unbenutzt. Teile und Stützen verwenden PLA; **kein PETG und keine Materialwechsel**. Beim erneuten Öffnen die tatsächliche AMS-Zuordnung prüfen, da sie vom verbundenen Drucker abhängt.

Alle sechs Modelle sind **ohne Brim** eingestellt. Erforderliche Stützen und die vier lokalen dichten Bereiche um die Gurtschlitze bleiben erhalten. Beim kleinen P11 die erste Schicht kurz auf Haftung beobachten. Im geprüften Sendedialog standen Bettnivellierung und Flusskalibrierung auf Auto; der Senden-Knopf war aktiv. **Kein Druckauftrag wurde gestartet.**

Vier innenliegende 27 × 4-mm-Schlitze für zwei 25-mm-Gurte ersetzen die äußeren R14-Laschen auf beiden Seiten. Die griffnahe Handballenauflage bleibt erhalten. Gegenüber R14 ist nur P01 neu; die anderen Teile können weiterverwendet werden. Gurtführung, federfreie Passmontage und Sicherung unter Federlast stehen in der [Montage](MONTAGE.md). Q01 nur federfrei verwenden und vor Sensor-/Federeinbau entfernen.

[Verbundenes Projekt und tatsächlicher Slice](validation/{audit_path.name}) · [Bambu-Studio-Beobachtung](validation/connected-gui-check.json) · [Onshape R15]({version['url']})

Die frühere Generic-PLA-Variante bleibt separat erhalten. Ihr CLI-Wert **10 h 59 min 19 s / 230,01 g** gehört zu ihrem eigenen Materialprofil und ist keine Schätzung dieses PLA-Basic-Projekts. Die vorliegende Prüfung bindet das gespeicherte Projekt an dessen tatsächlichen GUI-Slice. Reale Haftung, Passung, Oberfläche, Rastkraft und Belastbarkeit sind am Ausdruck zu bestätigen. Interne Prüfgcodes werden nicht ausgeliefert.
'''
 (OUT/'README.md').write_text(text);copied.append(OUT/'README.md')
 for p in [p for p in copied if p.suffix=='.md']:
  for link in re.findall(r'\]\(([^)]+)\)',p.read_text()):
   if '://' not in link and not link.startswith('#'):assert (p.parent/link.split('#')[0]).is_file(),(p,link)
 hashes={str(p.relative_to(OUT)):sha(p) for p in copied};manifest={'status':'CONNECTED_READY_DELIVERY_HASH_MANIFEST','files':hashes,'source_sha256':version['source_sha256'],'onshape_version':version['version_id'],'print_started':False}
 (OUT/'SHA256.json').write_text(json.dumps(manifest,indent=2)+'\n');copied.append(OUT/'SHA256.json')
 target=PACK/(BASE+'_Package.zip')
 with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
  for p in sorted(copied):z.write(p,p.relative_to(OUT))
 with zipfile.ZipFile(target) as z:
  assert z.testzip() is None and all(hashlib.sha256(z.read(n)).hexdigest()==h for n,h in hashes.items())
  assert sum(n.endswith('.3mf') for n in z.namelist())==1 and sum(n.endswith('.stl') for n in z.namelist())==6
  assert not any(n.endswith(('.gcode','.gcode.3mf')) for n in z.namelist())
 report=dict(status='PASS_CONNECTED_READY_DELIVERY',project=str(project.relative_to(ROOT)),package=str(target.relative_to(ROOT)),source_sha256=version['source_sha256'],onshape_version=version['version_id'],project_sha256=sha(project),package_sha256=sha(target),sliced_archive_sha256=sha(sliced),gui_sha256=sha(gui_path),audit_path=str(audit_path.relative_to(ROOT)),audit_sha256=sha(audit_path),displayed_estimate=gui['displayed_estimate'],displayed_filament_g=gui['displayed_filament_g'],printer_job_started=False,physical_objects=6,plates=1,files_sha256={str(p.relative_to(ROOT)):sha(p) for p in [project,target,OUT/'SHA256.json',gui_path,audit_path,OUT/'README.md']})
 (PACK/'connected-ready-delivery.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
