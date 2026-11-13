from pathlib import Path
import zipfile,xml.etree.ElementTree as ET
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
source=ROOT/'print/bambu-2026-10-13-RevE/Fingerworker_RevE_seed.3mf'
with zipfile.ZipFile(source) as z:data={n:z.read(n) for n in z.namelist()}
c=ET.fromstring(data['Metadata/model_settings.config'])
for o in c.findall('object'):
 n=o.find("metadata[@key='name']").get('value')
 if n.startswith('P08 -'):
  o.find("metadata[@key='support_on_build_plate_only']").set('value','0')
data['Metadata/model_settings.config']=ET.tostring(c,encoding='utf-8',xml_declaration=True)
with zipfile.ZipFile(OUT/'tray_support_candidate.3mf','w',zipfile.ZIP_DEFLATED) as z:
 for n,b in data.items():z.writestr(n,b)
print('P08-only model surface support enabled candidate ready')
