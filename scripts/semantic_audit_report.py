"""Aggregate semantic-audit verdicts (audit/GUIA_AUDITORIA_SEMANTICA.md) into rates per run, model and configuration.

Outputs contain item IDs, verdicts and error codes only; no original text.
"""
import argparse,collections,csv,gzip,json,math,pathlib,re

p=argparse.ArgumentParser()
p.add_argument('--sample',default='private_runs/semantic_audit');p.add_argument('--results',default='results')
p.add_argument('--out',default='audit');a=p.parse_args()
sample=pathlib.Path(a.sample);out=pathlib.Path(a.out);out.mkdir(exist_ok=True)
S=json.load(open(sample/'sample_index.json'));manifest={pathlib.Path(e['file']).name:e for e in json.load(open(pathlib.Path(a.results)/'manifest.json'))}
MODELS=[l.strip() for l in open('models.txt') if l.strip()];CONFIGS=['full','no_retry','no_tags'];TASKS=['ssa','asqp']
INVALID={'O1','O2','A1','A2','A3','S1'}

verdict=lambda codes:'VALIDA' if not codes else 'INVALIDA' if INVALID&set(codes) else 'PARCIAL'
# optional second pass on out-of-domain codes under the narrowed location rule (guide, section 7)
task_of={json.loads(l)['item_id']:json.loads(l)['task'] for l in open(sample/'items.jsonl')}
rev={}
if (sample/'ood_decisions.jsonl').exists():
 rev={d['item_id']:d for d in map(json.loads,open(sample/'ood_decisions.jsonl'))}
primary={};secondary={};revised=0
for f in sorted((sample/'judgments').glob('chunk_*.jsonl')):
 c=int(f.stem.split('_')[1])
 for l in open(f):
  j=json.loads(l);j['codes']=sorted(set(j['codes']))
  assert j['verdict']==verdict(j['codes']),(f.name,j)
  d=rev.get(j['item_id'])
  if d and {'A2','A3'}&set(j['codes']):
   codes=set(j['codes'])-{'A2','A3'}
   if d['decision']=='keep':codes.add(d['code'])
   elif d['add_c1'] and task_of[j['item_id']]=='asqp':codes.add('C1')
   j['codes']=sorted(codes);j['verdict']=verdict(j['codes']);revised+=1
  if S['primary'].get(j['item_id'])==c:primary[j['item_id']]=j
  elif S['secondary'].get(j['item_id'])==c:secondary[j['item_id']]=j
missing=set(S['primary'])-set(primary);assert not missing,f'{len(missing)} items without verdict'

def flags(j,task):
 c=set(j['codes'])
 return {'valid':j['verdict']=='VALIDA','domain':j['verdict']!='INVALIDA','out_of_domain':bool(c&{'A2','A3'}),
         'geo':'A2' in c,'other_entity':'A3' in c,'no_opinion':bool(c&{'O1','O2','S1'}),'aspect_ok':not c&{'A1','A2','A3','A4'},
         'sentiment_ok':not c&{'S1','S2','S3','O1','O2'},'polarity_ok':'P1' not in c,
         'category_ok':'C1' not in c if task=='asqp' else None,'holder_ok':'H1' not in c if task=='ssa' else None}
METRICS=['valid','domain','out_of_domain','geo','other_entity','no_opinion','aspect_ok','sentiment_ok','polarity_ok','category_ok','holder_ok']

def wilson(k,n,z=1.96):
 if n==0:return (math.nan,math.nan)
 ph=k/n;d=1+z*z/n;c=(ph+z*z/(2*n))/d;h=z*math.sqrt(ph*(1-ph)/n+z*z/(4*n*n))/d
 return (max(0,c-h),min(1,c+h))

runs=collections.defaultdict(list)
run_codes=collections.defaultdict(list)
for r in S['index']:runs[r['file']].append(flags(primary[r['item_id']],r['task']));run_codes[r['file']].append(set(primary[r['item_id']]['codes']))
rows=[]
for fname,e in manifest.items():
 fl=runs.get(fname,[]);N=e['retained_tuples'];row={'file':fname,'model':e['model'],'task':e['task'],'config':e['config'],'retained_tuples':N,'sampled':len(fl)}
 for m in METRICS:
  v=[x[m] for x in fl if x[m] is not None];row[m+'_k']=sum(v);row[m+'_n']=len(v)
  row[m]=sum(v)/len(v) if v else math.nan;row[m+'_lo'],row[m+'_hi']=wilson(sum(v),len(v)) if v else (math.nan,math.nan)
 row['est_valid_tuples']=round(N*row['valid']) if fl else 0;row['est_domain_tuples']=round(N*row['domain']) if fl else 0
 rows.append(row)

