(()=>{
'use strict';
const $=id=>document.getElementById(id);
const data=JSON.parse($('overview-data').textContent);
const normalized=s=>String(s).toLocaleLowerCase('de').normalize('NFD').replace(/[\u0300-\u036f]/g,'');
function filterPrint(){
 const query=normalized($('print-search').value),scope=$('print-scope').value;
 let count=0;
 document.querySelectorAll('#print-table tbody tr').forEach(row=>{
  const matchesScope=scope==='all'||(scope==='new'?row.dataset.new==='true':scope==='reuse'?row.dataset.new!=='true':row.dataset.scope===scope);
  const show=matchesScope&&normalized(row.textContent).includes(query);
  row.hidden=!show;if(show)count++;
 });
 $('print-count').textContent=count+' von '+data.print_count+' Stücken';$('print-empty').hidden=count>0;
}
['print-search','print-scope'].forEach(id=>$(id).addEventListener(id==='print-search'?'input':'change',filterPrint));
function filterHardware(){
 const query=normalized($('hardware-search').value),group=$('hardware-group').value;let count=0;
 document.querySelectorAll('#hardware-table tbody tr').forEach(row=>{
  const show=(group==='all'||row.dataset.group===group)&&normalized(row.textContent).includes(query);
  row.hidden=!show;if(show)count++;
 });
 $('hardware-count').textContent=count+' von '+data.hardware.length+' Positionen';$('hardware-empty').hidden=count>0;
}
$('hardware-search').addEventListener('input',filterHardware);$('hardware-group').addEventListener('change',filterHardware);
$('export-hardware').addEventListener('click',()=>{
 const rows=[['Gruppe','Kennung','Menge','Ausführung','Dokumentierter Status','Hinweis'],...data.hardware];
 const csv='\ufeff'+rows.map(row=>row.map(v=>'"'+String(v).replace(/"/g,'""')+'"').join(';')).join('\r\n');
 const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));
 const anchor=document.createElement('a');anchor.href=url;anchor.download='Fingerworker_R19_Funktionshardware_2026-11-13.csv';document.body.append(anchor);anchor.click();anchor.remove();setTimeout(()=>URL.revokeObjectURL(url),10000);
});
const storageKey='fingerworker-overview-r19-v1';let saved={checks:{},notes:''};let storageAvailable=true;
try{const raw=localStorage.getItem(storageKey);if(raw){const parsed=JSON.parse(raw);if(parsed&&typeof parsed==='object')saved={checks:parsed.checks||{},notes:typeof parsed.notes==='string'?parsed.notes:''};}}catch(error){storageAvailable=false;}
const checkboxes=Array.from(document.querySelectorAll('.check-item input[type=checkbox]'));
function progress(){const count=checkboxes.filter(c=>c.checked).length;$('check-progress').textContent=count+' von '+checkboxes.length+' Punkten selbst abgehakt';}
function persist(){try{localStorage.setItem(storageKey,JSON.stringify(saved));}catch(error){storageAvailable=false;$('storage-note').textContent='Lokales Speichern ist hier nicht verfügbar. Die Eingaben bleiben nur bis zum Schließen dieser Seite erhalten.';}}
checkboxes.forEach(c=>{c.checked=saved.checks[c.dataset.check]===true;c.addEventListener('change',()=>{saved.checks[c.dataset.check]=c.checked;persist();progress();});});
$('personal-notes').value=saved.notes;$('personal-notes').addEventListener('input',()=>{saved.notes=$('personal-notes').value;persist();});
$('reset-checks').addEventListener('click',()=>{checkboxes.forEach(c=>{c.checked=false;});saved.checks={};persist();progress();});
if(!storageAvailable)$('storage-note').textContent='Lokales Speichern ist hier nicht verfügbar. Die Eingaben bleiben nur bis zum Schließen dieser Seite erhalten.';
progress();
$('print-page').addEventListener('click',()=>window.print());
let printedDetails=[];
window.addEventListener('beforeprint',()=>{printedDetails=Array.from(document.querySelectorAll('details')).map(el=>[el,el.open]);printedDetails.forEach(([el])=>{el.open=true;});});
window.addEventListener('afterprint',()=>printedDetails.forEach(([el,open])=>{el.open=open;}));
const dialog=$('image-dialog');
document.querySelectorAll('[data-zoom]').forEach(button=>button.addEventListener('click',()=>{const source=button.querySelector('img');$('image-large').src=source.src;$('image-large').alt=source.alt;$('image-title').textContent=button.dataset.zoom;dialog.showModal();}));
$('close-image').addEventListener('click',()=>dialog.close());dialog.addEventListener('click',e=>{if(e.target===dialog)dialog.close();});
const navLinks=Array.from(document.querySelectorAll('.sidebar nav a'));
const sections=navLinks.map(a=>document.querySelector(a.getAttribute('href'))).filter(Boolean);
let pending=false;
function updateNav(){let selected=sections[0];const offset=window.innerWidth<=900?150:100;for(const section of sections){if(section.getBoundingClientRect().top<=offset)selected=section;}navLinks.forEach(a=>{const active=a.hash==='#'+selected.id;a.classList.toggle('active',active);if(active)a.setAttribute('aria-current','location');else a.removeAttribute('aria-current');});pending=false;}
window.addEventListener('scroll',()=>{if(!pending){pending=true;requestAnimationFrame(updateNav);}},{passive:true});window.addEventListener('resize',updateNav);updateNav();
filterPrint();filterHardware();
})();
