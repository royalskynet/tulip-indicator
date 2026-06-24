# 鬱金香指標 · Tulip Indicator (TI) v2.0

> 泛用的「內生型經濟泡沫破滅計」。單一指數 0–100，偵測榮景尾端的**脆弱度累積與點火**——不是估值高低，不是擇時倒數。
>
> A general-purpose *endogenous bubble-burst meter*. A single 0–100 index that detects the **buildup of fragility and the ignition** at the tail end of a boom — not valuation level, not a market-timing countdown.

---

## 這是什麼 · What it is

**繁體中文**
TI 把跨所有內生泡沫都成立的因果鏈拆成**七個機制（M1–M7）**，每個機制用當代最貼切的代理變數量測，對各自的歷史分佈取**連續百分位**，再加權合成 0–100 的「鬱金香值」。100 ＝ 泡沫破滅的傳導正在發生（1637 鬱金香、1929、2000、2008 那一刻）。

> 不在範圍：外生衝擊（SARS、開戰、天災）。那是另一類事件，本指標不混入、不設 override。

**English**
TI decomposes the causal chain common to every endogenous bubble into **seven mechanisms (M1–M7)**. Each is measured by the proxy variable that best fits the current era, scored as a **continuous percentile** against its own history, then weighted into a 0–100 "Tulip Value." 100 means the burst transmission is actively underway (the 1637 tulip mania, 1929, 2000, 2008 moment).

> Out of scope: exogenous shocks (pandemics, war, disasters). Those are a different class of event — never mixed in, no override.

---

## 七機制 · The Seven Mechanisms

| 代碼<br>Code | 機制（不變骨架）<br>Mechanism (fixed skeleton) | 2026 權重<br>Weight | 角色 · Role |
|---|---|---|---|
| **M1** | 信貸計價 · Credit pricing (shadow-bank mismatch) | 25% | 領頭＋脈衝源 · Lead + pulse |
| **M2** | 資本支出轉折 · Capex inflection (real capacity) | 18% | 領頭 · Lead |
| **M3** | 邊際買家枯竭 · Marginal-buyer exhaustion | 14% | 領頭 · Lead |
| **M4** | 槓桿 · Leverage / credit expansion | 10% | 嚴重度放大器 · Severity amplifier |
| **M5** | 集中度/偽分散 · Concentration / false diversification | 10% | 結構 · Structure |
| **M6** | 結構確認 · Structural confirmation (synchronized ignition) | 15% | 脈衝源/確認 · Pulse / confirm |
| **M7** | 情緒/全民化 · Sentiment / retail mania | 8% | 油表 · Fuel gauge |

機制是**不變骨架**；代理隨時代換（1929 券商 call loan → 2000 dot-com IPO → 2008 房貸證券化 → 2026 AI capex × 私募信貸 × 被動 ETF 集中）。
Mechanisms are the **fixed skeleton**; proxies rotate with the era. Weights float with the dominant bubble structure — see `METHODOLOGY.md` §8.

---

## 三組摘要 · The Three-Group Readout

七機制在底層計算，報告層收斂成三組，一眼看懂「柴、火、燒」。
Seven mechanisms compute underneath; the report collapses them into three groups — *fuel, spark, fire*.

| 組 · Group | 含機制 · Contains | 讀什麼 · Reads |
|---|---|---|
| 放大器（乾柴多高）<br>Amplifier (how much dry tinder) | M4 + M5 + M7 | 結構多脆、爆了多慘（可高位盤旋數年）<br>How fragile / how bad it gets (can hover for years) |
| 領先引信（火星點了沒）<br>Leading fuse (is the spark lit) | M1 + M2 + M3 | 領先轉折是否開始——**這組才是計時器**<br>Whether the lead inflection has begun — *the real clock* |
| 確認（燒起來沒）<br>Confirmation (is it burning) | M6 | 災難是否正在傳導，亮即 90→100 那一哩<br>Whether the cascade is transmitting — the final mile |

**判讀口訣 · Rule of thumb:** 放大器高＋引信低＋確認趴 ＝ 滿地汽油、火柴未劃（累積期）。最該盯的是「領先引信」由低轉高那一刻，而非總分絕對值。
High amplifier + low fuse + flat confirmation = gasoline everywhere, match unlit (accumulation). Watch the *moment the leading fuse turns up*, not the absolute total.

---

## 顯示刻度與區間 · Display Scale & Bands

