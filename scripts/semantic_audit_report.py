"""Aggregate semantic-audit verdicts (audit/GUIA_AUDITORIA_SEMANTICA.md) into one table of all models.

Outputs contain item IDs, verdicts, error codes and rates only; no original text.
"""
import argparse,collections,csv,gzip,json,math,pathlib,re

p=argparse.ArgumentParser()
p.add_argument('--sample',default='private_runs/semantic_audit');p.add_argument('--results',default='results')
p.add_argument('--out',default='audit');a=p.parse_args()
sample=pathlib.Path(a.sample);out=pathlib.Path(a.out);out.mkdir(exist_ok=True)
S=json.load(open(sample/'sample_index.json'))
# samples drawn before the project dropped SSA also index SSA runs; keep only ASQP
S['index']=[r for r in S['index'] if r['task']=='asqp']
manifest={pathlib.Path(e['file']).name:e for e in json.load(open(pathlib.Path(a.results)/'manifest.json')) if e['task']=='asqp' and e['config'] in S['configs']}
MODELS=['Qwen/Qwen2.5-0.5B-Instruct','Qwen/Qwen2.5-1.5B-Instruct','Qwen/Qwen2.5-3B-Instruct','Qwen/Qwen2.5-7B-Instruct',
 'unsloth/gemma-3-4b-it','unsloth/gemma-3-12b-it','Qwen/Qwen3.8-27B','google/gemma-4-31B-it']
NAMES={'Qwen/Qwen2.5-0.5B-Instruct':'Qwen2.5-0.5B','Qwen/Qwen2.5-1.5B-Instruct':'Qwen2.5-1.5B','Qwen/Qwen2.5-3B-Instruct':'Qwen2.5-3B','Qwen/Qwen2.5-7B-Instruct':'Qwen2.5-7B',
 'unsloth/gemma-3-4b-it':'Gemma 3 4B','unsloth/gemma-3-12b-it':'Gemma 3 12B','Qwen/Qwen3.8-27B':'Qwen3.8-27B','google/gemma-4-31B-it':'Gemma 4 31B'}
INVALID={'O1','O2','A1','A2','A3','S1'}
verdict=lambda codes:'VALIDA' if not codes else 'INVALIDA' if INVALID&set(codes) else 'PARCIAL'

# verdicts: reused from an earlier sample plus new chunks; optional second pass on out-of-domain codes (guide, section 7)
rev={d['item_id']:d for d in map(json.loads,open(sample/'ood_decisions.jsonl'))} if (sample/'ood_decisions.jsonl').exists() else {}
def load(f):
 for l in open(f):
  j=json.loads(l);j['codes']=sorted(set(j['codes']))
  assert j['verdict']==verdict(j['codes']),(f.name,j)
  d=rev.get(j['item_id'])
  if d and {'A2','A3'}&set(j['codes']):
   codes=set(j['codes'])-{'A2','A3'}
   if d['decision']=='keep':codes.add(d['code'])
   elif d['add_c1']:codes.add('C1')
   j['codes']=sorted(codes);j['verdict']=verdict(j['codes'])
  yield j
J=sample/'judgments';primary={};secondary={}
reused=set(S.get('reused',[]))
if (J/'reused.jsonl').exists():primary.update((j['item_id'],j) for j in load(J/'reused.jsonl') if j['item_id'] in reused)
if (J/'reused_secondary.jsonl').exists():secondary.update((j['item_id'],j) for j in load(J/'reused_secondary.jsonl') if j['item_id'] in reused)
for f in sorted(J.glob('chunk_*.jsonl')):
 c=int(f.stem.split('_')[1])
 for j in load(f):
  if S['primary'].get(j['item_id'])==c:primary[j['item_id']]=j
  elif S['secondary'].get(j['item_id'])==c:secondary[j['item_id']]=j
missing={r['item_id'] for r in S['index']}-set(primary);assert not missing,f'{len(missing)} items without verdict'

def flags(j):
 c=set(j['codes'])
 return {'valid':j['verdict']=='VALIDA','domain':j['verdict']!='INVALIDA','out_of_domain':bool(c&{'A2','A3'}),'geo':'A2' in c,
         'no_opinion':bool(c&{'O1','O2','S1'}),'aspect_ok':not c&{'A1','A2','A3','A4'},'sentiment_ok':not c&{'S1','S2','S3','O1','O2'},
         'polarity_ok':'P1' not in c,'category_ok':'C1' not in c}
