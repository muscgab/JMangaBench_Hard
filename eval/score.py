"""JMangaBench_Hard v1.0 scoring: python eval/score.py --pred preds.jsonl [--gt data/gt.jsonl] [--name MODEL] [--out result.json]
preds.jsonl: one line per box, {"key": ..., "pred": "..."}; missing keys count as empty predictions.
Main metrics use RIN v1.2 (eval/normalize/rin.py, same as JMangaBench_Read v1.3.3) on prediction and label:
score = mean over boxes of 1 - NED (x100), CER (total edit distance / total label characters), EM with 95% Wilson CI.
EM_NFKC: exact match after Unicode NFKC only (prediction and raw label "text"), reported for reference.
Subsets: all / agreed / human / box_adjusted, visual style, orientation and length buckets."""
import argparse, json, math, sys, unicodedata
from pathlib import Path
B = Path(__file__).resolve().parent
sys.path.insert(0, str(B / "normalize")); from rin import normalize_rin as N, POLICY_RIN

def edit(a, b):
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1): cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]

def wilson(k, n, z=1.96):
    if not n: return [0, 0]
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(100 * (c - h), 2), round(100 * (c + h), 2)]

def score(pred, gt):
    K = lambda s: unicodedata.normalize("NFKC", s).replace(" ", "")
    rows = []
    for g in gt:
        p = pred.get(g["key"], ""); pn = N(p); ref = g.get("text_rin") or N(g["text"])
        ed = edit(pn, ref)
        rows.append({**g, "em": pn == ref, "em_nfkc": K(p) == K(g["text"]), "ed": ed, "nref": len(ref),
                     "s": 1 - ed / max(len(ref), len(pn), 1), "missing": g["key"] not in pred})
    L = lambda g: "1-2" if g["n_chars"] <= 2 else "3-4" if g["n_chars"] <= 4 else "5-9" if g["n_chars"] <= 9 else ">=10"
    sections = {"all": lambda g: True, "agreed": lambda g: g["review"] == "consensus", "human": lambda g: g["review"] == "human",
                "box_adjusted": lambda g: g["box_edited"]}
    for v in ("sfx_lettering", "handwritten", "decorative_font", "printed"): sections[f"style_{v}"] = (lambda v: lambda g: g["visual_style"] == v)(v)
    for o in ("vertical", "horizontal", "curved_or_diagonal"): sections[f"orient_{o}"] = (lambda o: lambda g: g["orientation"] == o)(o)
    for b in ("1-2", "3-4", "5-9", ">=10"): sections[f"len_{b}"] = (lambda b: lambda g: L(g) == b)(b)
    out = {}
    for name, f in sections.items():
        rs = [r for r in rows if f(r)]
        if not rs: continue
        k = sum(r["em"] for r in rs)
        out[name] = {"n": len(rs), "score": round(100 * sum(r["s"] for r in rs) / len(rs), 2),
                     "cer": round(100 * sum(r["ed"] for r in rs) / max(1, sum(r["nref"] for r in rs)), 2),
                     "em": round(100 * k / len(rs), 2), "em_ci95": wilson(k, len(rs)),
                     "em_nfkc": round(100 * sum(r["em_nfkc"] for r in rs) / len(rs), 2), "missing": sum(r["missing"] for r in rs)}
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pred", required=True); ap.add_argument("--gt", default=str(B.parent / "data" / "gt.jsonl"))
    ap.add_argument("--name", default=None); ap.add_argument("--out", default=None)
    a = ap.parse_args()
    gt = [json.loads(l) for l in open(a.gt, encoding="utf-8")]
    pred = {}
    for l in open(a.pred, encoding="utf-8"):
        if l.strip(): d = json.loads(l); pred[d["key"]] = d.get("pred") or ""
    res = {"model": a.name or Path(a.pred).stem, "normalization": POLICY_RIN, "sections": score(pred, gt)}
    s = res["sections"]["all"]
    print(f"{res['model']}: score {s['score']}  CER {s['cer']}  EM {s['em']} {s['em_ci95']}  EM_NFKC {s['em_nfkc']}  (n={s['n']}, missing {s['missing']})")
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True); Path(a.out).write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")

if __name__ == "__main__":
    main()