def stratified(group,m):
 # population estimate over runs weighted by retained tuples, with finite-population correction
 g=[r for r in group if r[m+'_n']>0];N=sum(r['retained_tuples'] for r in g)
 if not N:return (math.nan,math.nan,math.nan,0)
 est=sum(r['retained_tuples']*r[m] for r in g)/N
 var=sum((r['retained_tuples']/N)**2*r[m]*(1-r[m])/r[m+'_n']*(1-r[m+'_n']/r['retained_tuples']) for r in g if r[m+'_n']>1)
 se=math.sqrt(var);return (est,max(0,est-1.96*se),min(1,est+1.96*se),N)

# lexical screen over every retained tuple
GEO=re.compile(r"^(rua|r\.|av\.?|avenida|pra[çc]a|largo|travessa|alameda|estrada|rodovia|beco|museu|igreja|catedral|bas[íi]lica|mosteiro|convento|capela|castelo|torre|ponte|pal[áa]cio|praia|parque|jardim|esta[çc][ãa]o|aeroporto|bairro|cidade|shopping|elevador de santa|mercado|feira|miradouro|mirante|monumento|est[áa]dio|teatro|avenidas?)\b",re.I)
NOT_NAMES={'metro','metrô','metropolitano','estação','centro','rua','praça','bairro','avenida','ipod','iphone','wifi','wi-fi','tv'}
FUNC={'o','a','os','as','um','uma','de','do','da','dos','das','e','que','muito','bem','tão','tao','mais','bastante','super','é','foi','era','não','nao','já','ja','isso','este','esta','isto'}
lex={};geo_terms=collections.Counter();geo_by_model=collections.defaultdict(collections.Counter)
for fname,e in manifest.items():
 d=json.loads(gzip.decompress((pathlib.Path(a.results)/fname).read_bytes()));g=gen=f=0
 for r in d['records']:
  for t in r['predictions']:
   raw=t['aspect']['term'].strip(' .,;:!?()"\'«»');term=raw.lower()
   if GEO.match(term):
    # named place: a capitalised word after the marker ("Rua Augusta", "Torre Eiffel")
    if any(w[:1].isupper() and w.lower().strip(',.') not in NOT_NAMES for w in raw.split()[1:]):g+=1;geo_terms[raw]+=1;geo_by_model[e['model']][raw]+=1
    else:gen+=1
   if term in FUNC:f+=1
 lex[fname]=(g,gen,f)
for r in rows:r['lex_geo'],r['lex_generic'],r['lex_func']=lex[r['file']]

with open(out/'semantic_audit_runs.csv','w',newline='') as fh:
 w=csv.DictWriter(fh,fieldnames=list(rows[0]));w.writeheader()
 for r in sorted(rows,key=lambda r:(MODELS.index(r['model']),CONFIGS.index(r['config']),TASKS.index(r['task']))):w.writerow({k:(round(v,4) if isinstance(v,float) else v) for k,v in r.items()})
with open(out/'semantic_audit_verdicts.csv','w',newline='') as fh:
 w=csv.writer(fh);w.writerow(['item_id','file','doc','tuple_index','verdict','codes'])
 for r in S['index']:j=primary[r['item_id']];w.writerow([r['item_id'],r['file'],r['doc'],r['tuple_index'],j['verdict'],' '.join(j['codes'])])

# agreement between the two judges on double-judged items
pairs=[(primary[i]['verdict'],secondary[i]['verdict']) for i in secondary if i in primary]
labs=['VALIDA','PARCIAL','INVALIDA'];n=len(pairs);po=sum(x==y for x,y in pairs)/n if n else math.nan
pe=sum((sum(x==l for x,_ in pairs)/n)*(sum(y==l for _,y in pairs)/n) for l in labs) if n else math.nan
kappa=(po-pe)/(1-pe) if n and pe<1 else math.nan
ood=[(bool({'A2','A3'}&set(primary[i]['codes'])),bool({'A2','A3'}&set(secondary[i]['codes']))) for i in secondary if i in primary]

