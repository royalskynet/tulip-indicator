"""tulip CLI entry — auto-fetches FRED proxies, merges manual proxies.json, scores."""
import argparse, json, os, sys
from pathlib import Path
from . import __version__, fred, score

def load_env(path=".env"):
    """Minimal .env parser. Sets os.environ for K=V lines, ignores #comments."""
    p = Path(path)
    if not p.exists(): return
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line: continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

def load_proxies(path):
    """Load proxies.json next to package by default; user override via --proxies."""
    if path is None:
        path = Path(__file__).parent / "proxies.json"
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return {k: v for k, v in data.items() if not k.startswith("_")}

def fetch_fred_proxies(api_key, window=756):
    """Return ({M1: {proxy: pct}}, sources_dict). Adds hy_oas + hy_ig."""
    sources = {}
    out = {"M1": {}}
    try:
        hy = fred.fetch_series("BAMLH0A0HYM2", api_key, limit=window+50)
        latest, pct = fred.percentile_high(hy, window)
        out["M1"]["hy_oas"] = pct
        sources["M1.hy_oas"] = f"FRED BAMLH0A0HYM2 latest={latest} pct={pct}"
    except Exception as e:
        sources["M1.hy_oas"] = f"FRED fail: {e}"
    try:
        ig = fred.fetch_series("BAMLC0A0CM", api_key, limit=window+50)
        latest, pct = fred.spread_percentile(hy, ig, window)
        out["M1"]["hy_ig"] = pct
        sources["M1.hy_ig"] = f"FRED BAMLH0A0HYM2-BAMLC0A0CM latest={latest} pct={pct}"
    except Exception as e:
        sources["M1.hy_ig"] = f"FRED fail: {e}"
    return out, sources

def merge(base, overlay):
    """Overlay wins per (mech, proxy). None values are kept as None (unverified)."""
    out = {m: dict(ps) for m, ps in base.items()}
    for m, ps in overlay.items():
        out.setdefault(m, {})
        for k, v in ps.items():
            out[m][k] = v
    return out

def parse_set(set_list):
    """['M1.hy_oas=42'] -> {'M1': {'hy_oas': 42.0}}"""
    overlay = {}
    for s in set_list or []:
        key, _, val = s.partition("=")
        m, _, p = key.partition(".")
        overlay.setdefault(m, {})[p] = None if val.lower() in ("none","null","") else float(val)
    return overlay

def main(argv=None):
    ap = argparse.ArgumentParser(prog="tulip", description=f"Tulip Indicator v2 ({__version__})")
    ap.add_argument("--date", help="ISO date (default today)")
    ap.add_argument("--proxies", help="Path to proxies.json (default: bundled)")
    ap.add_argument("--history", default="history/ti_history_v2.csv")
    ap.add_argument("--note", default="")
    ap.add_argument("--no-fred", action="store_true", help="Skip FRED auto-fetch")
    ap.add_argument("--window", type=int, default=756, help="Percentile window in days")
    ap.add_argument("--set", action="append", metavar="MECH.PROXY=PCT",
                    help="Override one proxy percentile (repeatable)")
    ap.add_argument("--show", action="store_true", help="Print resolved proxies and exit")
    ap.add_argument("--version", action="version", version=__version__)
    args = ap.parse_args(argv)

    load_env()
    manual = load_proxies(args.proxies)
    proxies = manual
    sources = {}

    api_key = os.environ.get("FRED_API_KEY")
    if not args.no_fred:
        if not api_key:
            print("⚠ FRED_API_KEY 未設定，跳過自動抓取（用 manual proxies.json 值）", file=sys.stderr)
        else:
            fred_proxies, sources = fetch_fred_proxies(api_key, window=args.window)
            proxies = merge(manual, fred_proxies)

    overrides = parse_set(args.set)
    if overrides:
        proxies = merge(proxies, overrides)

    if args.show:
        print(json.dumps(proxies, ensure_ascii=False, indent=2))
        return 0

    score.run(proxies, date=args.date, history=args.history,
              note=args.note, sources=sources or None)
    return 0

if __name__ == "__main__":
    sys.exit(main())
