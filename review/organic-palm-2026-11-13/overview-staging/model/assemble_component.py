from pathlib import Path
import json,base64,gzip,hashlib,re
p=Path(__file__).resolve().parent
m=json.loads((p/'manifest.json').read_text())
packed=base64.b64decode((p/'model-data.b64').read_text())
assert hashlib.sha256(packed).hexdigest()==m['data_sha256']
parts=json.loads(gzip.decompress(packed))
assert m['revision']=='R18' and len(parts)==sum(m['counts'].values()) and m['counts']['print']==7
t=(p/'component-template.html').read_text()
t=t.replace('%%MODEL_DATA%%',(p/'model-data.b64').read_text()).replace('%%VIEWER_JS%%',(p/'viewer.js').read_text())
for k,v in {'COUNT_ALL':len(parts),'COUNT_PRINT':m['counts']['print'],'COUNT_METAL':m['counts']['metal'],
            'COUNT_BUY':m['counts']['buy'],'COUNT_ELECTRONICS':m['counts']['electronics'],'ONSHAPE_VERSION':m['onshape_version']}.items():
    t=t.replace('%%'+k+'%%',str(v))
assert not re.search(r'%%[A-Z_]+%%',t)
(p/'component.html').write_text(t)
(p/'test.html').write_text('<!doctype html><html lang="de"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Fingerworker R18 · Baugruppe</title><style>body{margin:0;padding:30px;background:#edf2f2;font:16px system-ui}main{max-width:1200px;margin:auto}h1{color:#183a45;font-size:25px}p{color:#60757c}@media(max-width:650px){body{padding:12px}}</style><main><h1>Fingerworker R18 · Baugruppenübersicht</h1><p>Lokale Offline-Ansicht der finalen R18-Baugruppe.</p>'+t+'</main></html>')
print('Component bytes',len(t.encode()))