pct=lambda x:'—' if x!=x else f'{100*x:.1f}'.replace('.',',')
ci=lambda e,lo,hi:'—' if e!=e else f'{pct(e)} [{100*lo:.0f}–{100*hi:.0f}]'
num=lambda x:f'{x:,}'.replace(',','.')
short=lambda m:m.split('/')[-1]
L=['# Relatório da auditoria semântica','',
 'Gerado por `scripts/semantic_audit_report.py` seguindo `audit/GUIA_AUDITORIA_SEMANTICA.md`.',
 f"Amostra: {len(S['index'])} tuplas sorteadas (até {S['per_run']} por run, semente {S['seed']}), {len(primary)} itens únicos julgados."+(f" Segunda passada da regra de localização: {len(rev)} itens revisados ({sum(d['decision']=='drop' for d in rev.values())} passaram a entorno aceito)." if rev else ''),
 'Percentuais com IC de 95%: Wilson por run; estimativa estratificada ponderada pelas tuplas retidas nos agregados.','',
 '**Validade estrita**: tupla correta em todos os campos. **Validade de domínio**: opinião real sobre o hotel, talvez com algum campo a corrigir. **Fora do domínio**: aspecto é rua, monumento, cidade, outro estabelecimento etc. (`A2`/`A3`).','']
L+=['## Visão geral','','| Recorte | Tuplas retidas | Validade estrita (%) | Validade de domínio (%) | Fora do domínio (%) | Sem opinião (%) |','|---|---:|---:|---:|---:|---:|']
def agg_line(name,group):
 v=stratified(group,'valid');d=stratified(group,'domain');o=stratified(group,'out_of_domain');s=stratified(group,'no_opinion')
 return f'| {name} | {num(v[3])} | {ci(*v[:3])} | {ci(*d[:3])} | {ci(*o[:3])} | {ci(*s[:3])} |'
L.append(agg_line('Todos os runs',rows))
for t in TASKS:L.append(agg_line(t.upper(),[r for r in rows if r['task']==t]))
for c in CONFIGS:L.append(agg_line(f'`{c}`',[r for r in rows if r['config']==c]))
CODES=['A1','A2','A3','A4','O1','O2','S1','S2','S3','C1','P1','H1','D1']
def code_rate(group,code):
 # stratified estimate of the share of retained tuples carrying `code`
 g=[r for r in group if run_codes.get(r['file'])];N=sum(r['retained_tuples'] for r in g)
 return sum(r['retained_tuples']*sum(code in c for c in run_codes[r['file']])/len(run_codes[r['file']]) for r in g)/N if N else math.nan
of_model=lambda m:[r for r in rows if r['model']==m]
L+=['','## Resumo por modelo (todas as tarefas e configurações)','','Detalhes de cada modelo em `audit/por_modelo/`.','',
 '| Modelo | Tuplas retidas | Amostradas | Válidas estimadas | Validade estrita (%) | Validade de domínio (%) | Fora do domínio (%) | Sem opinião (%) |','|---|---:|---:|---:|---:|---:|---:|---:|']
for m in MODELS:
 g=of_model(m);v,d,o,so=(stratified(g,k) for k in ['valid','domain','out_of_domain','no_opinion'])
 L.append(f"| {short(m)} | {num(sum(r['retained_tuples'] for r in g))} | {sum(r['sampled'] for r in g)} | {num(sum(r['est_valid_tuples'] for r in g))} | {ci(*v[:3])} | {ci(*d[:3])} | {ci(*o[:3])} | {ci(*so[:3])} |")
