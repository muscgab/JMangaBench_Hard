"""JMangaBench_Hard v1.0 interactive leaderboard (2026-11-02), adapted from JMangaBench_Read v1.3 (its figures/build_site.py)
-> figures/pareto_interactive.html (copied to docs/index.html). Self-contained, no external scripts. English and Chinese UI.
X: per-image latency (default) / max throughput. Y: score (default) / CER / EM / EM (NFKC). Subsets: all / agreed / human / sfx lettering /
handwritten / box adjusted. "More models" (nar-small-R16, hidden by default). LLM readers: table only, marked *, listed last.
Points beyond the y range (mangaOCR) are drawn at the edge as a triangle with the value in the label."""
import json
from pathlib import Path
D = Path(__file__).resolve().parent
rows = json.load(open(D / "interactive_data.json")); llm = json.load(open(D / "llm_rows.json"))
NOTES = {"ar_exp": ["By the authors. Experimental release: muscgab/manga-ocr-ar-experimental, tag ema106k (ViT-B encoder + 2-layer autoregressive decoder). fp16; outputs equal fp32 on 3,014 of 3,015 boxes.", "本评测集作者的实验性发布：muscgab/manga-ocr-ar-experimental，标签 ema106k（ViT-B 编码器 + 2 层自回归解码器）。fp16；与 fp32 输出在 3,015 框中 3,014 框相同。"],
         "nar_small": ["By the authors. Released: muscgab/manga-ocr-nar-small.", "本评测集作者的模型。已发布：muscgab/manga-ocr-nar-small。"],
         "nar_small_r16": ["By the authors. Experimental model, weights on the r16 branch of muscgab/manga-ocr-nar-small. Listed without a rank.", "本评测集作者的实验模型，权重在 muscgab/manga-ocr-nar-small 的 r16 分支。列出但不排名。"],
         "charspot_small": ["By the authors. Character detection + learned reading order, no text decoder. CUDA backend of the released package (fp32). Released: muscgab/manga-ocr-charspot-small.", "本评测集作者的模型。逐字检测 + 学习的阅读顺序，没有文本解码器。发布包的 CUDA 后端（fp32）。已发布：muscgab/manga-ocr-charspot-small。"],
         "charspot_nano": ["By the authors. Character detection + learned reading order, no text decoder. CUDA backend of the released package (fp16 dense network). Released: muscgab/manga-ocr-charspot-nano.", "本评测集作者的模型。逐字检测 + 学习的阅读顺序，没有文本解码器。发布包的 CUDA 后端（稠密网络 fp16）。已发布：muscgab/manga-ocr-charspot-nano。"],
         "cpt_flex": ["By the authors: mangaOCR after continued pre-training on the authors' training data. CUDA path of the released package; encoder fp16, decoder fp32. Released: muscgab/manga-ocr-base-CPT-flex.", "本评测集作者的模型：mangaOCR 在作者训练数据上继续预训练。发布包的 CUDA 路径；编码器 fp16、解码器 fp32。已发布：muscgab/manga-ocr-base-CPT-flex。"],
         "nar_small_distil": ["By the authors. Distilled from manga-ocr-nar-small, int8-quantisation-aware; on the GPU int8 is simulated in fp16. At its max-throughput batch size, outputs match batch 1 on 96.7% of the timed crops. Released: muscgab/manga-ocr-nar-small-distil.", "本评测集作者的模型。由 manga-ocr-nar-small 蒸馏、int8 量化感知训练；GPU 上以 fp16 模拟 int8。最大吞吐 batch 下 96.7% 的计时裁图输出与 batch 1 相同。已发布：muscgab/manga-ocr-nar-small-distil。"],
         "preview": ["By the authors.", "本评测集作者的模型。"],
         "hayai_v2": ["hayai-ocr-v2 main branch (weights = v2.1).", "hayai-ocr-v2 main 分支（权重 = v2.1）。"],
         "baberu_v12": ["genshiai-daichi/baberu-ocr, tag v1.2.", "genshiai-daichi/baberu-ocr，标签 v1.2。"],
         "manga_ocr": ["kha-white/manga-ocr-base. Parameter count estimated from the fp32 weight file size.", "kha-white/manga-ocr-base。参数量按 fp32 权重文件大小估算。"],
         "paddleocr_vl_1_6_manga_lora_v6": ["sorryhyun/paddleocr-vl-1.6-manga-lora, folder v6 (commit 57e7c650): PaddleOCR-VL-1.6 with a LoRA on the vision tower and 18 fully trained decoder layers; trained on Manga109-s and COO, among others. Accuracy only: Ascend 910B, bf16, the model card's code (batch 16, greedy, at most 80 new tokens); speed not measured.",
                                            "sorryhyun/paddleocr-vl-1.6-manga-lora 的 v6 目录（commit 57e7c650）：PaddleOCR-VL-1.6，视觉塔 LoRA + 18 层解码器全量训练；训练数据包括 Manga109-s 与 COO 等。只测准确率：Ascend 910B、bf16、模型卡代码（batch 16、贪心、最多 80 个新 token）；未测速度。"]}
