"""Export only generated fields; never copy original documents or gold labels."""
import argparse,json,gzip,hashlib
p=argparse.ArgumentParser();p.add_argument('input');p.add_argument('output');a=p.parse_args();d=json.load(open(a.input));s=d['summary'];rows=[];units=[];spans=0
for r in d['records']:
 for ann in r['predictions']:
  for k in ['holder','aspect','sentiment']:
   v=ann.get(k)
   if isinstance(v,dict) and v.get('location'):
    b,e=v['location'];assert type(b)==type(e)==int and 0<=b<e<=len(r['text']) and r['text'][b:e]==v['term'];spans+=1
 us=[{k:u[k] for k in ['location','annotations','attempts','rejected','parse_errors','validation_errors']} for u in r['sentences']];units+=us
 rows.append({'id':r['id'],'source_sha256':hashlib.sha256(r['text'].encode()).hexdigest(),'predictions':r['predictions'],'units':us})
summary={k:s[k] for k in ['model','task','config','documents','elapsed_seconds','dataset_sha256']};summary.update(units=len(units),rejected_units=sum(u['rejected'] for u in units),empty_units=sum(not u['rejected'] and not u['annotations'] for u in units),retained_tuples=sum(len(r['predictions']) for r in rows),attempts=sum(u['attempts'] for u in units),retained_spans_audited=spans)
open(a.output,'wb').write(gzip.compress(json.dumps({'summary':summary,'records':rows},ensure_ascii=False,separators=(',',':')).encode(),mtime=0))
