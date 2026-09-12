#!/usr/bin/env python3
from __future__ import annotations
import argparse,asyncio,hashlib,json,time
from pathlib import Path
from openai import AsyncOpenAI
from run_experiment import ASQP_CATEGORIES,POLARITIES,annotate_sentence,annotation_guide,few_shot_messages,parse_json,score_documents,split_sentences
CONFIGS={"no_retry","no_tags"}

def raw_prompt(task):
    common="""Voce e especialista em analise de sentimento estruturada em portugues.
Extraia TODAS as opinioes e responda somente JSON {\"annotations\":[...]}.
Cada span usa location=[inicio,fim], caracteres relativos ao TEXTO,
com inicio inclusivo e fim exclusivo; term deve ser exatamente TEXTO[inicio:fim].
Use o menor span suficiente. polarity: POS, NEG ou NEU. sentiment.type: explicit ou implicit.
"""
    if task=="ssa":
        task_prompt="""Campos: holder, aspect, sentiment, polarity. Holder e o emissor;
se ausente use {"term":"null","location":[]}. Aspect e sentiment nunca sao vazios."""
    else:
        task_prompt="""Campos: category, aspect, sentiment, polarity. category e uma de:
structure, service, location, general, price, others. Aspect e sentiment nunca sao vazios."""
    return common+task_prompt+"\n\nGUIA DE ANOTACAO:\n"+annotation_guide(task).replace("token_ids","location")

def normalize_raw(payload,text,start,task,enforce):
    rows=payload.get("annotations")
    if not isinstance(rows,list): return [],["annotations precisa ser lista"]
    resolved,errors=[],[]; fields=("holder","aspect","sentiment") if task=="ssa" else ("aspect","sentiment")
    for i,row in enumerate(rows):
        if not isinstance(row,dict): errors.append(f"anotacao {i}: deve ser objeto"); continue
        out,bad={"polarity":row.get("polarity")},[]
        if row.get("polarity") not in POLARITIES: bad.append("polarity invalida")
        if task=="asqp":
            out["category"]=row.get("category")
            if row.get("category") not in ASQP_CATEGORIES: bad.append("category invalida")
        for field in fields:
            span=row.get(field)
            if not isinstance(span,dict):
                out[field]={"term":"","location":[]}; bad.append(f"{field} deve ser objeto"); continue
            term,loc=span.get("term"),span.get("location")
            if task=="ssa" and field=="holder" and (term=="null" or loc==[]):
                out[field]={"term":"null","location":[]}
                if term!="null" or loc!=[]: bad.append("holder nulo inconsistente")
                continue
            valid=isinstance(loc,list) and len(loc)==2 and all(isinstance(x,int) for x in loc)
            if valid:
                begin,end=loc; absolute=[start+begin,start+end]
                exact=text[begin:end] if 0<=begin<=end<=len(text) else None
            else: begin=end=0; absolute=loc if isinstance(loc,list) else []; exact=None
            out[field]={"term":term,"location":absolute}
            if field=="sentiment": out[field]["type"]=span.get("type","explicit")
            if not valid or begin>=end or exact!=term: bad.append(f"{field} location/term invalido")
        errors.extend(f"anotacao {i}: {e}" for e in bad)
        if not enforce or not bad: resolved.append(out)
    return resolved,errors

async def annotate_raw(client,model,task,text,start,retries,enforce):
    msgs=[{"role":"system","content":raw_prompt(task)}]+few_shot_messages(task,False)+[{"role":"user","content":"FRASE:\n"+text}]
    meta={"attempts":0,"rejected":False,"parse_errors":0,"validation_errors":0}
    for _ in range(retries+1):
        meta["attempts"]+=1; raw=""
        try:
            response=await client.chat.completions.create(model=model,messages=msgs,temperature=0.0,
                top_p=0.8,presence_penalty=1.0,max_tokens=768,
                extra_body={"top_k":20,"chat_template_kwargs":{"enable_thinking":False}})
            raw=response.choices[0].message.content or ""
            resolved,errors=normalize_raw(parse_json(raw),text,start,task,enforce)
            if not enforce or not errors: return resolved,meta
            meta["validation_errors"]+=len(errors); feedback="Corrija:\n- "+"\n- ".join(errors[:20])
        except Exception as exc:
            meta["parse_errors"]+=1; feedback=f"Resposta invalida ({type(exc).__name__}: {exc}). Retorne JSON."
        msgs.extend([{"role":"assistant","content":raw},{"role":"user","content":feedback}])
    meta["rejected"]=True; return [],meta

async def main(args):
    source,output=Path(args.dataset),Path(args.output); items=list(json.loads(source.read_text()).items())
    if args.limit: items=items[:args.limit]
    output.parent.mkdir(parents=True,exist_ok=True); existing={}
    if output.exists() and not args.overwrite: existing={x["id"]:x for x in json.loads(output.read_text())["records"]}
    client=AsyncOpenAI(base_url=args.base_url,api_key="local",timeout=180)
    sem,lock,records=asyncio.Semaphore(args.concurrency),asyncio.Lock(),dict(existing); started=time.time()
    split=args.config not in {"no_sentence_split","no_components"}; tags=args.config not in {"no_tags","no_components"}
    retries=0 if args.config in {"no_retry","no_components"} else 3; enforce=args.config!="no_components"
    async def process(doc_id,item):
        if doc_id in records:return
        spans=split_sentences(item["text"]) if split else [(item["text"],0,len(item["text"]))]
        async def unit(text,begin,end):
            async with sem:
                if tags: anns,meta=await annotate_sentence(client,args.model,args.task,text,begin,retries)
                else: anns,meta=await annotate_raw(client,args.model,args.task,text,begin,retries,enforce)
            return {"text":text,"location":[begin,end],"annotations":anns,**meta}
        units=await asyncio.gather(*(unit(*span) for span in spans))
        rec={"id":doc_id,"text":item["text"],"gold":item.get("annotations", []),"predictions":[a for u in units for a in u["annotations"]],"sentences":units}
        async with lock:
            records[doc_id]=rec
            if len(records)%10==0 or len(records)==len(items):
                ordered=[records[k] for k,_ in items if k in records]; summary=score_documents(ordered,args.task)
                summary.update({"model":args.model,"task":args.task,"config":args.config,"documents":len(ordered),
                    "units":sum(len(x["sentences"]) for x in ordered),"rejected_units":sum(u["rejected"] for x in ordered for u in x["sentences"]),
                    "retry_attempts":sum(max(0,u["attempts"]-1) for x in ordered for u in x["sentences"]),
                    "elapsed_seconds":time.time()-started,"dataset_sha256":hashlib.sha256(source.read_bytes()).hexdigest()})
                tmp=output.with_suffix(output.suffix+".tmp");tmp.write_text(json.dumps({"summary":summary,"records":ordered},ensure_ascii=False,indent=2))
                tmp.replace(output);print(json.dumps(summary),flush=True)
    await asyncio.gather(*(process(k,v) for k,v in items));await client.close()

def args():
    p=argparse.ArgumentParser();p.add_argument("--config",choices=sorted(CONFIGS),required=True)
    p.add_argument("--task",choices=("ssa","asqp"),required=True);p.add_argument("--dataset",required=True);p.add_argument("--model",required=True)
    p.add_argument("--base-url",required=True);p.add_argument("--output",required=True);p.add_argument("--limit",type=int,default=0)
    p.add_argument("--concurrency",type=int,default=16);p.add_argument("--overwrite",action="store_true");return p.parse_args()
if __name__=="__main__":asyncio.run(main(args()))
