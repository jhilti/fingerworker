#!/usr/bin/env python3
"""Publish current local pointers only after native CAD and print checks pass."""
from pathlib import Path
from hashlib import sha256
import json,re,zipfile
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
PACK=ROOT/'print/bambu-R11-PLA-click-2026-11-03'
def sha(p):return sha256(p.read_bytes()).hexdigest()
binding=json.loads((HERE/'onshape-binding.json').read_text())
source=HERE/'fingerworker_flat132_PLA_click.fs'
assert sha(source)==binding['source_sha256']=='c8ec18f08149553001ccf8173f35fe57eee6a16be0294be2d7f88577f658cf5e'
checks=[HERE/'validation/native-geometry.json',HERE/'enclosure/local-enclosure-preflight.json',
        HERE/'enclosure/motion-preflight.json',HERE/'rear-shoes-geometry-preflight.json']
checks += [PACK/'validation'/n for n in ['native-project-check.json','toolpath-check.json',
    'independent-native-review.json','enclosure-toolpath-check.json','p04-surface-check.json','rear-shoe-toolpath-check.json']]
reports={}
for p in checks:
    j=json.loads(p.read_text());assert j['status'].startswith(('PASS','NATIVE_PROJECT')),p
    assert j.get('failed_checks',j.get('failed_count',0))==0,p
    reports[str(p.relative_to(ROOT))]=dict(status=j['status'],sha256=sha(p))
layout=json.loads((PACK/'plate-layout.json').read_text())
qa=json.loads((PACK/'validation/native-project-check.json').read_text())
project=PACK/layout['native_project'];archive=PACK/'Fingerworker_R11_H2D_04mm_PLA_Fit_Test_Package.zip'
assert sha(project)==qa['native_sha256'] and layout['CAD_source_sha256']==sha(source)
assert layout['native_R11_version']==binding['onshape_version']
assert qa['plate_count']==3 and qa['object_count']==13
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    hashes=json.loads(z.read('SHA256.json'))['files']
    for n,h in hashes.items():assert sha256(z.read(n)).hexdigest()==h

(ROOT/'fingerworker_mvp.fs').write_bytes(source.read_bytes())
for name in ['README.md','PRINTING.md','EINKAUFSTEILE.md','ELECTRONICS_PACKAGING.md','CAD_REVIEW.md','print/REVISION_STATUS.md']:
    p=ROOT/name;text=p.read_text();prefix='../' if p.parent.name=='print' else ''
    for revision in ['R10','R11']:
        text=re.sub(r'<!-- CURRENT_FLAT132_'+revision+r'_START -->.*?<!-- CURRENT_FLAT132_'+revision+r'_END -->\s*','',text,flags=re.S)
    cad=prefix+'review/flat132-click-assembly-2026-11-03/';pack=prefix+'print/bambu-R11-PLA-click-2026-11-03/'
    block=f'''<!-- CURRENT_FLAT132_R11_START -->
> **03.11.2026 – aktueller Flat132 R11, PLA als Standard:** Elektronikwanne P08 klickt an den vorhandenen R10-Rahmen; P09 klickt an P08. P10 und vier P07 entfallen durch Integration in Deckel und Führungsschuhe. **P01 bleibt geometrisch unverändert – vorhandenen R10-Druck weiterverwenden.** P04 bleibt geometrisch gleich und wird für saubere Fingerflächen mit vorderer Stirnseite unten und schlanken Baumstützen nur vom Bett gedruckt. P06, verstellbare P12-Schuhe und P11 behalten ihre Funktionsschrauben. [CAD/Review]({cad}README.md) · [Verbindungsmatrix]({cad}ASSEMBLY_JOINT_REVIEW.md) · [Montage]({cad}MONTAGE.md) · [Stücklistenänderungen]({cad}BOM_Aenderungen.csv) · [Onshape R11]({binding['onshape_url']}).
>
> [Bambu H2D / 0,4 mm / PLA – 3MF]({pack}Fingerworker_R11_H2D_04mm_PLA_Fit_Test.3mf) · [Druckpaket ZIP]({pack}Fingerworker_R11_H2D_04mm_PLA_Fit_Test_Package.zip). **13 Druckstücke auf drei Platten:** Rahmen / elf Montage- und Passstücke / Fingergriff. Keine Schrauben oder Muttern drucken. Fünf kleine Druckteile weniger als R10; ein PLA-Filament genügt. Alle drei Platten sind gesliced und geprüft. Federfreier Passsatz mit Stangen-Formhilfen und Q01; reale Passung und Festigkeit sind noch am Muster zu prüfen. Die folgenden älteren Revisionsangaben bleiben historische Stände.
<!-- CURRENT_FLAT132_R11_END -->

'''
    p.write_text(block+text)
