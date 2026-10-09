"""Draw the stratified sample for the semantic audit (audit/GUIA_AUDITORIA_SEMANTICA.md).

With --previous, the tuples already sampled in each run are kept and the sample is
topped up uniformly from the remaining tuples, so verdicts can be reused. The sample
contains original text, so it must be written under the ignored private_runs/ directory.
"""
import argparse,gzip,hashlib,json,pathlib,random

p=argparse.ArgumentParser()
p.add_argument('--asqp',required=True)
p.add_argument('--results',default='results');p.add_argument('--out',default='private_runs/semantic_audit')
p.add_argument('--configs',nargs='+',default=['full']);p.add_argument('--per-run',type=int,default=100)
p.add_argument('--seed',type=int,default=20260930);p.add_argument('--previous')
p.add_argument('--chunks',type=int,default=3);p.add_argument('--overlap',type=float,default=0.10)
a=p.parse_args()
source=json.loads(pathlib.Path(a.asqp).read_bytes())
out=pathlib.Path(a.out);(out/'chunks').mkdir(parents=True,exist_ok=True);(out/'judgments').mkdir(exist_ok=True)

def key(doc,t):
 # the trailing None keeps item IDs stable with samples drawn when the audit also covered SSA
 return json.dumps(['asqp',doc,t['aspect']['location'],t['sentiment']['location'],t['polarity'],t['category'],None])

def unit_of(units,b):
 for i,u in enumerate(units):
  if u['location'][0]<=b<u['location'][1]:return i
 return None

# previous sample: positions to keep, primary verdicts and location-rule decisions to reuse
kept={};reuse={};reuse_sec={};decisions={}
if a.previous:
 prev=pathlib.Path(a.previous);P=json.load(open(prev/'sample_index.json'))
 for r in P['index']:kept.setdefault(r['file'],set()).add((r['doc'],r['tuple_index']))
 for f in sorted((prev/'judgments').glob('*.jsonl')):
  for l in open(f):
   j=json.loads(l)
   if f.stem=='reused' or P['primary'].get(j['item_id'])==int(f.stem.split('_')[1]):reuse[j['item_id']]=j
   elif f.stem=='reused_secondary' or P['secondary'].get(j['item_id'])==int(f.stem.split('_')[1]):reuse_sec[j['item_id']]=j
 if (prev/'ood_decisions.jsonl').exists():decisions={d['item_id']:d for d in map(json.loads,open(prev/'ood_decisions.jsonl'))}

index=[];items={}
for f in sorted(pathlib.Path(a.results).glob('*.json.gz')):
 d=json.loads(gzip.decompress(f.read_bytes()));s=d['summary']
 if s['task']!='asqp' or s['config'] not in a.configs:continue
 pool=[(r,i) for r in d['records'] for i in range(len(r['predictions']))]
 keep=[j for j,(r,i) in enumerate(pool) if (r['id'],i) in kept.get(f.name,set())]
 rest=[j for j in range(len(pool)) if j not in set(keep)]
 chosen=sorted(keep+random.Random(f'{a.seed}:{f.name}').sample(rest,max(0,min(a.per_run,len(pool))-len(keep))))
 for j in chosen:
  r,i=pool[j];t=r['predictions'][i];text=source[r['id']]['text']
  assert hashlib.sha256(text.encode()).hexdigest()==r['source_sha256']
  item_id=hashlib.sha1(key(r['id'],t).encode()).hexdigest()[:12]
  index.append({'item_id':item_id,'file':f.name,'model':s['model'],'task':'asqp','config':s['config'],'doc':r['id'],'tuple_index':i})
  if item_id in items:continue
  u=unit_of(r['units'],t['aspect']['location'][0]);u=unit_of(r['units'],t['sentiment']['location'][0]) if u is None else u
  sb,se=r['units'][u]['location'];ctx=lambda k:text[slice(*r['units'][k]['location'])] if 0<=k<len(r['units']) else ''
  rel=lambda span:[span[0]-sb,span[1]-sb] if span else []
  tup={'polarity':t['polarity'],'aspect':t['aspect']['term'],'aspect_pos':rel(t['aspect']['location']),
       'sentiment':t['sentiment']['term'],'sentiment_pos':rel(t['sentiment']['location']),'sentiment_type':t['sentiment'].get('type'),
       'category':t['category']}
  items[item_id]={'item_id':item_id,'task':'asqp','before':ctx(u-1),'sentence':text[sb:se],'after':ctx(u+1),'tuple':tup}
 print(f.name,len(pool),len(chosen),'kept',len(keep))

reused=sorted(i for i in items if i in reuse)
(out/'judgments'/'reused.jsonl').write_text(''.join(json.dumps(reuse[i],ensure_ascii=False)+'\n' for i in reused))
(out/'judgments'/'reused_secondary.jsonl').write_text(''.join(json.dumps(reuse_sec[i],ensure_ascii=False)+'\n' for i in reused if i in reuse_sec))
(out/'ood_decisions.jsonl').write_text(''.join(json.dumps(decisions[i],ensure_ascii=False)+'\n' for i in reused if i in decisions))
ids=sorted(i for i in items if i not in reuse);random.Random(a.seed+1).shuffle(ids)
chunks=[ids[c::a.chunks] for c in range(a.chunks)];double={}
for c,ch in enumerate(chunks):
 for item_id in ch[:round(len(ch)*a.overlap)]:double[item_id]=(c+1)%a.chunks
for old in (out/'chunks').glob('chunk_*.jsonl'):old.unlink()
for c in range(a.chunks):
 rows=chunks[c]+[i for i,d in double.items() if d==c];random.Random(a.seed+2+c).shuffle(rows)
 (out/'chunks'/f'chunk_{c:02d}.jsonl').write_text(''.join(json.dumps(items[i],ensure_ascii=False)+'\n' for i in rows))
(out/'items.jsonl').write_text(''.join(json.dumps(items[i],ensure_ascii=False)+'\n' for i in sorted(items)))
json.dump({'seed':a.seed,'per_run':a.per_run,'configs':a.configs,'reused':reused,'primary':{i:c for c,ch in enumerate(chunks) for i in ch},'secondary':double,'index':index},open(out/'sample_index.json','w'))
print('sampled tuples:',len(index),'unique items:',len(items),'reused verdicts:',len(reused),'to judge:',len(ids),'double-judged:',len(double))
