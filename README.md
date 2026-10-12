# Tulip Indicator (TI) v2.1

> A general-purpose *endogenous bubble-burst meter*. A single 0–100 index that detects the **buildup of fragility and the ignition** at the tail end of a boom — not valuation level, not a market-timing countdown.

**English** | [繁體中文](README.zh-TW.md)

Methodology is documented in [`METHODOLOGY.md`](METHODOLOGY.md) (methodology v2.0); the code is v2.1.0.

---

## Quick install

Pure Python 3.9+ standard library — no third-party dependencies, nothing to build.

```bash
git clone https://github.com/royalskynet/tulip-indicator && cd tulip-indicator && ./tulip.py
```

That single line clones the repo, scores the index, prints the full report (display TI, band + action, three-group readout, seven mechanism scores) and appends the run to `history/ti_history_v2.csv`.

**Prefer a `tulip` command on your PATH?**

```bash
pip install "tulip-indicator @ git+https://github.com/royalskynet/tulip-indicator" && tulip --version
```

**Driving it as a Claude skill?** The repo ships `SKILL.md` (rigid trigger + step-by-step runbook); drop the clone into your skills directory:

```bash
git clone https://github.com/royalskynet/tulip-indicator ~/.claude/skills/tulip-indicator
```

Requirements: Python 3.9 or newer, `git`, and network access for the FRED auto-fetch (optional — see [Updating the proxies](#updating-the-proxies)). `tulip.py` is committed with the executable bit set, so no `chmod` is needed after cloning.

---

## What it is

TI decomposes the causal chain common to every endogenous bubble into **seven mechanisms (M1–M7)**. Each is measured by the proxy variable that best fits the current era, scored as a **continuous percentile** against its own history, then weighted into a 0–100 "Tulip Value." 100 means the burst transmission is actively underway (the 1637 tulip mania, 1929, 2000, 2008 moment).

> Out of scope: exogenous shocks (pandemics, war, disasters). Those are a different class of event — never mixed in, no override.

---

## The seven mechanisms

| Code | Mechanism (fixed skeleton) | 2026 weight | Role |
|---|---|---|---|
| **M1** | Credit pricing (shadow-bank mismatch) | 25% | Lead + pulse |
| **M2** | Capex inflection (real capacity) | 18% | Lead |
| **M3** | Marginal-buyer exhaustion | 14% | Lead |
| **M4** | Leverage / credit expansion | 10% | Severity amplifier |
| **M5** | Concentration / false diversification | 10% | Structure |
| **M6** | Structural confirmation (synchronized ignition) | 15% | Pulse / confirm |
| **M7** | Sentiment / retail mania | 8% | Fuel gauge |

The mechanisms are the **fixed skeleton**; the proxies rotate with the era (1929 broker call loans → 2000 dot-com IPOs → 2008 mortgage securitization → 2026 AI capex × private credit × passive-ETF concentration). Weights float with the dominant bubble structure — see `METHODOLOGY.md` §8.

---

## The three-group readout

The seven mechanisms compute underneath; the report collapses them into three groups — *fuel, spark, fire*.

| Group | Contains | Reads |
|---|---|---|
| Amplifier (how much dry tinder) | M4 + M5 + M7 | How fragile / how bad it gets (can hover for years) |
| Leading fuse (is the spark lit) | M1 + M2 + M3 | Whether the lead inflection has begun — *the real clock* |
| Confirmation (is it burning) | M6 | Whether the cascade is transmitting — the final mile |

**Rule of thumb:** high amplifier + low fuse + flat confirmation = gasoline everywhere, match unlit (accumulation). Watch the *moment the leading fuse turns up*, not the absolute total.

---

## Display scale & bands

The internal raw danger line is 70; a monotone mapping pushes it to an intuitive **90** for display. Display 90 = fuse armed / danger line; 90–100 = the few-day pulse.

| TI (display) | State | Action |
|---|---|---|
| 0–50 | Calm | Normal allocation, check monthly |
| 50–75 | Accumulating | Stop adding risk, stress-test −35% |
| 75–90 | Alert / phased exit | **Phased-exit window, be out before 90**; check weekly |
| 90–100 | Underway / too late | Damage control, don't sell forced at the bottom |

**On the bailout point:** don't set the parachute at 90. By the time you see 90, that mile is already running and you are selling into the crash. **Exit in tranches from 75, be out before 90.** 75–90 is the action line; past 90 is just description.

---

## Running it

```
./tulip.py                      # single-file entry point (stdlib only)
./tulip.py --no-fred            # skip the FRED fetch
./tulip.py --show               # print the resolved proxy percentiles and exit
./tulip.py --set M1.hy_oas=45 --set M4.margin_debt_yoy=92
./tulip.py --selftest           # built-in assertions
./tulip.py --version

python3 -m tulip                # same thing via the installed package
```

| Flag | Effect |
|---|---|
| `--no-fred` | Skip the FRED auto-fetch and score the bundled manual percentiles only |
| `--set MECH.PROXY=PCT` | Override one proxy percentile (repeatable); `none` marks it unverified |
| `--show` | Print the resolved proxy JSON and exit without scoring |
| `--date YYYY-MM-DD` | Override the run date (default: today) |
| `--history PATH` | History CSV (default `history/ti_history_v2.csv`, created if missing) |
| `--note TEXT` | Free-text note stored alongside the row |
| `--window N` | Percentile window in days (default 756) |
| `--version` | Print the version |
| `--selftest` | `tulip.py` only: run the built-in assertions |

Run the smoke tests with:

```bash
PYTHONPATH=. python3 tests/test_smoke.py
```

(`python3 -m pytest tests/` works too if pytest is installed.)

### Updating the proxies

Two proxies are fetched automatically from FRED when `FRED_API_KEY` is present in the environment or in a `.env` file next to the working directory:

- `M1.hy_oas` — FRED series `BAMLH0A0HYM2` (high-yield OAS)
- `M1.hy_ig` — FRED series `BAMLH0A0HYM2` − `BAMLC0A0CM`, the high-yield minus investment-grade spread

Every other proxy is a **manual percentile** kept in `tulip/proxies.json` (the bundled `tulip.py` carries the same values inline). Refresh those per run — or let the Claude skill in `SKILL.md` do the fetching and scoring — and override individual values with `--set M1.hy_oas=45`. Without an API key the tool still runs, on the bundled numbers, and says so on stderr.

```bash
echo "FRED_API_KEY=your-key" > .env
```

`.env` is git-ignored. Never commit a key.

### Driving it from an agent

Tell Claude 「跑一次鬱金香指標」 / `!ti` / "run the Tulip Indicator". The agent walks the proxy list in `indicators.yaml`, fetches each one, percentile-scores against its own window, weights the seven mechanisms, emits the display TI + three-group readout, appends to `history/ti_history_v2.csv` and writes the traffic-light report defined in `SKILL.md`. `CLAUDE.md` is the same runbook in longer form for any model.

**Cadence:** TI < 50 monthly; 50–75 check the leading fuse weekly; > 75 full table weekly, M6 may be daily.

---

## Files

| File | Description |
|---|---|
| `tulip.py` | Single-file, stdlib-only entry point — clone and run |
| `tulip/cli.py` | CLI: FRED fetch, `--set` overrides, report, history append |
| `tulip/score.py` | Scoring engine: proxy percentiles → mechanisms → raw → display TI + three-group readout |
| `tulip/fred.py` | FRED fetch + percentile / spread helpers |
| `tulip/proxies.json` | Manual percentiles for the proxies that are not auto-fetched |
| `METHODOLOGY.md` | Full v2 methodology: mechanisms, percentile scoring, weights, display scale, falsification tests |
| `indicators.yaml` | Machine-readable spec: each proxy's fetch command, transform, window, thresholds |
| `SKILL.md` | RIGID skill trigger and steps |
| `CLAUDE.md` | Agent runbook (any model, including Sonnet) |
| `history/ti_history_v2.csv` | v2 reading log (raw value + percentile per proxy) |
| `history/ti_history.csv` | Deprecated v1.1 log (different schema, kept for history) |
| `CHANGELOG.md` | Version and threshold revisions — the guard against tuning rules to flatter the score |
| `tests/test_smoke.py` | Smoke tests for percentile, spread alignment, merge, overrides and bands |

---

## Discipline

- **No fitting to the past.** 2000/2008 are used only to catch broken proxies, never to tune weights (n≤5, fitting = self-deception).
- **Two-period confirmation.** A single-period band jump is labeled "pending confirmation".
- **No date predictions.** Time frames are expressed as conditional ranges plus historical analogues only.
- **Scores ignore your position.** No proxy score may be adjusted for the reader's holdings or mood.

---

## Disclaimer

The index is deliberately leading (M1+M2+M3 = 57% weight): it warns early, throws false bear signals, and can sit high for a long time — by design, not malfunction. Time frames rest on n≤5 historical analogues — conditional ranges, not forecasts. Prime directive: **never be forced to sell at the bottom**, not precise timing. Not investment advice.