COLS=['valid','domain','geo','other_entity','no_opinion']
cell=lambda r,k:'—' if not r['sampled'] else f'{pct(r[k])} (censo)' if r['sampled']==r['retained_tuples'] else ci(r[k],r[k+'_lo'],r[k+'_hi'])
def model_table(m):
 T=['| Tarefa | Config | Tuplas retidas | Julgadas | Válidas estimadas | Validade estrita (%) | Validade de domínio (%) | Lugar nomeado `A2` (%) | Outra entidade `A3` (%) | Sem opinião (%) |','|---|---|---:|---:|---:|---:|---:|---:|---:|---:|']
 for t in TASKS:
  for c in CONFIGS:
   r=next(x for x in rows if x['model']==m and x['task']==t and x['config']==c)
   T.append(f"| {t.upper()} | `{c}` | {num(r['retained_tuples'])} | {r['sampled']} | {num(r['est_valid_tuples'])} | "+' | '.join(cell(r,k) for k in COLS)+' |')
 g=of_model(m)
 T.append(f"| **Total** | | **{num(sum(r['retained_tuples'] for r in g))}** | **{sum(r['sampled'] for r in g)}** | **{num(sum(r['est_valid_tuples'] for r in g))}** | "+' | '.join(f'**{ci(*stratified(g,k)[:3])}**' for k in COLS)+' |')
 return T
L+=['','## Tabela por modelo','','Uma tabela por modelo: linhas por tarefa e configuração, IC de 95% entre colchetes, “censo” quando o run foi julgado por inteiro. O total pondera cada run pelas suas tuplas retidas.']
for m in MODELS:L+=['',f'### {m}','']+model_table(m)
L+=['','## Erros por modelo (% estimado das tuplas retidas)','','| Modelo | '+' | '.join(f'`{c}`' for c in CODES)+' |','|---|'+'---:|'*len(CODES)]
for m in MODELS:L.append(f'| {short(m)} | '+' | '.join(pct(code_rate(of_model(m),c)) for c in CODES)+' |')
L+=['','Percentuais sobre todas as tuplas do modelo (SSA + ASQP). `H1` só existe em SSA e `C1` só em ASQP; a taxa por tarefa está em `audit/por_modelo/`. Uma tupla pode ter mais de um código.']
L+=['','## Por modelo e configuração (SSA + ASQP)','','| Modelo | Config | Tuplas retidas | Válidas estimadas | Validade estrita (%) | Validade de domínio (%) | Fora do domínio (%) |','|---|---|---:|---:|---:|---:|---:|']
for m in MODELS:
 for c in CONFIGS:
  g=[r for r in rows if r['model']==m and r['config']==c];v=stratified(g,'valid');d=stratified(g,'domain');o=stratified(g,'out_of_domain')
  L.append(f"| {short(m)} | `{c}` | {num(sum(r['retained_tuples'] for r in g))} | {num(sum(r['est_valid_tuples'] for r in g))} | {ci(*v[:3])} | {ci(*d[:3])} | {ci(*o[:3])} |")
L+=['','## Correção por campo (todos os runs, estratificado)','','| Campo | SSA (%) | ASQP (%) |','|---|---:|---:|']
for m,name in [('aspect_ok','Aspecto correto'),('sentiment_ok','Expressão de opinião correta'),('category_ok','Categoria correta'),('polarity_ok','Polaridade correta'),('holder_ok','Holder correto'),('geo','Aspecto geográfico (`A2`)')]:
 L.append(f"| {name} | {ci(*stratified([r for r in rows if r['task']=='ssa'],m)[:3])} | {ci(*stratified([r for r in rows if r['task']=='asqp'],m)[:3])} |")
codes=collections.Counter(c for r in S['index'] for c in primary[r['item_id']]['codes'])
L+=['','## Frequência dos códigos de erro na amostra','','| Código | Ocorrências |','|---|---:|']+[f'| `{k}` | {v} |' for k,v in codes.most_common()]
L+=['','## Concordância entre juízes','',f'{n} itens julgados duas vezes. Concordância bruta no veredito: {pct(po)}%; kappa de Cohen (3 classes): {f'{kappa:.2f}'.replace('.',',')}.' if n else 'Sem itens duplicados.',
 f'Concordância na marcação de fora do domínio: {pct(sum(x==y for x,y in ood)/len(ood))}%.' if ood else '','',
 '## Triagem lexical sobre todas as tuplas','','Limite inferior determinístico (seção 8 do guia): lugar nomeado como aspecto (marcador geográfico + nome próprio), entorno genérico (aceito) e aspecto que é só palavra funcional ou intensificador.','',
 '| Modelo | Config | Tarefa | Tuplas | Lugar nomeado (`A2`) | Entorno genérico (aceito) | Aspecto funcional (`A1`) |','|---|---|---|---:|---:|---:|---:|']