METRICS=['valid','domain','out_of_domain','geo','no_opinion','aspect_ok','sentiment_ok','polarity_ok','category_ok']
def wilson(k,n,z=1.96):
 ph=k/n;d=1+z*z/n;c=(ph+z*z/(2*n))/d;h=z*math.sqrt(ph*(1-ph)/n+z*z/(4*n*n))/d
 return (max(0,c-h),min(1,c+h))

runs=collections.defaultdict(list)
for r in S['index']:runs[r['file']].append(flags(primary[r['item_id']]))
rows=[]
for fname,e in manifest.items():
 fl=runs[fname];N=e['retained_tuples'];row={'file':fname,'model':e['model'],'task':e['task'],'config':e['config'],'retained_tuples':N,'sampled':len(fl)}
 for m in METRICS:
  v=[x[m] for x in fl if x[m] is not None];row[m+'_n']=len(v);row[m]=sum(v)/len(v) if v else math.nan
  row[m+'_lo'],row[m+'_hi']=wilson(sum(v),len(v)) if v else (math.nan,math.nan)
 row['est_valid_tuples']=round(N*row['valid']) if fl else 0;row['est_domain_tuples']=round(N*row['domain']) if fl else 0
 rows.append(row)
run=lambda m:next(r for r in rows if r['model']==m)

def stratified(group,m):
 # population estimate weighted by retained tuples, with finite-population correction
 g=[r for r in group if r[m+'_n']>0];N=sum(r['retained_tuples'] for r in g)
 if not N:return (math.nan,math.nan,math.nan)
 est=sum(r['retained_tuples']*r[m] for r in g)/N
 se=math.sqrt(sum((r['retained_tuples']/N)**2*r[m]*(1-r[m])/r[m+'_n']*(1-r[m+'_n']/r['retained_tuples']) for r in g if r[m+'_n']>1))
 return (est,max(0,est-1.96*se),min(1,est+1.96*se))

# lexical screen over every retained tuple of the audited runs (guide, section 8)
GEO=re.compile(r"^(rua|r\.|av\.?|avenida|pra[çc]a|largo|travessa|alameda|estrada|rodovia|beco|museu|igreja|catedral|bas[íi]lica|mosteiro|convento|capela|castelo|torre|ponte|pal[áa]cio|praia|parque|jardim|esta[çc][ãa]o|aeroporto|bairro|cidade|shopping|mercado|feira|miradouro|mirante|monumento|est[áa]dio|teatro)\b",re.I)
NOT_NAMES={'metro','metrô','metropolitano','estação','centro','rua','praça','bairro','avenida','ipod','iphone','wifi','wi-fi','tv'}
geo_terms=collections.Counter()
for r in rows:
 d=json.loads(gzip.decompress((pathlib.Path(a.results)/r['file']).read_bytes()));r['lex_geo']=0
 for rec in d['records']:
  for t in rec['predictions']:
   raw=t['aspect']['term'].strip(' .,;:!?()"\'«»')
   if GEO.match(raw.lower()) and any(w[:1].isupper() and w.lower().strip(',.') not in NOT_NAMES for w in raw.split()[1:]):r['lex_geo']+=1;geo_terms[raw]+=1

audited={r['item_id'] for r in S['index']}
pairs=[(primary[i]['verdict'],secondary[i]['verdict']) for i in secondary if i in primary and i in audited];n=len(pairs)
po=sum(x==y for x,y in pairs)/n if n else math.nan
pe=sum((sum(x==l for x,_ in pairs)/n)*(sum(y==l for _,y in pairs)/n) for l in ['VALIDA','PARCIAL','INVALIDA']) if n else math.nan
kappa=(po-pe)/(1-pe) if n and pe<1 else math.nan

order=lambda r:MODELS.index(r['model'])
with open(out/'semantic_audit_runs.csv','w',newline='') as fh:
 w=csv.DictWriter(fh,fieldnames=list(rows[0]));w.writeheader()
 for r in sorted(rows,key=order):w.writerow({k:(round(v,4) if isinstance(v,float) else v) for k,v in r.items()})
with open(out/'semantic_audit_verdicts.csv','w',newline='') as fh:
 w=csv.writer(fh);w.writerow(['item_id','file','doc','tuple_index','verdict','codes'])
 for r in S['index']:j=primary[r['item_id']];w.writerow([r['item_id'],r['file'],r['doc'],r['tuple_index'],j['verdict'],' '.join(j['codes'])])

