"""11-02 JMB_HARD 测速（用户：开 RTX 4070 测速机，测 15 行）：沿用 Read v1.3 测速脚本（run_eval.py 单张延迟 + 准确率、speed2.py 最大吞吐），
补上 Read 测速时在别的脚本里的发布包适配器：nar-small / R16 / distil（manga-ocr-nar 包 CUDA 后端）、CPT-flex（manga-ocr-CPT 包 CUDA 路径，解码器 fp32）、
charspot-small / nano（各自发布的 CUDA 后端，warmup 后测）、ar-exp（infer.MangaOCR，精度 AREXP_DTYPE，默认 fp16；ar_exp_fp32 = 同一包 fp32，用于逐框比对；batch_size = 调用的张数）。
  BENCH_ROOT=/data/jmb_bench python jmb_adapters.py preds MODEL      → preds/MODEL.jsonl + results/MODEL_preds.json
  BENCH_ROOT=/data/jmb_bench python jmb_adapters.py speed2 MODEL     → results/MODEL_speed2.json
  BENCH_ROOT=/data/jmb_bench python jmb_adapters.py smoke MODEL      → 前 16 框读法与 RIN 前标签对照"""
import os, sys, time
import numpy as np
import torch
MODE, NAME = sys.argv[1], sys.argv[2]
sys.argv = [sys.argv[0], NAME]
import run_eval as RE  # noqa: E402
import speed2 as S2  # noqa: E402
M = RE.MODELS
to_u8 = lambda imgs: [np.asarray(i.convert("RGB")) for i in imgs]

def pkg(name):
    """发布包构造器：返回 (cpu_prep, build_infer)，infer(prepped) -> list[str]。run_eval 用 infer(cpu_prep(imgs))。"""
    if name in ("nar_small", "nar_small_r16", "nar_small_distil"):
        d = M / {"nar_small": "manga-ocr-nar-small", "nar_small_r16": "nar-small-r16", "nar_small_distil": "manga-ocr-nar-small-distil"}[name]
        def build():
            sys.path.insert(0, str(d)); from manga_ocr_nar_small import MangaOcrNarSmall
            return MangaOcrNarSmall("cuda", model_dir=d)
        return to_u8, build
    if name == "cpt_flex":
        def build():
            sys.path.insert(0, str(M / "manga-ocr-CPT-code")); from manga_ocr_cpt import MangaOcrCPT
            return MangaOcrCPT(str(M / "manga-ocr-base-CPT-flex"), device="cuda")
        return to_u8, build
    if name in ("charspot_small", "charspot_nano"):
        sub = name.split("_")[1]; d = M / f"manga-ocr-charspot-{sub}"
        def build():
            sys.path.insert(0, str(d))
            mod = __import__(f"manga_ocr_charspot_{sub}"); ocr = getattr(mod, f"MangaOcrCharspot{sub.title()}")(model_dir=d, backend="cuda")
            ocr.warmup(); return ocr
        return to_u8, build
    if name in ("ar_exp", "ar_exp_fp32"):
        def build():
            d = M / "manga-ocr-ar-experimental"; sys.path.insert(0, str(d)); from infer import MangaOCR
            dt = {"fp16": torch.float16, "bf16": torch.bfloat16, "fp32": torch.float32}["fp32" if name == "ar_exp_fp32" else os.environ.get("AREXP_DTYPE", "fp16")]
            m = MangaOCR(d, device="cuda", dtype=dt)
            return lambda imgs: m(list(imgs), batch_size=len(imgs))
        return (lambda imgs: [i.convert("RGB") for i in imgs]), build
    return None

def _re(n):
    def load():
        prep, build = pkg(n); infer = build()
        return lambda imgs: infer(prep(imgs))
    return load

def _s2(n):
    def f():
        prep, build = pkg(n)
        return (lambda: prep), build
    return f

for n in ("nar_small", "nar_small_r16", "nar_small_distil", "cpt_flex", "charspot_small", "charspot_nano", "ar_exp", "ar_exp_fp32"):
    RE.ADAPTERS[n] = _re(n); S2.ADAPTERS[n] = _s2(n)

# 11-02 用户「baberu你用v1.2」：Read 的 baberu 适配器原样复用，只把 MODELS 指到垫片目录（baberu → models/baberu_v12 = tag v1.2，dinov2_base 同前）
SHIM = M.parent / "models_baberu_v12"
def _baberu_v12_re():
    RE.MODELS = SHIM; return RE.load_baberu()
def _baberu_v12_s2():
    S2.MODELS = SHIM; return S2.baberu()
RE.ADAPTERS["baberu_v12"] = _baberu_v12_re; S2.ADAPTERS["baberu_v12"] = _baberu_v12_s2

if MODE == "smoke":
    gt, imgs = RE.load_images(); predict = RE.ADAPTERS[NAME](); sub = gt[:16]
    t = time.perf_counter(); preds = [predict([imgs[g["key"]]])[0] for g in sub]; RE.sync()
    for p, g in zip(preds, sub): print(repr(g["text_rin"]), "->", repr(p))
    print(f"SMOKE {NAME}: {1000 * (time.perf_counter() - t) / 16:.1f} ms/img, mem {torch.cuda.max_memory_allocated() / 2**20:.0f} MB", flush=True)
elif MODE == "preds":
    sys.argv = [sys.argv[0], NAME, "--stage", "preds"]; RE.main()
elif MODE == "speed2":
    sys.argv = [sys.argv[0], NAME, "--check", "64"]; S2.main()
else:
    raise SystemExit(MODE)
