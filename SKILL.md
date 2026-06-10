---
name: tulip-indicator
description: >
  鬱金香指標（Tulip Indicator, TI）——泡沫崩解型大回調傳導鏈監測系統。
  合成四層指標（A 倉位→B 邊緣流動性→C 信貸→D 結構確認）為 0–100 的鬱金香值。
  觸發：「跑一次鬱金香指標」「今天 TI 多少」「鬱金香日報」「TI 更新」「bubble check」
metadata:
  emoji: "🌷"
  requires:
    tools: [web_search]
---

# 鬱金香指標（Tulip Indicator）執行 Skill

泡沫崩解型大回調的傳導鏈偵測器。四層加權合成 0–100 的「鬱金香值（TI）」。

## 觸發條件

用戶說以下任一詞語時啟動：
- 「跑一次鬱金香指標」「鬱金香指標」「TI 日報」「鬱金香日報」
- 「今天 TI 多少」「TI 更新」「bubble check」「鬱金香值」

## 執行流程

### Step 1 — 逐項抓數（用 web_search）

依以下 fetch 指令抓每個指標的最新值：

| 代碼 | 指標 | Fetch 指令 |
|---|---|---|
| A1 | NAAIM 主動經理人曝險指數 | 搜尋 "NAAIM Exposure Index latest" |
| A2 | AAII 股票配置% + 空頭情緒% | 搜尋 "AAII asset allocation survey stock allocation" + "AAII sentiment survey bearish" |
| A3 | BofA FMS 現金水位 | 搜尋 "BofA Global Fund Manager Survey cash level latest" |
| A4 | FINRA 保證金債務 YoY | 搜尋 "FINRA margin debt statistics latest" |
| A5 | 台股融資餘額 | 搜尋 "台股融資餘額最新" |
| B1 | ARKK/SPY 比值方向 | 搜尋 "ARKK SPY performance comparison" |
| B2 | BTC dominance + 山寨廣度 | 搜尋 "Bitcoin dominance BTC.D latest" |
| B3 | IPO 撤回 / 垃圾債流標 | 搜尋 "IPO withdrawn this month" + "junk bond deal pulled" |
| B4 | 台股當沖佔比 + 新開戶數 | 搜尋 "台股當沖比例" + "台股新開戶數" |
| C1 | HY OAS（FRED BAMLH0A0HYM2） | 搜尋 "ICE BofA high yield OAS spread current basis points" |
| C2 | AI 基建融資鏈壓力 | 搜尋 "CoreWeave AI data center debt financing 2026" |
| C3 | BDC 對 NAV 折價 | 搜尋 "BDC price to NAV discount average" |
| D1 | SPY 站上 200DMA 成分股% | 搜尋 "S&P 500 percent stocks above 200 day moving average" |
| D2 | VIX vs VIX3M | 搜尋 "VIX VIX3M term structure contango backwardation" |
| D3 | 美國初領失業金四週均值 | 搜尋 "initial jobless claims 4 week moving average FRED" |

抓不到的項目：計 0 分，標註「未驗證」。

### Step 2 — 計分

每項指標 **0（綠）/ 1（黃）/ 2（紅）**：

**Layer A（倉位，滿分10）**
- A1: 🟡 NAAIM >90 持續四週；🔴 四週內從 >90 急降至 <60
- A2: 🟡 股票配置 >70%；🔴 >70% 且現金 <15% 且空頭情緒 >40%（言行背離）
- A3: 🟡 現金水位 <4%；🔴 單月從 <4% 跳升 >0.5pp
- A4: 🟡 YoY >+25%；🔴 YoY 由正轉負
- A5: 🟡 創高且增速 > 大盤漲速；🔴 大盤距高點 <5% 但融資連兩週下降

A_score = (A實得 / 10) × 100

**Layer B（邊緣流動性，滿分8）**
- B1: 🟡 ARKK/SPY 比值見頂回落而 SPY 續創新高；🔴 背離 >2 個月
- B2: 🟡 BTC.D 上升且山寨普跌；🔴 該狀態持續 >1 個月
- B3: 🟡 當月 ≥1 起撤回/流標；🔴 當月 ≥3 起
- B4: 🟡 當沖 >40% 或 新開戶創高（擇一）；🔴 兩者同時成立

B_score = (B實得 / 8) × 100

**Layer C（信貸，滿分6）**
- C1: 🟡 >400bp；🔴 >500bp 且四週不回落
- C2: 🟡 利差走闊或評級展望轉負；🔴 大型借款方再融資失敗或債務重組
- C3: 🟡 折價 >10%；🔴 折價 >15% 且持續擴大

C_score = (C實得 / 6) × 100

**Layer D（結構確認，滿分6）**
- D1: 🟡 <50%；🔴 <40% 且指數距歷史高點 <5%
- D2: 🟡 VIX > VIX3M 出現；🔴 倒掛持續 ≥3 個交易日
- D3: 🟡 >260k；🔴 >300k 且趨勢向上

D_score = (D實得 / 6) × 100

**TI 計算：**
```
TI_base = 0.20×A_score + 0.30×B_score + 0.30×C_score + 0.20×D_score
```

**組合加成：**
- A1=🔴 且 C1≥🟡 → +10
- A2=🔴 且 B層任一=🔴 → +5
- C2=🔴 → +8
- B3=🔴 → +5

```
TI = min(100, TI_base + 組合加成)
```

### Step 3 — 輸出報告（固定格式）

```
## 🌷 鬱金香指標 | YYYY-MM-DD
TI = XX（前次 XX，YYYY-MM-DD）　狀態：[平靜/累積期/引信備妥/點火/進行中]

| 層 | 分數 | 亮燈項 |
|---|---|---|
| A 倉位 | xx | A3🟡 A4🟡 ... |
| B 邊緣流動性 | xx | ... |
| C 信貸 | xx | ... |
| D 結構確認 | xx | ... |
組合加成：+x（觸發條件）
未驗證：...

### 分析（3–5 句）
- 與前次比較：哪些指標變動
- 當前最值得盯的單一斷點
- 條件時間框架（附「歷史類比 n≤5」免責）

### 建議動作
[對應區間的一條行動建議]
```

## 區間判讀

| TI | 狀態 | 行動建議 |
|---|---|---|
| 0–20 | 平靜 | 正常配置，每月查 |
| 20–40 | 累積期 | 停止增加風險，確認組合可承受 -35% 不被迫賣 |
| 40–60 | 引信備妥 | 現金墊高，B/C 層改週查 |
| 60–80 | 點火 | 防禦配置完成，最後主動調整窗口 |
| 80–100 | 進行中 | 控損模式，不在底部被迫賣出 |

## 判讀紀律

- 狀態遷移需**連續兩期確認**，單期跳區間先標「待確認」
- 不得給出具體日期預測
- 時間框架只能以區間 + 歷史類比（n≤5）表述
- 本工具最高原則：**不被迫在底部賣出**，非精準擇時
