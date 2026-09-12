import gzip,hashlib,json,pathlib
root=pathlib.Path(__file__).resolve().parents[1]
print('model,task,config,documents,rejection_percent,tuples,empty_units,attempts_per_unit,minutes,tuples_per_minute')
for entry in json.loads((root/'results/manifest.json').read_text()):
 p=root/entry['file'];assert hashlib.sha256(p.read_bytes()).hexdigest()==entry['sha256']
 d=json.loads(gzip.decompress(p.read_bytes()));s=d['summary'];rows=d['records'];u=[u for r in rows for u in r['units']]
 assert len(rows)==s['documents']==763 and len(u)==s['units']==3831
 assert sum(len(r['predictions']) for r in rows)==s['retained_tuples']
 assert sum(x['rejected'] for x in u)==s['rejected_units']
 assert sum(x['attempts'] for x in u)==s['attempts']
 assert sum(not x['rejected'] and not x['annotations'] for x in u)==s['empty_units']
 def check(v):
  if isinstance(v,dict):
   assert not {'text','gold','reference_annotations','gold_polarity'}&v.keys()
   for x in v.values():check(x)
  elif isinstance(v,list):
   for x in v:check(x)
 check(d)
 minutes=s['elapsed_seconds']/60
 print(f"{s['model']},{s['task']},{s['config']},763,{100*s['rejected_units']/3831:.1f},{s['retained_tuples']},{s['empty_units']},{s['attempts']/3831:.2f},{minutes:.2f},{s['retained_tuples']/minutes:.1f}")
