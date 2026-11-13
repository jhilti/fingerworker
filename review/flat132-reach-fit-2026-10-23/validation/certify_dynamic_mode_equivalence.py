#!/usr/bin/env python3
"""Exact narrow ISO81 delta proof; dynamic native exports retain their ISO86 origin."""
import hashlib,json
from pathlib import Path
import validate_finished as v
PRIOR='61885fd717b30eaf1dfc39a1f7f65f017bfc1b4ac077c3e3493399ef3373a9a3'
FINAL='d7f476fa34e862e2b0e1b5a5e91fff0f852b9308a589fafd11ce59e01269915a'
def proof():
 root=v.HERE.parent;metadata=json.loads((root/'source-build.json').read_text());source=root/'fingerworker_flat132_reach_fit.fs';prior=root/'fingerworker_flat132_reach_fit_ISO86_61885fd7.fs'
 assert v.sha(source)==FINAL and v.sha(prior)==PRIOR
 replacements=metadata['ISO81_changes_from_prior_R5'];assert len(replacements)==5
 current=source.read_text()
 for item in replacements:
  assert current.count(item['new'])==1
  current=current.replace(item['new'],item['old'],1)
 assert hashlib.sha256(current.encode()).hexdigest()==PRIOR and current==prior.read_text()
 old='const stroke = definition.isometricLock ? 15 * mm - preload : restOffset+definition.previewTravel;'
 new='const stroke = definition.isometricLock ? 20 * mm - preload : restOffset+definition.previewTravel;'
 assert prior.read_text().count(old)==source.read_text().count(new)==1
 # Comments, annotations and purchased-body display names are the other four edits.
 assert replacements[0]['new'].startswith(' * ') and replacements[1]['new'].startswith(' * ')
 assert replacements[2]['new'].startswith('"Isometric: BOTH81 mm sleeves;')
 assert replacements[4]['new']=='ISOMETRIC steel compression lock sleeve 16 x 8 x 81 mm'
 assert replacements[3]['new'].splitlines()[-1].strip()==new and replacements[3]['old'].splitlines()[-1].strip()==old
 files={}
 for name in ['Flat132_R5_neutral_final.zip','Flat132_R5_final_AP214.step','Flat132_R5_max28_p2_heavy_final.zip','Flat132_R5_max28_p2_trimN08_final.zip','Flat132_R5_max30_p0_trimP08_final.zip']:
  path=root/'native'/name;files[str(path.resolve())]={'sha256':v.sha(path),'original_source_sha256':PRIOR,'isometricLock':False,'geometry_equivalent_to_final_source':True}
 return {'status':'PASS_EXACT_MODE_CONDITIONED_EQUIVALENCE','scope':'Only isometricLock=false. Original neutral/dynamic exports are not claimed to originate from the final ISO81 source. IsometricLock=true requires a new final-source native export.','certificate_generator_sha256':v.sha(Path(__file__)),'final_source':str(source),'final_source_sha256':FINAL,'prior_source_snapshot':str(prior),'prior_source_sha256':PRIOR,'inverse_replacements':replacements,'exact_inverse_source_sha256':hashlib.sha256(current.encode()).hexdigest(),'only_coordinate_expression_delta':{'old':old,'new':new,'unchanged_false_branch':'restOffset+definition.previewTravel'},'unchanged_mode':{'isometricLock':False},'domain_extension':False,'native_export_origins':files}
if __name__=='__main__':
 report=proof();v.write(v.HERE/'dynamic-mode-equivalence.json',report);print(report['status'])
