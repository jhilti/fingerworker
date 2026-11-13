#!/usr/bin/env python3
"""Structural/link validation for the generated offline overview."""
from pathlib import Path
from html.parser import HTMLParser
from collections import Counter
from urllib.parse import urlsplit,unquote
import hashlib,json,re

HERE=Path(__file__).resolve().parent;ROOT=next(p for p in HERE.parents if (p/'firmware').is_dir())
html_path=(ROOT/'Uebersicht.html') if HERE==ROOT/'overview' else HERE/'Uebersicht.preview.html';html=html_path.read_text()
manifest=json.loads((HERE/'build-manifest.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(html_path)==manifest['html_sha256'] and manifest['revision']=='R18'
assert manifest['print_items']==6 and manifest['hardware_rows']==25
assert manifest['primary_print_variant']=='P01_replacement'
assert not re.search(r'@@[A-Z0-9_]+@@|%%[A-Z_]+%%',html)

class Parser(HTMLParser):
 def __init__(self):
  super().__init__();self.ids=[];self.links=[];self.runtime=[];self.images=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id' in a:self.ids.append(a['id'])
  if tag=='a' and 'href' in a:self.links.append(a['href'])
  if tag in ['script','img','iframe','video','audio','source'] and a.get('src'):self.runtime.append(a['src'])
  if tag=='link' and a.get('href'):self.runtime.append(a['href'])
  if tag=='img' and a.get('src'):self.images.append(a['src'])
p=Parser();p.feed(html)
duplicates=[k for k,v in Counter(p.ids).items() if v>1];assert not duplicates,duplicates
local=[];anchors=[];external=[]
for link in p.links:
 u=urlsplit(link)
 if u.scheme:
  assert u.scheme in ['https','http'],link
  external.append(link)
 elif u.path:
  target=ROOT/unquote(u.path);assert target.is_file(),link;local.append(link)
 else:
  assert u.fragment in p.ids,link;anchors.append(link)
assert all(x.startswith('data:') for x in p.runtime),[x for x in p.runtime if not x.startswith('data:')]
assert len(p.images)==5 and all(x.startswith('data:image/') for x in p.images)
for path,digest in manifest['source_files'].items():assert sha(ROOT/path)==digest,path
if HERE==ROOT/'overview':assert sha(ROOT/'fingerworker_mvp.fs')==manifest['source_sha256']
visible=re.sub(r'<script\b[^>]*>.*?</script>|<style\b[^>]*>.*?</style>','',html,flags=re.S|re.I)
visible=re.sub(r'<[^>]+>',' ',visible)
visible=re.sub(r'\s+',' ',visible)
assert not re.search(r'(?:2|3|4|5)\s*mm\s*(?:Außen)?[Bb]rim|[Bb]rim\s*(?:2|3|4|5)\s*mm',visible)
assert 'Alle sechs Modelle sind ohne Brim' in visible
assert 'Teile und Stützen verwenden nur PLA' in visible
assert 'Bambu Studio' in visible
assert manifest['primary_print_profile']=='PLA_Basic'
assert 'organische' in visible and 'Daumenmulden' in visible and 'P01-Ersatzpaket' in visible
assert 'noch nicht angezeigt' not in visible and 'bestehende Nutzerprojekt blieb erhalten' not in visible
assert 'X28/X65' in visible and '37 mm' in visible and '132,4 mm P01-Außenmaß' in visible
result=dict(status='PASS_STATIC_OVERVIEW',revision='R18',html_sha256=sha(html_path),
 html_ids=len(p.ids),duplicate_ids=duplicates,local_file_links=len(local),external_navigation_links=len(external),
 internal_anchors=len(anchors),embedded_images=len(p.images),external_runtime_assets=0,
 print_rows=manifest['print_items'],hardware_rows=manifest['hardware_rows'],source_bindings_verified=True,
 limitation='Structural offline checks only. Visual and interactive behavior requires separate browser preview.')
(HERE/'static-validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