for r in sorted(rows,key=lambda r:(MODELS.index(r['model']),CONFIGS.index(r['config']),TASKS.index(r['task']))):
 if r['retained_tuples']:L.append(f"| {short(r['model'])} | `{r['config']}` | {r['task']} | {num(r['retained_tuples'])} | {r['lex_geo']} ({pct(r['lex_geo']/r['retained_tuples'])}%) | {r['lex_generic']} ({pct(r['lex_generic']/r['retained_tuples'])}%) | {r['lex_func']} ({pct(r['lex_func']/r['retained_tuples'])}%) |")
tg=sum(r['lex_geo'] for r in rows);tt=sum(r['retained_tuples'] for r in rows)
L+=['',f'Total: {num(tg)} de {num(tt)} tuplas ({pct(tg/tt)}%) têm um lugar nomeado como aspecto. Termos mais frequentes (gerados pelos modelos): '+', '.join(f'“{k}” ({v})' for k,v in geo_terms.most_common(15))+'.','',
 '## Limites','','- Os vereditos foram emitidos por juízes LLM seguindo o guia; antes de citar estas taxas como avaliação humana, revise uma subamostra conforme a seção 7 do guia.',
 '- As taxas medem precisão semântica das tuplas retidas, não cobertura.','- Runs com até 50 tuplas foram julgados por inteiro: o intervalo degenerado (ex.: [83–83]) indica censo, sem erro amostral, mas ainda sujeito ao erro dos juízes. Runs pequenos têm pouca informação; ver `semantic_audit_runs.csv`.','']
(out/'RELATORIO_AUDITORIA_SEMANTICA.md').write_text('\n'.join(L))

CODE_NAMES={'A1':'aspecto não é alvo','A2':'lugar nomeado como aspecto','A3':'entidade fora do domínio','A4':'aspecto não pareado com a opinião','O1':'sem avaliação','O2':'tupla alucinada','S1':'expressão não avaliativa','S2':'expressão incompleta','S3':'expressão excessiva','C1':'categoria errada','P1':'polaridade errada','H1':'holder errado','D1':'duplicata'}
(out/'por_modelo').mkdir(exist_ok=True)
for m in MODELS:
 g=of_model(m);v,d,o,so=(stratified(g,k) for k in ['valid','domain','out_of_domain','no_opinion'])
 M=[f'# Auditoria semântica: {m}','',f"Gerado por `scripts/semantic_audit_report.py` seguindo `audit/GUIA_AUDITORIA_SEMANTICA.md`. Visão comparativa em `audit/RELATORIO_AUDITORIA_SEMANTICA.md`.",'',
  f"**{num(sum(r['retained_tuples'] for r in g))} tuplas retidas** nos 6 runs; {sum(r['sampled'] for r in g)} julgadas. Estimativa de **{num(sum(r['est_valid_tuples'] for r in g))} válidas** sem correção e **{num(sum(r['est_domain_tuples'] for r in g))}** opiniões reais sobre o hotel.",'',
  '| Métrica (todas as tarefas e configurações) | % [IC 95%] |','|---|---:|',f'| Validade estrita | {ci(*v[:3])} |',f'| Validade de domínio | {ci(*d[:3])} |',f'| Fora do domínio (`A2`/`A3`) | {ci(*o[:3])} |',f'| Sem opinião (`O1`/`O2`/`S1`) | {ci(*so[:3])} |','',
  '## Por tarefa e configuração','']+model_table(m)
 M+=['','## Correção por campo','','| Campo | SSA (%) | ASQP (%) |','|---|---:|---:|']
 for k,name in [('aspect_ok','Aspecto correto'),('sentiment_ok','Expressão de opinião correta'),('category_ok','Categoria correta'),('polarity_ok','Polaridade correta'),('holder_ok','Holder correto')]:
  M.append(f"| {name} | {ci(*stratified([r for r in g if r['task']=='ssa'],k)[:3])} | {ci(*stratified([r for r in g if r['task']=='asqp'],k)[:3])} |")
 M+=['','## Erros (% estimado das tuplas retidas)','','| Código | Significado | SSA (%) | ASQP (%) |','|---|---|---:|---:|']
 for c in CODES:
  a_,b_=code_rate([r for r in g if r['task']=='ssa'],c),code_rate([r for r in g if r['task']=='asqp'],c)
  if (a_ or 0)>0 or (b_ or 0)>0:M.append(f'| `{c}` | {CODE_NAMES[c]} | {pct(a_)} | {pct(b_)} |')
 lg=sum(r['lex_geo'] for r in g);lt=sum(r['retained_tuples'] for r in g)
 M+=['','## Triagem lexical (todas as tuplas do modelo)','',f"Lugar nomeado como aspecto: {num(lg)} de {num(lt)} tuplas ({pct(lg/lt) if lt else '—'}%)."+(' Termos mais frequentes: '+', '.join(f'“{k}” ({v})' for k,v in geo_by_model[m].most_common(10))+'.' if geo_by_model[m] else ''),
  f"Aspecto funcional ou intensificador: {num(sum(r['lex_func'] for r in g))}. Entorno genérico (aceito): {num(sum(r['lex_generic'] for r in g))}.",'',
  '## Limites','','- Vereditos de juízes LLM; ver a seção 7 do guia antes de citar como avaliação humana.','- Runs com até 50 tuplas foram julgados por inteiro e aparecem como “censo”: não há erro amostral, mas há o erro dos juízes.','- Os percentuais agregados ponderam cada run pelas suas tuplas retidas.','']
 (out/'por_modelo'/(m.replace('/','__')+'.md')).write_text('\n'.join(M))