for r in rows: r["note"] = NOTES.get(r["id"], ["", ""])
HTML = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>JMangaBench_Hard Leaderboard</title>
<style>
:root{--surface:#fcfcfb;--ink:#0b0b0b;--ink2:#52514e;--muted:#8a8984;--grid:#e9e8e3;--axis:#c3c2b7;--front:#52514e;
--ours:#2a78d6;--hayai:#eb6834;--other:#8a8984;--tip:#ffffff;--tipb:#e2e1db;--hl:#eef3fb}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--surface:#1a1a19;--ink:#ffffff;--ink2:#c3c2b7;--muted:#8a8984;
--grid:#2e2e2c;--axis:#4a4a46;--front:#c3c2b7;--ours:#3987e5;--hayai:#d95926;--other:#8a8984;--tip:#262625;--tipb:#3a3a37;--hl:#1f2a38}}
:root[data-theme="dark"]{--surface:#1a1a19;--ink:#ffffff;--ink2:#c3c2b7;--muted:#8a8984;--grid:#2e2e2c;--axis:#4a4a46;--front:#c3c2b7;
--ours:#3987e5;--hayai:#d95926;--other:#8a8984;--tip:#262625;--tipb:#3a3a37;--hl:#1f2a38}
*{box-sizing:border-box}body{margin:0;background:var(--surface);color:var(--ink);font:14px/1.45 "Helvetica Neue",Helvetica,Arial,"PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif}
.wrap{max-width:1100px;margin:0 auto;padding:24px 16px 40px}
.top{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;flex-wrap:wrap}
h1{font-size:22px;margin:0 0 4px;font-weight:600}.sub{color:var(--ink2);margin:0 0 16px}a{color:var(--ink2)}
.controls{display:flex;flex-wrap:wrap;gap:12px 16px;align-items:center;margin-bottom:8px}
.seg{display:inline-flex;flex-wrap:wrap;border:1px solid var(--axis);border-radius:8px;overflow:hidden}
.seg button{background:transparent;color:var(--ink2);border:0;padding:6px 12px;font:inherit;cursor:pointer}
.seg button+button{border-left:1px solid var(--axis)}.seg button[aria-pressed="true"]{background:var(--hl);color:var(--ink);font-weight:600}
.lab{color:var(--muted);font-size:12px;margin-right:6px}label.chk{color:var(--ink2);cursor:pointer;user-select:none}
.legend{display:flex;flex-wrap:wrap;gap:16px;color:var(--ink2);font-size:13px;margin:4px 0}.legend i{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:6px;vertical-align:-1px}
.chart{position:relative;width:100%}svg{display:block;width:100%;height:auto}
.tick{fill:var(--ink2);font-size:12px}.axlab{fill:var(--ink2);font-size:12.5px}.mlab{fill:var(--ink);font-size:12.5px;pointer-events:none}
.tip{position:absolute;pointer-events:none;background:var(--tip);border:1px solid var(--tipb);border-radius:8px;padding:10px 12px;box-shadow:0 4px 18px rgba(0,0,0,.12);
font-size:12.5px;min-width:260px;max-width:340px;display:none;z-index:5}.tip h3{margin:0 0 2px;font-size:14px}.tip .k{color:var(--ink2)}.tip table{border-collapse:collapse;width:100%}
.tip td{padding:1px 0}.tip td:last-child{text-align:right;font-variant-numeric:tabular-nums;padding-left:8px}.tip .sec{color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:.04em;padding-top:6px}
.note{color:var(--ink2);font-size:12px;margin-top:8px}
h2{font-size:16px;margin:28px 0 6px;font-weight:600}
table.data{border-collapse:collapse;width:100%;font-size:12.5px}table.data th,table.data td{padding:5px 8px;border-bottom:1px solid var(--grid);text-align:right;white-space:nowrap}
table.data th:first-child,table.data td:first-child{text-align:left}table.data th{color:var(--ink2);font-weight:600;cursor:pointer}
table.data tr.llm td{color:var(--ink2)}table.data tr.more td:first-child::after{content:" ·";color:var(--muted)}
.tablewrap{overflow-x:auto}.foot{color:var(--ink2);font-size:12px;margin-top:8px}
[data-lang="en"] .zh,[data-lang="zh"] .en{display:none}
</style></head><body data-lang="en"><div class="wrap">
<div class="top"><div><h1 id="title"></h1>
<p class="sub"><span class="en">JMangaBench_Hard v1.0 · 3,015 text boxes (sound effects, stylised lettering, handwriting) from 1,339 pages · RTX 4070, fp16 · hover a dot for details · </span><span class="zh">JMangaBench_Hard v1.0 · 1,339 页的 3,015 个文字框（拟声词、风格化字体、手写）· RTX 4070，fp16 · 悬停查看详情 · </span><a href="https://github.com/muscgab/JMangaBench_Hard">GitHub</a></p></div>
<span class="seg" id="lseg"><button data-l="en" aria-pressed="true">English</button><button data-l="zh" aria-pressed="false">中文</button></span></div>
<div class="controls">
 <div><span class="lab">X</span><span class="seg" id="xseg"></span></div>
 <div><span class="lab">Y</span><span class="seg" id="yseg"></span></div>
 <div><span class="lab" id="slab"></span><span class="seg" id="sseg"></span></div>
 <label class="chk"><input type="checkbox" id="more"> <span id="morelab"></span></label>
</div>
<div class="legend" id="legend"></div>
<div class="chart" id="chart"><svg id="svg" viewBox="0 0 1000 600" role="img" aria-label="Pareto chart"></svg><div class="tip" id="tip"></div></div>
<p class="note" id="note"></p>
<h2 id="ttitle"></h2><div class="tablewrap"><table class="data" id="tbl"></table></div>
<p class="foot" id="tfoot"></p>
</div>
<script>
const DATA = __DATA__, LLM = __LLM__;
const T = {
 en:{x:{lat:"Per-image latency",thr:"Max throughput"},
     xl:{lat:"Per-image latency (ms, batch = 1, mean, preprocessing included)  ←  faster",
         thr:"Max throughput (images/s, best batch size per model)  faster  →"},
     xt:{lat:"per-image latency",thr:"max throughput"},
     y:{score:"Score",cer:"CER",em:"Exact match",em_nfkc:"EM (NFKC)"},
     yl:{score:"Score (mean 1 − NED, all boxes)",cer:"CER (%) — lower is better, axis reversed",em:"Exact match (%)",em_nfkc:"Exact match after NFKC only (%)"},
     yt:{score:"Accuracy",cer:"CER",em:"Exact match",em_nfkc:"Exact match (NFKC)"},
     s:{all:"All",agreed:"Agreed",human:"Human-decided",sfx:"SFX lettering",handwritten:"Handwritten",adjusted:"Box adjusted"},
     sn:{all:"all boxes, 3,015",agreed:"agreed by three LLMs, 2,161 boxes",human:"human-decided, 854 boxes",sfx:"sfx lettering, 1,835 boxes",handwritten:"handwritten, 1,056 boxes",adjusted:"box redrawn in review, 75 boxes"},
     subset:"Subset",more:"More models (nar-small-R16)",vs:"vs.",ned:"1 − NED",
     legend:{ours:"By the authors (NAR / CharDet; ar-experimental and CPT-flex are AR)",hayai:"Hayai family (AR)",other:"Other"},
     note:{lat:"Scores from batch = 1 outputs. ",thr:"Scores from batch = 1 outputs. Batch size at max throughput in the hover card. "},
     note2:"Main scores use RIN v1.2 (reading-invariant normalization), as in JMangaBench_Read. Triangles at an edge: value beyond the axis range.",
     card:{acc:"Accuracy (batch = 1)",comp:"Score",cer:"CER",em:"Exact match",nfkc:"Exact match (NFKC)",
           subs:"Subsets: 1 − NED / CER / EM",speed:"Speed (RTX 4070, fp16)",lat:"Per-image latency (mean / p50)",thr:"Max throughput",
           agree:"Max-throughput outputs = batch 1",mem:"Memory at batch 1",params:"params"},
     ttitle:"Full results",tfoot:"Accuracy columns: batch = 1 outputs, selected subset. * LLM readers whose agreed reading defines 2,161 of the labels and whose readings were shown in review; listed for reference, not ranked. Rows marked · are shown with “More models”. PaddleOCR-VL-For-Manga was not measured for this version.",
     cols:["Model","Type","Params (M)","SCORE","CER %","EM %","EM NFKC %","Per-image (ms)","Max img/s"]},
 zh:{x:{lat:"逐张延迟",thr:"最大吞吐"},
     xl:{lat:"逐张延迟（ms，batch = 1，平均值，含预处理）  ←  更快",
         thr:"最大吞吐（张/秒，各模型最佳 batch）  更快  →"},
     xt:{lat:"逐张延迟",thr:"最大吞吐"},
     y:{score:"得分",cer:"CER",em:"完全匹配",em_nfkc:"完全匹配（NFKC）"},
     yl:{score:"得分（全部框 1 − NED 平均）",cer:"CER（%）——越低越好，纵轴已翻转",em:"完全匹配（%）",em_nfkc:"仅做 NFKC 后的完全匹配（%）"},
     yt:{score:"准确率",cer:"CER",em:"完全匹配",em_nfkc:"完全匹配（NFKC）"},
     s:{all:"全部",agreed:"三家一致",human:"人工裁定",sfx:"拟声字",handwritten:"手写",adjusted:"调整过框"},
     sn:{all:"全部 3,015 框",agreed:"三家 LLM 一致 2,161 框",human:"人工裁定 854 框",sfx:"拟声字 1,835 框",handwritten:"手写 1,056 框",adjusted:"审核时重画框 75 框"},
     subset:"板块",more:"更多模型（nar-small-R16）",vs:"与",ned:"1 − NED",
     legend:{ours:"本评测集作者的模型（NAR / CharDet；ar-experimental 与 CPT-flex 为 AR）",hayai:"Hayai 系列（AR）",other:"其他"},
     note:{lat:"分数取 batch = 1 的输出。",thr:"分数取 batch = 1 的输出。最大吞吐对应的 batch 见悬停卡片。"},
     note2:"主分数使用 RIN v1.2（阅读等价归一化），与 JMangaBench_Read 相同。边缘的三角：数值超出坐标范围。",
     card:{acc:"准确率（batch = 1）",comp:"得分",cer:"CER",em:"完全匹配",nfkc:"完全匹配（NFKC）",
           subs:"板块：1 − NED / CER / EM",speed:"速度（RTX 4070，fp16）",lat:"逐张延迟（平均 / p50）",thr:"最大吞吐",
           agree:"最大吞吐输出 = batch 1",mem:"batch = 1 显存",params:"参数"},
     ttitle:"完整成绩",tfoot:"准确率各列：batch = 1 输出，所选板块。* LLM 识别器：2,161 个标签就是三家一致的读法，审核时也展示了它们的读法，仅供参考，不参与排名。带 · 的行在勾选“更多模型”后显示。PaddleOCR-VL-For-Manga 本版本未测。",
     cols:["模型","架构","参数量（M）","SCORE","CER %","EM %","EM NFKC %","逐张（ms）","最大吞吐 张/秒"]}};
const XK = {lat:"lat",thr:"thr"}, XB = {lat:"low",thr:"high"}, XCLIP = {lat:null,thr:null}, YOUT = new Set(["manga_ocr"]);
const SHORT = n => n.replace("Hayai v2.5 Nova ","Nova ");
let L = (navigator.language || "en").toLowerCase().startsWith("zh") ? "zh" : "en", sx = "lat", sy = "score", ss = "all", more = false;
const svg = document.getElementById("svg"), tip = document.getElementById("tip"), NS = "http://www.w3.org/2000/svg";
const W = 1000, H = 600, M = {l:64, r:24, t:16, b:56};
const el = (t, a, p) => { const e = document.createElementNS(NS, t); for (const k in a) e.setAttribute(k, a[k]); (p||svg).appendChild(e); return e; };
function nice(lo, hi, n){ const span = hi - lo, step0 = span / n, mag = Math.pow(10, Math.floor(Math.log10(step0)));
  const step = [1,2,2.5,5,10].map(m => m*mag).find(s => s >= step0); const a = Math.floor(lo/step)*step, b = Math.ceil(hi/step)*step;
  const t = []; for (let v = a; v <= b + 1e-9; v += step) t.push(+v.toFixed(6)); return {a, b, t}; }
function yval(d){ return d.sub[ss] ? d.sub[ss][sy] : null; }
const vis = () => DATA.filter(d => more || !d.more);
function segs(){
  const mk = (id, obj, cur, attr) => { const s = document.getElementById(id); s.innerHTML = Object.entries(obj).map(([k, v]) => `<button data-${attr}="${k}" aria-pressed="${k === cur}">${v}</button>`).join(""); };
  mk("xseg", T[L].x, sx, "x"); mk("yseg", T[L].y, sy, "y"); mk("sseg", T[L].s, ss, "s");
  document.querySelectorAll("#xseg button").forEach(b => b.onclick = () => { sx = b.dataset.x; render(); });
  document.querySelectorAll("#yseg button").forEach(b => b.onclick = () => { sy = b.dataset.y; render(); });
  document.querySelectorAll("#sseg button").forEach(b => b.onclick = () => { ss = b.dataset.s; render(); });
  document.querySelectorAll("#lseg button").forEach(b => b.setAttribute("aria-pressed", b.dataset.l === L));
  document.getElementById("slab").textContent = T[L].subset; document.getElementById("morelab").textContent = T[L].more;
  document.getElementById("legend").innerHTML = ["ours","hayai","other"].map(g => `<span><i style="background:var(--${g})"></i>${T[L].legend[g]}</span>`).join("");
  document.getElementById("ttitle").textContent = T[L].ttitle; document.getElementById("tfoot").textContent = T[L].tfoot;
  document.body.dataset.lang = L; document.documentElement.lang = L === "zh" ? "zh-CN" : "en";
}
function ylabel(){ const t = T[L]; if (sy === "score") return ss === "all" ? t.yl.score : `${t.ned}, ${t.sn[ss]}`; return `${t.yl[sy]} · ${t.sn[ss]}`; }
function draw(){
  svg.innerHTML = ""; const t = T[L], xk = XK[sx], clip = XCLIP[sx], yb = sy === "cer" ? "low" : "high";
  const pts = vis().filter(d => d[xk] != null && yval(d) != null).map(d => ({d, x0:d[xk], x:clip ? Math.min(d[xk], clip) : d[xk], y:yval(d), out:clip && d[xk] > clip}));
  const xr = clip ? nice(0, clip, 6) : nice(0, Math.max(...pts.map(p => p.x)) * 1.05, 6);
  const core = pts.filter(p => !YOUT.has(p.d.id)), ylo = Math.min(...core.map(p => p.y)), yhi = Math.max(...core.map(p => p.y)), pad = (yhi - ylo) * 0.08 || 1;
  const yr = nice(ylo - pad, yhi + pad, 7);
  for (const p of pts){ p.y0 = p.y; if (p.y < yr.a){ p.y = yr.a; p.yout = true; } if (p.y > yr.b){ p.y = yr.b; p.yout = true; } }
  const px = v => M.l + (v - xr.a) / (xr.b - xr.a) * (W - M.l - M.r);
  const py = yb === "high" ? v => H - M.b - (v - yr.a) / (yr.b - yr.a) * (H - M.t - M.b) : v => M.t + (v - yr.a) / (yr.b - yr.a) * (H - M.t - M.b);
  for (const v of xr.t){ el("line", {x1:px(v), x2:px(v), y1:M.t, y2:H-M.b, stroke:"var(--grid)"}); const e = el("text", {x:px(v), y:H-M.b+20, "text-anchor":"middle", class:"tick"}); e.textContent = v; }
  for (const v of yr.t){ el("line", {x1:M.l, x2:W-M.r, y1:py(v), y2:py(v), stroke:"var(--grid)"}); const e = el("text", {x:M.l-10, y:py(v)+4, "text-anchor":"end", class:"tick"}); e.textContent = v; }
  el("line", {x1:M.l, x2:W-M.r, y1:H-M.b, y2:H-M.b, stroke:"var(--axis)"});
  let e = el("text", {x:(M.l+W-M.r)/2, y:H-12, "text-anchor":"middle", class:"axlab"}); e.textContent = t.xl[sx];
  e = el("text", {x:16, y:(M.t+H-M.b)/2, "text-anchor":"middle", class:"axlab", transform:`rotate(-90 16 ${(M.t+H-M.b)/2})`}); e.textContent = ylabel();
  const bx = (a, b) => XB[sx] === "low" ? a < b : a > b, by = (a, b) => yb === "low" ? a < b : a > b;
  const front = pts.filter(p => !p.yout).filter(p => !pts.some(q => q !== p && (bx(q.x0, p.x0) || q.x0 === p.x0) && (by(q.y, p.y) || q.y === p.y) && !(q.x0 === p.x0 && q.y === p.y))).sort((a, b) => a.x - b.x);
  if (front.length > 1) el("polyline", {points:front.map(p => `${px(p.x)},${py(p.y)}`).join(" "), fill:"none", stroke:"var(--front)", "stroke-width":1.6, "stroke-linejoin":"round"});
  const placed = [], dots = pts.map(p => ({x:px(p.x), y:py(p.y)}));
  const cands = [[18,-18],[18,18],[-18,-18],[-18,18],[26,0],[-26,0],[0,-26],[0,26],[34,-30],[-34,-30],[34,30],[-34,30],[48,-8],[-48,-8],[52,-40],[-52,-40],[52,40],[-52,40]];
  const g = el("g", {});
  for (const p of pts.slice().sort((a, b) => b.y - a.y)){
    const cx = px(p.x), cy = py(p.y), tx = el("text", {class:"mlab"}, g);
    tx.textContent = SHORT(p.d.name) + (p.out ? ` (${Math.round(p.x0).toLocaleString()} →)` : "") + (p.yout ? ` (${p.y0.toFixed(1)})` : "");
    let best = null;
    for (const [dx, dy] of cands){
      const anchor = dx < 0 ? "end" : (dx === 0 ? "middle" : "start"); tx.setAttribute("text-anchor", anchor); tx.setAttribute("x", cx + dx); tx.setAttribute("y", cy + dy + 4);
      const b = tx.getBBox(), box = {x:b.x-3, y:b.y-2, w:b.width+6, h:b.height+4};
      const inside = box.x >= M.l && box.x + box.w <= W - M.r && box.y >= M.t && box.y + box.h <= H - M.b;
      const hit = placed.some(o => box.x < o.x + o.w && box.x + box.w > o.x && box.y < o.y + o.h && box.y + box.h > o.y)
              || dots.some(d => d.x > box.x - 6 && d.x < box.x + box.w + 6 && d.y > box.y - 6 && d.y < box.y + box.h + 6);
      const cost = (inside ? 0 : 1000) + (hit ? 100 : 0) + Math.hypot(dx, dy) / 10;
      if (!best || cost < best.cost) best = {cost, dx, dy, anchor, box};
    }
    tx.setAttribute("text-anchor", best.anchor); tx.setAttribute("x", cx + best.dx); tx.setAttribute("y", cy + best.dy + 4); placed.push(best.box);
    const lx = best.anchor === "end" ? best.box.x + best.box.w : (best.anchor === "start" ? best.box.x : cx), ly = best.box.y + best.box.h / 2;
    el("line", {x1:cx, y1:cy, x2:lx, y2:ly, stroke:"var(--muted)", "stroke-width":0.8}, g).parentNode.insertBefore(g.lastChild, g.firstChild);
  }
  for (const p of pts){
    const col = `var(--${p.d.group})`, cx = px(p.x), cy = py(p.y);
    const c = p.yout ? el("path", {d:`M${cx-7},${cy-6} L${cx+7},${cy-6} L${cx},${cy+6} Z`, fill:col, stroke:"var(--surface)", "stroke-width":1.5})
            : p.out ? el("path", {d:`M${cx-6},${cy-7} L${cx+6},${cy} L${cx-6},${cy+7} Z`, fill:col, stroke:"var(--surface)", "stroke-width":1.5})
                    : el("circle", {cx, cy, r:5, fill:col, stroke:"var(--surface)", "stroke-width":2, "fill-opacity":p.d.more ? 0.55 : 1});
    const hit = el("circle", {cx, cy, r:14, fill:"transparent", style:"cursor:pointer"});
    hit.addEventListener("mouseenter", ev => { show(p.d, ev); }); hit.addEventListener("mousemove", ev => move(ev));
    hit.addEventListener("mouseleave", () => { tip.style.display = "none"; });
  }
  document.getElementById("title").textContent = L === "zh" ? `${t.yt[sy]}${t.vs}${t.xt[sx]}` + (ss === "all" ? "" : ` — ${t.s[ss]}`) : `${t.yt[sy]} vs. ${t.xt[sx]}` + (ss === "all" ? "" : ` — ${t.s[ss]}`);
  document.getElementById("note").textContent = t.note[sx] + t.note2;
}
const f = (v, s = "", d = 1) => v == null ? "—" : (+v).toFixed(d) + s;
function show(d, ev){
  const c = T[L].card, sn = T[L].s;
  tip.innerHTML = `<h3>${d.name}</h3><div class="k">${d.arch} · ${f(d.params_m, "M", 1)} ${c.params} · ${d.precision}</div>
  <table><tr><td class="sec" colspan="2">${c.acc}</td></tr>
  <tr><td>${c.comp}</td><td><b>${f(d.score, "", 2)}</b></td></tr><tr><td>${c.cer}</td><td>${f(d.cer, "%", 2)}</td></tr>
  <tr><td>${c.em}</td><td>${f(d.em, "%", 2)}</td></tr><tr><td>${c.nfkc}</td><td>${f(d.em_nfkc, "%", 2)}</td></tr>
  <tr><td class="sec" colspan="2">${c.subs}</td></tr>
  ${["agreed","human","sfx","handwritten","adjusted"].map(k => `<tr><td>${sn[k]}</td><td>${f(d.sub[k].score, "", 2)} / ${f(d.sub[k].cer, "%", 2)} / ${f(d.sub[k].em, "%", 1)}</td></tr>`).join("")}
  <tr><td class="sec" colspan="2">${c.speed}</td></tr>
  <tr><td>${c.lat}</td><td>${f(d.lat, "")} / ${f(d.lat_p50, " ms")}</td></tr>
  <tr><td>${c.thr}</td><td>${f(d.thr, " img/s")}${d.best_bs ? ` @ b${d.best_bs}` : ""}</td></tr>
  <tr><td>${c.agree}</td><td>${f(100 * d.agree_bs1, "%", 1)}</td></tr>
  <tr><td>${c.mem}</td><td>${d.vram_bs1 ? f(d.vram_bs1 / 1024, " GB", 2) : "—"}</td></tr></table>
  ${d.note[L === "zh" ? 1 : 0] ? `<div class="k" style="margin-top:6px">${d.note[L === "zh" ? 1 : 0]}</div>` : ""}`;
  tip.style.display = "block"; move(ev);
}
function move(ev){ const r = document.getElementById("chart").getBoundingClientRect(); let x = ev.clientX - r.left + 14, y = ev.clientY - r.top + 14;
  if (x + tip.offsetWidth > r.width) x = Math.max(0, ev.clientX - r.left - tip.offsetWidth - 14); if (y + tip.offsetHeight > r.height) y = Math.max(0, r.height - tip.offsetHeight);
  tip.style.left = x + "px"; tip.style.top = y + "px"; }
const COLK = ["name","arch","params_m","s_score","s_cer","s_em","s_nfkc","lat","thr"];
let sortK = "s_score", sortD = -1;
function table(){ const t = document.getElementById("tbl"), cols = T[L].cols;
  for (const d of DATA){ const m = d.sub[ss]; d.s_score = m.score; d.s_cer = m.cer; d.s_em = m.em; d.s_nfkc = m.em_nfkc; }
  const head = ss === "all" ? T[L].y.score : T[L].ned;
  const rows = vis().slice().sort((a, b) => ((a[sortK] ?? -1e9) > (b[sortK] ?? -1e9) ? 1 : -1) * sortD);
  const llm = LLM.map(r => ({name:r.name + " *", arch:"LLM", s_score:r.sub[ss].score, s_cer:r.sub[ss].cer, s_em:r.sub[ss].em, s_nfkc:r.sub[ss].em_nfkc, llm:true}));
  const cell = (d, k) => { const v = d[k]; if (typeof v !== "number") return v ?? "—"; return v.toFixed(["params_m","lat","thr"].includes(k) ? 1 : 2); };
  t.innerHTML = "<tr>" + COLK.map((k, i) => `<th data-k="${k}">${cols[i] === "SCORE" ? head : cols[i]}${k === sortK ? (sortD < 0 ? " ↓" : " ↑") : ""}</th>`).join("") + "</tr>" +
    rows.concat(llm).map(d => `<tr class="${d.llm ? "llm" : d.more ? "more" : ""}">` + COLK.map(k => `<td>${cell(d, k)}</td>`).join("") + "</tr>").join("");
  t.querySelectorAll("th").forEach(th => th.onclick = () => { const k = th.dataset.k; sortD = k === sortK ? -sortD : -1; sortK = k; table(); }); }
function render(){ segs(); draw(); table(); }
document.querySelectorAll("#lseg button").forEach(b => b.onclick = () => { L = b.dataset.l; render(); });
document.getElementById("more").onchange = ev => { more = ev.target.checked; render(); };
render();
</script></body></html>"""
out = HTML.replace("__DATA__", json.dumps(rows, ensure_ascii=False)).replace("__LLM__", json.dumps(llm, ensure_ascii=False))
(D / "pareto_interactive.html").write_text(out, encoding="utf-8")
print("written", (D / "pareto_interactive.html").stat().st_size, "bytes")