# Markdown report (Portuguese)
pt=lambda x:'—' if x!=x else f'{100*x:.1f}'.replace('.',',')
ptci=lambda e,lo,hi:'—' if e!=e else f'{pt(e)} [{100*lo:.0f}–{100*hi:.0f}]'
num=lambda x:f'{x:,}'.replace(',','.')
cfg=', '.join(f'`{c}`' for c in S['configs']);tot=sum(r['retained_tuples'] for r in rows)
L=['# Relatório da auditoria semântica','',
 f"Gerado por `scripts/semantic_audit_report.py` seguindo `audit/GUIA_AUDITORIA_SEMANTICA.md`. Configuração auditada: {cfg}.",
 f"Amostra: {num(len(S['index']))} tuplas sorteadas uniformemente, {S['per_run']} por run (semente {S['seed']}), {num(len({r['item_id'] for r in S['index']}))} itens únicos julgados."+(f" Segunda passada da regra de localização em {len(rev)} itens." if rev else ''),
 'Percentuais sobre as tuplas retidas, com IC de 95% (Wilson por run; estimativa estratificada ponderada pelas tuplas retidas nos totais).','',
 '**Válidas**: corretas em todos os campos. **No domínio**: opinião real sobre o hotel, talvez com algum campo a corrigir. **Fora do domínio**: aspecto é lugar nomeado ou monumento (`A2`) ou outra entidade fora do hotel (`A3`).','',
 '## Tabela por modelo','',
 '| Modelo | Retidas | Válidas (%) | No domínio (%) | Fora do domínio (%) | Válidas estimadas |',
 '|---|---:|---:|---:|---:|---:|']
cell=lambda r,k:ptci(r[k],r[k+'_lo'],r[k+'_hi'])
for m in MODELS:
 q_=run(m)
 L.append(f"| {NAMES[m]} | {num(q_['retained_tuples'])} | {cell(q_,'valid')} | {cell(q_,'domain')} | {cell(q_,'out_of_domain')} | {num(q_['est_valid_tuples'])} |")
L.append(f"| **Todos** | **{num(tot)}** | **{ptci(*stratified(rows,'valid'))}** | **{ptci(*stratified(rows,'domain'))}** | **{ptci(*stratified(rows,'out_of_domain'))}** | **{num(sum(r['est_valid_tuples'] for r in rows))}** |")
v=stratified(rows,'valid');d=stratified(rows,'domain');o=stratified(rows,'out_of_domain');g=stratified(rows,'geo');s=stratified(rows,'no_opinion')
L+=['',f"No total, das {num(tot)} tuplas retidas, {ptci(*v)}% são válidas e {ptci(*d)}% estão no domínio. Fora do domínio: {ptci(*o)}%, dos quais lugar nomeado ou monumento como aspecto (`A2`): {ptci(*g)}%. Sem opinião: {ptci(*s)}%.",'',
 '## Correção por campo','','| Campo | Corretos (%) |','|---|---:|']
for k,name in [('aspect_ok','Aspecto correto'),('sentiment_ok','Expressão de opinião correta'),('category_ok','Categoria correta'),('polarity_ok','Polaridade correta')]:
 L.append(f"| {name} | {ptci(*stratified(rows,k))} |")
codes=collections.Counter(c for r in S['index'] for c in primary[r['item_id']]['codes'])
L+=['','## Códigos de erro na amostra','','| Código | Ocorrências |','|---|---:|']+[f'| `{k}` | {c} |' for k,c in codes.most_common()]
tg=sum(r['lex_geo'] for r in rows)
L+=['','## Concordância e triagem lexical','',
 f"{n} itens julgados duas vezes: concordância bruta no veredito de {pt(po)}%, kappa de Cohen (3 classes) de {f'{kappa:.2f}'.replace('.',',')}. Os juízes são o mesmo modelo, então isso mede consistência, não validade." if n else 'Sem itens julgados duas vezes.','',
 f"Triagem determinística sobre todas as {num(tot)} tuplas (seção 8 do guia): {num(tg)} ({pt(tg/tot)}%) têm lugar nomeado como aspecto. Mais frequentes: "+', '.join(f'“{k}” ({c})' for k,c in geo_terms.most_common(10))+'. Contagem por run em `semantic_audit_runs.csv`.','',
 '## Limites','','- Vereditos de juízes LLM seguindo o guia, não de anotadores humanos; revise uma subamostra (seção 7 do guia) antes de citar como avaliação humana.',
 f"- Com {S['per_run']} tuplas por run, cada célula tem margem de cerca de ±10 pontos percentuais.",'- As taxas medem precisão das tuplas retidas, não cobertura.','']
