import argparse,gzip,hashlib,json
p=argparse.ArgumentParser();p.add_argument('result');p.add_argument('dataset');a=p.parse_args()
d=json.loads(gzip.decompress(open(a.result,'rb').read()));raw=open(a.dataset,'rb').read();assert hashlib.sha256(raw).hexdigest()==d['summary']['dataset_sha256'],'Dataset bytes differ'
source=json.loads(raw);n=0
for r in d['records']:
 text=source[r['id']]['text'];assert hashlib.sha256(text.encode()).hexdigest()==r['source_sha256']
 for annotation in r['predictions']:
  for field in ['holder','aspect','sentiment']:
   span=annotation.get(field)
   if span is None:continue
   if field=='holder' and span['location']==[]:assert span['term']=='null';continue
   b,e=span['location'];assert type(b)==type(e)==int and 0<=b<e<=len(text) and text[b:e]==span['term'];n+=1
print('Verified retained spans:',n)
