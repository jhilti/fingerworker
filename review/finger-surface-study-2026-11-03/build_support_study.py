from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import xml.etree.ElementTree as ET,json
OUT=Path(__file__).resolve().parent
cases=[('front_tree_bed',{'support_type':'tree(auto)','support_on_build_plate_only':'1','support_style':'tree_slim'}),('front_normal_bed',{'support_type':'normal(auto)','support_on_build_plate_only':'1'}),('front_tree_any',{'support_type':'tree(auto)','support_on_build_plate_only':'0','support_style':'tree_slim'})]
for name,opts in cases:
 with ZipFile(OUT/'P04_front_down_H2D_04mm_PLA_seed.3mf') as z:files={n:z.read(n) for n in z.namelist()}
 cfg=ET.fromstring(files['Metadata/model_settings.config']);obj=cfg.find('object')
 for key,val in opts.items():
  elem=obj.find(f"metadata[@key='{key}']")
  if elem is None:elem=ET.SubElement(obj,'metadata',{'key':key})
  elem.set('value',val)
 files['Metadata/model_settings.config']=ET.tostring(cfg,encoding='utf-8',xml_declaration=True)
 folder=OUT/name;folder.mkdir(exist_ok=True)
 with ZipFile(folder/'seed.3mf','w',ZIP_DEFLATED) as z:
  for n,b in files.items():z.writestr(n,b)
print('3 support studies authored')
