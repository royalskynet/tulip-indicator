---
name: tulip-indicator
description: "鬱金香指標（TI）v2：內生泡沫破滅計，0–100。七機制 M1–M7 加權（信貸/capex/邊際買家/槓桿/集中度/結構確認/情緒），代理對自身歷史取連續百分位，三組摘要（放大器/領先引信/確認）。含抓數清單、計分公式、報告模板。Endogenous bubble-burst meter, seven mechanisms, percentile scoring."
metadata:
  hermes:
    requires_toolsets: [web]
    tags: [market, risk, bubble, indicator, finance]
---

# 鬱金香指標 v2 執行 Skill · Tulip Indicator Runbook

**這是 RIGID skill。觸發後立即執行全部步驟，不要先描述你要做什麼，不要詢問確認，直接開始搜尋。**
**RIGID skill. On trigger, execute all steps immediately — don't describe, don't ask, start fetching.**

完整方法論見 `METHODOLOGY.md`，機讀規格見 `indicators.yaml`，計分引擎見 `score.py`。

## 觸發詞 · Triggers

**指令**：`!ti`（精確比對，立即執行）
**自然語言**：「跑一次鬱金香指標」「鬱金香指標」「TI 日報」「今天 TI 多少」「TI 更新」「bubble check」「run the tulip indicator」

---

## 核心模型 · Core Model（先懂再跑）

七機制 M1–M7（不變骨架），各以當代代理量測 → 對自身歷史窗取**百分位 0–100**（泡沫極端＝高）→ 加權 → raw → 顯示刻度。**無 bonus**。

| 機制 | 權重 | 組別 |
|---|---|---|
| M1 信貸計價 · Credit pricing | 25% | 領先引信 |
| M2 資本支出轉折 · Capex inflection | 18% | 領先引信 |
| M3 邊際買家枯竭 · Marginal-buyer exhaustion | 14% | 領先引信 |
| M4 槓桿 · Leverage | 10% | 放大器 |
| M5 集中度/偽分散 · Concentration | 10% | 放大器 |
| M6 結構確認 · Structural confirmation | 15% | 確認 |
| M7 情緒/全民化 · Sentiment | 8% | 放大器 |

---

## STEP 1：立刻執行以下搜尋，拿到即時數值 · Fetch now

用 web_fetch/web_search 逐代理取最新具體數字，抓不到標「未驗證」。優先 `primary_url`，空殼改 `search`：

```
# M1 信貸計價
M1.hy_oas:        FRED BAMLH0A0HYM2  →  "high yield OAS BAMLH0A0HYM2 latest"
M1.hy_ig:         FRED BAMLC0A0CM    →  "IG corporate OAS latest"（算 HY−IG）
M1.bdc_navdisc:   "MVIS BDC index price to NAV discount latest; BDC redemption gate"
# M2 資本支出轉折
M2.capex:         "Microsoft Alphabet Amazon Meta capex latest quarter operating cash flow"（capex YoY 二階導 × capex/OCF）
M2.ai_credit_fast:"AI data center high yield bond issuance spread latest; GPU rental price"
# M3 邊際買家枯竭
M3.ipo_withdrawal:stockanalysis.com/ipos/withdrawn/  →  "IPO withdrawn pulled latest month"
M3.inflow_decel:  "spot bitcoin ETF net flows latest; US equity ETF net inflows latest"
# M4 槓桿
M4.margin_debt:   FINRA margin statistics  →  "FINRA margin debt YoY latest"
M4.ai_debt:       "AI data center debt outstanding growth; leveraged loan issuance latest"
# M5 集中度
M5.mag7_share:    "Magnificent 7 share of S&P 500 market cap latest"
M5.xasset_corr:   "bond equity correlation tech AI latest"
# M6 結構確認
M6.breadth_200dma:barchart $S5TH  →  "S&P 500 percent above 200 day moving average latest"
M6.vix_term:      vixcentral.com   →  "VIX VIX3M ratio latest"（>1 倒掛）
M6.drawdown_ath:  "S&P 500 drawdown from all time high latest"
# M7 情緒
M7.ipo_pop_fomo:  "IPO first day pop median latest year; retail FOMO"
M7.positioning:   "BofA fund manager survey cash equity overweight latest; AAII allocation; 0DTE volume"
```

