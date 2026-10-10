"""Compare model tuples with the human annotations and build the tuple-review batch for anotai.

Each predicted tuple has four elements (category, aspect, expression, polarity) and is compared with every
human tuple of the same review; its level comes from the human tuple that shares the most elements:
- identical: all four elements equal;
- similar: two or three equal;
- different: at most one equal.
Aspect and expression are equal when their offsets are; a human tuple without polarity (the ote_acd part of
the test set) counts its polarity as equal. Several predictions can match the same human tuple. Reviews
without human annotations (33 in train) are left out of the comparison.

Each run's tuples are written per level into the model's folder, --models-out/MODEL/LEVEL/SPLIT.CONFIG.json,
in the format of the human dataset ({doc_id: {"text", "annotations"}}, reviews in the original order, only
those with a tuple at that level), each annotation with the elements it shares with the closest human tuple;
--models-out/MODEL/summary.json holds the counts of every run of the model. Identical tuples are not reviewed; --per-level similar and --per-level different
tuples are sampled per model into the batch for anotai's importTupleReview.js at --out (contains review
sentences; keep it under private_runs/). Every config in --configs is compared and written; only the runs of
--sample-configs are sampled and go into the batch. A model is sampled only once all its runs for
--sample-configs are complete, so re-running never changes a sample.
"""
import argparse,csv,hashlib,json,pathlib,random
root=pathlib.Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser()
p.add_argument('--train',default='datasets/train.json');p.add_argument('--test',default='datasets/test.json')
p.add_argument('--raw',default='private_runs/v2_{split}');p.add_argument('--configs',default='full,no_retry,no_tags')
p.add_argument('--sample-configs',default='full')
p.add_argument('--per-level',type=int,default=10);p.add_argument('--seed',default='20261009')
p.add_argument('--batch',default='offset_aware_v2')
p.add_argument('--out',default='private_runs/tuple_review/tuple_review.json')
p.add_argument('--counts',default='audit/tuple_review_counts.csv')
p.add_argument('--models-out',default='results');a=p.parse_args()

sample_cfgs=a.sample_configs.split(',')
datasets={s:json.load(open(root/getattr(a,s))) for s in ['train','test']}
ELEMENTS=['category','aspect','expression','polarity']
def shared(h,t):
 return [e for e,ok in zip(ELEMENTS,[h['category']==t['category'],h['aspect']['location']==t['aspect']['location'],
  h['sentiment']['location']==t['sentiment']['location'],h['polarity'] in (None,t['polarity'])]) if ok]

def compare(records,gold):
 excluded=0;levels={'identical':[],'similar':[],'different':[]}
 for r in records:
  g=gold[r['id']].get('annotations') or []
  if not g:excluded+=len(r['predictions']);continue
  for i,t in enumerate(r['predictions']):
   best=max((shared(h,t) for h in g),key=len)
   levels['identical' if len(best)==4 else 'similar' if len(best)>=2 else 'different'].append((r,i,t,best))
 return levels,excluded,sum(len(gold[r['id']].get('annotations') or []) for r in records)

def item(model,split,cfg,r,i,t,best,level):
 b,e=t['aspect']['location'];u=next(u for u in r['sentences'] if u['location'][0]<=b<u['location'][1])
 o=u['location'][0];s=r['text'][o:u['location'][1]]
 rel=lambda loc:[loc[0]-o,loc[1]-o]
 asp,exp=rel(t['aspect']['location']),rel(t['sentiment']['location'])
 assert s[asp[0]:asp[1]]==t['aspect']['term'] and s[exp[0]:exp[1]]==t['sentiment']['term']
 k=f"{model}|{split}|{cfg}|{r['id']}|{i}"
 return {'key':k,'doc_id':r['id'],'sentence':s,'category':t['category'],'aspect':t['aspect']['term'],'aspect_span':asp,
  'expression':t['sentiment']['term'],'expression_span':exp,'polarity':t['polarity'],'level':level,'shared_elements':best,
  'position':int(hashlib.sha256((a.seed+k).encode()).hexdigest()[:12],16)}

runs=[];rows=[]
for model in (root/'models.txt').read_text().split():
 mine=[];complete=True
 for split in ['train','test']:
  for cfg in a.configs.split(','):
   f=root/a.raw.format(split=split)/f"{model.replace('/','__')}.{cfg}.asqp.json"
   d=json.load(open(f)) if f.exists() else None
   if not d or d['summary']['documents']!=len(datasets[split]):
    complete=complete and cfg not in sample_cfgs;continue
   levels,excl,human=compare(d['records'],datasets[split])
   ident,sim,diff=(len(levels[k]) for k in ['identical','similar','different'])
   run={'model':model,'split':split,'config':cfg,'predicted':ident+sim+diff,'equal_to_human':ident,'similar_to_human':sim,
        'different':diff,'human_tuples':human,'items':[]}
   rows.append({'model':model,'split':split,'config':cfg,'predicted':run['predicted'],'identical':ident,'similar':sim,
                'different':diff,'human_tuples':human,'excluded_unannotated':excl})
   for level,xs in levels.items():
    dd=root/a.models_out/model.replace('/','__')/level;dd.mkdir(parents=True,exist_ok=True)
    by={}
    for r,i,t,best in xs:by.setdefault(r['id'],[]).append({**{k:t[k] for k in ['category','aspect','sentiment','polarity']},'shared_elements':best})
    body={k:{'text':v['text'],'annotations':by[k]} for k,v in datasets[split].items() if k in by}
    (dd/f'{split}.{cfg}.json').write_text(json.dumps(body,ensure_ascii=False,indent=4),encoding='utf-8')
   if cfg in sample_cfgs:runs.append(run);mine.append((run,levels))
 if not complete:continue
 for level in ['similar','different']:
  pool=[(run,x) for run,lv in mine for x in lv[level]]
  for run,x in random.Random(f"{a.seed}:{model}:{level}").sample(pool,min(a.per_level,len(pool))):
   run['items'].append(item(model,run['split'],run['config'],*x,level))
for r in rows:
 its=next((x['items'] for x in runs if (x['model'],x['split'],x['config'])==(r['model'],r['split'],r['config'])),[])
 for level in ['similar','different']:r[f'sampled_{level}']=sum(it['level']==level for it in its)

for model in (root/'models.txt').read_text().split():
 mr=[{k:v for k,v in r.items() if k!='model'} for r in rows if r['model']==model]
 if mr:(root/a.models_out/model.replace('/','__')/'summary.json').write_text(json.dumps({'model':model,'runs':mr},indent=1))
out=root/a.out;out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps({'batch':a.batch,'runs':runs},ensure_ascii=False,indent=1))
with open(root/a.counts,'w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=['model','split','config','predicted','identical','similar','different','human_tuples','excluded_unannotated','sampled_similar','sampled_different']);w.writeheader();w.writerows(rows)
pc=lambda x,n:f"{100*x/max(n,1):.1f}%"
for r in rows:print(f"{r['model']:28} {r['split']:5} {r['config']:8} pred {r['predicted']:5} identical {r['identical']:5} ({pc(r['identical'],r['predicted'])}) similar {r['similar']:5} ({pc(r['similar'],r['predicted'])}) different {r['different']:5} ({pc(r['different'],r['predicted'])}) sampled {r['sampled_similar']}+{r['sampled_different']}")
print(f"{sum(len(x['items']) for x in runs)} items -> {out}; counts -> {a.counts}")