(out/'RELATORIO_AUDITORIA_SEMANTICA.md').write_text('\n'.join(L))

# LaTeX appendix for the paper (English)
en=lambda x:f'{100*x:.1f}';enum=lambda x:f'{x:,}'
tci=lambda e,lo,hi:f'{en(e)} {{\\scriptsize[{100*lo:.0f}--{100*hi:.0f}]}}'
X=['% Generated by scripts/semantic_audit_report.py from the semantic audit (audit/GUIA_AUDITORIA_SEMANTICA.md). Do not edit by hand.',
 '\\section{Semantic Audit of Retained Annotations}','\\label{app:semantic_audit}',
 'Structural validation guarantees that every retained span matches its source substring, not that the tuple is meaningful. '
 'We therefore estimate, for each model under Full, the share of retained tuples that a hotel manager would accept as a guest opinion about the hotel or the stay. '
 f"For each of the {len(rows)} Full runs we draw {S['per_run']} retained tuples uniformly without replacement (seed {S['seed']}), "
 f"giving {enum(len(S['index']))} sampled tuples and {enum(len(audited))} unique items, since identical tuples produced by different models are judged once. "
 'Each tuple is judged in the context of its sentence and the neighboring sentences, following a written guide with error codes for the aspect, opinion expression, category and polarity.','',
 'A tuple is \\emph{invalid} when it contains no evaluation, when its aspect is not a target (a function word, an evaluative word or a whole clause), when its aspect is a named place or landmark (a street name, a monument, a city), when its aspect is another out-of-domain entity (another establishment, the guest, the weather, a booking platform), or when its expression is not evaluative. '
 'It is \\emph{partial} when it records an in-domain opinion but has a wrong category or polarity, a mispaired aspect, or an incomplete or excessive expression; otherwise it is \\emph{valid}. '
 'Generic surroundings that describe the hotel\'s location, such as proximity to the metro or a safe neighborhood, count as in-domain location opinions.','',
 'The judgments were produced by LLM judges (Claude Opus 5.5) following the guide, not by human annotators. '
 +(f"{n} items were judged twice without the judges' knowledge: raw agreement on the three-way verdict is {100*po:.1f}\\% (Cohen's $\\kappa={kappa:.2f}$). Because both judges are the same model, this measures consistency rather than validity. " if n else '')+
 'The rates should be checked against a human-reviewed subsample before they are read as human evaluation.','',
 f"Table~\\ref{{tab:semantic_audit}} reports the results. Across the {enum(tot)} tuples retained under Full, an estimated {en(v[0])}\\% are valid and {en(d[0])}\\% record an in-domain opinion; "
 f"{en(o[0])}\\% have an out-of-domain aspect, {en(g[0])}\\% of them a named place or landmark, and {en(s[0])}\\% contain no opinion. "
 f"With {S['per_run']} judged tuples per model, each rate has a margin of about $\\pm$10 points.",'',
 '\\begin{table}[H]','\\centering\\footnotesize','\\setlength{\\tabcolsep}{4pt}','\\begin{tabular}{lrrrrr}','\\toprule',
 'Model & Retained & Valid & \\shortstack[r]{In-\\\\domain} & \\shortstack[r]{Out-of-\\\\domain} & \\shortstack[r]{Est.\\\\valid} \\\\','\\midrule']
grp=lambda r:f"{enum(r['retained_tuples'])} & {tci(r['valid'],r['valid_lo'],r['valid_hi'])} & {en(r['domain'])} & {en(r['out_of_domain'])} & {enum(r['est_valid_tuples'])}"
for m in MODELS:X.append(f"{NAMES[m]} & {grp(run(m))} \\\\")
X+=['\\midrule',f"All models & {enum(tot)} & {tci(*v)} & {en(d[0])} & {en(o[0])} & {enum(sum(r['est_valid_tuples'] for r in rows))} \\\\",'\\bottomrule','\\end{tabular}',
 f"\\caption{{Semantic audit of the tuples retained under Full ({S['per_run']} judged tuples per model). Rates are percentages of retained tuples; brackets give 95\\% Wilson intervals for the valid rate, and the all-models row weights each model by its retained tuples. \\emph{{In-domain}} counts valid and partial tuples; \\emph{{Est.\\ valid}} multiplies the valid rate by the retained tuples.}}",
 '\\label{tab:semantic_audit}','\\end{table}','']
(out/'semantic_audit_appendix.tex').write_text('\n'.join(X))
print('\n'.join(L[:22]))
