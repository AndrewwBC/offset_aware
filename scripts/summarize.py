import hashlib,json,pathlib
root=pathlib.Path(__file__).resolve().parents[1]
# documents and processing units of each dataset, by sha256
SIZES={'615335780065212b1e155dddc76ee10c2d338b479966ae47a171d398e1d43daa':(763,3831),
       '4214afea6f51d4f158075aba2caa891ad9184f77f4f4b79bce93094d10114987':(506,2773)}
print('split,model,task,config,documents,rejection_percent,tuples,empty_units,attempts_per_unit,minutes,tuples_per_minute')
f=root/'results'/'manifest.json'
for split in ['train','test']:
 for entry in [e for e in json.loads(f.read_text()) if e['split']==split] if f.exists() else []:
  p=root/entry['file'];assert hashlib.sha256(p.read_bytes()).hexdigest()==entry['sha256']
  d=json.loads(p.read_bytes());s=d['summary'];rows=d['records'];u=[u for r in rows for u in r['units']]
  docs,units=SIZES[s['dataset_sha256']]
  assert len(rows)==s['documents']==docs and len(u)==s['units']==units
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
  print(f"{split},{s['model']},{s['task']},{s['config']},{docs},{100*s['rejected_units']/units:.1f},{s['retained_tuples']},{s['empty_units']},{s['attempts']/units:.2f},{minutes:.2f},{s['retained_tuples']/minutes:.1f}")
