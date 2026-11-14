"""JMangaBench_Hard v1.0 model table for the figures, site and README (2026-11-02). Accuracy from eval/score.py on data/predictions
(batch = 1 outputs, RIN v1.2); speed from results/ (RTX 4070, 2026-11-02: <id>_preds.json = per-image run, <id>_speed2.json =
max throughput). -> figures/interactive_data.json (OCR models) + figures/llm_rows.json (LLM readers, table only)."""
import json, sys
from pathlib import Path
F = Path(__file__).resolve().parent; R = F.parent
sys.path.insert(0, str(R / "eval")); import score as SC
gt = [json.loads(l) for l in open(R / "data/gt.jsonl", encoding="utf-8")]
# id (prediction file) -> display name, arch, group, params (M), precision, more?
M = [("ar_exp", "manga-ocr-ar-experimental", "AR", "ours", 130.6, "fp16", False),
     ("ns3-98k", "ns3-98k", "AR", "ours", 130.596108, "fp16", False),
     ("hayai_supernova_p256", "Hayai v2.7 Supernova p256", "AR", "hayai", 158.379408, "fp16", False),
     ("nar_small_r16", "nar-small-R16", "NAR", "ours", 54.2, "fp16", True),
     ("cpt_flex", "manga-ocr-base-CPT-flex", "AR", "ours", 110.9, "fp16 enc / fp32 dec", False),
     ("nar_small", "manga-ocr-nar-small", "NAR", "ours", 54.2, "fp16", False),
     ("charspot_small", "manga-ocr-charspot-small", "CharDet", "ours", 10.96, "fp32", False),
     ("nar_small_distil", "manga-ocr-nar-small-distil", "NAR", "ours", 29.8, "fp16 (sim. int8)", False),
     ("charspot_nano", "manga-ocr-charspot-nano", "CharDet", "ours", 1.70, "fp16", False),
     ("preview", "Preview", "NAR", "ours", 196.0, "fp16", False),
     ("hayai_nova_p256", "Hayai v2.5 Nova p256", "AR", "hayai", 157.0, "fp16", False),
     ("hayai_nova_p384", "Hayai v2.5 Nova p384", "AR", "hayai", 157.0, "fp16", False),
     ("hayai_nova_p512", "Hayai v2.5 Nova p512", "AR", "hayai", 157.0, "fp16", False),
     ("hayai_v2", "Hayai v2.1", "AR", "hayai", 156.0, "fp16", False),
     ("baberu_v12", "baberuOCR v1.2", "AR", "other", 113.0, "fp16", False),
     ("paddleocr_vl_1_6_manga_lora_v6", "PaddleOCR-VL-1.6 manga LoRA v6", "AR (VLM)", "other", 959.0, "bf16 (Ascend 910B)", False),  # 11-10: accuracy only, no speed
     ("manga_ocr", "mangaOCR", "AR", "other", 111.0, "fp16", False)]
SUBS = {"all": "all", "agreed": "agreed", "human": "human", "sfx": "style_sfx_lettering", "handwritten": "style_handwritten", "adjusted": "box_adjusted"}
def subs(pred):
    s = SC.score(pred, gt)
    return {k: {m: s[v][m] for m in ("score", "cer", "em", "em_nfkc", "n")} for k, v in SUBS.items()}
rows = []
for i, name, arch, group, par, prec, more in M:
    pred = {d["key"]: d.get("pred") or "" for d in map(json.loads, open(R / f"data/predictions/{i}.jsonl", encoding="utf-8"))}
    tp = R / f"results/{i}_preds.json"  # 11-10: models without GPU timing get speed fields None
    p = json.load(open(tp)) if tp.exists() else None; s2 = json.load(open(R / f"results/{i}_speed2.json")) if tp.exists() else None
    sb = subs(pred); a = sb["all"]
    rows.append({"id": i, "name": name, "arch": arch, "group": group, "more": more, "precision": prec, "params_m": par,
                 "score": a["score"], "cer": a["cer"], "em": a["em"], "em_nfkc": a["em_nfkc"],
                 "lat": p["lat_ms_mean"] if p else None, "lat_p50": p["lat_ms_p50"] if p else None, "vram_bs1": p["peak_mem_mb_bs1"] if p else None,
                 "thr": s2["best"]["imgs_per_sec"] if s2 else None, "best_bs": s2["best"]["batch"] if s2 else None, "best_mem": s2["best"]["peak_reserved_mb"] if s2 else None,
                 "agree_bs1": s2["best"]["agree_with_bs1"] if s2 else None, "sub": sb})
llm = []
L = {d["key"]: d["readings"] for d in map(json.loads, open(R / "data/llm_readings.jsonl", encoding="utf-8"))}
for k, name in (("sol", "GPT-6.1 Sol"), ("opus", "Claude Opus 5.5"), ("terra", "GPT-6.1 Terra")):
    sb = subs({key: r[k] for key, r in L.items()}); llm.append({"id": f"llm_{k}", "name": name, "score": sb["all"]["score"], "sub": sb})
json.dump(rows, open(F / "interactive_data.json", "w"), ensure_ascii=False, indent=1)
json.dump(llm, open(F / "llm_rows.json", "w"), ensure_ascii=False, indent=1)
for r in sorted(rows, key=lambda r: -r["score"]): print(f"{r['name']:28s} {r['score']:6.2f} {r['cer']:6.2f} {r['em']:6.2f}  {r['lat']} ms  {r['thr']} img/s")
for r in llm: print(r["name"], r["score"], r["sub"]["human"])
