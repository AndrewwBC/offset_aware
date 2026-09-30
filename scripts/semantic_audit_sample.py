"""Draw the stratified sample for the semantic audit (audit/GUIA_AUDITORIA_SEMANTICA.md).

The sample contains original text, so it must be written outside the repository
or under the ignored private_runs/ directory.
"""
import argparse,gzip,hashlib,json,pathlib,random

p=argparse.ArgumentParser()
p.add_argument('--ssa',required=True);p.add_argument('--asqp',required=True)
p.add_argument('--results',default='results');p.add_argument('--out',default='private_runs/semantic_audit')
p.add_argument('--per-run',type=int,default=50);p.add_argument('--seed',type=int,default=20260930)
p.add_argument('--chunks',type=int,default=8);p.add_argument('--overlap',type=float,default=0.10)
a=p.parse_args()
source={'ssa':json.loads(pathlib.Path(a.ssa).read_bytes()),'asqp':json.loads(pathlib.Path(a.asqp).read_bytes())}
out=pathlib.Path(a.out);(out/'chunks').mkdir(parents=True,exist_ok=True)

def key(task,doc,t):
 h=(t.get('holder') or {}).get('location')
 return json.dumps([task,doc,t['aspect']['location'],t['sentiment']['location'],t['polarity'],t.get('category'),h])

def unit_of(units,b):
 for i,u in enumerate(units):
  if u['location'][0]<=b<u['location'][1]:return i
 return None

rng=random.Random(a.seed);index=[];items={}
for f in sorted(pathlib.Path(a.results).glob('*.json.gz')):
 d=json.loads(gzip.decompress(f.read_bytes()));s=d['summary'];task=s['task']
 pool=[(r,i) for r in d['records'] for i in range(len(r['predictions']))]
 chosen=sorted(rng.sample(range(len(pool)),min(a.per_run,len(pool))))
 for j in chosen:
  r,i=pool[j];t=r['predictions'][i];text=source[task][r['id']]['text']
  assert hashlib.sha256(text.encode()).hexdigest()==r['source_sha256']
  k=key(task,r['id'],t);item_id=hashlib.sha1(k.encode()).hexdigest()[:12]
  index.append({'item_id':item_id,'file':f.name,'model':s['model'],'task':task,'config':s['config'],'doc':r['id'],'tuple_index':i})
  if item_id in items:continue
  u=unit_of(r['units'],t['aspect']['location'][0]);u=unit_of(r['units'],t['sentiment']['location'][0]) if u is None else u
  sb,se=r['units'][u]['location'];ctx=lambda k:text[slice(*r['units'][k]['location'])] if 0<=k<len(r['units']) else ''
  rel=lambda span:[span[0]-sb,span[1]-sb] if span else []
  tup={'polarity':t['polarity'],'aspect':t['aspect']['term'],'aspect_pos':rel(t['aspect']['location']),
       'sentiment':t['sentiment']['term'],'sentiment_pos':rel(t['sentiment']['location']),'sentiment_type':t['sentiment'].get('type')}
  if task=='asqp':tup['category']=t['category']
  else:tup['holder']=t['holder']['term'];tup['holder_pos']=rel(t['holder'].get('location'))
  items[item_id]={'item_id':item_id,'task':task,'before':ctx(u-1),'sentence':text[sb:se],'after':ctx(u+1),'tuple':tup}
 print(f.name,len(pool),len(chosen))

ids=sorted(items);random.Random(a.seed+1).shuffle(ids)
chunks=[ids[c::a.chunks] for c in range(a.chunks)];double={}
for c,ch in enumerate(chunks):
 for item_id in ch[:round(len(ch)*a.overlap)]:double[item_id]=(c+1)%a.chunks
for c in range(a.chunks):
 rows=chunks[c]+[i for i,d in double.items() if d==c];random.Random(a.seed+2+c).shuffle(rows)
 (out/'chunks'/f'chunk_{c:02d}.jsonl').write_text(''.join(json.dumps(items[i],ensure_ascii=False)+'\n' for i in rows))
(out/'items.jsonl').write_text(''.join(json.dumps(items[i],ensure_ascii=False)+'\n' for i in sorted(items)))
json.dump({'seed':a.seed,'per_run':a.per_run,'primary':{i:c for c,ch in enumerate(chunks) for i in ch},'secondary':double,'index':index},open(out/'sample_index.json','w'))
print('sampled tuples:',len(index),'unique items:',len(items),'double-judged:',len(double))
