"""Reproducible, read-only import. Master tabs avoid counting overlapping category tabs."""
from pathlib import Path
import json,re,hashlib,struct
from datetime import date,datetime
from decimal import Decimal
import openpyxl
from merge_supplement import merge
ROOT=Path(__file__).resolve().parents[1]
def clean(x):
 if x is None:return ''
 if isinstance(x,(datetime,date)):return x.isoformat()
 return re.sub(r'\s+',' ',str(x)).strip()
def money(x,multiplier=1):
 s=clean(x).replace(',','').lower().replace('₹','')
 if not s:return None
 if re.fullmatch(r'\d+(\.\d+)?l',s):s=s[:-1];multiplier=100000
 if not re.fullmatch(r'\d+(\.\d+)?',s):return None
 return int(Decimal(s)*multiplier)
def doc_text(path):
 import olefile
 with olefile.OleFileIO(path) as ole:
  w=ole.openstream('WordDocument').read();flags=struct.unpack_from('<H',w,10)[0]
  t=ole.openstream('1Table' if flags&512 else '0Table').read()
  off,size=struct.unpack_from('<II',w,0x1a2);clx=t[off:off+size];p=0
  while p<len(clx) and clx[p]==1:p+=3+struct.unpack_from('<H',clx,p+1)[0]
  if p>=len(clx) or clx[p]!=2:raise ValueError('Unsupported DOC piece table')
  n=(struct.unpack_from('<I',clx,p+1)[0]-4)//12;d=clx[p+5:];cps=struct.unpack_from('<'+'I'*(n+1),d)
  out=[]
  for i in range(n):
   fc=struct.unpack_from('<I',d,4*(n+1)+8*i+2)[0];compressed=bool(fc&0x40000000);fc=fc&0x3fffffff
   if compressed:fc//=2
   count=cps[i+1]-cps[i]
   out.append(w[fc:fc+count*(1 if compressed else 2)].decode('cp1252' if compressed else 'utf-16-le',errors='replace'))
  return ''.join(out)
