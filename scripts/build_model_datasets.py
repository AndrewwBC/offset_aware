"""Write the annotations of each complete run as a dataset in the format of the human one.

For every model in models.txt, split and config whose raw run covers all documents, writes
results/MODEL/complete/SPLIT.CONFIG.json: {doc_id: {"text": ..., "annotations": [...]}}, with the model's
tuples (category, aspect, sentiment, polarity) in place of the human annotations and the documents in the
order of the original split.
"""
import argparse,json,pathlib
root=pathlib.Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser()
p.add_argument('--train',default='datasets/train.json');p.add_argument('--test',default='datasets/test.json')
p.add_argument('--raw',default='private_runs/v2_{split}');p.add_argument('--out',default='results')
p.add_argument('--configs',default='full,no_retry,no_tags');a=p.parse_args()

written=0
for split in ['train','test']:
 source=json.load(open(root/getattr(a,split)))
 for model in (root/'models.txt').read_text().split():
  for cfg in a.configs.split(','):
   f=root/a.raw.format(split=split)/f"{model.replace('/','__')}.{cfg}.asqp.json"
   d=json.load(open(f)) if f.exists() else None
   if not d or d['summary']['documents']!=len(source):continue
   rec={r['id']:r for r in d['records']};assert rec.keys()==source.keys(),f
   data={}
   for k,v in source.items():
    assert rec[k]['text']==v['text'],(f,k)
    data[k]={'text':v['text'],'annotations':[{x:t[x] for x in ['category','aspect','sentiment','polarity']} for t in rec[k]['predictions']]}
   out=root/a.out/model.replace('/','__')/'complete'/f'{split}.{cfg}.json';out.parent.mkdir(parents=True,exist_ok=True)
   out.write_text(json.dumps(data,ensure_ascii=False,indent=4),encoding='utf-8');written+=1
   print(f"{model:28} {cfg:8} {split:5} {len(data)} reviews, {sum(len(x['annotations']) for x in data.values())} tuples")
print(f"{written} datasets -> {a.out}/MODEL/complete")