summary=dict(revision='Flat132 R11 PLA click assembly',date='2026-11-03',status='PASS_NOMINAL_CAD_AND_PLA_PRINT',
    source_sha256=sha(source),onshape_version=binding['onshape_version'],onshape_url=binding['onshape_url'],
    native_solids=117,device_bodies=64,electronics_reference_bodies=53,printed_device_bodies=10,fit_test_pieces=13,plates=3,
    changed=['P08','P09','P120','P121'],removed=['P10','P070a','P070b','P071a','P071b'],unchanged_exact_native_breps=113,
    PLA_standard=True,second_material_required=False,P01_reprint_required=False,P04_reprint_for_surface=True,
    inherited_functional_service='R10 sensor, preload and H15/H16/H18 service routes unchanged; see R10 reports bound through exact113-body identity.',
    estimates=qa['estimates'],verification=reports,
    files_sha256={str(p.relative_to(ROOT)):sha(p) for p in [source,project,archive,HERE/'native/Flat132_R11_final_AP214.step',HERE/'native/Flat132_R11_neutral_final.zip']},
    limitations='Nominal CAD and calculated toolpaths only. Actual PLA tolerances, latch force, support removal, cycling, creep, comfort, sensor calibration and load performance need physical validation. Guide caps, return-shoe retainers, cam and loaded hardware retain screws; no all-screwless or load-rating claim.')
(HERE/'final-specification.json').write_text(json.dumps(summary,indent=2)+'\n')
readme=(HERE/'README.md').read_text().split('<!-- FINAL_NATIVE -->')[0].rstrip()
readme+=f'''

<!-- FINAL_NATIVE -->
## Finaler nativer Stand

[Onshape R11]({binding['onshape_url']}) · Quellhash `{sha(source)}`.

Die finale Regeneration enthält117 gültige Körper. Vier geänderte BReps stimmen exakt mit der unabhängigen CSG überein;113 übrige BReps einschließlich P01 und P04 sind exakt unverändert. [Natives CAD-Protokoll](validation/native-geometry.json). Die neuen Gehäusestocks sind über den vollständigen korrelierten Bewegungsbereich geprüft:882 konservative Prüfungen ohne Konflikt. [Bewegungsnachweis](enclosure/motion-preflight.json). Die Montage-/Entriegelprüfung des Gehäuses enthält307 Prüfungen. [Montagenachweis](enclosure/local-enclosure-preflight.json).

Das finale native Bambu-Projekt wurde unabhängig gegen alle13 Quellmeshes zurückgeprüft und auf drei Platten erfolgreich gesliced. [Prüfberichte und Slicerzeiten](../../print/bambu-R11-PLA-click-2026-11-03/PRINT_QA_NOTES.md). Die berechneten Kontaktregionen von P04 bleiben ohne Stützen; reale Oberfläche, Clips und Stützentfernung sind am Druck zu bestätigen.
'''
readme=readme.replace('enthält117','enthält 117').replace(';113','; 113').replace('geprüft:882','geprüft: 882').replace('enthält307','enthält 307').replace('alle13','alle 13')
(HERE/'README.md').write_text(readme)
print(json.dumps(dict(status=summary['status'],source_sha256=sha(source),onshape_version=binding['onshape_version'],bound_reports=len(reports),zip_sha256=sha(archive)),indent=2))