def build():
 originals=ROOT/'data/originals';publications={};grants=[];raw=[];issues=[];inventory=[]
 for f in sorted(originals.glob('*')):
  inventory.append({'file':f.name,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size})
  if f.suffix!='.xlsx':continue
  w=openpyxl.load_workbook(f,read_only=True,data_only=True)
  if f.name.startswith('202'):
   s=w.worksheets[0];headers=None;count=0;summary_count=None
   for r,row in enumerate(s.iter_rows(max_col=65,values_only=True),1):
    vals=[clean(x) for x in row]
    if vals[0].lower()=='total publication' and len(row)>2 and isinstance(row[2],(int,float)):summary_count=int(row[2])
    if 'PUBLICATION TITLE' in vals:headers=vals;continue
    if not headers:continue
    d={k:v for k,v in zip(headers,vals) if k}
    title=d.get('PUBLICATION TITLE','')
    if not title or title=='PUBLICATION TITLE':continue
    pid=d.get('PUB ID','');doi=d.get('DOI','').strip().lower().removeprefix('https://doi.org/')
    key='PUB-'+pid if pid else ('DOI-'+doi if doi else 'TITLE-'+hashlib.sha256(title.lower().encode()).hexdigest()[:16])
    src={'file':f.name,'sheet':s.title,'row':r};count+=1
    if key in publications:
     publications[key]['sources'].append(src);continue
    publications[key]={'id':key,'title':title,'authors':d.get('AUTHORS',''),'home_authors':d.get('HOME AUTHORS',''),'department':d.get('HOME AUTHOR DEPARTMENT',''),'year':d.get('YEAR',''),'type':d.get('ARTICLE TYPE',''),'venue':d.get('SOURCE PUBLICATION',''),'doi':doi,'url':d.get('LINK',''),'abstract':d.get('ABSTRACT',''),'tags':d.get('TECHNOLOGYAREAS',''),'cycle':f.name[:7],'sources':[src],'evidence_level':'uploaded_metadata_and_abstract_not_full_text','mock':False}
   issues.append({'source':f.name,'severity':'info','message':f'Imported {count} title rows from {s.title}; overlapping subsidiary tabs excluded.'})
   if summary_count is not None and summary_count!=count:issues.append({'source':f.name,'severity':'warning','message':f'Summary states {summary_count} publications but the master table contains {count} title rows; missing records were not fabricated.'})
  elif f.name.startswith('External'):
   for s in w:
    for r,row in enumerate(s.iter_rows(max_col=20,values_only=True),1):
     if any(x is not None for x in row):raw.append({'file':f.name,'sheet':s.title,'row':r,'cells':[clean(x) for x in row]})
   s=w['Details_2022-23-24-25']
   for r,row in enumerate(s.iter_rows(max_col=15,values_only=True),1):
    if not isinstance(row[0],(float,int)) or not row[2]:continue
    amount=money(row[9]);rec=money(row[11]);non=money(row[12])
    g={'id':f'GRANT-{r}','title':clean(row[2]),'investigators':clean(row[3]),'agency':clean(row[5]),'department':clean(row[7]),'year':clean(row[8]),'amount_inr':amount,'recurring_inr':rec,'nonrecurring_inr':non,'received_inr':money(row[13]),'date':clean(row[1]),'status':'Historical award','source':{'file':f.name,'sheet':s.title,'row':r},'notes':clean(row[14]),'mock':False}
    grants.append(g)
    if amount is not None and rec is not None and non is not None and rec+non!=amount:issues.append({'source':g['id'],'severity':'warning','message':'Recurring + non-recurring differs from sanctioned amount; source values preserved, not corrected.'})
  else:
   for s in w:
    for r,row in enumerate(s.iter_rows(max_col=16,values_only=True),1):
     if any(x is not None for x in row):raw.append({'file':f.name,'sheet':s.title,'row':r,'cells':[clean(x) for x in row]})
     if not isinstance(row[0],(int,float)) or not row[3]:continue
     grants.append({'id':f'APP-{r}','title':clean(row[3]),'investigators':clean(row[4]),'agency':clean(row[6]),'department':clean(row[1]),'year':'2025-26','amount_inr':money(row[10],100000),'date':clean(row[2]),'status':'Applied (outcome unknown)','source':{'file':f.name,'sheet':s.title,'row':r},'notes':clean(row[12]),'mock':False})
     if '2026' in clean(row[2]) and '14/8' in clean(row[2]):issues.append({'source':f.name+f' row {r}','severity':'warning','message':'Application date 14/08/2026 falls outside the stated July 2025–July 2026 cycle. Preserved for office review.'})
  w.close()
 legacy=[]
 for f in originals.glob('*.doc'):
  text=doc_text(f);(ROOT/'data/legacy_grants_extracted.txt').write_text(text.replace('\x07',' | ').replace('\r','\n'),encoding='utf-8')
  # Preserve DOC table rows as evidence. Amount columns are ambiguous; no financial aggregation.
  chunks=re.split(r'\r?\x07\r?\x07',text)
  for i,chunk in enumerate(chunks,1):
   if chunk.strip():legacy.append({'id':f'LEGACY-{i}','text':chunk.replace('\x07',' | ').replace('\r','\n').strip(),'source':f.name,'status':'Historical source; unnormalized','mock':False})
  issues.append({'source':f.name,'severity':'info','message':'Legacy DOC text extracted with cell boundaries; searchable separately. Excluded from financial totals to avoid overlap and ambiguous units.'})
 bundle={'publications':list(publications.values()),'grants':grants,'legacy':legacy,'raw_rows':raw,'issues':issues,'inventory':inventory,'imported_at':'2026-10-27','method':'Master-tab import; PUB ID then DOI then normalized-title deduplication. Historical awards and applications separate; legacy rows not aggregated.'}
 merge(ROOT/'data/supplement',bundle,clean)
 (ROOT/'data/catalog.json').write_text(json.dumps(bundle,ensure_ascii=False,indent=2),encoding='utf-8')
 print({k:len(bundle[k]) for k in ['publications','grants','legacy','issues']})
if __name__=='__main__':build()