print('\n'.join(L[:40]))

# LaTeX appendix for the paper: one table per model, English, paper naming and condition order
PAPER_NAMES={'Qwen/Qwen2.5-0.5B-Instruct':'Qwen2.5-0.5B','Qwen/Qwen2.5-1.5B-Instruct':'Qwen2.5-1.5B','Qwen/Qwen2.5-3B-Instruct':'Qwen2.5-3B','Qwen/Qwen2.5-7B-Instruct':'Qwen2.5-7B',
 'unsloth/gemma-3-4b-it':'Gemma 3 4B','unsloth/gemma-3-12b-it':'Gemma 3 12B','Qwen/Qwen3.8-27B':'Qwen3.8-27B','google/gemma-4-31B-it':'Gemma 4 31B'}
PAPER_ORDER=['Qwen/Qwen2.5-0.5B-Instruct','Qwen/Qwen2.5-1.5B-Instruct','Qwen/Qwen2.5-3B-Instruct','Qwen/Qwen2.5-7B-Instruct','unsloth/gemma-3-4b-it','unsloth/gemma-3-12b-it','Qwen/Qwen3.8-27B','google/gemma-4-31B-it']
PAPER_CONFIGS=[('full','Full'),('no_tags','$-$tokens'),('no_retry','$-$retry')]
en=lambda x:f'{100*x:.1f}';enum=lambda x:f'{x:,}'
def tcell(e,lo,hi,census=False):
 if e!=e:return '--'
 return en(e)+'$^\\dagger$' if census else f'{en(e)} {{\\scriptsize[{100*lo:.0f}--{100*hi:.0f}]}}'
def run_row(label,r):
 if not r['sampled']:return f"{label} & 0 & 0 & 0 & -- & -- & -- & -- & -- \\\\"
 cen=r['sampled']==r['retained_tuples']
 return f"{label} & {enum(r['retained_tuples'])} & {r['sampled']} & {enum(r['est_valid_tuples'])} & "+' & '.join(tcell(r[k],r[k+'_lo'],r[k+'_hi'],cen) for k in COLS)+' \\\\'
