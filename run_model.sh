#!/usr/bin/env bash
set -euo pipefail
[[ $# -ge 3 ]] || { echo "usage: $0 MODEL GPU PORT [LIMIT]" >&2; exit 2; }
MODEL=$1; GPU=$2; PORT=$3; LIMIT=${4:-0}
ROOT=$(cd "$(dirname "$0")" && pwd); SAFE_MODEL=${MODEL//\//__}
CONFIGS=${CONFIGS:-full,no_retry,no_tags}
RESULT_DIR=${RESULT_DIR:-"$ROOT/private_runs"}
LOG_DIR="$RESULT_DIR/logs"; mkdir -p "$LOG_DIR" "$RESULT_DIR"
SERVER_LOG="$LOG_DIR/${SAFE_MODEL}.server.log"; RUN_LOG="$LOG_DIR/${SAFE_MODEL}.experiment.log"
[[ "$MODEL" =~ ^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$ ]] || { echo "unsafe model id" >&2; exit 2; }
cleanup(){ if [[ -n "${SERVER_PID:-}" ]] && kill -0 "$SERVER_PID" 2>/dev/null;then kill -TERM "$SERVER_PID" 2>/dev/null||true;wait "$SERVER_PID" 2>/dev/null||true;fi; }
trap cleanup EXIT INT TERM
CUDA_VISIBLE_DEVICES="$GPU" VLLM_USE_FLASHINFER_SAMPLER=0 "${VLLM:-vllm}" serve "$MODEL" \
 --host 127.0.0.1 --port "$PORT" --max-model-len "${MAX_MODEL_LEN:-8192}" --gpu-memory-utilization "${GPU_MEM_UTIL:-0.95}" --max-num-seqs "${MAX_NUM_SEQS:-256}" >"$SERVER_LOG" 2>&1 &
SERVER_PID=$!
for _ in $(seq 1 360);do
 curl -fsS "http://127.0.0.1:$PORT/health" >/dev/null&&break
 kill -0 "$SERVER_PID" 2>/dev/null||{ echo "vLLM failed; see $SERVER_LOG" >&2;exit 1; }
 sleep 5
done
curl -fsS "http://127.0.0.1:$PORT/health" >/dev/null
IFS=',' read -ra CFGS <<<"$CONFIGS"
DATA="${ASQP_DATA:?Set ASQP_DATA}"
for CONFIG in "${CFGS[@]}";do
 OUT="$RESULT_DIR/${SAFE_MODEL}.${CONFIG}.asqp.json"
 if [[ "$CONFIG" == full ]];then RUNNER="$ROOT/run_experiment.py";EXTRA=()
 else RUNNER="$ROOT/run_ablation_direct_v3.py";EXTRA=(--config "$CONFIG");fi
 "${PYTHON:-python3}" "$RUNNER" "${EXTRA[@]}" --dataset "$DATA" --model "$MODEL" \
  --base-url "http://127.0.0.1:$PORT/v1" --output "$OUT" --limit "$LIMIT" --concurrency "${CONCURRENCY:-200}" 2>&1|tee -a "$RUN_LOG"
done
cleanup;trap - EXIT INT TERM
# Cache removal is restricted to this model's directory.
if [[ "${KEEP_MODEL_CACHE:-0}" != 1 ]]; then
 "${PYTHON:-python3}" - "$MODEL" <<'PYTHON'
import os,pathlib,shutil,sys
base=pathlib.Path(os.environ.get('HF_HUB_CACHE',str(pathlib.Path(os.environ.get('HF_HOME',str(pathlib.Path.home()/'.cache/huggingface')))/'hub')))
target=base/('models--'+sys.argv[1].replace('/','--'))
if target.is_dir() and not target.is_symlink():shutil.rmtree(target)
PYTHON
fi
