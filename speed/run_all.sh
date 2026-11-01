#!/bin/bash
# 11-02 JMB_HARD 测速链（RTX 4070 单卡，逐模型顺序跑）：每个模型 smoke → preds（bs1 全量 3,015，延迟 + 读法）→ speed2（512 张最大吞吐）。
# ar_exp_fp32 只跑 preds（与 fp16 逐框比对）。单个模型失败不停链，记入 logs/run_all.status。全部结束写 logs/RUN_ALL_DONE。
# 用法：bash run_all.sh [模型 ...]（缺省 = 全部）
cd /data/jmb_bench/code
export BENCH_ROOT=/data/jmb_bench BENCH_THREADS=8 HF_HUB_OFFLINE=1 PYTHONUNBUFFERED=1
P=/data/jmb_bench/env/bin/python; L=/data/jmb_bench/logs
echo $$ > $L/run_all.pid; rm -f $L/RUN_ALL_DONE
MODELS=("$@")
[ ${#MODELS[@]} -eq 0 ] && MODELS=(ar_exp ar_exp_fp32 nar_small nar_small_r16 nar_small_distil cpt_flex charspot_small charspot_nano preview
                                    hayai_nova_p256 hayai_nova_p384 hayai_nova_p512 hayai_v2 baberu manga_ocr paddleocr_vl_manga)
for m in "${MODELS[@]}"; do
  extra=()
  if [ "$m" = paddleocr_vl_manga ]; then
    export PYTHONPATH=/data/jmb_bench/tf455 PADDLE_DIR=/data/jmb_bench/models/paddleocr_vl_manga PADDLE_DTYPE=fp16
  else
    unset PYTHONPATH PADDLE_DIR PADDLE_DTYPE
  fi
  steps=(smoke preds speed2); [ "$m" = ar_exp_fp32 ] && steps=(preds)
  for s in "${steps[@]}"; do
    t0=$(date +%s)
    if $P jmb_adapters.py $s $m > $L/${m}_${s}.log 2>&1; then st=ok; else st=FAIL; fi
    echo "$(date '+%F %T') $m $s $st $(( $(date +%s) - t0 ))s" >> $L/run_all.status
    [ $st = FAIL ] && break
  done
done
date > $L/RUN_ALL_DONE