ov={k:stratified(rows,k) for k in ['valid','domain','geo','other_entity','out_of_domain','no_opinion']}
X=['% Generated by scripts/semantic_audit_report.py from the semantic audit (audit/GUIA_AUDITORIA_SEMANTICA.md). Do not edit by hand.',
 '\\section{Semantic Audit of Retained Annotations}','\\label{app:semantic_audit}',
 'Structural validation guarantees that every retained span matches its source substring, not that the tuple is meaningful. '
 'We therefore estimate, for each model, the share of retained tuples that a hotel manager would accept as a guest opinion about the hotel or the stay. '
 f"For each of the {sum(1 for r in rows if r['sampled'])} runs with retained tuples we draw up to {S['per_run']} tuples uniformly without replacement (seed {S['seed']}); runs with fewer tuples are judged completely. "
 f"This yields {enum(len(S['index']))} sampled tuples and {enum(len(primary))} unique items, since identical tuples in different runs are judged once. "
 'Each tuple is judged in the context of its sentence and the neighboring sentences, following a written guide with error codes for the aspect, opinion expression, category (ASQP), polarity and holder (SSA).','',
 'A tuple is \\emph{invalid} when it contains no evaluation, when its aspect is not a target (a function word, an evaluative word or a whole clause), when its aspect is a named place or landmark (a street name, a monument, a city), when its aspect is another out-of-domain entity (another establishment, the guest, the weather, a booking platform), or when its expression is not evaluative. '
 'It is \\emph{partial} when it records an in-domain opinion but has a wrong category, polarity or holder, a mispaired aspect, or an incomplete or excessive expression; otherwise it is \\emph{valid}. '
 'Generic surroundings that describe the hotel\'s location, such as proximity to the metro or a safe neighborhood, count as in-domain location opinions.','',
 f"The judgments were produced by LLM judges (Claude Opus 5.5) following the guide, not by human annotators. "
 f"{n} items were judged twice without the judges' knowledge: raw agreement on the three-way verdict is {po*100:.1f}\\% (Cohen's $\\kappa={kappa:.2f}$). Because both judges are the same model, this measures consistency rather than validity. "
 +(f"A second pass re-examined the {len(rev)} out-of-domain codes under the location rule above and reclassified {sum(d['decision']=='drop' for d in rev.values())} of them as accepted surroundings. " if rev else '')+
 'The rates should be checked against a human-reviewed subsample before they are read as human evaluation.','',
 f"Across all {enum(sum(r['retained_tuples'] for r in rows))} retained tuples, an estimated {en(ov['valid'][0])}\\% are valid and {en(ov['domain'][0])}\\% record an in-domain opinion. "
 f"Named places or landmarks as aspects account for {en(ov['geo'][0])}\\%, other out-of-domain entities for {en(ov['other_entity'][0])}\\%, and tuples without an opinion for {en(ov['no_opinion'][0])}\\%.",'',
 'Tables~\\ref{tab:audit-'+PAPER_NAMES[PAPER_ORDER[0]].lower().replace(' ','').replace('.','')+'}--\\ref{tab:audit-'+PAPER_NAMES[PAPER_ORDER[-1]].lower().replace(' ','').replace('.','')+'} report one table per model. '
 '\\emph{Strict} is the share of valid tuples; \\emph{Domain} adds partial tuples; \\emph{Named place} and \\emph{Other entity} are the two out-of-domain codes; \\emph{No opinion} covers tuples without an evaluation or with a non-evaluative expression. '
 'Rates are percentages of retained tuples; brackets give 95\\% Wilson intervals; $^\\dagger$ marks runs judged completely. \\emph{Est.\\ valid} multiplies the strict rate by the retained tuples. '
 f"Totals weight each run by its retained tuples. With {S['per_run']} judged tuples, a run's interval spans roughly $\\pm$13 points, so differences between conditions of the same model are often within the margin.",'']
for m in PAPER_ORDER:
 slug=PAPER_NAMES[m].lower().replace(' ','').replace('.','');g=of_model(m)
 X+=['\\begin{table}[!ht]','\\centering\\footnotesize','\\setlength{\\tabcolsep}{4pt}','\\begin{tabular}{lrrrrrrrr}','\\toprule',
  'Condition & Retained & Judged & Est.\\ valid & Strict & Domain & Named place & Other entity & No opinion \\\\','\\midrule']
 for t in TASKS:
  X.append(f'\\multicolumn{{9}}{{l}}{{\\textbf{{{t.upper()}}}}} \\\\')
  for c,label in PAPER_CONFIGS:X.append(run_row(label,next(x for x in g if x['task']==t and x['config']==c)))
  X.append('\\midrule')
 X.append(f"Total & {enum(sum(r['retained_tuples'] for r in g))} & {sum(r['sampled'] for r in g)} & {enum(sum(r['est_valid_tuples'] for r in g))} & "+' & '.join(tcell(*stratified(g,k)[:3]) for k in COLS)+' \\\\')
 X+=['\\bottomrule','\\end{tabular}',f'\\caption{{Semantic audit of {PAPER_NAMES[m]}: estimated validity of retained tuples (\\%) by task and condition.}}',f'\\label{{tab:audit-{slug}}}','\\end{table}','']
(out/'semantic_audit_appendix.tex').write_text('\n'.join(X))
