# offset_aware

Reproducibility package for structured sentiment annotation: eight models, SSA and ASQP, three configurations, 48 completed runs.

## Contents

- Annotation code, sentence segmentation, whitespace token indexing, validation, four synthetic demonstrations and Portuguese task guides.
- All final generated annotations in `results/*.json.gz`: predicted terms, labels, character offsets, unit outcomes, attempts and timing. `results/manifest.json` provides checksums and summaries.
- Software and hardware details in `environment.json`.
- Semantic audit of the retained annotations in `audit/`: the audit guide, the report with one table per model, per-run rates and per-tuple verdicts, produced by `scripts/semantic_audit_sample.py` and `scripts/semantic_audit_report.py`.
- The manuscript source in `paper/paper.tex`, including the semantic audit appendix generated as `audit/semantic_audit_appendix.tex`.

Original review texts and reference annotations are excluded, except the ten reviews reproduced verbatim in the manuscript appendix *Texts Used in Human Inspection* (`paper/paper.tex`), which also contain names of people mentioned in them. Model-generated terms remain verbatim and can reproduce source fragments and entity names; they are not guaranteed to be de-identified. Document IDs and source checksums allow alignment with separately acquired datasets. Private reviewer comments, databases, credentials, server logs and model weights are not included.

## Reproduce tables without GPU or original datasets

```bash
python3 scripts/summarize.py > summary.csv
```

The command checks file hashes, completeness and counts. Rejection includes parsing/schema/span failures, not just refusals. Retained output is not semantic accuracy. Raw failed generations were not fully archived, so metadata does not reconstruct every attempt.

## Run the experiments

Use Python 3.12 with a compatible NVIDIA/CUDA environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-server.txt
export SSA_DATA=/absolute/path/to/ssa.json
export ASQP_DATA=/absolute/path/to/asqp.json
./run_model.sh Qwen/Qwen3.8-27B 0 8030
```

Acquire the original datasets separately. Each file is a JSON object keyed by document ID; each value contains `text` and optionally `annotations`. Original references are not required for generation or sent as answers. Each original file contains 763 reviews and produces 3,831 processing units. Expected file hashes are in the manifest. Preserve all whitespace and Unicode. Dataset acquisition is not automated in this package.

Repeat for the IDs in `models.txt`. Two model commands can run concurrently on different GPU indices and ports. The recorded hardware used two 96-GB RTX PRO 6000 Blackwell GPUs, with one model per GPU in BF16. Smaller hardware may require deviations. `PYTHON` and `VLLM` select executables from separate environments if needed.

The launcher runs `full`, `no_retry`, and `no_tags` on both tasks. Full and direct offsets permit three retries after an initial request; no-retry permits one attempt. Defaults: context 8,192, concurrency 200, at most 256 scheduled sequences, temperature 0, top-p 0.8, top-k 20, presence penalty 1.0, output cap 768, thinking disabled. The exact model cache is removed after successful completion unless `KEEP_MODEL_CACHE=1`.

New runner checkpoints contain source text and are stored in ignored `private_runs/`. **Never commit these raw files directly.** Export a sanitized copy first:

```bash
python3 scripts/export_result.py private_runs/MODEL.full.ssa.json exported.json.gz
```

To use an already-running OpenAI-compatible server:

```bash
python3 run_experiment.py --task ssa --dataset "$SSA_DATA" --model Qwen/Qwen3.8-27B --base-url http://127.0.0.1:8030/v1 --output private_runs/full.ssa.json --concurrency 200
python3 run_ablation_direct_v3.py --config no_tags --task ssa --dataset "$SSA_DATA" --model Qwen/Qwen3.8-27B --base-url http://127.0.0.1:8030/v1 --output private_runs/direct.ssa.json --concurrency 200
```

The historical runner filename is retained; the published direct-offset condition uses no token-ID cues. Release changes remove reference-agreement scoring, allow absent reference labels, restrict the CLI to published ablations and make server paths portable. Inference functions, guides, token mapping and validation are unchanged from the executed code.

## Audit offsets with original data obtained separately

```bash
python3 scripts/audit_offsets.py results/Qwen__Qwen3.8-27B.full.ssa.json.gz "$SSA_DATA"
```

Offsets count Python Unicode characters, not UTF-8 bytes or model subwords, with an exclusive end. Attached punctuation is preserved: `competente.Tem` is one indivisible whitespace token. Exact source alignment does not guarantee a semantically appropriate span.

## Semantic audit

Structural validation checks offsets, not meaning. `audit/GUIA_AUDITORIA_SEMANTICA.md` (Portuguese) defines how each retained tuple is judged as a guest opinion about the hotel: error codes per field, including named places and landmarks used as aspects, and valid, partial and invalid verdicts. Up to 50 tuples per run are sampled (seed 20260930); `audit/RELATORIO_AUDITORIA_SEMANTICA.md` and `audit/por_modelo/` report rates with 95% intervals per model, task and configuration.

**The verdicts were produced by LLM judges following the guide, not by human annotators.** Treat the rates as model-assisted estimates until a human-reviewed subsample is reported (guide, section 7).

The sample contains original text and is not published. With the datasets obtained separately:

```bash
python3 scripts/semantic_audit_sample.py --ssa "$SSA_DATA" --asqp "$ASQP_DATA"
# judge private_runs/semantic_audit/chunks/*.jsonl into private_runs/semantic_audit/judgments/
python3 scripts/semantic_audit_report.py
```

`paper/paper.tex` compiles with the ACL style files and the bibliography `custom.bib`, which are not included.

## Limits and anonymity

Model weight commit hashes were not archived: model revisions were resolved from `main`. Exact weight-level replication is therefore not guaranteed. GPU kernels and concurrent scheduling can affect results. Timings are single-run wall times excluding startup, not individual request latency. The published environment records observed versions rather than a fully locked container image.

No author names, institutional machine names, absolute home paths or private Git history are included. Public GitHub ownership and activity still identify the account: **this repository URL is not an anonymous submission artifact**. Use an independently anonymized distribution channel for double-blind review. Generated terms can also identify source entities; removal of complete originals is not a privacy guarantee.
