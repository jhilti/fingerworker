#!/usr/bin/env python3
"""Bind the completed R10 evidence and update the project's current pointers."""
from pathlib import Path
from hashlib import sha256
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PRINT = ROOT / 'print/bambu-R10-integrated-palm-2026-11-03'
SOURCE_SHA = '5ce830ff2b06cd8d318d3c44dbc1f3385697526a9a679d2a2078f64f81854237'
VERSION = '1d91807cca19866934a439eb'
URL = f'https://cad.onshape.com/documents/15316cc6370631845af136b2/v/{VERSION}/e/d253eb87b70818ebde8215f0'


def digest(p):
    return sha256(p.read_bytes()).hexdigest()


source = HERE / 'fingerworker_flat132_integrated_palm.fs'
assert digest(source) == SOURCE_SHA
reports = {}
paths = [HERE / 'validation' / n for n in (
    'native-geometry.json', 'service-native.json', 'motion-native.json',
    'independent-print-qa.json')]
paths += [PRINT / 'validation' / n for n in (
    'native-project-check.json', 'toolpath-check.json')]
for p in paths:
    j = json.loads(p.read_text())
    assert j['status'].startswith(('PASS', 'NATIVE_PROJECT')), (p, j['status'])
    assert j.get('source_sha256', j.get('CAD_source_sha256')) == SOURCE_SHA, p
    for k in ('failed_count', 'failed_checks', 'failures_count'):
        if k in j:
            assert j[k] == 0, (p, k)
    reports[str(p.relative_to(ROOT))] = {'sha256': digest(p), 'status': j['status']}

native = json.loads((PRINT / 'validation/native-project-check.json').read_text())
assert native['native_R10_version'] == VERSION
assert native['plate_count'] == 2 and native['object_count'] == 18
project = PRINT / native['native_project']
assert digest(project) == native['native_sha256']

# Preserve the previous root source once, then make the shared entry point current.
root_source = ROOT / 'fingerworker_mvp.fs'
backup = HERE / 'reference/root-before-R10/fingerworker_mvp.fs'
if root_source.read_bytes() != source.read_bytes():
    backup.parent.mkdir(parents=True, exist_ok=True)
    if not backup.exists():
        backup.write_bytes(root_source.read_bytes())
    root_source.write_bytes(source.read_bytes())

for name in ('README.md', 'PRINTING.md', 'EINKAUFSTEILE.md',
             'ELECTRONICS_PACKAGING.md', 'print/REVISION_STATUS.md', 'CAD_REVIEW.md'):
    p = ROOT / name
    prefix = '../' if p.parent.name == 'print' else ''
    cad = prefix + 'review/flat132-integrated-palm-2026-11-03/'
    pack = prefix + 'print/bambu-R10-integrated-palm-2026-11-03/'
    block = f'''<!-- CURRENT_FLAT132_R10_START -->
> **03.11.2026 – aktueller Flat132 R10:** Grundrahmen und massive Handballenauflage sind **ein durchgängiges Druckteil P01**. Separate P02, Sleeve, zwei Palm-M4-Schrauben und zwei Palm-Inserts entfallen. Die Handkontaktkurve und die 6-mm-Grundplatte bleiben erhalten. Sensor- und Elektronikservice sind für die feste Auflage überarbeitet: seitliche H18-Zugänge, sensorseitige H16-Köpfe und revidierte H15-Platte ohne alte Senkungen. [CAD und Nachweise]({cad}README.md) · [Montage]({cad}MONTAGE.md) · [Stücklistenänderungen]({cad}BOM_Aenderungen.csv) · [Onshape R10]({URL}).
>
> [Bambu H2D / 0,4 mm / PLA – 3MF]({pack}Fingerworker_R10_H2D_04mm_PLA_Fit_Test.3mf) · [Druckpaket ZIP]({pack}Fingerworker_R10_H2D_04mm_PLA_Fit_Test_Package.zip). **Für vorhandene R9-Restteile nur Platte 1 neu drucken**; Platte 2 enthält die übrigen 17 Stücke. Der komplette federfreie Passsatz enthält 18 Stücke auf zwei Platten, einschließlich harter Puffer-/Stangen-Dummies und Q01. Keine Schrauben oder Muttern drucken. Reale Passung und Festigkeit sind am Muster zu prüfen; keine Lastfreigabe. Die folgenden älteren Revisionsangaben bleiben historische Stände.
<!-- CURRENT_FLAT132_R10_END -->

'''
    text = p.read_text()
    if '<!-- CURRENT_FLAT132_R10_START -->' in text:
        start = text.index('<!-- CURRENT_FLAT132_R10_START -->')
        end = text.index('<!-- CURRENT_FLAT132_R10_END -->', start)
        text = text[:start] + text[end + len('<!-- CURRENT_FLAT132_R10_END -->'):].lstrip('\n')
    p.write_text(block + text)

files = [source, HERE / 'native/Flat132_R10_neutral_final.zip',
         HERE / 'native/Flat132_R10_final_AP214.step',
         HERE / 'mechanical-mm/H15.step',
         HERE / 'MONTAGE.md', HERE / 'BOM_Aenderungen.csv', project,
         PRINT / 'Fingerworker_R10_H2D_04mm_PLA_Fit_Test_Package.zip']
assert all(p.is_file() for p in files)
summary = {
    'revision': 'Flat132 R10 integrated palm and service access',
    'date': '2026-11-03', 'status': 'PASS_NOMINAL_CAD_SERVICE_AND_PRINT_PROJECT',
    'source_sha256': SOURCE_SHA, 'onshape_version': VERSION, 'onshape_url': URL,
    'native_solids': 122, 'device_bodies': 69, 'electronics_reference_bodies': 53,
    'printed_device_bodies': 15, 'fit_test_pieces': 18, 'plates': 2,
    'integrated_main_part_mm': [175.1, 132, 35], 'nominal_base_mm': 6,
    'removed': ['Separate P02', 'Palm sleeve', '2 palm M4x10 bolts', '2 palm M4 inserts'],
    'compatibility': 'Other R9 printed parts retained; H15 plain-hole steel plate and reversed H16/H17 required for functional assembly.',
    'verification': reports,
    'files_sha256': {str(p.relative_to(ROOT)): digest(p) for p in files},
    'limitations': 'Nominal geometry/toolpaths only. Actual printed fits, support removal, strength, creep, fatigue, comfort and sensor calibration unqualified. Fit fixture/printed rods/pad proxies only for spring-free assessment.'
}
(HERE / 'final-specification.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False) + '\n')
print(json.dumps({'status': summary['status'], 'source_sha256': SOURCE_SHA,
                  'onshape_version': VERSION, 'bound_reports': len(reports)}, indent=2))
