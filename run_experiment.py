#!/usr/bin/env python3
"""Run the paper's offset-aware annotation pipeline against SSA or ASQP gold data."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import re
import time
from collections import Counter
from pathlib import Path
from typing import Any

from openai import AsyncOpenAI


POLARITIES = {"POS", "NEG", "NEU"}
ASQP_CATEGORIES = {"structure", "service", "location", "general", "price", "others"}
ABBREVIATIONS = {
    "sr.", "sra.", "srta.", "dr.", "dra.", "prof.", "av.", "etc.", "ex.",
    "aprox.", "obs.", "p.ex.", "st.", "mr.", "mrs.", "e.g.", "i.e.",
}
GUIDE_DIR = Path(__file__).resolve().parent / "prompts"


def annotation_guide(task: str) -> str:
    """Load the semantic annotation guide appended to each system prompt."""
    return (GUIDE_DIR / f"{task}_annotation_guide.md").read_text(encoding="utf-8").strip()



def split_sentences(text: str) -> list[tuple[str, int, int]]:
    """Return abbreviation-aware sentence spans without changing source bytes."""
    spans: list[tuple[str, int, int]] = []
    start = 0
    for match in re.finditer(r"[.!?]+(?=\s+|$)", text):
        candidate = text[start : match.end()]
        last = candidate.rstrip().split()[-1].lower() if candidate.strip() else ""
        if last in ABBREVIATIONS or re.fullmatch(r"[a-zá-ú]\.", last, re.I):
            continue
        end = match.end()
        left = start
        while left < end and text[left].isspace():
            left += 1
        if left < end:
            spans.append((text[left:end], left, end))
        start = end
    left = start
    while left < len(text) and text[left].isspace():
        left += 1
    if left < len(text):
        spans.append((text[left:], left, len(text)))
    return spans or [(text, 0, len(text))]


def token_map(sentence: str) -> list[dict[str, Any]]:
    return [
        {"id": i, "token": m.group(), "start": m.start(), "end": m.end()}
        for i, m in enumerate(re.finditer(r"\S+", sentence))
    ]


def system_prompt(task: str) -> str:
    common = """Você é especialista em análise de sentimento estruturada em português.