**抓取分級**：primary_url → search → 標「未驗證」。禁止用記憶舊值或推測補值。

---

## STEP 2：代理 → 百分位 → 機制 → raw → 顯示 · Score

1. **代理百分位**：對自身歷史窗取 percentile（0–100，泡沫極端＝高）。
   - 視窗：市場/日頻 504–756 日｜capex 季度 8–12 季｜流量 24–36 月。
   - 水位類直接取值取百分位；轉折類先算 RoC/二階導再取百分位。
   - 自存歷史不足 → 以外部序列 bootstrap，旗標 `bootstrapped=true`。
2. **機制**：`M_i = mean(可得代理百分位)`。缺代理只對可得者平均並重正規化、旗標未驗證；機制不憑空補值。
3. **raw**：`raw = Σ(w_i · M_i)`；缺整個機制 → 對可得權重重新正規化。
4. **顯示刻度**：
   ```
   raw ≤ 70 : display = raw × 90/70
   raw > 70 : display = 90 + (raw−70)/3
   ```
   顯示 90 ＝ 引信備妥/危險線；90–100 ＝ 幾天的脈衝段。

> 可直接用 `score.py`：把當期百分位填入 `PROXIES` 後 `python3 score.py`，輸出顯示 TI、區間、三組摘要，並可寫 history。

---

## STEP 3：輸出固定格式報告 · Report

```
## 🌷 鬱金香指標 v2 | YYYY-MM-DD
TI = XX（顯示；raw XX）　前次 XX（YYYY-MM-DD）　狀態：[平靜/累積/警戒-逐步退場/進行中-太晚]

### 三組摘要
| 組 | 分數 | 讀什麼 |
|---|---|---|
| 放大器（乾柴多高） M4+M5+M7 | xx | 結構多脆、爆了會多慘 |
| 領先引信（火星點了沒） M1+M2+M3 | xx | ← 計時器，最該盯 |
| 確認（燒起來沒） M6 | xx | 亮即 90→100 那一哩 |

### 七機制明細
| 機制 | 百分位 | 主要代理讀數 |
| M1…M7 | xx | 實際數值（第 xx 百分位） |

未驗證：…

### 分析（3–5 句）
- 與前次比較（強調領先引信有無由低轉高）
- 當前最值得盯的單一斷點
- 條件時間框架（必附「歷史類比 n≤5」免責）

### 建議動作
[對應區間一條，不多給]
```

完成後追加一列到 `history/ti_history_v2.csv`（格式見表頭）。

---

## 區間對照 · Bands（顯示刻度）

| TI | 狀態 | 建議 |
|---|---|---|
| 0–50 | 平靜 | 正常配置，每月查 |
| 50–75 | 累積 | 停止加碼風險，壓測能否扛 −35% |
| 75–90 | 警戒/逐步退場 | **逐步退場窗口，90 前退完**；改週查 M1/M2/M6 |
| 90–100 | 進行中/太晚 | 控損，不在底部被迫賣 |

**判讀口訣**：放大器高＋引信低＋確認趴 ＝ 滿地汽油、火柴未劃（累積期）。盯「領先引信」由低轉高那一刻，非總分。

## 判讀紀律 · Discipline

- 不得給具體日期預測；時間框架只以區間 + 歷史類比（n≤5）表述。
- 狀態遷移需連續兩期確認，單期跳區先標「待確認」。
- 不得因使用者倉位或情緒調整任何代理分數。
- 不為過去擬合：2000/2008 只當否證抓壞代理，禁止為命中歷史調權重。
- 最高原則：**不被迫在底部賣出**，非精準擇時。
