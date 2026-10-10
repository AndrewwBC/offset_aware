# offset_aware

Reproducibility package for aspect sentiment quad prediction (ASQP) annotation: the twelve models in `models.txt`, three configurations and two splits (train and test), 72 runs. Runs are committed as they finish; the split manifests list the completed set.

## Contents

- Annotation code, sentence segmentation, word-only token indexing, validation, four synthetic demonstrations and the Portuguese annotation guide.
- All generated annotations in `results/train/` and `results/test/` (`*.json.gz`): predicted terms, labels, character offsets, unit outcomes, attempts and timing. Each split's `manifest.json` provides checksums and summaries.
- Software and hardware details in `environment.json`.
- Semantic audit of the annotations retained under `full` in `audit/`: the audit guide, the report with one table of all models, per-run rates and per-tuple verdicts, produced by `scripts/semantic_audit_sample.py` and `scripts/semantic_audit_report.py`.
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
export ASQP_DATA=/absolute/path/to/asqp.json
./run_model.sh Qwen/Qwen3.8-27B 0 8030
```

Acquire the original datasets separately. Each file is a JSON object keyed by document ID; each value contains `text` and optionally `annotations`. Original references are not required for generation or sent as answers. The training file used for the published runs contains 763 reviews (730 annotated) and produces 3,831 processing units. Its hash is in the manifest. Preserve all whitespace and Unicode. Dataset acquisition is not automated in this package.

The test split comes as two subtask CSVs that annotate disjoint reviews: `ate_asqp.csv` (253 reviews with quadruples) and `ote_acd.csv` (253 reviews with aspects, opinion terms and categories, but no polarity). `scripts/build_test_dataset.py` merges them into one JSON file in the training format, with null polarity for the `ote_acd` reviews and each opinion term placed at its occurrence closest to the aspect in the same sentence (a rule that reproduces 3,431 of the 3,436 training offsets). The result has 506 reviews and 2,773 processing units; with the 730 annotated training reviews this gives 1,236.

```bash
python3 scripts/build_test_dataset.py /path/to/test_full/subtasks --out datasets/test.json
```

Repeat for the IDs in `models.txt`. Two model commands can run concurrently on different GPU indices and ports. The recorded hardware used two 96-GB RTX PRO 6000 Blackwell GPUs, with one model per GPU in BF16, for the 27B to 32B models and Gemma 3 12B; the five smallest models (Qwen2.5-0.5B, 1.5B, 3B and 7B, Gemma 3 4B) ran on one 32-GB RTX 5090, also in BF16 with the same software versions. Timings are therefore comparable only within the same GPU type; the first RTX PRO 6000 was also capped at 400 W, against 600 W for the second. Smaller hardware may require deviations. `PYTHON` and `VLLM` select executables from separate environments if needed.

The launcher runs `full`, `no_retry`, and `no_tags` on ASQP. Full and direct offsets permit three retries after an initial request; no-retry permits one attempt. Defaults: context 8,192, GPU memory utilization 0.95, concurrency 200, at most 256 scheduled sequences, temperature 0, top-p 0.8, top-k 20, presence penalty 1.0, output cap 768, thinking disabled. The exact model cache is removed after successful completion unless `KEEP_MODEL_CACHE=1`.

New runner checkpoints contain source text and are stored in ignored `private_runs/`. **Never commit these raw files directly.** Export a sanitized copy first:

```bash
python3 scripts/export_result.py private_runs/MODEL.full.asqp.json exported.json.gz
```

To export every complete run of a split into `results/SPLIT/` and rewrite its manifest (incomplete checkpoints are skipped):

```bash
python3 scripts/export_split.py train private_runs/v2_train "$ASQP_DATA"
```

To use an already-running OpenAI-compatible server:

```bash
python3 run_experiment.py --dataset "$ASQP_DATA" --model Qwen/Qwen3.8-27B --base-url http://127.0.0.1:8030/v1 --output private_runs/full.asqp.json --concurrency 200
python3 run_ablation_direct_v3.py --config no_tags --dataset "$ASQP_DATA" --model Qwen/Qwen3.8-27B --base-url http://127.0.0.1:8030/v1 --output private_runs/direct.asqp.json --concurrency 200
```

The historical runner filename is retained; the published direct-offset condition uses no token-ID cues. Release changes remove reference-agreement scoring, allow absent reference labels, restrict the CLI to published ablations and make server paths portable. The earlier results, produced at commit `3dbafa2` and removed from `results/`, used a tokenizer that indexed whitespace-separated tokens, so punctuation stayed attached to words (`más.`). That tokenizer could represent only 65% of the reference spans exactly, since reference spans never start or end with punctuation. The current code indexes only words (`\w+`) in the indexed-token conditions: punctuation stays in the text and offsets but has no token ID, so a selected span can contain inner punctuation (`wi-fi`, `R$ 50`) but can never start or end with it. 99.5% of reference spans are representable; the annotation guide, shared by all three configurations, also instructs the model not to include a period, comma, question mark, exclamation mark or other punctuation at the start or end of a span. Validation does not reject such spans. All runs in `results/train/` and `results/test/` were produced with this code.

## Agreement with the human annotations and tuple review

`scripts/tuple_review_export.py` compares every run (all three configs) with the human annotations. Each predicted tuple has four elements (category, aspect, expression, polarity) and takes the level of the human tuple in the same review that shares the most elements with it: identical (all four equal), similar (two or three) or different (at most one). Aspect and expression are equal when their offsets are; a human tuple without polarity (test reviews from `ote_acd.csv`) counts its polarity as equal. The 33 training reviews without human annotations are left out. `audit/tuple_review_counts.csv` records, per run, the identical, similar and different tuples. The per-level tuple files of each model reproduce human annotations and stay in `private_runs/human_comparison/`. The script also samples 10 similar and 10 different tuples per model from its `full` runs (seed 20261009) into a batch for the Gasann/anotai tuple-review page, where reviewers judge, blind to the model, whether each annotation makes sense; the batch contains review sentences and stays in `private_runs/`.

```bash
python3 scripts/tuple_review_export.py --train "$ASQP_DATA" --test datasets/test.json
```

`scripts/build_model_datasets.py` writes the annotations of every complete run as a dataset in the format of the human one, `datasets/models/MODEL/CONFIG/{train,test}.json` (same reviews and order, with the model's tuples as annotations). These files contain review text and stay in the ignored `datasets/` directory.

```bash
python3 scripts/build_model_datasets.py --train "$ASQP_DATA" --test datasets/test.json
```

## Audit offsets with original data obtained separately

```bash
python3 scripts/audit_offsets.py results/train/Qwen__Qwen3.8-27B.full.asqp.json.gz "$ASQP_DATA"
```

Offsets count Python Unicode characters, not UTF-8 bytes or model subwords, with an exclusive end. Only words receive token IDs, numbered consecutively: `competente.Tem` is two tokens (`competente`, `Tem`). Offsets come from each word's character position, so punctuation between selected words is kept in the span, while edge punctuation cannot be selected. In the direct-offset condition the guide's instruction is the only safeguard against edge punctuation. Exact source alignment does not guarantee a semantically appropriate span.

## Semantic audit

Structural validation checks offsets, not meaning. `audit/GUIA_AUDITORIA_SEMANTICA.md` (Portuguese) defines how each retained tuple is judged as a guest opinion about the hotel: error codes per field, including named places and landmarks used as aspects, and valid, partial and invalid verdicts. The audit covers the `full` configuration (indexed tokens with retries): 100 retained tuples are sampled per model (seed 20260930), and `audit/RELATORIO_AUDITORIA_SEMANTICA.md` reports the valid, in-domain and out-of-domain rates of all models in one table, with 95% intervals.

**The verdicts were produced by LLM judges following the guide, not by human annotators.** Treat the rates as model-assisted estimates until a human-reviewed subsample is reported (guide, section 7).

The sample contains original text and is not published. With the datasets obtained separately:

```bash
python3 scripts/semantic_audit_sample.py --asqp "$ASQP_DATA" --configs full --per-run 100
# judge private_runs/semantic_audit/chunks/*.jsonl into private_runs/semantic_audit/judgments/
python3 scripts/semantic_audit_report.py
```

`paper/paper.tex` compiles with the ACL style files and the bibliography `custom.bib`, which are not included.

## Limits and anonymity

Model weight commit hashes were not archived: model revisions were resolved from `main`. Exact weight-level replication is therefore not guaranteed. GPU kernels and concurrent scheduling can affect results. Timings are single-run wall times excluding startup, not individual request latency. The published environment records observed versions rather than a fully locked container image.

No author names, institutional machine names, absolute home paths or private Git history are included. Public GitHub ownership and activity still identify the account: **this repository URL is not an anonymous submission artifact**. Use an independently anonymized distribution channel for double-blind review. Generated terms can also identify source entities; removal of complete originals is not a privacy guarantee.
