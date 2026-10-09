"""Merge the two test subtask CSVs into one JSON file in the format of the training set.

The test split annotates disjoint reviews in two files: ate_asqp.csv (quadruples) and
ote_acd.csv (one row per aspect, with opinion terms and category but no polarity).
Polarity is null for reviews from ote_acd.csv. The CSVs give no sentiment offsets, so each
sentiment term is placed at its occurrence in the aspect's sentence closest to the aspect;
this rule reproduces 3,431 of the 3,436 sentiment offsets of the training set.
The output contains original text, so write it under the ignored datasets/ directory.
"""
import argparse,ast,csv,io,json,pathlib,re,sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from run_experiment import split_sentences

p=argparse.ArgumentParser();p.add_argument('subtasks',help='directory with ate_asqp.csv and ote_acd.csv')
p.add_argument('--out',default='datasets/test.json');a=p.parse_args()
csv.field_size_limit(sys.maxsize)
read=lambda name:list(csv.DictReader(io.StringIO((pathlib.Path(a.subtasks)/name).read_text(encoding='utf-8-sig')),delimiter=';'))

def gap(s,e,b,f):return 0 if s<f and b<e else (b-e if e<=b else s-f)
def annotation(text,aspect,term,category,polarity):
 b,e=aspect['start_pos'],aspect['end_pos'];assert text[b:e]==aspect['term']
 spans=split_sentences(text);unit=lambda x:next(i for i,(_,s,f) in enumerate(spans) if s<=x<f)
 starts=[m.start() for m in re.finditer(re.escape(term),text)];assert starts,term
 s=min(starts,key=lambda s:(unit(s)!=unit(b),gap(s,s+len(term),b,e),s))
 return {'category':category,'aspect':{'term':aspect['term'],'location':[b,e]},
         'sentiment':{'term':term,'location':[s,s+len(term)],'type':'explicit'},'polarity':polarity}

data={}
# ate_asqp ids share the numbering of the training set (ex_NNNN) and do not collide with it
for r in read('ate_asqp.csv'):
 key=f"ex_{int(r['id']):04d}";assert key not in data
 data[key]={'text':r['text'],'annotations':[annotation(r['text'],q['aspect'],q['sentiment'],q['category'],q['polarity'])
                                            for q in ast.literal_eval(r['target_quadruples'])]}
# ote_acd ids number rows, not reviews; key each review by its first row id
ote={}
for r in read('ote_acd.csv'):
 doc=ote.setdefault(r['text'],{'key':f"ote_{int(r['id']):04d}",'text':r['text'],'annotations':[]})
 aspect=ast.literal_eval(r['aspect'])
 doc['annotations']+=[annotation(r['text'],aspect,t,r['target_aspect_category'],None) for t in ast.literal_eval(r['target_opinion_terms'])]
for doc in ote.values():
 assert doc['key'] not in data;data[doc['key']]={'text':doc['text'],'annotations':doc['annotations']}

out=pathlib.Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(data,ensure_ascii=False,indent=4),encoding='utf-8')
units=sum(len(split_sentences(d['text'])) for d in data.values())
print(f"{len(data)} reviews ({len(data)-len(ote)} ate_asqp, {len(ote)} ote_acd), {units} sentences, "
      f"{sum(len(d['annotations']) for d in data.values())} annotations -> {out}")