Você receberá uma frase e TAGS de tokens indexados. Extraia TODAS as opiniões.
Responda somente um objeto JSON {\"annotations\": [...]}.
Use apenas token_ids existentes, únicos, crescentes e contíguos. O campo term deve ser
exatamente o trecho formado do primeiro ao último token, incluindo pontuação quando ela
faz parte do token. Use o menor span semanticamente suficiente. Nunca invente texto.
aspect e sentiment devem ter ao menos um token. polarity deve ser POS, NEG ou NEU.
sentiment.type deve ser explicit ou implicit; use explicit sempre que houver expressão
avaliativa textual. Se não houver opinião, retorne {\"annotations\": []}.
"""
    if task == "ssa":
        task_prompt = """
Cada anotação tem holder, aspect, sentiment e polarity. Holder é quem expressa a opinião;
se não estiver expresso, use {\"term\":\"null\",\"token_ids\":[]}.
Formato: {\"holder\":{\"term\":str,\"token_ids\":[int]},
\"aspect\":{\"term\":str,\"token_ids\":[int]},
\"sentiment\":{\"term\":str,\"token_ids\":[int],\"type\":\"explicit\"},
\"polarity\":\"POS\"}.
Não confunda sujeito sintático com holder: holder precisa ser o emissor da avaliação.
"""
    else:
        task_prompt = """
Cada anotação tem category, aspect, sentiment e polarity. category deve ser exatamente uma
de: structure, service, location, general, price, others.
Formato: {\"category\":\"structure\",
\"aspect\":{\"term\":str,\"token_ids\":[int]},
\"sentiment\":{\"term\":str,\"token_ids\":[int],\"type\":\"explicit\"},
\"polarity\":\"POS\"}.
"""
    return common + task_prompt + "\nGUIA DE ANOTAÇÃO:\n" + annotation_guide(task)



FEW_SHOT_EXAMPLES = [
    ("O hotel e excelente.", [
        {"holder_ids": [], "aspect_ids": [1], "sentiment_ids": [3], "polarity": "POS", "category": "general"}
    ]),
    ("Eu achei o quarto pequeno.", [
        {"holder_ids": [0], "aspect_ids": [3], "sentiment_ids": [4], "polarity": "NEG", "category": "structure"}
    ]),
    ("A localizacao e otima, mas o preco e alto.", [
        {"holder_ids": [], "aspect_ids": [1], "sentiment_ids": [3], "polarity": "POS", "category": "location"},
        {"holder_ids": [], "aspect_ids": [6], "sentiment_ids": [8], "polarity": "NEG", "category": "price"}
    ]),
    ("Nos consideramos o atendimento impecavel.", [
        {"holder_ids": [0], "aspect_ids": [3], "sentiment_ids": [4], "polarity": "POS", "category": "service"}
    ]),
]


def few_shot_messages(task: str, use_tags: bool) -> list[dict[str, str]]:
    messages: list[dict[str, str]] = []
    for text, specs in FEW_SHOT_EXAMPLES:
        tokens = token_map(text)
        annotations = []
        for spec in specs:
            def span(ids: list[int], sentiment: bool = False, holder: bool = False) -> dict[str, Any]:
                if holder and not ids:
                    return {"term": "null", "token_ids" if use_tags else "location": []}
                begin, end = tokens[ids[0]]["start"], tokens[ids[-1]]["end"]
                result: dict[str, Any] = {"term": text[begin:end]}
                result["token_ids" if use_tags else "location"] = ids if use_tags else [begin, end]
                if sentiment:
                    result["type"] = "explicit"
                return result
            row = {
                "aspect": span(spec["aspect_ids"]),
                "sentiment": span(spec["sentiment_ids"], sentiment=True),
                "polarity": spec["polarity"],
            }
            if task == "ssa":
                row["holder"] = span(spec["holder_ids"], holder=True)
            else:
                row["category"] = spec["category"]
            annotations.append(row)
        user = "FRASE:\n" + text
        if use_tags:
            user += "\n\nTAGS:\n" + json.dumps(tokens, ensure_ascii=False)
        messages.extend([
            {"role": "user", "content": user},
            {"role": "assistant", "content": json.dumps({"annotations": annotations}, ensure_ascii=False)},
        ])
    return messages

def parse_json(raw: str) -> dict[str, Any]:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.I)
        raw = re.sub(r"\s*```$", "", raw)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        begin, end = raw.find("{"), raw.rfind("}")
        if begin >= 0 and end > begin:
            return json.loads(raw[begin : end + 1])
        raise


def validate_and_resolve(
    payload: dict[str, Any], tokens: list[dict[str, Any]], sentence: str,
    sentence_start: int, task: str,
) -> tuple[list[dict[str, Any]], list[str]]:
    errors: list[str] = []
    rows = payload.get("annotations")
    if not isinstance(rows, list):
        return [], ["annotations precisa ser uma lista"]
    resolved: list[dict[str, Any]] = []
    span_fields = ("holder", "aspect", "sentiment") if task == "ssa" else ("aspect", "sentiment")
    for row_i, row in enumerate(rows):
        if not isinstance(row, dict):
            errors.append(f"anotação {row_i}: deve ser objeto")
            continue
        out: dict[str, Any] = {}
        polarity = row.get("polarity")
        if polarity not in POLARITIES:
            errors.append(f"anotação {row_i}: polarity inválida {polarity!r}")
        out["polarity"] = polarity
        if task == "asqp":
            category = row.get("category")
            if category not in ASQP_CATEGORIES:
                errors.append(f"anotação {row_i}: category inválida {category!r}")
            out["category"] = category
        bad_row = False
        for field in span_fields:
            span = row.get(field)
            if not isinstance(span, dict):
                errors.append(f"anotação {row_i}: {field} deve ser objeto")
                bad_row = True
                continue
            ids = span.get("token_ids")
            term = span.get("term")
            if task == "ssa" and field == "holder" and (ids == [] or term == "null"):
                if ids != [] or term != "null":
                    errors.append(f"anotação {row_i}: holder nulo deve usar term null e token_ids []")
                    bad_row = True
                out[field] = {"term": "null", "location": []}
                continue
            if not isinstance(ids, list) or not ids or not all(isinstance(x, int) for x in ids):
                errors.append(f"anotação {row_i}: {field}.token_ids inválido")
                bad_row = True
                continue
            if ids != list(range(ids[0], ids[-1] + 1)) or ids[0] < 0 or ids[-1] >= len(tokens):
                errors.append(f"anotação {row_i}: {field}.token_ids precisa ser contíguo e existir")
                bad_row = True
                continue
            begin, end = tokens[ids[0]]["start"], tokens[ids[-1]]["end"]
            exact = sentence[begin:end]
            if term != exact:
                errors.append(f"anotação {row_i}: {field}.term deveria ser {exact!r}, recebido {term!r}")
                bad_row = True
            out[field] = {
                "term": exact,
                "location": [sentence_start + begin, sentence_start + end],
            }
            if field == "sentiment":
                sentiment_type = span.get("type", "explicit")
                if sentiment_type not in {"explicit", "implicit"}:
                    errors.append(f"anotação {row_i}: sentiment.type inválido")
                    bad_row = True
                out[field]["type"] = sentiment_type
        if not bad_row:
            resolved.append(out)
    return resolved, errors


async def annotate_sentence(client: AsyncOpenAI, model: str, task: str, sentence: str,
                            sentence_start: int, retries: int) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    tokens = token_map(sentence)
    user = "FRASE:\n" + sentence + "\n\nTAGS:\n" + json.dumps(tokens, ensure_ascii=False)
    messages = ([{"role": "system", "content": system_prompt(task)}] + few_shot_messages(task, True) + [{"role": "user", "content": user}])
    meta = {"attempts": 0, "rejected": False, "parse_errors": 0, "validation_errors": 0}
    for attempt in range(retries + 1):
        meta["attempts"] += 1
        try:
            response = await client.chat.completions.create(
                model=model, messages=messages, temperature=0.0, top_p=0.8,
                presence_penalty=1.0, max_tokens=768,
                extra_body={"top_k": 20, "chat_template_kwargs": {"enable_thinking": False}},
            )
            raw = response.choices[0].message.content or ""
            payload = parse_json(raw)
            resolved, errors = validate_and_resolve(payload, tokens, sentence, sentence_start, task)
            if not errors:
                return resolved, meta
            meta["validation_errors"] += len(errors)
            feedback = "Corrija o JSON. Erros:\n- " + "\n- ".join(errors[:20])
        except Exception as exc:
            meta["parse_errors"] += 1
            raw = locals().get("raw", "")
            feedback = f"A resposta não foi um JSON válido ({type(exc).__name__}: {exc}). Corrija."
        messages.extend([{"role": "assistant", "content": raw}, {"role": "user", "content": feedback}])
    meta["rejected"] = True
    return [], meta


def score_documents(records, task):
    """Summarize retained output; do not score agreement with reference labels."""
    return {"retained_tuples": sum(len(r["predictions"]) for r in records)}


async def main_async(args: argparse.Namespace) -> None:
    dataset = json.loads(Path(args.dataset).read_text(encoding="utf-8"))
    items = list(dataset.items())
    if args.limit:
        items = items[: args.limit]
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    existing: dict[str, dict[str, Any]] = {}
    if output.exists() and not args.overwrite:
        existing = {x["id"]: x for x in json.loads(output.read_text(encoding="utf-8"))["records"]}

    client = AsyncOpenAI(base_url=args.base_url, api_key=args.api_key, timeout=args.timeout)
    semaphore = asyncio.Semaphore(args.concurrency)
    lock = asyncio.Lock()
    records = dict(existing)
    started = time.time()

    async def process(doc_id: str, item: dict[str, Any]) -> None:
        if doc_id in records:
            return
        sentence_outputs = []
        async def one(sentence: str, begin: int, end: int) -> dict[str, Any]:
            async with semaphore:
                anns, meta = await annotate_sentence(client, args.model, args.task, sentence, begin, args.retries)
            return {"text": sentence, "location": [begin, end], "annotations": anns, **meta}
        sentence_outputs = await asyncio.gather(*(one(*span) for span in split_sentences(item["text"])))
        predictions = [ann for sent in sentence_outputs for ann in sent["annotations"]]
        rec = {"id": doc_id, "text": item["text"], "gold": item.get("annotations", []),
               "predictions": predictions, "sentences": sentence_outputs}
        async with lock:
            records[doc_id] = rec
            if len(records) % args.checkpoint_every == 0 or len(records) == len(items):
                ordered = [records[k] for k, _ in items if k in records]
                summary = score_documents(ordered, args.task)
                summary.update({
                    "model": args.model, "task": args.task, "config": "full", "documents": len(ordered),
                    "sentences": sum(len(x["sentences"]) for x in ordered),
                    "rejected_sentences": sum(s["rejected"] for x in ordered for s in x["sentences"]),
                    "retry_attempts": sum(max(0, s["attempts"] - 1) for x in ordered for s in x["sentences"]),
                    "elapsed_seconds": time.time() - started,
                    "dataset_sha256": hashlib.sha256(Path(args.dataset).read_bytes()).hexdigest(),
                })
                temp = output.with_suffix(output.suffix + ".tmp")
                temp.write_text(json.dumps({"summary": summary, "records": ordered}, ensure_ascii=False, indent=2), encoding="utf-8")
                temp.replace(output)
                print(json.dumps(summary, ensure_ascii=False), flush=True)

    await asyncio.gather(*(process(k, v) for k, v in items))
    await client.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", choices=("ssa", "asqp"), required=True)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--base-url", default="http://127.0.0.1:8000/v1")
    parser.add_argument("--api-key", default="local")
    parser.add_argument("--output", required=True)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--concurrency", type=int, default=16)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--checkpoint-every", type=int, default=10)
    parser.add_argument("--timeout", type=float, default=180.0)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    asyncio.run(main_async(parse_args()))
