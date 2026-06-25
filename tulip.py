#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
鬱金香指標 v2.1 — 單檔可直跑（純 stdlib）

用法：
    chmod +x tulip.py
    echo "FRED_API_KEY=你的key" > .env
    ./tulip.py
    ./tulip.py --no-fred
    ./tulip.py --set M1.hy_oas=45 --set M4.margin_debt_yoy=92
    ./tulip.py --show
    ./tulip.py --selftest
"""
import argparse, csv, datetime, json, os, sys, urllib.parse, urllib.request
from pathlib import Path

__version__ = "2.1.0"

# ============================================================ 計分核心
WEIGHTS = {'M1':0.25,'M2':0.18,'M3':0.14,'M4':0.10,'M5':0.10,'M6':0.15,'M7':0.08}
NAMES = {'M1':'信貸計價','M2':'資本支出轉折','M3':'邊際買家枯竭',
         'M4':'槓桿','M5':'集中度/偽分散','M6':'結構確認','M7':'情緒/全民化'}
GROUPS = {
    '放大器(乾柴多高)':    ['M4','M5','M7'],
    '領先引信(火星點了沒)': ['M1','M2','M3'],
    '確認(燒起來沒)':       ['M6'],
}
BANDS = [
    (0,  50,  '平靜',           '正常配置，每月查'),
    (50, 75,  '累積',           '停止加碼風險，壓力測試組合能否扛 -35% 不被迫賣'),
    (75, 90,  '警戒/逐步退場',  '防禦準備並逐步減碼，目標 90 前退完；改週查 M1/M2/M6'),
    (90, 101, '進行中/太晚',    '脈衝/cascade 已啟動，控損模式，不在底部被迫賣'),
]

def to_display(raw):
    return raw * 90.0/70.0 if raw <= 70 else 90.0 + (raw - 70.0) * 10.0/30.0

def band(disp):
    for lo,hi,name,act in BANDS:
        if lo <= disp < hi: return name, act
    return BANDS[-1][2], BANDS[-1][3]

def mechanism_scores(proxies):
    M, missing = {}, {}
    for m, ps in proxies.items():
        vals = [v for v in ps.values() if v is not None]
        miss = [k for k,v in ps.items() if v is None]
        M[m] = round(sum(vals)/len(vals),1) if vals else None
        missing[m] = miss
    return M, missing

def composite(M):
    avail = {m:s for m,s in M.items() if s is not None}
    wsum = sum(WEIGHTS[m] for m in avail)
    return round(sum(WEIGHTS[m]*avail[m] for m in avail)/wsum,1) if wsum else 0

def group_scores(M):
    out={}
    for g,ms in GROUPS.items():
        avail=[(WEIGHTS[m],M[m]) for m in ms if M.get(m) is not None]
        out[g]=round(sum(w*s for w,s in avail)/sum(w for w,_ in avail),1) if avail else None
    return out

# ============================================================ FRED
FRED_URL = "https://api.stlouisfed.org/fred/series/observations"

def fred_fetch(series_id, api_key, limit=800, timeout=20):
    qs = urllib.parse.urlencode({
        "series_id": series_id, "api_key": api_key, "file_type": "json",
        "sort_order": "desc", "limit": limit,
    })
    with urllib.request.urlopen(f"{FRED_URL}?{qs}", timeout=timeout) as r:
        data = json.load(r)
    out = []
    for o in data.get("observations", []):
        v = o.get("value")
        if v in (".", "", None): continue
        try: out.append((o["date"], float(v)))
        except ValueError: pass
    return out

def pct_high(series, window=756):
    if not series: return None, None
    vals = [v for _, v in series[:window]]
    latest = vals[0]
    return latest, round(sum(1 for v in vals if v <= latest) / len(vals) * 100, 1)

def pct_spread(hy, ig, window=756):
    if not hy or not ig: return None, None
    ig_map = dict(ig)
    spread = [(d, h - ig_map[d]) for d, h in hy if d in ig_map]
    return pct_high(spread, window)

# ============================================================ CLI 雜事
DEFAULT_PROXIES = {
    "M1": {"bdc_navdisc_gate": 80},
    "M2": {"hyperscaler_capex_trigger_x_gate": 30, "ai_credit_fast": 25},
    "M3": {"ipo_withdrawal_rate": 15, "inflow_decel": 45},
    "M4": {"margin_debt_yoy": 88, "ai_debt_growth": 85},
    "M5": {"mag7_share": 88, "xasset_corr": 68},
    "M6": {"breadth_200dma": 30, "vix_term": 20, "drawdown_ath": 18},
    "M7": {"ipo_first_day_pop_fomo": 88, "us_sentiment_positioning": 80},
}

def load_env(path=".env"):
    p = Path(path)
    if not p.exists(): return
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line: continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

def load_proxies(path):
    if path is None: return {k: dict(v) for k, v in DEFAULT_PROXIES.items()}
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return {k: v for k, v in data.items() if not k.startswith("_")}

def merge(base, overlay):
    out = {m: dict(ps) for m, ps in base.items()}
    for m, ps in overlay.items():
        out.setdefault(m, {})
        for k, v in ps.items(): out[m][k] = v
    return out

def parse_set(set_list):
    overlay = {}
    for s in set_list or []:
        key, _, val = s.partition("=")
        m, _, p = key.partition(".")
        overlay.setdefault(m, {})[p] = None if val.lower() in ("none","null","") else float(val)
    return overlay

def fetch_fred_proxies(api_key, window=756):
    sources, out = {}, {"M1": {}}
    hy = ig = None
    try:
        hy = fred_fetch("BAMLH0A0HYM2", api_key, limit=window+50)
        latest, p = pct_high(hy, window)
        out["M1"]["hy_oas"] = p
        sources["M1.hy_oas"] = f"FRED BAMLH0A0HYM2 latest={latest} pct={p}"
    except Exception as e:
        sources["M1.hy_oas"] = f"FRED fail: {e}"
    try:
        ig = fred_fetch("BAMLC0A0CM", api_key, limit=window+50)
        latest, p = pct_spread(hy, ig, window)
        out["M1"]["hy_ig"] = p
        sources["M1.hy_ig"] = f"FRED BAMLH0A0HYM2-BAMLC0A0CM latest={latest} pct={p}"
    except Exception as e:
        sources["M1.hy_ig"] = f"FRED fail: {e}"
    return out, sources

# ============================================================ 報告 + 寫 history
def report(proxies, date=None, history="history/ti_history_v2.csv", note="", sources=None):
    date = date or datetime.date.today().isoformat()
    M, missing = mechanism_scores(proxies)
    raw = composite(M); disp = round(to_display(raw))
    name, act = band(disp); groups = group_scores(M)

    print(f"\n🌷 鬱金香指標 v2 ｜ {date}")
    print(f"   TI = {disp} / 100   狀態：{name}")
    print(f"   (內部raw {raw} → 顯示刻度；顯示90=raw70=引信備妥)")
    print(f"   行動：{act}\n   三組摘要：")
    for g,s in groups.items(): print(f"     {g:<22} {s}")
    print("\n   七機制：")
    for m in WEIGHTS:
        flag = f"  ⚠未驗證:{missing[m]}" if missing[m] else ""
        print(f"     {m} {NAMES[m]:<10} 權重{int(WEIGHTS[m]*100):>2}%  分 {M[m]}{flag}")
    if sources:
        print("\n   來源(自動抓):")
        for k,v in sources.items(): print(f"     {k}: {v}")

    os.makedirs(os.path.dirname(history) or ".", exist_ok=True)
    flat = {f"{m}.{p}":v for m,ps in proxies.items() for p,v in ps.items()}
    header = ['date','TI_display','TI_raw','state'] + list(WEIGHTS) + \
             list(GROUPS) + sorted(flat) + ['unverified','note']
    row = {'date':date,'TI_display':disp,'TI_raw':raw,'state':name,
           **{m:M[m] for m in WEIGHTS}, **groups, **flat,
           'unverified':';'.join(f"{m}:{','.join(v)}" for m,v in missing.items() if v),
           'note':note}
    newfile = not os.path.exists(history)
    with open(history,'a',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=header)
        if newfile: w.writeheader()
        w.writerow(row)

# ============================================================ self-check
def selftest():
    assert pct_high([("d2",10),("d1",4)], 2)[1] == 100.0
    assert pct_high([("d4",6),("d3",10),("d2",8),("d1",4)], 4)[1] == 50.0
    assert pct_spread([("d1",10)],[("d1",4)],1)[1] == 100.0
    assert merge({"M1":{"a":10}}, {"M1":{"a":99,"b":1}}) == {"M1":{"a":99,"b":1}}
    assert parse_set(["M1.a=42","M2.b=none"]) == {"M1":{"a":42.0},"M2":{"b":None}}
    assert to_display(70) == 90.0 and to_display(100) == 100.0
    assert band(89)[0] == "警戒/逐步退場" and band(95)[0] == "進行中/太晚"
    print("✓ selftest passed")

# ============================================================ main
def main(argv=None):
    ap = argparse.ArgumentParser(prog="tulip", description=f"Tulip Indicator v2.1 ({__version__})")
    ap.add_argument("--date"); ap.add_argument("--proxies")
    ap.add_argument("--history", default="history/ti_history_v2.csv")
    ap.add_argument("--note", default="")
    ap.add_argument("--no-fred", action="store_true")
    ap.add_argument("--window", type=int, default=756)
    ap.add_argument("--set", action="append", metavar="MECH.PROXY=PCT")
    ap.add_argument("--show", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--version", action="version", version=__version__)
    args = ap.parse_args(argv)

    if args.selftest: selftest(); return 0

    load_env()
    proxies = load_proxies(args.proxies)
    sources = {}
    api_key = os.environ.get("FRED_API_KEY")
    if not args.no_fred:
        if not api_key:
            print("⚠ FRED_API_KEY 未設定，跳過自動抓取（用 manual 預設值）", file=sys.stderr)
        else:
            fred_p, sources = fetch_fred_proxies(api_key, window=args.window)
            proxies = merge(proxies, fred_p)
    overrides = parse_set(args.set)
    if overrides: proxies = merge(proxies, overrides)

    if args.show:
        print(json.dumps(proxies, ensure_ascii=False, indent=2)); return 0
    report(proxies, date=args.date, history=args.history,
           note=args.note, sources=sources or None)
    return 0

if __name__ == "__main__":
    sys.exit(main())
