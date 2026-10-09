"""Compare model tuples with the human annotations and build the tuple-review batch for anotai.

A predicted tuple is equal to a human one when category, aspect offsets and opinion offsets match and the
polarity matches (human tuples without polarity, from the ote_acd part of the test set, match on the other
three fields). Each human tuple matches at most one prediction. Reviews without human annotations (33 in
train) are left out of the comparison.

Writes one row per complete run to --counts (no text; safe to commit) and the batch for
anotai's importTupleReview.js to --out (contains review sentences; keep it under private_runs/). A model's
items are sampled only once all its runs for --configs are complete, so re-running never changes a sample.
"""
import argparse,csv,hashlib,json,pathlib,random
root=pathlib.Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser()
p.add_argument('--train',default='datasets/train.json');p.add_argument('--test',default='datasets/test.json')
p.add_argument('--raw',default='private_runs/v2_{split}');p.add_argument('--configs',default='full')
p.add_argument('--per-model',type=int,default=20);p.add_argument('--seed',default='20261009')
p.add_argument('--batch',default='offset_aware_v2')
p.add_argument('--out',default='private_runs/tuple_review/tuple_review.json')
p.add_argument('--counts',default='audit/tuple_review_counts.csv');a=p.parse_args()

datasets={s:json.load(open(root/getattr(a,s))) for s in ['train','test']}
def key(t):return t['category'],tuple(t['aspect']['location']),tuple(t['sentiment']['location'])

def compare(records,gold):
 equal=0;diff=[];excluded=0
 for r in records:
  g=gold[r['id']].get('annotations') or []
  if not g:excluded+=len(r['predictions']);continue
  free=list(g)
  for i,t in enumerate(r['predictions']):
   m=next((h for h in free if key(h)==key(t) and h['polarity'] in (None,t['polarity'])),None)
   if m is not None:free.remove(m);equal+=1
   else:diff.append((r,i,t))
 return equal,diff,excluded,sum(len(gold[r['id']].get('annotations') or []) for r in records)

def item(model,split,cfg,r,i,t):
 b,e=t['aspect']['location'];u=next(u for u in r['sentences'] if u['location'][0]<=b<u['location'][1])
 o=u['location'][0];s=r['text'][o:u['location'][1]]
 rel=lambda loc:[loc[0]-o,loc[1]-o]
 asp,exp=rel(t['aspect']['location']),rel(t['sentiment']['location'])
 assert s[asp[0]:asp[1]]==t['aspect']['term'] and s[exp[0]:exp[1]]==t['sentiment']['term']
 k=f"{model}|{split}|{cfg}|{r['id']}|{i}"
 return {'key':k,'doc_id':r['id'],'sentence':s,'category':t['category'],'aspect':t['aspect']['term'],'aspect_span':asp,
  'expression':t['sentiment']['term'],'expression_span':exp,'polarity':t['polarity'],
  'position':int(hashlib.sha256((a.seed+k).encode()).hexdigest()[:12],16)}

runs=[];rows=[]
for model in (root/'models.txt').read_text().split():
 mine=[];complete=True
 for split in ['train','test']:
  for cfg in a.configs.split(','):
   f=root/a.raw.format(split=split)/f"{model.replace('/','__')}.{cfg}.asqp.json"
   d=json.load(open(f)) if f.exists() else None
   if not d or d['summary']['documents']!=len(datasets[split]):complete=False;continue
   eq,diff,excl,human=compare(d['records'],datasets[split])
   run={'model':model,'split':split,'config':cfg,'predicted':eq+len(diff),'equal_to_human':eq,'different':len(diff),'human_tuples':human,'items':[]}
   rows.append({**{k:run[k] for k in ['model','split','config','predicted','equal_to_human','different','human_tuples']},'excluded_unannotated':excl})
   runs.append(run);mine.append((run,diff))
 if not complete:continue
 pool=[(run,x) for run,diff in mine for x in diff]
 for run,x in random.Random(f"{a.seed}:{model}").sample(pool,min(a.per_model,len(pool))):
  run['items'].append(item(model,run['split'],run['config'],*x))
for r in rows:r['sampled']=next(len(x['items']) for x in runs if (x['model'],x['split'],x['config'])==(r['model'],r['split'],r['config']))

out=root/a.out;out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps({'batch':a.batch,'runs':runs},ensure_ascii=False,indent=1))
with open(root/a.counts,'w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=['model','split','config','predicted','equal_to_human','different','human_tuples','excluded_unannotated','sampled']);w.writeheader();w.writerows(rows)
for r in rows:print(f"{r['model']:28} {r['split']:5} {r['config']:8} pred {r['predicted']:5} equal {r['equal_to_human']:5} ({100*r['equal_to_human']/max(r['predicted'],1):.1f}%) diff {r['different']:5} human {r['human_tuples']:5} sampled {r['sampled']}")
print(f"{sum(len(x['items']) for x in runs)} items -> {out}; counts -> {a.counts}")
