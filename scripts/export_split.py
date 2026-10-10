"""Export every complete raw run of one dataset split into results/MODEL/runs/SPLIT.CONFIG.asqp.json.

results/manifest.json lists the runs of both splits; this rewrites the entries of SPLIT and keeps the others.

Runs are ordered as in models.txt, then full, no_retry, no_tags. A raw file only counts as complete
when it covers every document of the dataset (checkpoints are written mid-run); incomplete or
missing runs are listed and skipped.
"""
import argparse,hashlib,json,pathlib,sys
root=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'scripts'))
from export_result import export

p=argparse.ArgumentParser();p.add_argument('split',help='e.g. train or test');p.add_argument('raw_dir');p.add_argument('dataset');a=p.parse_args()
raw=open(a.dataset,'rb').read();sha=hashlib.sha256(raw).hexdigest();n=len(json.loads(raw))
out=root/'results';mf=out/'manifest.json'
manifest=[e for e in (json.loads(mf.read_text()) if mf.exists() else []) if e['split']!=a.split];new=0
for m in (root/'models.txt').read_text().split():
 for cfg in ['full','no_retry','no_tags']:
  name=f"{m.replace('/','__')}.{cfg}.asqp.json";src=pathlib.Path(a.raw_dir)/name
  s=json.load(open(src))['summary'] if src.exists() else None
  if not s or s['documents']!=n:print('skip',name,'missing' if not s else f"{s['documents']}/{n} documents");continue
  assert s['dataset_sha256']==sha and (s['model'],s['config'])==(m,cfg),name
  dst=out/m.replace('/','__')/'runs'/f"{a.split}.{cfg}.asqp.json";dst.parent.mkdir(parents=True,exist_ok=True);s=export(src,dst)
  manifest.append({'file':str(dst.relative_to(root)),'sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'split':a.split,**s});new+=1
order={m:i for i,m in enumerate((root/'models.txt').read_text().split())}
manifest.sort(key=lambda e:(order.get(e['model'],len(order)),e['model'],e['split']!='train',['full','no_retry','no_tags'].index(e['config'])))
mf.write_text(json.dumps(manifest,indent=2)+'\n')
print(f"{new} {a.split} runs -> {out}/MODEL/runs")