內部 raw 危險線在 70，對外做單調映射把危險線推到直覺的 **90**。顯示 90 ＝ 引信備妥/危險線；90–100 ＝ 那段幾天的脈衝。
Internal raw danger line is 70; a monotone mapping pushes it to an intuitive **90** for display. Display 90 = fuse armed / danger line; 90–100 = the few-day pulse.

| TI（顯示 · display） | 狀態 · State | 行動 · Action |
|---|---|---|
| 0–50 | 平靜 · Calm | 正常配置，每月查 · Normal allocation, check monthly |
| 50–75 | 累積 · Accumulating | 停止加碼風險，壓測組合能否扛 −35% · Stop adding risk, stress-test −35% |
| 75–90 | 警戒/逐步退場 · Alert / phased exit | **逐步退場窗口，90 前退完**；改週查 · Phased-exit window, be out before 90; check weekly |
| 90–100 | 進行中/太晚 · Underway / too late | 控損，不在底部被迫賣 · Damage control, don't sell forced at the bottom |

**關於跳機點 · On the bailout point：** 不要把跳傘設在 90。看到 90，那一哩已在進行、你是賣在下殺裡。**理想是 75 起分批退、90 前退完。** 75–90 是行動線，90 之後是描述線。
Don't set the parachute at 90 — by the time you see 90 you're selling into the crash. **Exit in tranches from 75, be out before 90.** 75–90 is the action line; past 90 is just description.

---

## 檔案 · Files

| 檔案 · File | 說明 · Description |
|---|---|
| `METHODOLOGY.md` | 完整方法論 v2：七機制、百分位計分、權重、顯示刻度、否證測試 · Full v2 methodology |
| `indicators.yaml` | 機讀規格：每代理的抓數指令、transform、視窗、閾值 · Machine-readable spec |
| `score.py` | 計分引擎：代理百分位 → 機制 → raw → 顯示 TI ＋三組摘要 · Scoring engine |
| `CLAUDE.md` | AI 代理執行指令（任何型號含 Sonnet 可接手）· Agent runbook |
| `SKILL.md` | RIGID skill 觸發與步驟 · Skill trigger & steps |
| `history/ti_history_v2.csv` | v2 歷次讀數紀錄（每代理原始值＋百分位）· v2 reading log |
| `history/ti_history.csv` | v1.1 舊紀錄（schema 不同，保留為歷史）· deprecated v1.1 log |
| `CHANGELOG.md` | 版本/權重修訂紀錄（防止為了分數好看而調規則）· Version & threshold revisions |

---

## 使用方式 · Usage

**對 Claude 說 · Tell Claude:**「跑一次鬱金香指標」/ `!ti` / "run the Tulip Indicator"。

代理會：逐項依 `indicators.yaml` 上網抓最新數據 → 對自身歷史窗取百分位 → 七機制加權 → 顯示 TI ＋三組摘要 → 追加 `history/ti_history_v2.csv` → 輸出紅黃綠燈報告與分析。
The agent fetches each proxy per `indicators.yaml`, percentile-scores against its own window, weights the seven mechanisms, emits the display TI + three-group readout, appends to `history/ti_history_v2.csv`, and writes a traffic-light report.

**手動計分 · Manual scoring:** 把當期百分位填入 `score.py` 的 `PROXIES` 後 `python3 score.py`。

**頻率 · Cadence:** TI < 50 每月；50–75 每週查領先引信；> 75 全表每週、M6 可每日。

---

## 紀律 · Discipline

- **不為過去擬合 · No fitting to the past**：2000/2008 只當否證抓壞代理，禁止為命中歷史調權重（n≤5，擬合＝自欺）。Used only to catch broken proxies, never to tune weights.
- **連續兩期確認遷移 · Two-period confirmation**：單期跳區先標「待確認」。
- **不給具體日期 · No date predictions**：時間框架只以區間 + 歷史類比表述。
- **分數不為情緒讓步 · Scores ignore your position**：不得因使用者倉位或情緒調整任何代理分數。

---

## 免責 · Disclaimer

**繁體中文**　本指數刻意偏領先（M1+M2+M3 共 57% 權重），會提前示警、有空頭假訊號、會在高位卡很久——這是特性不是失靈。時間框架基於 n≤5 的歷史類比，是條件區間而非預測。最高原則：**不被迫在底部賣出**，而非精準擇時。

**English**　The index is deliberately leading (M1+M2+M3 = 57% weight): it warns early, throws false bear signals, and can sit high for a long time — by design, not malfunction. Time frames rest on n≤5 historical analogues — conditional ranges, not forecasts. Prime directive: **never be forced to sell at the bottom**, not precise timing. Not investment advice.
